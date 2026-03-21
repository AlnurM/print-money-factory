# Workflow: execute

Orchestrate the AI-driven backtest optimization loop. Load market data, write a custom Python backtest per strategy, run iterative optimization with AI analysis between iterations, stop when targets are hit or strategy is diagnosed as unviable.

Follow these sections in order, top to bottom. Each section contains behavioral instructions -- read them, then execute them using your tools (Read, Write, Bash, Glob). Do NOT skip sections unless explicitly told to.

---

## Preamble: Sequence Validation

Before anything else, verify that plan has been completed for the current phase.

1. Use the Read tool to check if `.pmf/STATE.md` exists
2. If it does not exist, STOP immediately:

```
[STOP] Cannot run execute -- no milestone exists.

No milestone exists. Create one first to define your strategy scope and targets.

Next step: `/brrr:new-milestone`
```

3. If it exists, read it and find:
   - **Status** field (must be "IN PROGRESS")
   - **Current Phase** number (N)
   - Whether plan is marked done for phase N: look for `- [x] Plan` under Phase N
4. If Status is not "IN PROGRESS", STOP:

```
[STOP] Cannot run execute -- milestone is not active.

Current milestone status: {status}

To start a new milestone: /brrr:new-milestone
```

5. If Plan is NOT done for Phase N, STOP:

```
[STOP] Cannot run execute -- plan has not been completed yet.

The plan phase designs the parameter space, optimization method, and train/test
split. Without it, there is nothing to optimize.

Current position:
  Phase {N}:
    {step_icon} Discuss    {status}
    {step_icon} Research   {status}
    {step_icon} Plan       {status}
    {step_icon} Execute    {status}
    {step_icon} Verify     {status}

Next step: `/brrr:plan`
```

6. If Execute is already checked for Phase N, STOP:

```
[STOP] Cannot run execute -- Phase {N} execute is already completed.

The execute phase runs the optimization loop -- running it again would
overwrite iteration artifacts.

Current position:
  Phase {N}:
    [DONE] Discuss
    [DONE] Research
    [DONE] Plan
    [DONE] Execute
    {step_icon} Verify     {status}

Next step: `/brrr:verify`
```

7. If Plan IS done and Execute is NOT done, proceed to the next section.

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
   - Ask the user: "I found this context file. Should I incorporate it into the current execution? (yes/no)"
   - Record processed files for STATE.md update later
8. Proceed to the next section

---

## Preamble: Parse Arguments

Parse `$ARGUMENTS` for execution flags.

Supported flags:
- `--iterations N` -- Maximum number of AI optimization iterations (default: 10). Each iteration writes a Python script, runs it, analyzes results, and decides next parameters.
- `--fast` -- Skip equity curve PNG generation during iterations. Faster execution at the cost of no visual analysis. Metrics JSON is still produced.
- `--resume` -- Continue from the last saved iteration instead of starting from scratch. Finds the last completed iteration by scanning for `iter_NN_verdict.json` files (verdict.json is the last artifact written per iteration, so its presence confirms the iteration completed fully).

Parse rules:
1. If `$ARGUMENTS` is empty or not provided, use defaults: iterations=10, fast=false, resume=false
2. If `--iterations` is followed by a number, use that as max_iterations
3. If `--fast` is present, set fast_mode=true
4. If `--resume` is present, set resume_mode=true
5. Store parsed flags for use throughout the workflow

---

## Step 1: Load Inputs

Gather all the information needed to run the optimization loop.

1. Read `.pmf/STRATEGY.md` and extract:
   - **Asset** (e.g., BTC/USDT, AAPL, EUR/USD)
   - **Exchange/Source** (e.g., Binance, yfinance, Dukascopy)
   - **Timeframe** (e.g., 1H, 4H, 1D)
   - **Date Range** (start and end dates)
   - **Success Criteria:** Sharpe target, Max Drawdown target, Minimum trade count
   - **Strategy type** (trend-following, mean-reversion, breakout, custom)

2. Read `.pmf/phases/phase_N_plan.md` and extract:
   - **Parameter space:** free parameters (name, min, max, step, type) and fixed parameters (name, value)
   - **Optimization method:** grid_search, random_search, or walk_forward
   - **Max iterations** from plan (may be overridden by --iterations flag)
   - **Evaluation criteria:** primary metric target, secondary filters, min trade count
   - **Train/test split:** percentage (e.g., 70/30) or walk-forward window config (train bars, test bars, step bars)
   - **Parameter constraints** (e.g., fast_period < slow_period)
   - **Plateau threshold** (default 3 iterations)

3. Read `.pmf/phases/phase_N_discuss.md` and extract:
   - **Strategy logic decisions:** entry conditions, exit conditions, stop-loss, take-profit
   - **Indicator definitions:** which indicators, how they're calculated
   - **Position sizing** and **commission** rate
   - All details needed to write the `calculate_signal()` function

4. Optionally read `.pmf/phases/phase_N_research.md` if it exists:
   - Pitfalls to watch for
   - Lookahead traps specific to this strategy type
   - Implementation recommendations

5. Read `~/.pmf/references/backtest-engine.md` for the anti-lookahead rules:
   - Rule 1: Signal sees only past and current bar (`history = df.iloc[:i+1]`)
   - Rule 2: Execution at next bar's open price
   - Rule 3: No future data in indicator calculations
   - Claude MUST follow these rules when writing `calculate_signal()`

6. Display a summary of what was loaded:

```
--- Inputs Loaded ---
Strategy:   {strategy_type} on {asset} ({timeframe})
Source:     {exchange/source}
Date range: {start} to {end}
Parameters: {X} to optimize, {Y} fixed
Method:     {optimization_method}
Split:      {train}% IS / {test}% OOS
Targets:    Sharpe > {target}, Max DD < {target}%
Flags:      iterations={N}, fast={true/false}, resume={true/false}
```

---

## Step 2: Load & Validate Data

Load OHLCV data using the appropriate adapter from `data_sources.py`.

### Determine Data Source

Read the exchange/source from STRATEGY.md (set during new-milestone). Do NOT re-ask the user.

- **Crypto** (Binance, Coinbase, Kraken, etc.): use `load_ccxt(exchange, symbol, timeframe, since, limit=50000)`
  - Note: `limit=50000` triggers internal pagination for large datasets. The default of 1000 is insufficient for most backtests.
- **Stocks/Forex daily** (yfinance): use `load_yfinance(ticker, start, end, interval)`
- **CSV fallback**: use `load_csv(filepath)`

### Check Cache First

1. Define cache path: `.pmf/cache/{asset}_{source}_{timeframe}.parquet`
   - Normalize the asset name for filesystem: replace `/` with `_`, remove special characters
   - Example: `.pmf/cache/BTC_USDT_binance_1h.parquet`

2. Write a Python script that checks if the cache file exists:
   - If cached file exists AND its date range covers the requested range: load from cache
   - If not cached: download using the appropriate adapter, then save to cache

3. Write the data loading Python script to `.pmf/phases/phase_N_execute/load_data.py`:

```python
import sys
from pathlib import Path
sys.path.insert(0, str(Path.home() / '.pmf' / 'references'))

import pandas as pd
from data_sources import load_ccxt, load_yfinance, load_csv, validate_ohlcv

cache_dir = Path('.pmf/cache')
cache_dir.mkdir(parents=True, exist_ok=True)

cache_file = cache_dir / '{normalized_asset}_{source}_{timeframe}.parquet'

if cache_file.exists():
    df = pd.read_parquet(cache_file)
    print(f"CACHE_HIT: {len(df)} bars loaded from cache")
else:
    # Use appropriate adapter based on source
    df = {appropriate_load_function_call}
    df.to_parquet(cache_file)
    print(f"DOWNLOADED: {len(df)} bars, cached to {cache_file}")

print(f"DATA_RANGE: {df.index[0]} to {df.index[-1]}")
print(f"DATA_BARS: {len(df)}")
print("SUCCESS")
```

4. Execute the script: `~/.pmf/venv/bin/python .pmf/phases/phase_N_execute/load_data.py`

5. Check for "SUCCESS" sentinel. If the script fails:
   - Read stderr for the error
   - If it's a network/API error: report NO DATA condition
   - If it's fixable (wrong ticker format, missing dependency): fix and retry once

### Enhanced Validation (per D-16)

After loading, apply enhanced validation beyond what `validate_ohlcv()` provides:

1. **Gap detection:** Check for gaps in the time series larger than 1.5x the expected interval
2. **Small gap auto-fix:** If gaps are < 5 bars, forward-fill them automatically
3. **Large gap warning:** If gaps are >= 5 bars, warn the user about data quality
4. **Refuse threshold:** If more than 10% of expected bars are missing/affected, STOP with NO DATA condition:

```
[NO DATA] Data quality too poor to proceed.

{affected_pct}% of data is missing or affected by gaps.
Threshold: 10%

Source: {source}
Asset: {asset}
Timeframe: {timeframe}
Date range: {start} to {end}
Expected bars: ~{N}
Actual bars: {M}
Affected bars: {K} ({pct}%)

Options:
1. Try a different date range
2. Try a different data source
3. Use a CSV file with clean data
```

5. Display data summary:

```
Data loaded: {N} bars from {start_date} to {end_date} ({source})
{If gaps fixed: "Auto-fixed {K} gap bars via forward-fill"}
{If any warnings: display them}
```

---

## Step 3: Calculate IS/OOS Split

Convert the plan's percentage-based split rules into exact date indices using the loaded data.

### Standard Split (grid_search or random_search)

1. Read train/test split percentage from `phase_N_plan.md` (e.g., 70/30)
2. Calculate exact split index: `split_idx = int(total_bars * train_pct)`
3. Record:
   - IS period: `df.iloc[:split_idx]` -- from data start to split point
   - OOS period: `df.iloc[split_idx:]` -- from split point to data end
   - IS date range and bar count
   - OOS date range and bar count

### Walk-Forward Split

If the optimization method is `walk_forward`:

1. Read window configuration from `phase_N_plan.md`:
   - `train_bars`: number of bars in each training window
   - `test_bars`: number of bars in each test window
   - `step_bars`: how far the window advances each iteration (typically = test_bars for non-overlapping)

2. Calculate the number of walk-forward windows:
   - `n_windows = (total_bars - train_bars) // step_bars`
   - Each window: train on `[start : start + train_bars]`, test on `[start + train_bars : start + train_bars + test_bars]`

3. Record all window start/end indices for later use

### Display Split Info

```
--- Data Split ---
Total bars: {N}

{If standard split:}
IS:  {start_date} to {split_date} ({IS_bars} bars, {train_pct}%)
OOS: {split_date} to {end_date} ({OOS_bars} bars, {test_pct}%)

{If walk-forward:}
Method: Walk-Forward
Train window: {train_bars} bars
Test window:  {test_bars} bars
Step size:    {step_bars} bars
Total windows: {n_windows}
```

---

## Step 4: Initialize Iteration State

Set up tracking variables and output directory for the optimization loop.

1. **Create output directory:** `.pmf/phases/phase_N_execute/`
   - Use Bash: `mkdir -p .pmf/phases/phase_N_execute`

2. **Initialize tracking variables:**
   - `iteration = 1` (1-indexed)
   - `max_iterations` = from --iterations flag or plan default
   - `best_sharpe = -inf`
   - `best_iteration = 0`
   - `best_params = {}`
   - `best_is_metrics = {}`
   - `best_oos_metrics = {}`
   - `plateau_counter = 0`
   - `iteration_history = []` (list of all iteration metrics for stop condition evaluation)
   - `current_params = {}` (initial parameter values from plan -- use midpoint of ranges or plan defaults)

3. **Handle --resume flag:**
   If `--resume` is set:
   - Scan `.pmf/phases/phase_N_execute/` for existing `iter_NN_verdict.json` files
   - Find the highest NN where `iter_NN_verdict.json` exists (verdict.json is the LAST artifact written per iteration, so its presence means the iteration completed fully)
   - Load all existing verdict JSONs into `iteration_history`
   - Set `iteration = last_completed + 1`
   - Load the last verdict's parameter changes as `current_params`
   - Update `best_sharpe`, `best_iteration`, `best_params` from history
   - Display: "Resuming from iteration {N} (found {M} completed iterations)"

4. **Set initial parameters:**
   If NOT resuming:
   - For each free parameter, use the midpoint of its range as the starting value:
     `initial_value = (min + max) / 2`, rounded to step
   - Include all fixed parameters at their specified values
   - Include commission rate from discuss/plan artifacts
   - Include `initial_capital` (default 10000 unless specified)

5. **Display initialization:**

```
--- Iteration State ---
{If not resuming:}
Starting iteration 1 of {max_iterations}
Initial parameters:
  {param}: {value} (range: {min}-{max})
  ...

{If resuming:}
Resuming from iteration {N} of {max_iterations}
Found {M} completed iterations
Best so far: iteration {K} (Sharpe: {best_sharpe})
Current parameters:
  {param}: {value}
  ...
```

---

## Step 5: Iteration Loop

**THIS IS THE CORE.** Repeat until a stop condition is triggered or max_iterations is reached.

For the FIRST iteration, display the full header block:

```
===========================================
  PRINT MONEY FACTORY -- brrr...
===========================================
Milestone: {milestone_name}
Pair:      {asset} ({source}, {timeframe})
Method:    {optimization_method} | {max_iterations} iterations
Split:     {train_pct}% IS / {test_pct}% OOS
-------------------------------------------
```

Then, for each iteration:

### Step 5a: Write Python Script

Write a complete, self-contained Python script to `.pmf/phases/phase_N_execute/run_iter_NN.py`.

The script MUST:

1. **Set up imports and paths:**
```python
import sys
from pathlib import Path
sys.path.insert(0, str(Path.home() / '.pmf' / 'references'))

import pandas as pd
import numpy as np
import json

import backtest_engine
from backtest_engine import run_backtest, save_iteration_artifacts
from metrics import compute_all_metrics
```

2. **Load cached data:**
```python
df = pd.read_parquet('.pmf/cache/{cache_filename}')
```

3. **Define the `calculate_signal()` function:**
   - Implement the strategy logic from discuss phase decisions
   - Use ONLY the `history` DataFrame (data up to current bar) -- NEVER access global `df`
   - Return one of: 'long', 'short', 'close', 'hold'
   - Follow ALL anti-lookahead rules from `backtest-engine.md`:
     - Rule 1: `history` contains only bars 0 through current (already sliced by engine)
     - Rule 2: Execution happens at next bar's open (handled by engine)
     - Rule 3: Compute indicators on `history` slice, not full dataset
   - Handle edge cases: return 'hold' if insufficient data for indicators (e.g., not enough bars for SMA period)

```python
def calculate_signal(history, params):
    # Claude implements strategy-specific logic here
    # Based on discuss phase decisions
    # MUST use only history[:] -- no future data
    if len(history) < params.get('slow_period', 50):
        return 'hold'
    # ... indicator calculations on history ...
    # ... entry/exit logic ...
    return signal
```

4. **Monkey-patch the engine's signal function:**
```python
backtest_engine.calculate_signal = calculate_signal
```

5. **Set parameters and run IS backtest:**
```python
params = {
    # Strategy parameters for this iteration
    'initial_capital': 10000,
    'commission': {commission_rate},
    'trading_days': {trading_days},
    # ... strategy-specific params ...
}

# IS backtest
df_train = df.iloc[:{split_idx}]
results_is = run_backtest(df_train, params)

# Save IS artifacts
save_iteration_artifacts(results_is, params, iteration={N}, output_dir='{output_dir}')
```

6. **Run OOS backtest:**
```python
# OOS backtest
df_test = df.iloc[{split_idx}:]
results_oos = run_backtest(df_test, params)

# Save OOS metrics separately
oos_file = Path('{output_dir}') / 'iter_{N:02d}_oos_metrics.json'
oos_serializable = {}
for k, v in results_oos.items():
    if isinstance(v, (int, float, str, bool, type(None))):
        oos_serializable[k] = v
    elif isinstance(v, np.ndarray):
        oos_serializable[k] = v.tolist()
    elif isinstance(v, (np.integer,)):
        oos_serializable[k] = int(v)
    elif isinstance(v, (np.floating,)):
        oos_serializable[k] = float(v)
with open(oos_file, 'w') as f:
    json.dump(oos_serializable, f, indent=2, default=str)
```

7. **For walk-forward method:** Instead of single IS/OOS split, run rolling windows:
```python
# Walk-forward loop
train_bars = {train_bars}
test_bars = {test_bars}
step_bars = {step_bars}

all_oos_trades = []
window_results = []
start = 0

while start + train_bars + test_bars <= len(df):
    df_window_train = df.iloc[start:start + train_bars]
    df_window_test = df.iloc[start + train_bars:start + train_bars + test_bars]

    results_window_is = run_backtest(df_window_train, params)
    results_window_oos = run_backtest(df_window_test, params)

    window_results.append({
        'window_start': start,
        'is_sharpe': results_window_is.get('sharpe_ratio', float('nan')),
        'oos_sharpe': results_window_oos.get('sharpe_ratio', float('nan')),
    })

    # Accumulate OOS trades for aggregate metrics
    # (trades from compute_all_metrics are embedded in the dict)
    all_oos_trades.extend(results_window_oos.get('trades', []))

    start += step_bars

# Compute aggregate OOS metrics from all windows
results_oos = compute_all_metrics(trades=all_oos_trades)
# Use last window's IS metrics as representative
results_is = results_window_is
```

8. **Generate equity curve PNG (unless --fast):**
```python
if not {fast_mode}:
    import matplotlib
    matplotlib.use('Agg')  # MUST be before pyplot import
    import matplotlib.pyplot as plt

    # Reconstruct equity curve from IS trades
    # (run_backtest returns compute_all_metrics output which does not include raw equity)
    trades_is = results_is.get('trades', [])
    initial_capital = params.get('initial_capital', 10000)
    if trades_is:
        pnls = [t['pnl'] for t in trades_is]
        equity = [initial_capital]
        for pnl in pnls:
            equity.append(equity[-1] + pnl)
        equity_arr = np.array(equity)
    else:
        equity_arr = np.array([initial_capital])

    fig, ax = plt.subplots(figsize=(12, 6))
    ax.plot(equity_arr, linewidth=1, color='#2196F3')
    ax.set_title(f'Equity Curve - Iteration {N:02d} (IS)')
    ax.set_ylabel('Equity ($)')
    ax.set_xlabel('Trade #')
    ax.axhline(y=initial_capital, color='gray', linestyle='--', alpha=0.5)
    ax.grid(True, alpha=0.3)
    fig.savefig('{output_dir}/iter_{N:02d}_equity.png', dpi=100, bbox_inches='tight')
    plt.close(fig)  # Critical: prevent memory leak
    plt.close('all')  # Safety net
```

9. **Print results summary and SUCCESS sentinel:**
```python
# Print summary for Claude to read
print(f"IS_SHARPE: {results_is.get('sharpe_ratio', 'nan')}")
print(f"IS_MAX_DD: {results_is.get('max_drawdown', 'nan')}")
print(f"IS_WIN_RATE: {results_is.get('win_rate', 'nan')}")
print(f"IS_PROFIT_FACTOR: {results_is.get('profit_factor', 'nan')}")
print(f"IS_TRADE_COUNT: {results_is.get('trade_count', 0)}")
print(f"IS_NET_PNL: {results_is.get('net_pnl', 0)}")
print(f"OOS_SHARPE: {results_oos.get('sharpe_ratio', 'nan')}")
print(f"OOS_MAX_DD: {results_oos.get('max_drawdown', 'nan')}")
print(f"OOS_WIN_RATE: {results_oos.get('win_rate', 'nan')}")
print(f"OOS_PROFIT_FACTOR: {results_oos.get('profit_factor', 'nan')}")
print(f"OOS_TRADE_COUNT: {results_oos.get('trade_count', 0)}")
print(f"OOS_NET_PNL: {results_oos.get('net_pnl', 0)}")
print("SUCCESS")
```

**CRITICAL RULES for the Python script:**
- Always use `~/.pmf/venv/bin/python` to execute (never system python)
- Always set `matplotlib.use('Agg')` BEFORE `import matplotlib.pyplot as plt`
- Always call `plt.close(fig)` after `fig.savefig()`
- Always use monkey-patching for `calculate_signal`, never modify reference files
- The script must be self-contained -- all imports, all logic, all output in one file
- Handle the case where indicators need warmup bars (return 'hold' for insufficient data)

### Step 5b: Execute Python Script

Run the iteration script via Bash.

1. Execute: `~/.pmf/venv/bin/python .pmf/phases/phase_N_execute/run_iter_NN.py`
2. Capture BOTH stdout and stderr
3. Check for "SUCCESS" sentinel in stdout

**If the script fails** (no SUCCESS in output, or non-zero exit code):
1. Read the error output (traceback, stderr)
2. Diagnose the issue:
   - Syntax error: fix the script and rewrite it
   - Import error: check sys.path setup
   - Data error: check if cache file exists and has expected columns
   - Runtime error: fix the logic in calculate_signal or parameter handling
3. Fix the script and retry -- up to **2 retries per iteration** (3 total attempts)
4. If still failing after retries:
   - If it's a data issue (file not found, empty data, wrong columns): trigger NO DATA stop condition
   - If it's a code issue: log the error, skip to next iteration, increment failure counter
   - If 3 consecutive iterations fail: STOP with error message explaining what's going wrong

### Step 5c: Read Artifacts

After successful script execution, read the output files.

1. Read `iter_NN_metrics.json` (IS metrics from `save_iteration_artifacts`)
2. Read `iter_NN_oos_metrics.json` (OOS metrics saved separately)
3. Read `iter_NN_params.json` (parameters used)
4. If NOT in `--fast` mode: Read `iter_NN_equity.png` using multimodal vision to analyze visual patterns:
   - Look for: overall trend direction, regime shifts, clustered losses, flat periods, drawdown severity
   - Note any visual concerns for the AI analysis section
   - Example observations: "Equity curve shows a sharp drawdown in Q3 2023 followed by flat performance -- possible regime shift"

### Step 5d: Evaluate Stop Conditions

After reading artifacts, check all stop conditions in priority order.

**1. MINT (D-06) -- Targets Hit**

Check if IS metrics meet ALL targets from the plan:
- Sharpe ratio >= target Sharpe (from plan evaluation criteria)
- Max drawdown >= target max DD (remember: max_drawdown is negative, so -0.15 >= -0.20 means DD is within target)
- Trade count >= minimum trades
- Any secondary hard filters pass (e.g., Profit Factor > threshold)

If ALL targets met:
```
-------------------------------------------
MINT -- Targets hit!

IS Sharpe: {value} (target: {target})
IS Max DD: {value}% (target: {target}%)
IS Trades: {count} (min: {min})

Targets met at iteration {N}. Run more iterations to improve? (yes/no)
-------------------------------------------
```

If user says "yes": continue loop with higher iteration limit. If "no": proceed to Step 6 (Finalize).

**2. PLATEAU (D-07) -- No Improvement**

Track the improvement history. After each iteration, compare the best Sharpe from the last `plateau_threshold` iterations against the best before that window.

- If `plateau_threshold` consecutive iterations pass without > 5% improvement in best Sharpe: trigger PLATEAU
- The plateau_threshold value comes from the plan (default: 3)

```
-------------------------------------------
PLATEAU -- Optimization has plateaued.

Best Sharpe: {value} (iteration {N})
Last {threshold} iterations: no improvement > 5%

Options:
1. Run more iterations (may not help)
2. Widen parameter ranges
3. Try a different optimization method
4. Adjust strategy logic via /brrr:discuss
-------------------------------------------
```

**3. REKT (D-08) -- No Edge**

If the last 5 iterations ALL have negative Sharpe ratio:

Diagnose the cause -- this is CRITICAL for user guidance. Distinguish between:

**a) Strategy logic has no edge:**
- Indicators: most parameter combinations produce negative Sharpe; no clear parameter sensitivity
- Recommendation: "The strategy logic itself may not have an edge in this market. Consider fundamentally different entry/exit conditions."

**b) Asset/timeframe wrong for this strategy:**
- Indicators: some parameters show promise but the overall pattern suggests the strategy type doesn't match the asset's behavior
- Recommendation: "Your {strategy_type} strategy may not suit {asset} on {timeframe}. Consider: (1) different timeframe, (2) different asset, (3) add regime filter."

```
-------------------------------------------
REKT -- No edge detected.

Last 5 iterations: all negative Sharpe
  Iteration {N-4}: Sharpe {value}
  Iteration {N-3}: Sharpe {value}
  Iteration {N-2}: Sharpe {value}
  Iteration {N-1}: Sharpe {value}
  Iteration {N}:   Sharpe {value}

Diagnosis: {strategy_no_edge OR wrong_asset_timeframe}

{Specific recommendation based on diagnosis}
-------------------------------------------
```

**4. NO DATA (D-09) -- Data Issues**

Triggered during data loading (Step 2) or if the backtest script fails with data-related errors.

```
-------------------------------------------
NO DATA -- Cannot proceed.

{Error description: API failure, empty data, insufficient bars, etc.}

Source: {source}
Asset: {asset}

Options:
1. Check data source availability
2. Try a different date range
3. Use a CSV file with pre-downloaded data
-------------------------------------------
```

**If any stop condition triggers:** Break out of the iteration loop and proceed to Step 6 (Finalize).

**If no stop condition:** Continue to Step 5e.

### Step 5e: AI Analysis & Terminal Display

This is where Claude performs HOLISTIC analysis -- reading ALL artifacts and forming a hypothesis.

**Analysis process (per D-01, D-03):**

1. Read all metrics: IS Sharpe, IS Max DD, IS Win Rate, IS PF, IS Trades, IS Net P&L, AND their OOS counterparts
2. Compare against previous iterations (from iteration_history)
3. If equity PNG exists: analyze the visual pattern for regime shifts, clustered losses, drawdown characteristics
4. Read all prior verdict JSONs to understand the trajectory of optimization
5. Form a SPECIFIC hypothesis in trading domain language:
   - Good: "Sharpe improved from 1.4 to 1.8 but drawdown worsened from -15% to -22%. The wider stop-loss is letting winners run longer but also allowing deeper pullbacks. The equity curve shows a sharp drawdown cluster in Aug-Sep 2023 that coincides with BTC ranging after the July rally."
   - Bad: "Parameters adjusted, metrics changed."

**Overfitting detection (per D-18, D-19):**

Check for overfitting signals after each iteration:

1. **IS vs OOS divergence (D-18):** If IS Sharpe > 2x OOS Sharpe:
   ```
   OVERFITTING WARNING: IS Sharpe ({is_sharpe}) is {ratio}x OOS Sharpe ({oos_sharpe}).
   The strategy may be curve-fitting to training data.
   ```

2. **Suspiciously good metrics (D-19):**
   - If Sharpe > 3.0: "SUSPICIOUS: Sharpe {value} > 3.0 -- possible lookahead bias or extreme overfit"
   - If Profit Factor > 5.0: "SUSPICIOUS: Profit Factor {value} > 5.0 -- too good to be true"
   - If Win Rate > 80%: "SUSPICIOUS: Win Rate {value}% > 80% -- likely overfit or insufficient trades"

**Terminal display (per D-10):**

Print this formatted block for EVERY iteration:

```
Iteration {NN}/{MM}                    brrr...
-------------------------------------------
Parameters:
  {param}: {value} {(was {old_value}) if changed, (unchanged) if not}
  ...

Metrics (IS / OOS):
  Sharpe:         {is_value} / {oos_value}
  Max Drawdown:  {is_value}% / {oos_value}%
  Win Rate:       {is_value}% / {oos_value}%
  Profit Factor:  {is_value} / {oos_value}
  Trades:         {is_value} / {oos_value}
  Net P&L:       ${is_value} / ${oos_value}

{If overfitting warnings: display them here}

AI Analysis:
  {Claude's specific trading-domain analysis}
  {What changed, why, what the metrics tell us}
  {If equity curve analyzed: visual observations}

  {If not --fast: "Equity curve: iter_NN_equity.png saved"}
-------------------------------------------
```

### Step 5f: Decide Next Parameters

Based on the analysis, decide what to change for the next iteration.

**Adaptive change rate (per D-02):**
- If plateau_counter == 0: change 1-2 parameters per iteration (conservative exploration)
- If plateau_counter > 0: change 3-4 parameters per iteration (aggressive exploration to escape plateau)
- If this iteration was significantly better than previous: keep the direction, make smaller adjustments

**Parameter selection strategy:**
- **Grid search:** Systematically move through the parameter space. Each iteration tests the next combination in the grid.
- **Random search:** Sample random combinations from the parameter space, guided by AI analysis of which directions are promising.
- **Walk-forward / AI-guided:** Claude decides which parameters to change based on the metrics and analysis. This is the default behavior when the plan selects walk_forward or when the AI override is most effective.

**For each parameter change, explain the reasoning (per D-03):**

```
Next iteration changes:
  {param}: {old_value} -> {new_value}
    Reason: {specific trading-domain justification}
  {param}: {old_value} -> {new_value}
    Reason: {specific trading-domain justification}

Expected outcome: {hypothesis about what this should improve/change}
```

**Enforce parameter constraints:** Before applying changes, verify all constraints from the plan are satisfied (e.g., fast_period < slow_period). If a change would violate a constraint, adjust the other parameter accordingly.

**Write verdict JSON** to `iter_NN_verdict.json`:

```json
{
  "iteration": {N},
  "hypothesis": "Brief statement of what was being tested this iteration",
  "changes_made": [
    {
      "param": "{param_name}",
      "old": {old_value},
      "new": {new_value},
      "reason": "Why this change was made"
    }
  ],
  "expected_outcome": "What the next iteration should show if the hypothesis is correct",
  "is_metrics": {
    "sharpe_ratio": {value},
    "max_drawdown": {value},
    "win_rate": {value},
    "profit_factor": {value},
    "trade_count": {value},
    "net_pnl": {value}
  },
  "oos_metrics": {
    "sharpe_ratio": {value},
    "max_drawdown": {value},
    "win_rate": {value},
    "profit_factor": {value},
    "trade_count": {value},
    "net_pnl": {value}
  },
  "overfitting_check": {
    "is_oos_sharpe_ratio": {is_sharpe / oos_sharpe},
    "warning": {true/false}
  },
  "stop_condition": "CONTINUE",
  "plateau_counter": {plateau_counter}
}
```

**IMPORTANT:** The verdict JSON is the LAST artifact written per iteration. Its presence confirms the iteration completed fully. This is critical for the `--resume` flag to work correctly.

**Update tracking variables:**
- Add current metrics to `iteration_history`
- Update `best_sharpe`, `best_iteration`, `best_params` if this iteration was the best
- Update `plateau_counter` (increment if no improvement, reset if improved)
- Set `current_params` to the new parameter values for the next iteration

**Loop back to Step 5a** with the new parameters.

---

## Step 6: Finalize

After the iteration loop ends (via stop condition or max iterations reached), produce the final output.

### Find Best Iteration

1. Scan all verdict JSONs in `.pmf/phases/phase_N_execute/`
2. Find the iteration with the highest IS Sharpe ratio
3. If multiple iterations have similar Sharpe (within 5%), prefer the one with better OOS Sharpe (more robust)

### Write Best Result JSON

Write `.pmf/phases/phase_N_best_result.json`:

```json
{
  "best_iteration": {N},
  "stop_reason": "{MINT | PLATEAU | REKT | NO_DATA | MAX_ITERATIONS}",
  "total_iterations": {N},
  "params": {
    // All parameters from the best iteration
  },
  "is_metrics": {
    "sharpe_ratio": {value},
    "sortino_ratio": {value},
    "calmar_ratio": {value},
    "max_drawdown": {value},
    "win_rate": {value},
    "profit_factor": {value},
    "expectancy": {value},
    "trade_count": {value},
    "net_pnl": {value}
  },
  "oos_metrics": {
    "sharpe_ratio": {value},
    "sortino_ratio": {value},
    "calmar_ratio": {value},
    "max_drawdown": {value},
    "win_rate": {value},
    "profit_factor": {value},
    "expectancy": {value},
    "trade_count": {value},
    "net_pnl": {value}
  },
  "iteration_summary": {
    "1": {"sharpe_is": {value}, "sharpe_oos": {value}},
    "2": {"sharpe_is": {value}, "sharpe_oos": {value}},
    // ... all iterations
  },
  "overfitting_assessment": {
    "is_oos_sharpe_ratio": {ratio},
    "warning": {true/false},
    "notes": "Assessment of IS vs OOS divergence"
  }
}
```

### Display Final Summary

```
===========================================
  LOOP COMPLETE -- {STOP_CONDITION}
===========================================
Best iteration: {N} of {total}
  Sharpe:    {is_value} (IS) / {oos_value} (OOS)
  Max DD:    {is_value}% (IS) / {oos_value}% (OOS)
  Win Rate:  {is_value}% (IS) / {oos_value}% (OOS)
  Trades:    {is_count} (IS) / {oos_count} (OOS)
  Net P&L:  ${is_value} (IS) / ${oos_value} (OOS)

{If overfitting warning:}
  WARNING: IS/OOS Sharpe ratio is {ratio}x -- possible overfit

Result saved: .pmf/phases/phase_N_best_result.json
===========================================
```

**Stop condition-specific messages:**

- **MINT:** "Congratulations! Your strategy hit all targets. Review the OOS metrics to confirm the results generalize beyond the training data."

- **PLATEAU:** "Optimization has plateaued after {N} iterations without significant improvement. Consider:
  (1) Run more iterations with `--iterations {higher_N}`
  (2) Widen parameter ranges via /brrr:plan
  (3) Try a different optimization method
  (4) Revisit strategy logic via /brrr:discuss"

- **REKT:** Display the specific diagnosis from Step 5d:
  - Strategy no edge: "The {strategy_type} strategy does not appear to have an edge with these parameters on {asset}. Consider a fundamentally different approach or a different asset/timeframe."
  - Wrong asset/timeframe: "Your {strategy_type} strategy may work better on {suggestions}. Consider: (1) {specific suggestion based on strategy type}, (2) {alternative asset}, (3) {alternative timeframe}."

- **NO DATA:** "Data issues prevented the backtest from running. See above for details."

- **MAX_ITERATIONS:** "Reached maximum iterations ({N}). The best result was at iteration {K}. You can continue with `--resume --iterations {higher_N}` to run more iterations."

---

## Step 7: Update STATE.md

Update the milestone state to reflect execute completion.

1. Read `.pmf/STATE.md`
2. Mark execute step as done: `- [x] Execute`
3. Update Current Step to `verify` (the next step in the sequence)
4. Update Last Updated to today's date
5. Append to History (newest entries first):

```
### {date} -- Phase {N} execute completed
- **Stop condition:** {MINT/PLATEAU/REKT/NO_DATA/MAX_ITERATIONS}
- **Iterations:** {total}
- **Best Sharpe:** {is_value} (IS) / {oos_value} (OOS)
- **Best Max DD:** {is_value}% (IS) / {oos_value}% (OOS)
- **Best iteration:** {N}
```

6. Write updated STATE.md

---

## Step 8: Confirmation

Display the completion message with next step guidance.

```
Phase {N} execute complete!

Artifact:        .pmf/phases/phase_N_best_result.json
Stop condition:  {condition}
Iterations:      {total}
Best Sharpe:     {is_value} (IS) / {oos_value} (OOS)
Best Max DD:     {is_value}% (IS) / {oos_value}% (OOS)

Next step: `/brrr:verify`
```

---

## Appendix: Reference Code Integration

This workflow depends on these fixed reference modules. They MUST NOT be modified.

### backtest_engine.py

**Function:** `run_backtest(df, params) -> dict`
- Event-loop backtest with anti-lookahead enforcement
- Calls `calculate_signal(history, params)` which Claude monkey-patches
- Returns `compute_all_metrics()` output dict

**Function:** `save_iteration_artifacts(results, params, iteration, output_dir)`
- Saves `iter_NN_params.json` and `iter_NN_metrics.json`

**Function:** `calculate_signal(history, params) -> str`
- Default returns 'hold'
- Claude MUST override this via monkey-patching before calling `run_backtest()`

### data_sources.py

**Function:** `load_ccxt(exchange, symbol, timeframe, since, limit=1000) -> DataFrame`
- Handles pagination automatically
- Workflow MUST pass `limit=50000` for proper backtest data coverage

**Function:** `load_yfinance(ticker, start, end, interval='1d') -> DataFrame`
- Passes `multi_level_index=False` to prevent MultiIndex columns

**Function:** `load_csv(filepath, date_column='date', date_format=None) -> DataFrame`
- Handles column normalization and date parsing

**Function:** `validate_ohlcv(df, source='unknown') -> DataFrame`
- Validates and cleans OHLCV data

### metrics.py

**Function:** `compute_all_metrics(trades, equity_curve, daily_returns, ...) -> dict`
- Returns: sharpe_ratio, sortino_ratio, calmar_ratio, max_drawdown, win_rate, profit_factor, expectancy, trade_count, net_pnl
- Accepts trade list or daily returns as input
- Note: Does NOT include raw equity curve in return dict

---

## Appendix: Requirement Coverage

This workflow covers the following requirements:

| ID | Description | Where Covered |
|----|-------------|---------------|
| EXEC-01 | AI-driven backtest loop | Step 5 (full iteration loop) |
| EXEC-02 | Claude writes Python backtest | Step 5a (write Python script) |
| EXEC-03 | Data sourcing via ccxt, yfinance, CSV | Step 2 (load & validate data) |
| EXEC-04 | Core metrics per iteration | Step 5a (compute_all_metrics), Step 5c (read artifacts) |
| EXEC-05 | Commission modeling | Step 5a (commission in params dict) |
| EXEC-06 | IS/OOS split enforced | Step 3 (calculate split), Step 5a (separate IS/OOS runs) |
| EXEC-07 | Walk-forward analysis | Step 3 (walk-forward split), Step 5a (rolling window loop) |
| EXEC-08 | Stop conditions: MINT, PLATEAU, REKT, NO DATA | Step 5d (evaluate stop conditions) |
| EXEC-09 | AI reads metrics and equity curve | Step 5c (read artifacts), Step 5e (AI analysis) |
| EXEC-10 | Per-iteration artifacts | Step 5a (params, metrics, equity PNG), Step 5f (verdict JSON) |
| EXEC-11 | Terminal display | Step 5e (formatted iteration block with brrr...) |
| EXEC-12 | --iterations, --fast, --resume flags | Preamble: Parse Arguments |
| EXEC-13 | Overfitting detection | Step 5e (IS vs OOS comparison, suspicious metrics) |
| EXEC-14 | phase_N_best_result.json output | Step 6 (finalize) |
| DATA-01 | ccxt integration for crypto | Step 2 (load_ccxt with limit=50000) |
| DATA-02 | yfinance integration for stocks/forex | Step 2 (load_yfinance with multi_level_index fix) |
| DATA-03 | CSV fallback | Step 2 (load_csv) |
| DATA-04 | Data validation | Step 2 (validate_ohlcv + enhanced gap detection) |
| DATA-05 | Local data caching | Step 2 (parquet cache in .pmf/cache/) |

---

*Workflow: execute*
*Covers: EXEC-01, EXEC-02, EXEC-03, EXEC-04, EXEC-05, EXEC-06, EXEC-07, EXEC-08, EXEC-09, EXEC-10, EXEC-11, EXEC-12, EXEC-13, EXEC-14, DATA-01, DATA-02, DATA-03, DATA-04, DATA-05*
