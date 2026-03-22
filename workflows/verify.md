# Workflow: verify

Evaluate strategy results through an interactive HTML report. Present AI assessment with specific metrics vs targets. Handle --approved (close milestone, generate export package) or --debug (diagnose failure, open new phase cycle).

Follow these sections in order, top to bottom. Each section contains behavioral instructions -- read them, then execute them using your tools (Read, Write, Bash, Glob). Do NOT skip sections unless explicitly told to.

---

## Preamble: Version Check

**This check is silent and best-effort. It MUST NOT block or delay the workflow.**

1. Check if the version check was done recently:
   Run via Bash: `find ~/.pmf/.last_version_check -mtime -1 2>/dev/null`
   - If the command outputs the filename, the check was done within the last 24 hours -- SKIP the rest of this preamble and proceed to the next section.
   - If the command outputs nothing (file missing or older than 24h), continue.

2. Read `~/.pmf/.version` to get the current installed version:
   - Use the Read tool to read `~/.pmf/.version` and parse the JSON to extract the `version` field.
   - If the file does not exist, SKIP the rest of this preamble silently.

3. Check npm for the latest version:
   Run via Bash: `npm view @print-money-factory/cli version 2>/dev/null`
   - If the command fails (network error, package not found), SKIP silently -- no error, no notice.

4. Compare versions:
   - If the npm version differs from the installed version, display exactly:
     `Update available: v{current} -> v{latest}. Run /brrr:update`
   - If versions match, display nothing.

5. Update the timestamp file:
   Run via Bash: `touch ~/.pmf/.last_version_check`
   This gates the check to once per 24 hours.

---

## Preamble: Sequence Validation

Before anything else, verify that execute has been completed for the current phase.

1. Use the Read tool to check if `.pmf/STATE.md` exists
2. If it does not exist, STOP immediately:

```
[STOP] Cannot run verify -- no milestone exists.

No milestone exists. Create one first to define your strategy scope and targets.

Next step: `/brrr:new-milestone`
```

3. If it exists, read it and find:
   - **Status** field (must be "IN PROGRESS")
   - **Current Phase** number (N)
   - Whether Execute is marked done for phase N: look for `- [x] Execute` under Phase N
4. If Status is not "IN PROGRESS", STOP:

```
[STOP] Cannot run verify -- milestone is not active.

Current milestone status: {status}

To start a new milestone: /brrr:new-milestone
```

5. If Execute is NOT done for Phase N, STOP:

```
[STOP] Cannot verify: execute phase has not completed. Run /brrr:execute first.
```

6. If Verify is already checked for Phase N, STOP:

```
[STOP] Cannot run verify -- Phase {N} verify is already completed.

The verify phase generates the report and handles approval/debug.
Running it again would overwrite the existing report and export package.

Current position:
  Phase {N}:
    [DONE] Discuss
    [DONE] Research
    [DONE] Plan
    [DONE] Execute
    [DONE] Verify

This milestone is either closed or ready for the next cycle.
```

7. If Execute IS done and Verify is NOT done, proceed to the next section.

---

## Preamble: Context File Scan

Scan `.pmf/context/` for files the user may have dropped in for reference.

1. If `--no-context` was passed as an argument, skip this entire section
2. Use Glob to check if `.pmf/context/` directory exists and list all files in it: `.pmf/context/**/*`
3. If the directory does not exist or is empty, proceed to the next section
4. If `.pmf/STATE.md` exists, read the Processed Context table to identify which files have already been processed
5. Identify NEW files (present in directory but not in the Processed Context table)
6. If there are no new files, proceed to the next section
7. If there are new files, process them using the same pattern as new-milestone (images, PDFs, text files):
   - For each new file, read it (images via multimodal, PDFs via Read tool, text via Read tool)
   - Summarize what the file contains
   - Ask the user: "I found this context file. Should I incorporate it into the current verification? (yes/no)"
   - Record processed files for STATE.md update later
8. Proceed to the next section

---

## Preamble: Parse Arguments

Parse `$ARGUMENTS` for verification flags.

Supported flags:
- `--approved` -- Skip to approval flow after report generation and AI assessment. Closes the milestone and generates the full export package.
- `--debug` -- Skip to debug flow after report generation and AI assessment. Creates diagnosis document and opens new phase cycle.
- Neither flag -- Generate report, show AI assessment, then ask the user to choose.

Parse rules:
1. If `$ARGUMENTS` is empty or not provided, set mode to "interactive" (ask user after assessment)
2. If `--approved` is present, set mode to "approved"
3. If `--debug` is present, set mode to "debug"
4. If both `--approved` and `--debug` are present, STOP with error: "Cannot pass both --approved and --debug. Choose one."
5. Store the parsed mode for use throughout the workflow

---

## Step 1: Load Inputs

Gather all information needed for report generation and assessment.

1. Read `.pmf/STATE.md` and extract:
   - **Current Phase** number (N)
   - **Phase history** (previous debug cycles if any)

2. Read `.pmf/STRATEGY.md` and extract:
   - **Strategy name**
   - **Asset** (e.g., BTC/USDT, AAPL, EUR/USD)
   - **Timeframe** (e.g., 1H, 4H, 1D)
   - **Success criteria / targets** (Sharpe target, Max DD target, Win Rate target, etc.)
   - **Strategy type** (trend-following, mean-reversion, breakout, custom)

3. Read `.pmf/phases/phase_N_best_result.json` and extract:
   - **Best parameters** (the optimized parameter values)
   - **IS metrics** (in-sample performance: Sharpe, Max DD, Win Rate, Profit Factor, Trades, Net P&L)
   - **OOS metrics** (out-of-sample performance, if available)
   - **Stop reason** (MINT, PLATEAU, REKT, NO DATA)

4. Read `.pmf/phases/phase_N_plan.md` and extract:
   - **Optimization method** (grid_search, random_search, walk_forward) -- needed for heatmap decision
   - **Parameter space** (for report context)

5. Count iteration artifacts:
   - Use Glob to list `.pmf/phases/phase_N_execute/iter_*_verdict.json`
   - Count = number of completed iterations

6. Check for cached OHLCV data:
   - Use Glob to list `.pmf/cache/*.parquet`
   - If no parquet files found, note: regime breakdown and benchmark stats will be skipped

7. Display loading summary:

```
Loading {iteration_count} iterations for {strategy_name}...

  Asset:          {asset}
  Timeframe:      {timeframe}
  Optimization:   {method} ({iteration_count} iterations)
  Best Sharpe:    {sharpe} (target: {target})
  Stop reason:    {stop_reason}
```

---

## Step 2: Generate Report

Write and execute a Python script that calls the report generator module.

1. Create the verify directory if it does not exist:

```bash
mkdir -p .pmf/phases/phase_N_verify
```

2. Write a Python script to `.pmf/phases/phase_N_verify/generate_report_script.py`:

```python
"""Generate the verify report by calling report_generator module."""
import sys
import os
import json

# Add references directory to path so we can import report_generator
refs_dir = os.path.expanduser("~/.pmf/references")
sys.path.insert(0, refs_dir)

from report_generator import generate_report

# Configuration -- replace with actual values
phase_dir = ".pmf/phases"
strategy_name = "{strategy_name}"
targets = {targets_dict}  # e.g., {"sharpe_ratio": 1.5, "max_drawdown": -0.15}
output_path = ".pmf/phases/phase_{N}_verify/report_v{N}.html"
template_path = os.path.expanduser("~/.pmf/templates/report-template.html")
cache_dir = ".pmf/cache"
plan_path = ".pmf/phases/phase_{N}_plan.md"

try:
    result = generate_report(
        phase_dir=phase_dir,
        strategy_name=strategy_name,
        targets=targets,
        output_path=output_path,
        template_path=template_path,
        cache_dir=cache_dir,
        plan_path=plan_path
    )
    print(f"SUCCESS:{result}")
except Exception as e:
    print(f"ERROR:{e}", file=sys.stderr)
    sys.exit(1)
```

3. Execute the script:

```bash
~/.pmf/venv/bin/python .pmf/phases/phase_N_verify/generate_report_script.py
```

4. Check the result:

   - If the script exits with an error, display:
   ```
   Report generation failed: {python_error}. Check that all iteration artifacts exist in .pmf/phases/.
   ```
   Then STOP -- do not proceed without a valid report.

   - If the script succeeds, display:
   ```
   Report generated: .pmf/phases/phase_{N}_verify/report_v{N}.html

   You can open this file in your browser to explore the interactive charts.
   ```

---

## Step 3: AI Analysis

Formulate a specific assessment of the strategy's performance. This is YOUR analysis -- write it directly based on the data you loaded, not by running another script.

1. **Read the data you need:**
   - Re-read `.pmf/phases/phase_N_best_result.json` for all metrics
   - Read iteration verdict files to understand the optimization trajectory
   - If cached OHLCV data exists, note regime information from the report data
   - Read targets from STRATEGY.md

2. **Compare each metric against targets:**

   For each target defined in STRATEGY.md:
   - Sharpe Ratio: compare best IS Sharpe vs target. Note IS vs OOS if available.
   - Max Drawdown: compare best Max DD vs target (less negative = better)
   - Win Rate: compare vs target if defined
   - Profit Factor: compare vs target if defined
   - Total Trades: check minimum trade count if defined
   - Net P&L: report as dollar/percentage value

3. **Formulate the assessment** in the tone of a senior quant reviewing a backtest:

Begin with:
```
Here's my assessment of your {strategy_name} backtest results:
```

Then cover these points (adapt to the specific results):

   a. **Target comparison:** State which targets were met and which were not. Use specific numbers: "Sharpe of 1.82 exceeds your target of 1.5" or "Max drawdown of -18.3% is worse than your -15% target."

   b. **Equity curve observations:** Comment on the shape based on available data. Look for:
      - Long flat periods (strategy may not work in certain conditions)
      - Sharp drawdowns (risk events)
      - Consistent growth vs erratic jumps (sustainability)

   c. **IS vs OOS comparison:** If OOS metrics are available, compare them to IS. A large divergence (e.g., IS Sharpe 2.5, OOS Sharpe 0.8) signals overfitting. Comment specifically: "The IS Sharpe of 2.5 drops to 0.8 out-of-sample -- this is a strong overfitting signal."

   d. **Regime observations:** If regime data is available, note the performance distribution. "80% of profits came from the bull regime" or "The strategy loses money in sideways markets."

   e. **Trade count and frequency:** Comment on whether the trade count is sufficient for statistical significance (generally 30+ trades minimum).

   f. **Stop reason context:** Explain what the stop reason means:
      - MINT: "Optimization hit targets -- the strategy meets your criteria."
      - PLATEAU: "Results plateaued after N iterations -- further optimization unlikely to improve."
      - REKT: "Strategy consistently underperformed -- fundamental approach may need revision."
      - NO DATA: "Data issues prevented full optimization."

   g. **Overall recommendation:** Conclude with a clear directional statement. Examples:
      - "Overall, this strategy shows consistent performance across conditions. I recommend approving."
      - "The overfitting signal is concerning. I recommend debugging to investigate the IS/OOS divergence."
      - "Results are borderline -- the strategy works but doesn't comfortably exceed targets. Your call."

4. **Important:** This assessment should be 3-6 paragraphs. Not a bullet list. Write it like you're talking to a trader.

---

## Step 4: Present Choice

After showing the AI assessment, present the user with their options.

### If all targets are met:

```
All targets met. Ready to approve and generate export package?

  --approved: Close milestone, generate export package
  --debug: AI diagnosis, open new phase cycle
```

### If some targets are NOT met:

```
Some targets were not met. You can still approve if the results are acceptable, or debug to investigate further.

  --approved: Close milestone, generate export package
  --debug: AI diagnosis, open new phase cycle
```

### Route based on mode:

1. **If mode is "approved":**
   - If ALL targets met: proceed directly to Step 5a
   - If targets NOT met: show force-approve warning, then proceed to Step 5a:
   ```
   Warning: Approving with unmet targets. Your targets were: {list of unmet targets with values}. Proceeding anyway.
   ```

2. **If mode is "debug":**
   - Proceed directly to Step 5b

3. **If mode is "interactive":**
   - Present the choice and ask: "Which path would you like to take? (approve/debug)"
   - Wait for user response
   - If user says approve/approved/yes: proceed to Step 5a (with force-approve warning if targets not met)
   - If user says debug: proceed to Step 5b

---

## Step 5a: --approved Path (Export Package)

Close the milestone and generate the complete export package. All exports go in `.pmf/output/` per D-14.

### 5a.1: Create Output Directory

```bash
mkdir -p .pmf/output
```

### 5a.2: Generate PineScript Files (EXPT-01)

Read these references before generating PineScript code:

- `~/.pmf/references/pinescript-rules.md` (syntax rules -- the v5 reference)
- `~/.pmf/templates/pinescript-template.pine` (structural template)
- `~/.pmf/references/pinescript-examples/trend-following.pine` (complete example)
- `~/.pmf/references/pinescript-examples/mean-reversion.pine` (complete example)
- `~/.pmf/references/pinescript-examples/breakout.pine` (complete example)

Read strategy context:

- `.pmf/STRATEGY.md` for strategy logic overview, asset, timeframe
- `.pmf/phases/phase_N_discuss.md` for detailed entry/exit conditions, indicators, parameters
- `.pmf/phases/phase_N_best_result.json` for optimized parameter values

**Generate `pinescript_v5_strategy.pine`:**

Write a complete PineScript v5 strategy script to `.pmf/output/pinescript_v5_strategy.pine`:

```pine
// {strategy_name} - TradingView Strategy
//@version=5
strategy("{strategy_name}", overlay=true, initial_capital={initial_capital},
         default_qty_type=strategy.percent_of_equity, default_qty_value=100,
         commission_type=strategy.commission.percent, commission_value={commission})

// Note: This is PineScript v5. For v6 migration, see:
// https://www.tradingview.com/pine-script-docs/migration-guides/to-pine-version-6/
// Key v6 change: int/float no longer implicitly cast to bool -- use explicit comparisons.

// === INPUTS ===
// {All parameters from best_result.json as input() calls with best values as defaults}

// === INDICATORS ===
// {Indicator calculations from discuss decisions}

// === SIGNALS ===
// {Entry and exit conditions from discuss decisions}

// === EXECUTION ===
// {strategy.entry(), strategy.close(), strategy.exit() calls}

// === PLOTTING ===
// {Plot indicators for visual confirmation}
```

Rules:
- Use `strategy.entry()`, `strategy.close()`, `strategy.exit()` -- NEVER plotshape/alert in strategy scripts
- All parameters as `input.int()` / `input.float()` with best values as defaults
- Include stop loss via `strategy.exit()` with `stop=` parameter
- Include take profit if the strategy uses one
- Use `if` blocks for conditional execution (not `when` parameter)
- Translate the Python backtest logic to PineScript faithfully

**Generate `pinescript_v5_indicator.pine`:**

Write a complete PineScript v5 indicator script to `.pmf/output/pinescript_v5_indicator.pine`:

```pine
// {strategy_name} - TradingView Indicator (Signals + Alerts)
//@version=5
indicator("{strategy_name} Signals", overlay=true)

// Note: This is PineScript v5. For v6 migration, see:
// https://www.tradingview.com/pine-script-docs/migration-guides/to-pine-version-6/
// Key v6 change: int/float no longer implicitly cast to bool -- use explicit comparisons.

// === INPUTS ===
// {Same parameters as strategy version}

// === INDICATORS ===
// {Same indicator calculations}

// === SIGNALS ===
// {Same conditions}

// === VISUAL SIGNALS ===
// plotshape() for entry/exit markers on chart

// === ALERTS ===
// alert() for modern alerts
// alertcondition() for user-configurable alerts

// === PLOTTING ===
// {Plot indicators}
```

Rules:
- NEVER use `strategy.*` functions in indicator scripts
- Use `plotshape()` for visual signals (triangle up below bar for buy, triangle down above bar for sell)
- Include BOTH `alert()` and `alertcondition()` for maximum compatibility
- Same parameters and signal logic as the strategy version

**After generating both files, display:**

```
Note: PineScript output has not been validated against TradingView. Paste into Pine Editor to verify before live use.
```

### 5a.3: Generate trading-rules.md (EXPT-02)

Read `.pmf/STRATEGY.md` and `.pmf/phases/phase_N_discuss.md` for strategy logic.
Read `.pmf/phases/phase_N_best_result.json` for optimized parameters.

Write `.pmf/output/trading-rules.md` in practitioner tone:

```markdown
# Trading Rules: {strategy_name}

## Setup Conditions

{What conditions need to be true before looking for entries.
Example: "Wait for ADX > 25 to confirm a trending market.
Only trade during the London or New York session."}

## Entry Rules

### Long Entry
{Specific entry conditions written as instructions.
Example: "Enter long when:
1. Fast EMA (10) crosses above Slow EMA (50)
2. ADX is above 25
3. Price is above the 200 SMA
Enter at the next bar's open after all conditions are met."}

### Short Entry
{If applicable. Same format.}

## Exit Rules

### Stop Loss
{Specific stop loss rule.
Example: "Stop: 1.5x ATR below entry price.
For a trade entered at $100 with ATR of $2, stop is at $97."}

### Take Profit
{If applicable.
Example: "Target: 3x ATR above entry (2:1 R:R)."}

### Signal Exit
{When to exit based on signals rather than stops.
Example: "Close long when Fast EMA crosses below Slow EMA."}

## Position Sizing

{Position sizing rule from the strategy.
Example: "Risk 1% of account per trade. Calculate position size:
Position Size = (Account * 0.01) / (Entry Price - Stop Price)"}

## Risk Management

- Maximum {N} open positions at a time
- Do not trade during major news events
- {Any strategy-specific risk rules}

## Best Parameters

These are the optimized parameters from backtesting:

| Parameter | Value |
|-----------|-------|
| {param1}  | {value1} |
| {param2}  | {value2} |
| ...       | ...   |

**Test period:** {start_date} to {end_date}
**Asset:** {asset}
**Timeframe:** {timeframe}
```

### 5a.4: Generate performance-report.md (EXPT-03)

Write `.pmf/output/performance-report.md`:

```markdown
# Performance Report: {strategy_name}

## Strategy Summary

- **Strategy type:** {type}
- **Asset:** {asset}
- **Timeframe:** {timeframe}
- **Test period:** {start_date} to {end_date}
- **Optimization:** {method} over {iteration_count} iterations
- **Stop reason:** {stop_reason}

## Performance Metrics

| Metric | Value | Target | Status |
|--------|-------|--------|--------|
| Sharpe Ratio | {value} | {target} | {MET/NOT MET} |
| Max Drawdown | {value} | {target} | {MET/NOT MET} |
| Win Rate | {value} | {target} | {MET/NOT MET} |
| Profit Factor | {value} | {target} | {MET/NOT MET} |
| Total Trades | {value} | {target} | {MET/NOT MET} |
| Net P&L | {value} | -- | -- |
| Sortino Ratio | {value} | -- | -- |
| Calmar Ratio | {value} | -- | -- |

## In-Sample vs Out-of-Sample

| Metric | In-Sample | Out-of-Sample | Divergence |
|--------|-----------|---------------|------------|
| Sharpe | {is_value} | {oos_value} | {diff} |
| Max DD | {is_value} | {oos_value} | {diff} |
| Win Rate | {is_value} | {oos_value} | {diff} |

{Comment on IS/OOS comparison. Flag overfitting if divergence is large.}

## Key Statistics

- **Best iteration:** #{iter_num}
- **Average trade duration:** {duration}
- **Largest winning trade:** {value}
- **Largest losing trade:** {value}
- **Max consecutive winners:** {value}
- **Max consecutive losers:** {value}

## Data Source

- **Provider:** {source} (e.g., yfinance, ccxt/Binance, Dukascopy)
- **Data quality:** {any notes about gaps, splits, etc.}
```

### 5a.5: Generate backtest_final.py (EXPT-04)

Write `.pmf/output/backtest_final.py` -- a fully self-contained, reproducible backtest script.

This is a critical file. Read these before generating:

- `.pmf/phases/phase_N_discuss.md` for strategy logic
- `.pmf/phases/phase_N_best_result.json` for best parameters
- `~/.pmf/references/backtest_engine.py` for the engine pattern
- `~/.pmf/references/metrics.py` for metrics computation
- `~/.pmf/references/data_sources.py` for data download pattern

Write the script:

```python
"""Reproducible backtest: {strategy_name}. Run with: python backtest_final.py"""

import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from datetime import datetime
import os
import sys

# === CONFIGURATION ===
# Best parameters from optimization
PARAMS = {best_params_dict}

# Data settings
ASSET = "{asset}"
TIMEFRAME = "{timeframe}"
START_DATE = "{start_date}"
END_DATE = "{end_date}"
INITIAL_CAPITAL = {initial_capital}
COMMISSION = {commission_rate}

# === DATA LOADING ===
def load_data():
    """Load OHLCV data. Tries primary source, falls back to cached file."""
    # Try primary source
    try:
        {data_loading_code_from_strategy}
    except Exception as e:
        print(f"Primary data source failed: {e}")
        # Fall back to cached parquet
        cache_path = os.path.join(os.path.dirname(__file__), "..", "cache",
                                   f"{asset_filename}.parquet")
        if os.path.exists(cache_path):
            print(f"Using cached data from {cache_path}")
            return pd.read_parquet(cache_path)
        # Fall back to CSV
        csv_path = os.path.join(os.path.dirname(__file__), "..", "cache",
                                 f"{asset_filename}.csv")
        if os.path.exists(csv_path):
            print(f"Using cached data from {csv_path}")
            return pd.read_csv(csv_path, parse_dates=['date'], index_col='date')
        raise FileNotFoundError("No data source available. Place OHLCV data "
                                "in the cache directory or ensure network access.")

# === STRATEGY LOGIC ===
def calculate_signal(df, i, position, params):
    """Calculate trading signal for bar i.

    Args:
        df: OHLCV DataFrame
        i: Current bar index (integer position)
        position: Current position (1=long, -1=short, 0=flat)
        params: Strategy parameters dict

    Returns:
        str: 'BUY', 'SELL', 'SHORT', 'COVER', or 'HOLD'
    """
    {signal_logic_from_discuss}

# === BACKTEST ENGINE ===
{include_backtest_engine_code}

# === METRICS ===
{include_metrics_computation_code}

# === MAIN ===
if __name__ == "__main__":
    print(f"Running backtest: {strategy_name}")
    print(f"Asset: {ASSET}, Timeframe: {TIMEFRAME}")
    print(f"Period: {START_DATE} to {END_DATE}")
    print()

    # Load data
    df = load_data()
    print(f"Loaded {len(df)} bars")

    # Run backtest
    trades, equity_curve = run_backtest(df, PARAMS, INITIAL_CAPITAL, COMMISSION)
    print(f"Completed: {len(trades)} trades")

    # Compute metrics
    metrics = compute_all_metrics(trades, INITIAL_CAPITAL)

    # Display results
    print()
    print("=" * 50)
    print("RESULTS")
    print("=" * 50)
    for key, value in metrics.items():
        if isinstance(value, float):
            print(f"  {key:20s}: {value:.4f}")
        else:
            print(f"  {key:20s}: {value}")

    # Plot equity curve
    plt.figure(figsize=(12, 6))
    plt.plot(equity_curve, label='Strategy Equity')
    plt.title(f'{strategy_name} - Equity Curve')
    plt.xlabel('Bar')
    plt.ylabel('Equity ($)')
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig('equity_curve.png', dpi=100)
    print()
    print("Equity curve saved to: equity_curve.png")
```

Rules:
- The script MUST be self-contained -- include the backtest engine and metrics computation inline
- Use the exact `calculate_signal()` function from the execute phase
- Hardcode best parameters as defaults (not input prompts)
- Include both primary data source and fallback to cached parquet/CSV
- Use matplotlib (Agg backend) for the equity curve PNG -- no browser dependency
- Print a clear results summary

### 5a.6: Generate live-checklist.md (EXPT-05)

Write `.pmf/output/live-checklist.md`:

```markdown
# Live Trading Checklist: {strategy_name}

## Before You Start

- [ ] **Paper trade first.** Run this strategy on a demo/paper account for at least 2 weeks before risking real money.
- [ ] **Verify PineScript.** Paste `pinescript_v5_strategy.pine` into TradingView Pine Editor and run on historical data. Compare results with the backtest.
- [ ] **Set up alerts.** Load `pinescript_v5_indicator.pine` on your chart and configure alerts for entry/exit signals.

## Broker Setup

- [ ] Account funded with at least {initial_capital_recommendation} (recommended minimum to match backtest assumptions)
- [ ] Commission/fee structure matches backtest assumption ({commission_rate})
- [ ] Margin requirements understood for {asset}
- [ ] Order types available: market, limit, stop

## Position Sizing

- [ ] Calculate position size before each trade:
  - Account risk per trade: {risk_per_trade}
  - Position size = (Account * Risk%) / (Entry - Stop)
- [ ] Never risk more than {max_risk}% of account on a single trade
- [ ] Account for slippage: expect {slippage_estimate} per trade

## Strategy-Specific Setup

- [ ] Chart set to **{timeframe}** timeframe
- [ ] Required indicators added to chart:
  {list_of_indicators}
- [ ] Trading during **{optimal_sessions}** (when {asset} has sufficient liquidity)
- [ ] Signal checking frequency: every {signal_frequency}

## Risk Controls

- [ ] Daily loss limit set: stop trading after {daily_loss_limit} losing trades or {daily_loss_pct}% account drawdown
- [ ] Weekly review scheduled to compare live results vs backtest
- [ ] Maximum drawdown kill switch: stop trading if account drops {max_dd_threshold}% from peak
- [ ] Do NOT override stops -- the backtest results assume mechanical execution

## Common Mistakes to Avoid

- [ ] **Don't trade during major news events** unless your strategy specifically handles them. Check economic calendar before trading.
- [ ] **Don't modify parameters** without re-running the backtest. The optimized parameters are a set -- changing one may invalidate others.
- [ ] **Don't skip trades.** Cherry-picking signals invalidates the expected win rate and profit factor.
- [ ] **Don't widen stops** to avoid a loss. The stop level is calibrated to the strategy's risk profile.

## Journaling

- [ ] Record every trade: entry time, exit time, direction, P&L, notes
- [ ] After 30 trades, compare your live metrics to the backtest:
  - Win rate within 10% of backtest?
  - Average trade P&L similar?
  - Max consecutive losers within expectations?
- [ ] If live performance diverges significantly from backtest, stop trading and investigate.

## Emergency Procedures

- [ ] If spread widens abnormally (>3x normal), skip the signal
- [ ] If price gaps through your stop, assess actual loss vs expected loss
- [ ] If you experience 3 consecutive max-size losses, pause for 24 hours
```

### 5a.7: Copy Report HTML (EXPT-06)

Copy the generated HTML report to the output directory:

```bash
cp .pmf/phases/phase_N_verify/report_v{N}.html .pmf/output/report_v{N}.html
```

### 5a.8: Generate bot-building-guide.md (EXPT-08)

Read strategy context:

- `.pmf/STRATEGY.md` for asset class, exchange/source, timeframe
- `.pmf/phases/phase_N_discuss.md` for strategy logic details
- `.pmf/phases/phase_N_best_result.json` for optimized parameter values
- `.pmf/output/trading-rules.md` for cross-reference with entry/exit rules

Detect platform from STRATEGY.md:

- Crypto assets (BTC, ETH, SOL, pairs with USDT/BTC, or exchange names like Binance/Bybit) -> Exchange API section using ccxt
- Stock assets (ticker symbols like SPY, AAPL, TSLA, or broker names like Alpaca/IBKR) -> Broker API section (Alpaca, Interactive Brokers)
- Forex assets (pairs like EUR/USD, GBP/JPY, or "forex" in strategy type) -> MT5/OANDA section
- Ambiguous -> Include brief sections for all applicable platforms

Write `.pmf/output/bot-building-guide.md` in practitioner tone, using direct second-person language throughout ("Set your API key...", "Configure position size to..."). Target audience is an experienced trader who knows their platform but hasn't automated this specific strategy. Use actual parameter values from best_result.json, not generic `{placeholder}` syntax. Code snippets are at the pattern level -- showing API call structure, not a full runnable bot.

```markdown
# Bot Building Guide: {strategy_name}

> **Risk Warning:** This guide assumes you've validated the strategy in backtesting.
> Past performance does not guarantee future results. Start with paper trading
> or minimal position sizes.

## 1. Prerequisites

{Platform-specific requirements based on detected asset class.
Use the actual asset and exchange/source from STRATEGY.md.

For crypto: Exchange account (e.g., Binance, Bybit), API key with trading permissions,
Python 3.10+ with ccxt installed.

For stocks: Brokerage account (e.g., Alpaca, Interactive Brokers), API credentials,
Python 3.10+ with alpaca-py or ib_async installed.
NOTE: Use ib_async, NOT ib_insync (ib_insync is archived, ib_async is the active fork).

For forex: MT5 terminal (Windows only) or OANDA account, API access token,
Python 3.10+ with MetaTrader5 or oandapyV20 installed.}

## 2. Platform Setup

{Step-by-step API setup for the detected platform.
Include a connection/authentication code pattern.

For crypto (ccxt):
```python
import ccxt
import os

exchange = ccxt.binance({
    'apiKey': os.environ['EXCHANGE_API_KEY'],
    'secret': os.environ['EXCHANGE_SECRET'],
    'enableRateLimit': True,
    'options': {'defaultType': 'spot'}  # or 'future' for derivatives
})

# Verify connection
balance = exchange.fetch_balance()
```

For stocks (Alpaca):
```python
from alpaca.trading.client import TradingClient
import os

client = TradingClient(
    api_key=os.environ['ALPACA_API_KEY'],
    secret_key=os.environ['ALPACA_SECRET_KEY'],
    paper=True  # Start with paper trading
)

# Verify connection
account = client.get_account()
```

For stocks (Interactive Brokers):
```python
from ib_async import IB

ib = IB()
ib.connect('127.0.0.1', 7497, clientId=1)  # 7497 for paper, 7496 for live

# Verify connection
account_values = ib.accountValues()
```

For forex (OANDA):
```python
import oandapyV20
from oandapyV20 import API
import os

client = API(
    access_token=os.environ['OANDA_TOKEN'],
    environment='practice'  # Switch to 'live' when ready
)

# Note: OANDA uses underscores not slashes: EUR_USD not EUR/USD
```

For forex (MT5 -- Windows only):
```python
import MetaTrader5 as mt5

mt5.initialize()
mt5.login(login=YOUR_LOGIN, password='YOUR_PASSWORD', server='YOUR_SERVER')
```

For TradingView-based automation: Use the exported PineScript indicator with TradingView alerts connected to your broker's webhook endpoint. Most brokers (Alpaca, OANDA, some crypto exchanges) support webhook-triggered orders. Set the alert condition in TradingView to match the indicator's entry/exit signals, and configure the webhook URL provided by your broker or a middleware service like 3Commas or TradingView-to-anywhere.}

## 3. Strategy Configuration

{Map each parameter from best_result.json to the live trading configuration.
Show how each parameter translates to live trading settings.

Example for a momentum strategy with actual values from best_result.json:
- fast_period: 10 -> Used in EMA calculation for signal generation
- slow_period: 50 -> Used in EMA calculation for trend confirmation
- atr_multiplier: 1.5 -> Stop loss distance = ATR * 1.5
- risk_per_trade: 0.01 -> Risk 1% of account per trade

Include a config dict or similar structure showing all parameters together.}

## 4. Order Types & Execution

{Which order types to use based on this strategy's entry/exit style.

For strategies on higher timeframes (4H, Daily): Use limit orders to reduce slippage.
Place limit at expected entry price, cancel if not filled within N bars.

For strategies on lower timeframes (1M, 5M, 15M): Use market orders for speed.
Accept slippage cost as part of execution.

Slippage handling:
- Include a slippage buffer in position sizing (e.g., 0.1% for crypto, 0.05% for stocks)
- For stop losses: Use stop-market orders to guarantee execution
- For take profits: Use limit orders at target price

Platform-specific order patterns using the detected platform's API.}

## 5. Risk Management

{Position sizing formula using actual stop loss from best_result.json.

Position Size = (Account Balance * risk_per_trade) / (Entry Price - Stop Loss Price)

Example with actual values:
If account = $10,000, risk_per_trade = 0.01, entry = $100, stop = $97 (1.5x ATR):
Position Size = ($10,000 * 0.01) / ($100 - $97) = 33 shares

Circuit breakers:
- Daily loss limit: Stop trading if daily losses exceed 3-5% of account
- Consecutive loss limit: Pause after 5 consecutive losing trades
- Max drawdown kill switch: Stop all trading if drawdown exceeds the backtest max drawdown
  (reference the actual max drawdown from best_result.json)

Maximum concurrent positions: {from strategy logic or default to 1}.}

## 6. Monitoring & Alerts

{What to monitor:
- Order execution: Confirm fills match expected prices
- Position status: Verify open positions match expected state
- Account equity: Track equity curve in real-time
- API health: Monitor connection status and rate limits
- Strategy drift: Compare live win rate and avg trade to backtest metrics after 20+ trades

Notification setup (minimal webhook pattern):
```python
import requests

def send_alert(message):
    webhook_url = os.environ.get('ALERT_WEBHOOK_URL')
    if webhook_url:
        requests.post(webhook_url, json={
            'content': f'[{strategy_name}] {message}'
        })

# Usage
send_alert('BUY signal triggered: entry at $100.50')
send_alert('Daily P&L: +$150 (3 trades)')
```
Works with Discord webhooks directly, or Telegram via Bot API.

When to intervene: Only if execution fails, API disconnects, or metrics diverge
significantly from backtest expectations. Do not override signals manually.}

## 7. Go-Live Checklist

{Strategy-specific pre-launch verification -- distinct from the generic live-checklist.md.

- [ ] Paper traded for at least 2 weeks with this exact configuration
- [ ] Verified parameter values match best_result.json exactly
- [ ] API keys have correct permissions (trade, but no withdrawal)
- [ ] Position sizing produces expected lot/share sizes at current prices
- [ ] Stop loss orders are being placed correctly on the platform
- [ ] Alert/notification system is receiving messages
- [ ] Checked platform-specific constraints (minimum order size, tick size, trading hours)
- [ ] Have a plan for handling platform outages or API downtime
- [ ] Starting with minimum position size for first 10 live trades}
```

### 5a.9: Display Export Summary (EXPT-07)

Count the files in `.pmf/output/` and display:

```
Export package generated in output/ with 8 files.

  pinescript_v5_strategy.pine    TradingView strategy (backtest)
  pinescript_v5_indicator.pine   TradingView indicator (alerts)
  trading-rules.md               Entry/exit rules for manual trading
  performance-report.md          Metrics summary for sharing
  backtest_final.py              Reproducible Python backtest
  live-checklist.md              Checklist before going live
  bot-building-guide.md          Bot deployment guide for live trading
  report_v{N}.html               Interactive HTML report
```

Proceed to Step 6.

---

## Step 5b: --debug Path (Diagnosis)

Create a detailed diagnosis document and open a new phase cycle for further iteration.

### 5b.1: Write Debug Diagnosis (VRFY-12)

Read all available data for thorough diagnosis:

- `.pmf/phases/phase_N_best_result.json` (best metrics)
- `.pmf/phases/phase_N_execute/iter_*_verdict.json` (all iteration verdicts)
- `.pmf/phases/phase_N_execute/iter_*_metrics.json` (all iteration metrics)
- `.pmf/phases/phase_N_execute/iter_*_params.json` (all iteration params)
- `.pmf/STRATEGY.md` (targets)
- `.pmf/phases/phase_N_plan.md` (parameter space and method)
- Cached OHLCV data if available for regime analysis

Write diagnosis to `.pmf/phases/phase_N_verify/debug_diagnosis.md`:

```markdown
# Phase {N} Debug Diagnosis

## Assessment

{Specific assessment of what went wrong. Reference exact metrics vs targets.
Example: "Sharpe of 0.72 is well below the 1.5 target. Max drawdown of -28% exceeds
the -15% limit. The strategy is fundamentally unprofitable in its current form."}

## Equity Curve Analysis

{Describe the shape. Identify periods of flat performance, sharp drawdowns,
or rapid gains. Be specific about dates/periods.
Example: "Equity was flat from March 2023 to August 2023, suggesting the strategy
doesn't perform in sideways markets. The 28% drawdown occurred in September 2023
during a sharp reversal."}

## Regime Performance

| Regime | Trades | Win Rate | Avg P&L | Total P&L | Contribution |
|--------|--------|----------|---------|-----------|--------------|
| Bull   | {n}    | {wr}%    | ${avg}  | ${total}  | {pct}%       |
| Bear   | {n}    | {wr}%    | ${avg}  | ${total}  | {pct}%       |
| Sideways | {n}  | {wr}%    | ${avg}  | ${total}  | {pct}%       |

{Comment on the distribution. Is profit concentrated in one regime?
Is the strategy losing money in a specific regime?}

## Losing Trade Clusters

{Identify where losses concentrate. Are they clustered in specific time periods?
During specific market conditions? After specific events?
Example: "5 of the 8 largest losing trades occurred during low-ADX periods (<20).
The strategy's trend-following entries are generating false signals in ranging markets."}

## Parameter Sensitivity

{Which parameters had the most impact on results? Which were insensitive?
Look at the iteration history for patterns.
Example: "Sharpe was highly sensitive to the fast EMA period (range: 0.3 to 1.8 across
values 5-20) but insensitive to the stop loss multiplier (range: 0.9 to 1.1 across
values 1.0-3.0). The stop loss isn't the problem."}

## Hypothesis for Next Cycle

{ONE specific, actionable hypothesis for the next phase.
This is the most important section -- it drives the next /brrr:discuss session.
Example: "Add a regime filter using ADX: only take trend-following entries when ADX > 25.
This should eliminate the losing trades that clustered during sideways periods (40% of
total losses). Expected impact: Sharpe improvement from 0.72 to 1.0-1.2 based on
removing the sideways-regime losses."}

## Recommended Changes

1. {Specific, implementable change}
2. {Specific, implementable change}
3. {Optional additional change}
```

Rules for diagnosis:
- Be SPECIFIC. Use numbers, dates, metric values. Not "results were poor."
- The hypothesis must be actionable -- the next `/brrr:discuss` session should be able to implement it directly.
- Reference the data: "Based on the regime table, sideways trades had a 30% win rate vs 65% in bull."
- If the strategy is fundamentally flawed, say so: "Consider switching to a mean-reversion approach instead."

### 5b.2: Write Diagnosis JSON (DBUG-01)

After writing the human-readable diagnosis, write a machine-readable `phase_N_diagnosis.json` that captures failed approaches and explicit "do NOT retry" entries. This structured artifact is consumed by `/brrr:discuss` in debug mode to prevent retrying failed parameter regions.

1. **Check for existing diagnosis file**: Use the Read tool to check if `.pmf/phases/phase_N_diagnosis.json` exists (where N is the current phase number).
   - If it exists, parse the JSON and extract the existing `failed_approaches` array.
   - If it does not exist (first debug cycle for this phase), start with an empty `failed_approaches` array.

2. **Build a new `failed_approaches` entry** from the iteration data already loaded in 5b.1 (iteration verdicts, metrics, params, best_result). The entry MUST contain:

   - `iteration_range`: string like `"1-10"` covering the iterations in this phase cycle
   - `params_tried`: object mapping each parameter name to the array of distinct values tried across iterations (e.g., `{"fast_period": [5, 10, 15, 20], "slow_period": [20, 30, 50]}`)
   - `best_result`: object with the best metrics achieved in this cycle (e.g., `{"sharpe": 0.8, "max_dd": -0.15, "trades": 45, "win_rate": 0.52}`)
   - `diagnosis`: string -- 1-2 sentence AI diagnosis of why this approach failed (same analysis as debug_diagnosis.md but condensed to one key finding)
   - `do_not_retry`: array of strings -- explicit parameter regions or approaches that should NOT be retried. Formulate these from the iteration data by identifying which parameter regions consistently underperformed. Examples:
     - `"fast_period < 10 with slow_period < 30"`
     - `"stop_loss < 1.5%"`
     - `"mean-reversion without volume filter"`
     - `"RSI overbought threshold > 80 (insufficient entries)"`

   The `diagnosis` and `do_not_retry` fields are AI-generated analysis, NOT mechanical dumps of data. Analyze which parameter combinations failed and WHY, then formulate actionable exclusion rules.

3. **Append** the new entry to the `failed_approaches` array (existing entries from prior debug cycles on this phase are preserved).

4. **Assemble the full JSON object** with this structure:

```json
{
  "phase": N,
  "timestamp": "2026-03-22T14:30:00Z",
  "strategy_type": "from STRATEGY.md strategy type field",
  "best_metrics": {
    "sharpe": 0.8,
    "max_dd": -0.15,
    "win_rate": 0.52,
    "profit_factor": 1.1,
    "total_trades": 45
  },
  "targets": {
    "sharpe": 1.5,
    "max_dd": -0.10,
    "win_rate": 0.55
  },
  "failed_approaches": [
    {
      "iteration_range": "1-10",
      "params_tried": {
        "fast_period": [5, 10, 15, 20],
        "slow_period": [20, 30, 50]
      },
      "best_result": {
        "sharpe": 0.8,
        "max_dd": -0.15,
        "trades": 45,
        "win_rate": 0.52
      },
      "diagnosis": "Entries too frequent in sideways markets, stops too tight for volatility",
      "do_not_retry": [
        "fast_period < 10 with slow_period < 30",
        "stop_loss < 1.5%"
      ]
    }
  ],
  "overall_diagnosis": "AI synthesis of ALL failed approaches so far -- what has been tried, what the cumulative evidence suggests",
  "suggested_changes": [
    "Specific actionable change 1",
    "Specific actionable change 2"
  ]
}
```

   - `phase`, `strategy_type`, and `targets` stay the same if the file already existed.
   - `timestamp`, `best_metrics`, `overall_diagnosis`, and `suggested_changes` are updated to reflect the latest cycle.
   - `best_metrics` reflects the best result from the LATEST cycle (not all-time best).
   - `overall_diagnosis` synthesizes ALL `failed_approaches` entries (not just the latest).

5. **Write** the JSON to `.pmf/phases/phase_N_diagnosis.json` using the Write tool.

6. **Display** confirmation:

```
Diagnosis artifact written: .pmf/phases/phase_N_diagnosis.json ({M} failed approaches recorded)
```

Where `{M}` is the total number of entries in the `failed_approaches` array.

### 5b.3: Update STATE.md for New Phase Cycle

Read `.pmf/STATE.md` and update it for the new phase cycle:

1. Keep Status as "IN PROGRESS"
2. Mark Phase N Verify as `[x]` (it ran, even though the result was debug)
3. Increment phase number to N+1
4. Add Phase N+1 checklist with all steps unchecked:

```
### Phase {N+1}

- [ ] Discuss
- [ ] Research
- [ ] Plan
- [ ] Execute
- [ ] Verify
```

5. Add History entry:

```
| {timestamp} | Phase {N} debug: {one-line summary of diagnosis hypothesis} |
```

6. Update Current Phase to N+1
7. Update Last Updated timestamp

### 5b.4: Display Debug Output

```
Debug Diagnosis for Phase {N}:

{Brief summary of the diagnosis -- 2-3 sentences covering the main finding and hypothesis}

Diagnosis saved to:
  .pmf/phases/phase_{N}_verify/debug_diagnosis.md (human-readable)
  .pmf/phases/phase_{N}_diagnosis.json (structured, {M} failed approaches)

New phase cycle opened. Run /brrr:discuss to start from the diagnosis.
```

Proceed to Step 7 (skip Step 6 -- STATE.md already updated in 5b.3).

---

## Step 6: Update STATE.md (--approved path only)

Read `.pmf/STATE.md` and apply these updates:

1. Set Status to `CLOSED`
2. Mark Phase N Verify as `[x]`:
   ```
   - [x] Verify
   ```
3. Add or update Best Results section with final metrics:
   ```
   ## Best Results

   | Metric | Value |
   |--------|-------|
   | Sharpe Ratio | {value} |
   | Max Drawdown | {value} |
   | Win Rate | {value} |
   | Profit Factor | {value} |
   | Total Trades | {value} |
   | Net P&L | {value} |
   ```

4. Add History entry:
   ```
   | {timestamp} | Milestone approved. Export package generated with {N} files. |
   ```

5. Update Last Updated timestamp to current time

6. Write the updated STATE.md back to `.pmf/STATE.md`

---

## Step 7: Confirmation

### For --approved path:

```
Milestone complete. Your strategy has been exported to output/.

Files:
  - pinescript_v5_strategy.pine    TradingView strategy (backtest)
  - pinescript_v5_indicator.pine   TradingView indicator (alerts)
  - trading-rules.md               Entry/exit rules
  - performance-report.md          Metrics summary
  - backtest_final.py              Reproducible backtest
  - live-checklist.md              Pre-live checklist
  - report_v{N}.html               Interactive report

Next steps:
  1. Open report_v{N}.html in your browser for the full interactive report
  2. Paste PineScript files into TradingView Pine Editor to validate
  3. Review trading-rules.md and live-checklist.md before going live
  4. Run backtest_final.py to verify reproducibility

To start a new strategy: /brrr:new-milestone
```

### For --debug path:

```
Phase {N} debug cycle complete. The diagnosis has been saved and a new
phase cycle ({N+1}) has been opened.

Next step: /brrr:discuss

The discuss phase will start with the diagnosis context from Phase {N},
so you can refine the strategy based on what we learned.
```

---

## Appendix: Requirement Coverage

This workflow covers the following requirements:

| Requirement | Step | Description |
|-------------|------|-------------|
| VRFY-10 | Step 3 | AI analyzes full report and formulates conclusion |
| VRFY-11 | Step 5a + Step 6 | --approved closes milestone, triggers export, STATE.md set to CLOSED |
| VRFY-12 | Step 5b.1 | --debug creates diagnosis document, opens new phase cycle |
| DBUG-01 | Step 5b.2 | Structured diagnosis JSON with failed approaches and do_not_retry |
| EXPT-01 | Step 5a.2 | PineScript v5 strategy and indicator files |
| EXPT-02 | Step 5a.3 | trading-rules.md in practitioner tone |
| EXPT-03 | Step 5a.4 | performance-report.md with metrics summary |
| EXPT-04 | Step 5a.5 | backtest_final.py reproducible Python script |
| EXPT-05 | Step 5a.6 | live-checklist.md step-by-step guide |
| EXPT-06 | Step 5a.7 | Report HTML copied to output/ |
| EXPT-07 | Step 5a.9 | All exports in output/ directory |
| EXPT-08 | Step 5a.8 | bot-building-guide.md with platform-specific deployment instructions |
