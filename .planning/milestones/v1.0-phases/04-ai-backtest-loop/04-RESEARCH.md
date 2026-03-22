# Phase 4: AI Backtest Loop - Research

**Researched:** 2026-03-21
**Domain:** AI-driven iterative backtest optimization with Python execution bridge
**Confidence:** HIGH

## Summary

Phase 4 is the core product differentiator -- the iterative AI backtest loop. The workflow is a behavioral markdown file (~600-800 lines) that Claude Code follows step-by-step. The key architectural challenge is the "file-based bridge pattern": Claude writes Python scripts to disk, executes them via `~/.pmf/venv/bin/python`, reads JSON/PNG outputs, analyzes results (including multimodal equity curve reading), decides parameter adjustments, and repeats. All reference code (backtest_engine.py, data_sources.py, metrics.py) is already built and tested -- Claude adapts only the `calculate_signal()` function per strategy.

The existing data_sources.py has a critical yfinance bug: it does not pass `multi_level_index=False`, which causes multi-level column issues in recent yfinance versions (>=0.2.48). The existing ccxt pagination in data_sources.py is sound but the `limit` parameter defaults to 1000 which is too low for typical backtest data needs -- the workflow must request much higher limits. Walk-forward analysis requires careful window slicing logic that must be clearly specified in the workflow instructions.

**Primary recommendation:** Structure the workflow as a state machine with clear phases (preamble -> data load -> iteration loop -> stop evaluation -> finalize), where each iteration writes Python, executes it, reads artifacts, and makes a decision. The iteration loop is the inner engine; everything else is setup and teardown.

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions
- **D-01:** Holistic analysis per iteration -- Claude reads ALL artifacts (metrics JSON + equity PNG + trade list + prior iterations' verdicts). Forms a hypothesis about what's not working. Not just metric-driven rules.
- **D-02:** Adaptive change rate -- start with 1-2 parameter changes per iteration, increase to 3-4 if plateau detected. Accelerate when stuck.
- **D-03:** Always explain reasoning -- each iteration: "I'm changing X because Y, expecting Z". User learns and can redirect. No silent parameter tweaks.
- **D-04:** Claude writes Python backtest from scratch each time, adapting the reference skeleton (`~/.pmf/references/backtest_engine.py`) to the specific strategy. Uses fixed data adapters (`data_sources.py`) and fixed metrics module (`metrics.py`).
- **D-05:** Walk-forward, grid search, or random search per plan phase decision. Execute follows the method selected in plan.
- **D-06:** MINT -- targets hit. Stop, save best result, suggest: "targets hit -- run more iterations to improve?" User decides whether to continue.
- **D-07:** PLATEAU -- configurable in plan phase (default: 3 iterations without >5% improvement). Plan defines threshold, execute enforces.
- **D-08:** REKT -- no edge at any params. Diagnose cause: distinguish "strategy logic has no edge" vs "asset/timeframe wrong for this strategy". Different fix paths for each.
- **D-09:** NO DATA -- insufficient data, API error, delisting. Report clearly with what went wrong.
- **D-10:** Match spec format exactly: header with milestone/pair/method, then per-iteration block with params, metrics, AI commentary, "brrr..."
- **D-11:** Equity PNG saved to `.pmf/phases/phase_N_execute/iter_NN_equity.png` and mentioned in output.
- **D-12:** Per-iteration artifacts: `iter_NN_params.json`, `iter_NN_metrics.json`, `iter_NN_equity.png`, `iter_NN_verdict.json` -- all in phase_N_execute/ directory.
- **D-13:** `--iterations N` (default 10), `--fast` (skip PNG generation), `--resume` (continue from last saved iteration).
- **D-14:** Data source from STRATEGY.md -- user specified exchange/source in new-milestone. Execute reads it and calls the appropriate adapter. No re-asking.
- **D-15:** Data cache in `.pmf/cache/` -- project-local, persists across iterations. Clear manually or on new milestone.
- **D-16:** Data validation: auto-fix small gaps (<5 bars via forward-fill), drop NaN rows, warn user what was fixed. Refuse if >10% of data affected.
- **D-17:** ccxt for crypto (use exchange from STRATEGY.md), yfinance for stocks/forex daily, CSV fallback for any asset.
- **D-18:** Compare in-sample vs out-of-sample metrics each iteration. Warn when they diverge significantly (e.g., IS Sharpe > 2x OOS Sharpe).
- **D-19:** Warn when metrics look "too good" (Sharpe > 3.0, Profit Factor > 5.0, Win Rate > 80%).

### Claude's Discretion
- Exact Python code structure per strategy (within backtest_engine.py constraints)
- How to interpret equity curve visual patterns
- When to try radically different parameters vs incremental adjustments
- Error handling for Python execution failures
- How to format iteration verdict JSON

### Deferred Ideas (OUT OF SCOPE)
None -- discussion stayed within phase scope
</user_constraints>

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|-----------------|
| EXEC-01 | AI-driven backtest loop: load data -> run backtest -> compute metrics -> AI analyzes -> adjust params -> repeat | File-based bridge pattern: write Python -> Bash execute -> read JSON/PNG -> analyze -> repeat. Workflow state machine architecture. |
| EXEC-02 | Claude writes Python backtest engine from scratch based on plan phase decisions | Adapt backtest_engine.py skeleton: replace calculate_signal() body only. Write complete .py file per iteration to phase_N_execute/ dir. |
| EXEC-03 | Data sourcing via ccxt, yfinance, CSV fallback | Use existing data_sources.py adapters. Fix yfinance multi_level_index bug. Handle ccxt pagination for large datasets. |
| EXEC-04 | Core metrics computed per iteration | Use fixed metrics.py compute_all_metrics(). Already returns all 9 metrics. |
| EXEC-05 | Commission and slippage modeling | Already built into backtest_engine.py. Workflow reads commission from discuss/plan artifacts. |
| EXEC-06 | In-sample / out-of-sample split enforced | Workflow calculates exact date split from plan percentages. Run backtest on IS data, validate on OOS. Report both metric sets. |
| EXEC-07 | Walk-forward analysis available | Implement rolling window loop in workflow instructions. Train window -> optimize -> test window -> advance. Concatenate OOS results. |
| EXEC-08 | Stop conditions: MINT, PLATEAU, REKT, NO DATA | Evaluate after each iteration. MINT checks plan targets. PLATEAU tracks improvement history. REKT after N consecutive poor iterations. NO DATA on load failure. |
| EXEC-09 | AI reads metrics and equity curve each iteration | Read iter_NN_metrics.json + analyze iter_NN_equity.png via multimodal. Claude forms hypothesis and decides next params. |
| EXEC-10 | Per-iteration artifacts saved | save_iteration_artifacts() already in backtest_engine.py for params/metrics JSON. Add equity PNG via matplotlib and verdict JSON via workflow. |
| EXEC-11 | Real-time terminal display | Workflow prints formatted blocks per iteration with params, metrics table, AI commentary, "brrr..." |
| EXEC-12 | --iterations N, --fast, --resume flags | Parse from $ARGUMENTS. --fast skips matplotlib PNG. --resume reads existing iter_*_verdict.json to find last iteration. |
| EXEC-13 | Overfitting detection | Compare IS vs OOS Sharpe ratio. Warn if IS > 2x OOS. Warn on suspiciously good metrics (Sharpe > 3, PF > 5, WR > 80%). |
| EXEC-14 | Outputs phase_N_best_result.json | After loop ends, write best iteration's params + metrics + stop reason to best_result.json. |
| DATA-01 | ccxt integration for crypto | load_ccxt() in data_sources.py. Key edge cases: pagination limits, rate limiting, exchange-specific behaviors. |
| DATA-02 | yfinance integration for stocks/forex | load_yfinance() in data_sources.py. Must add multi_level_index=False fix. |
| DATA-03 | CSV fallback | load_csv() in data_sources.py. Already handles column normalization. |
| DATA-04 | Data validation before every backtest | validate_ohlcv() in data_sources.py + enhanced gap detection per D-16. |
| DATA-05 | Local data caching | Workflow saves downloaded data to .pmf/cache/ as parquet/CSV. Check cache before downloading. |
</phase_requirements>

## Standard Stack

### Core (already installed in venv)
| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| pandas | ^3.0 | OHLCV DataFrames, time series slicing | Already in venv. Used by data_sources.py and backtest_engine.py |
| numpy | ^2.4 | Equity curves, returns arrays | Already in venv. Used by metrics.py |
| matplotlib | ^3.10 | Per-iteration equity curve PNGs | Headless via Agg backend. No Chrome dependency. Already in venv |
| ccxt | latest | Crypto exchange OHLCV data | Already in venv. 100+ exchanges unified API |
| yfinance | ^1.2 | Stocks/forex daily OHLCV data | Already in venv. Must use multi_level_index=False |

### Supporting
| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| json (stdlib) | -- | Params, metrics, verdict serialization | Every iteration for artifact I/O |
| pathlib (stdlib) | -- | Cross-platform path handling | File operations throughout |
| subprocess (stdlib) | -- | Python script execution from Claude's Bash tool | Not used directly -- Claude uses Bash tool to invoke venv python |

### No New Dependencies Needed
This phase uses only libraries already installed by the Phase 1 install script. No new pip installs required.

## Architecture Patterns

### Recommended Workflow Structure
```
workflows/execute.md (~700 lines)
├── Preamble: Sequence Validation       # Same pattern as discuss.md/plan.md
├── Preamble: Context File Scan         # Same pattern
├── Step 1: Load Inputs                 # Read plan, discuss, strategy artifacts
├── Step 2: Load & Validate Data        # Call data adapters, cache, validate
├── Step 3: Calculate IS/OOS Split      # From plan percentages to exact dates
├── Step 4: Initialize Iteration State  # Set up tracking, handle --resume
├── Step 5: Iteration Loop              # THE CORE -- repeat until stop condition
│   ├── 5a: Write Python Script         # Adapt backtest_engine.py with strategy signal
│   ├── 5b: Execute Python Script       # Bash: ~/.pmf/venv/bin/python script.py
│   ├── 5c: Read Artifacts              # Read JSON metrics, optionally read PNG
│   ├── 5d: Evaluate Stop Conditions    # MINT/PLATEAU/REKT/NO DATA check
│   ├── 5e: AI Analysis & Display       # Analyze results, print formatted output
│   └── 5f: Decide Next Parameters      # Hypothesis -> param changes -> verdict JSON
├── Step 6: Finalize                    # Save best_result.json
├── Step 7: Update STATE.md             # Mark execute done
└── Step 8: Confirmation                # Display summary
```

### Pattern 1: File-Based Bridge (Write -> Execute -> Read)
**What:** Claude writes a complete Python script, executes it via Bash, reads the output files.
**When to use:** Every iteration of the backtest loop.
**Example:**
```python
# Claude writes this to .pmf/phases/phase_N_execute/run_iter_01.py
import sys
sys.path.insert(0, str(Path.home() / '.pmf' / 'references'))
from backtest_engine import run_backtest, save_iteration_artifacts
from data_sources import load_ccxt, validate_ohlcv
import pandas as pd
import json

# Load cached data
df = pd.read_parquet('/path/to/.pmf/cache/BTC_USDT_1h.parquet')

# Strategy signal function (Claude fills this in)
def calculate_signal(history, params):
    sma_fast = history['close'].rolling(params['fast_period']).mean().iloc[-1]
    sma_slow = history['close'].rolling(params['slow_period']).mean().iloc[-1]
    if sma_fast > sma_slow:
        return 'long'
    elif sma_fast < sma_slow:
        return 'close'
    return 'hold'

# Monkey-patch the engine's signal function
import backtest_engine
backtest_engine.calculate_signal = calculate_signal

# Run backtest
params = {"fast_period": 10, "slow_period": 50, "commission": 0.001, "initial_capital": 10000}
results = run_backtest(df, params)

# Save artifacts
save_iteration_artifacts(results, params, iteration=1, output_dir='/path/to/phase_N_execute/')

# Save equity curve PNG
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
fig, ax = plt.subplots(figsize=(12, 6))
ax.plot(results['equity_curve'])
ax.set_title('Equity Curve - Iteration 01')
ax.set_ylabel('Equity')
fig.savefig('/path/to/phase_N_execute/iter_01_equity.png', dpi=100, bbox_inches='tight')
plt.close(fig)

print("SUCCESS")
```

**Critical detail:** The monkey-patching approach (`backtest_engine.calculate_signal = calculate_signal`) lets Claude write the signal function without modifying the fixed engine file. The engine calls `calculate_signal()` from module scope, so overriding it before `run_backtest()` works.

### Pattern 2: IS/OOS Split Calculation
**What:** Convert plan percentage split to exact date indices.
**When to use:** After data is loaded, before first iteration.
**Example:**
```python
# In the Python script that Claude writes
total_bars = len(df)
train_pct = 0.70  # from plan
split_idx = int(total_bars * train_pct)
df_train = df.iloc[:split_idx]
df_test = df.iloc[split_idx:]

# Run backtest on both splits
results_is = run_backtest(df_train, params)
results_oos = run_backtest(df_test, params)
```

### Pattern 3: Walk-Forward Rolling Windows
**What:** Sliding train/test windows across the full dataset.
**When to use:** When plan specifies walk_forward optimization method.
**Example:**
```python
# Walk-forward loop structure
train_bars = 504  # from plan (e.g., 6 months of 4H bars)
test_bars = 168   # from plan (e.g., 2 months)
step_bars = 168   # from plan (non-overlapping)

all_oos_trades = []
all_oos_equity = []
start = 0

while start + train_bars + test_bars <= len(df):
    df_train = df.iloc[start:start + train_bars]
    df_test = df.iloc[start + train_bars:start + train_bars + test_bars]

    # Optimize on train
    results_is = run_backtest(df_train, params)

    # Validate on test
    results_oos = run_backtest(df_test, params)
    all_oos_trades.extend(results_oos.get('trades', []))

    start += step_bars

# Compute aggregate OOS metrics
from metrics import compute_all_metrics
aggregate = compute_all_metrics(trades=all_oos_trades)
```

### Pattern 4: Verdict JSON Structure
**What:** Structured decision output per iteration for history tracking.
**Claude's discretion** but recommended format:
```json
{
  "iteration": 3,
  "hypothesis": "Wide stop-loss is letting winners run but drawdown is too high",
  "changes_made": [
    {"param": "stop_loss_pct", "old": 5.0, "new": 3.0, "reason": "Reduce DD by tightening stop"},
    {"param": "tp_ratio", "old": 2.0, "new": 2.5, "reason": "Compensate tighter stop with higher TP"}
  ],
  "expected_outcome": "Lower DD with similar or slightly lower Sharpe",
  "is_metrics": {"sharpe_ratio": 1.8, "max_drawdown": -0.25, "trade_count": 47},
  "oos_metrics": {"sharpe_ratio": 1.2, "max_drawdown": -0.18, "trade_count": 21},
  "overfitting_check": {"is_oos_sharpe_ratio": 1.5, "warning": false},
  "stop_condition": "CONTINUE",
  "plateau_counter": 0
}
```

### Pattern 5: Matplotlib Headless Equity Curve
**What:** Generate equity curve PNG without GUI.
**Critical:** Must set `matplotlib.use('Agg')` BEFORE importing pyplot.
```python
import matplotlib
matplotlib.use('Agg')  # MUST be before pyplot import
import matplotlib.pyplot as plt

def save_equity_png(equity_curve, filepath, title="Equity Curve"):
    fig, ax = plt.subplots(figsize=(12, 6))
    ax.plot(equity_curve, linewidth=1)
    ax.set_title(title)
    ax.set_ylabel('Equity ($)')
    ax.set_xlabel('Bar')
    ax.grid(True, alpha=0.3)
    fig.savefig(filepath, dpi=100, bbox_inches='tight')
    plt.close(fig)  # Critical: prevent memory leak across iterations
```

### Anti-Patterns to Avoid
- **Modifying reference files:** NEVER write to backtest_engine.py, data_sources.py, or metrics.py. Always monkey-patch or write standalone scripts.
- **Executing at close price:** The engine already handles this, but Claude's written signal function must not try to access future data.
- **Forgetting plt.close():** Matplotlib accumulates figures in memory. Close after every savefig.
- **Running Python with system python:** Always use `~/.pmf/venv/bin/python` explicitly.
- **Hardcoding paths:** Use Path.home() / '.pmf' for reference files, and pass output_dir as argument for phase artifacts.

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Metric computation | Custom Sharpe/Sortino/DD functions | `metrics.py` `compute_all_metrics()` | Fixed, tested module with 32 known-answer tests. Trust anchor for all results. |
| Data fetching | Custom HTTP/REST calls | `data_sources.py` `load_ccxt()` / `load_yfinance()` / `load_csv()` | Handles pagination, validation, column normalization. Edge cases already covered. |
| Event loop | Custom bar-by-bar iteration | `backtest_engine.py` `run_backtest()` | Anti-lookahead rules enforced. Position management, commission tracking built in. |
| OHLCV validation | Custom NaN/gap checking | `data_sources.py` `validate_ohlcv()` | Handles duplicates, sort order, type coercion, NaN removal. |
| Artifact serialization | Custom JSON writers | `backtest_engine.py` `save_iteration_artifacts()` | Handles numpy type serialization, non-serializable value filtering. |

**Key insight:** Nearly all Python-side infrastructure already exists in references/. The workflow's job is ORCHESTRATION -- writing the glue script that connects these modules, not reimplementing them.

## Common Pitfalls

### Pitfall 1: yfinance Multi-Level Column Index
**What goes wrong:** yfinance >= 0.2.48 returns MultiIndex columns even for single tickers. The data_sources.py `load_yfinance()` handles this with `get_level_values(0)` but does NOT pass `multi_level_index=False` to prevent it upfront.
**Why it happens:** yfinance changed defaults in late 2024/early 2025.
**How to avoid:** The workflow-generated Python scripts should add `multi_level_index=False` to `yf.download()` calls. Or better: fix `data_sources.py` during this phase to add the parameter.
**Warning signs:** KeyError on 'open', 'close' columns. MultiIndex-related pandas errors.

### Pitfall 2: ccxt Pagination Limits
**What goes wrong:** Default `limit=1000` in `load_ccxt()` only fetches 1000 candles. A 1-year backtest on 1H data needs ~8760 candles.
**Why it happens:** Most exchanges cap single requests at 500-1500 candles.
**How to avoid:** The workflow must pass a higher `limit` parameter (e.g., 50000) to trigger pagination. The `load_ccxt()` function already handles pagination internally.
**Warning signs:** Backtest has unexpectedly few bars. Date range doesn't match request.

### Pitfall 3: Python Script Execution Failures
**What goes wrong:** The Python script Claude writes has syntax errors, import failures, or runtime exceptions. The iteration fails silently.
**Why it happens:** Claude is writing Python code in a markdown workflow -- no IDE, no linting.
**How to avoid:** Always capture stderr from Bash execution. Check for "SUCCESS" sentinel at end of script output. On failure, read the traceback, fix the script, and retry (up to 2 retries per iteration).
**Warning signs:** No output files created. Bash exit code != 0.

### Pitfall 4: Memory Leak from matplotlib Figures
**What goes wrong:** Each iteration creates a matplotlib figure. Without `plt.close(fig)`, figures accumulate in memory. After 10+ iterations, memory usage balloons.
**Why it happens:** matplotlib keeps references to all created figures.
**How to avoid:** Always call `plt.close(fig)` after `fig.savefig()`. Add `plt.close('all')` as safety net at end of script.
**Warning signs:** Script slows down or crashes on later iterations.

### Pitfall 5: IS/OOS Split Leakage
**What goes wrong:** The backtest accidentally uses OOS data during optimization. Most commonly via indicator warmup periods that need bars before the IS start date.
**Why it happens:** Rolling indicators (e.g., 200-bar SMA) produce NaN for the first 200 bars. If the IS period is sliced exactly at the split point, the first 200 bars of IS produce no signals.
**How to avoid:** Start the data slice with enough warmup bars before the IS period. Alternatively, accept that the first N bars produce no trades (the engine's signal function returns 'hold' for insufficient data).
**Warning signs:** First iteration has very few trades. IS period effectively shorter than expected.

### Pitfall 6: Equity Curve Not in Results Dict
**What goes wrong:** `compute_all_metrics()` does not include the raw equity curve in its return value. The workflow needs it for PNG generation.
**Why it happens:** The `run_backtest()` function returns `compute_all_metrics()` output which contains float metrics but not the equity array.
**How to avoid:** The workflow-generated Python script must capture the equity curve BEFORE calling `compute_all_metrics()`, or modify the script to build it from the trades list. Actually, looking at the code more carefully: `run_backtest()` passes `equity_curve=np.array(equity)` to `compute_all_metrics()`, but `compute_all_metrics()` does NOT include the equity curve in its return dict. The script must track equity separately.
**Warning signs:** KeyError when trying to access `results['equity_curve']`.

### Pitfall 7: Resume State Corruption
**What goes wrong:** `--resume` reads existing artifacts to find last iteration, but the artifacts from a partial run may be inconsistent (e.g., metrics.json exists but verdict.json doesn't).
**Why it happens:** The previous run was interrupted between artifact writes.
**How to avoid:** Resume should find the last iteration where verdict.json exists (the final artifact written per iteration). Treat any incomplete iteration as not finished.
**Warning signs:** Resume starts from wrong iteration. Missing artifacts for an iteration.

## Code Examples

### Data Loading with Cache
```python
# Source: project data_sources.py + caching pattern
import pandas as pd
from pathlib import Path
import sys

sys.path.insert(0, str(Path.home() / '.pmf' / 'references'))
from data_sources import load_ccxt, load_yfinance, load_csv, validate_ohlcv

cache_dir = Path('.pmf/cache')
cache_dir.mkdir(parents=True, exist_ok=True)

# Determine cache filename
cache_file = cache_dir / 'BTC_USDT_binance_1h.parquet'

if cache_file.exists():
    df = pd.read_parquet(cache_file)
    print(f"Loaded from cache: {len(df)} bars")
else:
    df = load_ccxt('binance', 'BTC/USDT', '1h', '2023-01-01', limit=50000)
    df.to_parquet(cache_file)
    print(f"Downloaded and cached: {len(df)} bars")
```

### Enhanced Data Validation (per D-16)
```python
# Source: project pattern extended for gap detection
def validate_and_fix_gaps(df, source="unknown", max_gap_bars=5, max_affected_pct=0.10):
    """Validate OHLCV data with gap auto-fixing per D-16."""
    original_len = len(df)

    # Run standard validation first
    df = validate_ohlcv(df, source=source)

    # Detect gaps in time index
    if hasattr(df.index, 'freq') and df.index.freq:
        expected_freq = df.index.freq
    else:
        # Infer frequency from median diff
        diffs = pd.Series(df.index).diff().dropna()
        expected_freq = diffs.median()

    # Forward-fill small gaps
    gaps = pd.Series(df.index).diff().dropna()
    large_gaps = gaps[gaps > expected_freq * 1.5]

    if len(large_gaps) > 0:
        total_missing = sum((g / expected_freq - 1) for g in large_gaps)
        affected_pct = total_missing / original_len

        if affected_pct > max_affected_pct:
            raise ValueError(
                f"[{source}] {affected_pct:.1%} of data affected by gaps "
                f"(threshold: {max_affected_pct:.0%}). Refusing to proceed."
            )

        # Reindex and forward-fill small gaps
        full_index = pd.date_range(df.index[0], df.index[-1], freq=expected_freq)
        df = df.reindex(full_index)
        df = df.ffill(limit=max_gap_bars)
        df = df.dropna()

        print(f"[{source}] Fixed {int(total_missing)} gap bars via forward-fill")

    return df
```

### Terminal Display Format (per D-10)
```
===========================================
  PRINT MONEY FACTORY -- brrr...
===========================================
Milestone: SMC Breakout Strategy
Pair:      BTC/USDT (Binance, 1H)
Method:    Walk-Forward | 10 iterations
Split:     70% IS / 30% OOS
-------------------------------------------

Iteration 03/10                    brrr...
-------------------------------------------
Parameters:
  fast_period:    10  (was 12)
  slow_period:    50  (unchanged)
  stop_loss_pct:  3.0 (was 5.0)
  tp_ratio:       2.5 (was 2.0)

Metrics (IS / OOS):
  Sharpe:         1.82 / 1.21
  Max Drawdown:  -18.3% / -14.1%
  Win Rate:       54.2% / 51.8%
  Profit Factor:  1.87 / 1.53
  Trades:         47 / 21
  Net P&L:       $2,841 / $1,203

AI Analysis:
  Tightening the stop from 5% to 3% reduced drawdown
  significantly (-25% -> -18% IS). Sharpe improved from
  1.65 to 1.82. The IS/OOS ratio is healthy (1.5x).
  Next: testing faster signal with fast_period=8 to catch
  more trends while keeping the tighter stop.

  Equity curve: iter_03_equity.png saved
-------------------------------------------
```

### Overfitting Detection (per D-18, D-19)
```python
# Source: project pattern from CONTEXT.md decisions
def check_overfitting(is_metrics, oos_metrics):
    """Check for overfitting signals. Returns list of warnings."""
    warnings = []

    # D-18: IS vs OOS divergence
    is_sharpe = is_metrics.get('sharpe_ratio', 0)
    oos_sharpe = oos_metrics.get('sharpe_ratio', 0)

    if oos_sharpe > 0 and is_sharpe / oos_sharpe > 2.0:
        warnings.append(
            f"OVERFITTING WARNING: IS Sharpe ({is_sharpe:.2f}) is "
            f"{is_sharpe/oos_sharpe:.1f}x OOS Sharpe ({oos_sharpe:.2f})"
        )

    # D-19: Suspiciously good metrics
    if is_sharpe > 3.0:
        warnings.append(f"SUSPICIOUS: Sharpe {is_sharpe:.2f} > 3.0 -- possible lookahead or overfit")
    if is_metrics.get('profit_factor', 0) > 5.0:
        warnings.append(f"SUSPICIOUS: Profit Factor {is_metrics['profit_factor']:.2f} > 5.0")
    if is_metrics.get('win_rate', 0) > 0.80:
        warnings.append(f"SUSPICIOUS: Win Rate {is_metrics['win_rate']:.0%} > 80%")

    return warnings
```

### Stop Condition Evaluation
```python
# Source: project pattern from CONTEXT.md decisions D-06 through D-09
def evaluate_stop_condition(
    current_metrics,
    targets,
    iteration_history,
    plateau_threshold=3,
    improvement_pct=0.05,
):
    """Evaluate stop conditions after each iteration."""

    # D-06: MINT -- targets hit
    sharpe_target = targets.get('sharpe_ratio', 1.5)
    dd_target = targets.get('max_drawdown', -0.20)  # negative fraction
    if (current_metrics['sharpe_ratio'] >= sharpe_target and
        current_metrics['max_drawdown'] >= dd_target):
        return 'MINT', "Targets hit! Sharpe and Max DD within goals."

    # D-07: PLATEAU -- no improvement
    if len(iteration_history) >= plateau_threshold:
        recent = iteration_history[-plateau_threshold:]
        best_recent = max(m['sharpe_ratio'] for m in recent)
        best_before = max(m['sharpe_ratio'] for m in iteration_history[:-plateau_threshold]) if len(iteration_history) > plateau_threshold else 0
        if best_before > 0 and (best_recent - best_before) / abs(best_before) < improvement_pct:
            return 'PLATEAU', f"{plateau_threshold} iterations without >{improvement_pct:.0%} Sharpe improvement."

    # D-08: REKT -- no edge at all
    if len(iteration_history) >= 5:
        all_negative = all(m['sharpe_ratio'] < 0 for m in iteration_history[-5:])
        if all_negative:
            return 'REKT', "Last 5 iterations all have negative Sharpe. No edge detected."

    return 'CONTINUE', None
```

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| yfinance single-level columns default | yfinance multi-level columns default | v0.2.48 (2024) | Must pass `multi_level_index=False` or handle MultiIndex |
| matplotlib implicit backend | matplotlib requires explicit Agg for headless | Always been this way | Must set `matplotlib.use('Agg')` before pyplot import |
| ccxt synchronous only | ccxt supports both sync and async | 2023+ | Use sync for simplicity in backtest scripts |

**Deprecated/outdated:**
- yfinance `auto_adjust=True` was the default but behavior may change. The existing data_sources.py already passes it explicitly -- good.
- pandas `infer_datetime_format` used in `load_csv()` is deprecated in pandas 2.x. Should use `format='mixed'` or explicit format. LOW priority since CSV is fallback path.

## Open Questions

1. **Equity Curve Access Pattern**
   - What we know: `run_backtest()` computes an equity list internally and passes it to `compute_all_metrics()`, but the returned dict does NOT include the raw equity curve array.
   - What's unclear: Whether to modify `run_backtest()` to return the equity curve, or have the workflow script track it separately.
   - Recommendation: Have the workflow-generated Python script capture the equity list by modifying `run_backtest()` return to include it, OR (safer, since references are "fixed") have the script reconstruct equity from the trades list using `compute_all_metrics()` which does accept an `equity_curve` parameter. Best approach: the generated script should call `run_backtest()` and also separately reconstruct the equity curve from trades for PNG generation.

2. **Monkey-Patching vs Standalone Script**
   - What we know: The backtest_engine.py expects `calculate_signal()` at module level. Claude needs to inject per-strategy logic.
   - What's unclear: Whether monkey-patching is reliable across all Python versions, or if a standalone script that copies the engine code is safer.
   - Recommendation: Use monkey-patching (`backtest_engine.calculate_signal = my_signal_function`). It's standard Python, works reliably. The alternative (copying engine code) risks divergence from the reference and violates the "DO NOT modify" rule. Monkey-patching respects the fixed engine while allowing per-strategy customization.

3. **Walk-Forward Iteration Counting**
   - What we know: `--iterations N` controls the AI optimization loop. Walk-forward has its own internal window iterations.
   - What's unclear: Does `--iterations N` mean N AI optimization rounds (each running the full walk-forward), or N total walk-forward windows?
   - Recommendation: `--iterations N` = N AI optimization rounds. Each round runs the complete walk-forward analysis with current parameters. The walk-forward windows are internal to each round.

## Validation Architecture

### Test Framework
| Property | Value |
|----------|-------|
| Framework | pytest (already in venv from Phase 1) |
| Config file | None -- tests run from references/ directory |
| Quick run command | `~/.pmf/venv/bin/python -m pytest references/test_metrics.py -x -q` |
| Full suite command | `~/.pmf/venv/bin/python -m pytest references/ -x -q` |

### Phase Requirements --> Test Map
| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|-------------|
| EXEC-01 | Full loop executes end-to-end | integration/manual | Manual -- workflow is markdown behavioral instructions | N/A |
| EXEC-02 | Claude writes valid Python backtest | manual | Manual -- generative code, not testable statically | N/A |
| EXEC-03 | Data adapters work | unit | `~/.pmf/venv/bin/python -c "from data_sources import load_csv; print('ok')"` | Existing |
| EXEC-04 | Metrics computed correctly | unit | `~/.pmf/venv/bin/python -m pytest references/test_metrics.py -x -q` | Existing |
| EXEC-05 | Commission modeling | unit | Covered by test_metrics.py trade fixtures | Existing |
| EXEC-06 | IS/OOS split | manual | Manual -- split logic is in workflow-generated Python | N/A |
| EXEC-07 | Walk-forward | manual | Manual -- window logic is in workflow-generated Python | N/A |
| EXEC-08 | Stop conditions evaluate correctly | manual | Manual -- stop logic is in workflow behavioral instructions | N/A |
| EXEC-09 | AI reads and analyzes artifacts | manual-only | Cannot automate -- requires Claude's judgment | N/A |
| EXEC-10 | Artifacts saved correctly | unit | `~/.pmf/venv/bin/python -c "from backtest_engine import save_iteration_artifacts; print('ok')"` | Existing |
| EXEC-11 | Terminal display format | manual-only | Visual verification during testing | N/A |
| EXEC-12 | CLI flags parsed | manual | Manual -- parsed from $ARGUMENTS in workflow | N/A |
| EXEC-13 | Overfitting detection | manual | Manual -- detection logic in workflow | N/A |
| EXEC-14 | best_result.json output | manual | Manual -- written by workflow | N/A |
| DATA-01 | ccxt loads crypto data | integration | `~/.pmf/venv/bin/python -c "import ccxt; print('ok')"` | N/A |
| DATA-02 | yfinance loads stock data | integration | `~/.pmf/venv/bin/python -c "import yfinance; print('ok')"` | N/A |
| DATA-03 | CSV loads data | unit | Covered by data_sources.py load_csv tests if they exist | N/A |
| DATA-04 | Data validation | unit | Covered by validate_ohlcv tests if they exist | N/A |
| DATA-05 | Caching works | manual | Manual -- caching logic in workflow | N/A |

### Sampling Rate
- **Per task commit:** `~/.pmf/venv/bin/python -m pytest references/test_metrics.py -x -q`
- **Per wave merge:** Full suite + manual workflow smoke test on a simple SMA crossover strategy
- **Phase gate:** Full end-to-end run: `/brrr:execute` with a test milestone producing MINT or PLATEAU

### Wave 0 Gaps
- [ ] `references/test_data_sources.py` -- unit tests for data adapter functions (load_csv at minimum, mock tests for load_ccxt/load_yfinance)
- [ ] Fix `data_sources.py` to add `multi_level_index=False` to `yf.download()` call
- [ ] Verify `backtest_engine.py` monkey-patching works: write a test that overrides `calculate_signal` and runs a simple backtest

Note: Most EXEC requirements are behavioral workflow instructions (markdown), not testable Python code. The primary validation method is end-to-end manual testing with a real or synthetic strategy. The fixed Python modules (metrics.py, backtest_engine.py, data_sources.py) already have or should have unit tests.

## Sources

### Primary (HIGH confidence)
- `references/backtest_engine.py` -- Event-loop skeleton with anti-lookahead rules, 241 lines. Examined directly.
- `references/data_sources.py` -- Data adapters for ccxt, yfinance, CSV with validate_ohlcv(). 333 lines. Examined directly.
- `references/metrics.py` -- Fixed metrics module with compute_all_metrics(). 286 lines. Examined directly.
- `references/backtest-engine.md` -- Pattern guide with 6 anti-lookahead rules. Examined directly.
- `references/common-pitfalls.md` -- 6 backtesting pitfalls catalog. Examined directly.
- `workflows/plan.md` -- Plan workflow defining parameter space, split rules. 532 lines. Examined directly.
- [matplotlib Agg backend docs](https://matplotlib.org/stable/api/backend_agg_api.html)

### Secondary (MEDIUM confidence)
- [yfinance multi_level_index parameter](https://ranaroussi.github.io/yfinance/advanced/multi_level_columns.html) -- multi_level_index=False fix for single ticker downloads
- [ccxt pagination issues](https://github.com/ccxt/ccxt/issues/26252) -- exchange-specific pagination edge cases
- [Walk-forward analysis in Python](https://medium.datadriveninvestor.com/what-is-walk-forward-backtesting-implementation-in-python-ae09baaa5802) -- rolling window implementation patterns

### Tertiary (LOW confidence)
- pandas `infer_datetime_format` deprecation -- needs verification against pandas 3.0 docs for exact replacement

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH -- all libraries already installed and in use by Phase 1 reference code
- Architecture: HIGH -- file-based bridge pattern is well-understood; workflow structure follows established patterns from discuss.md and plan.md
- Pitfalls: HIGH -- examined reference code line-by-line, identified concrete bugs (yfinance multi-level, equity curve access)
- Walk-forward: MEDIUM -- general pattern is clear but exact window management needs careful implementation
- Data caching: MEDIUM -- pattern is straightforward but parquet compatibility and cache invalidation details need implementation-time decisions

**Research date:** 2026-03-21
**Valid until:** 2026-04-21 (stable domain, reference code is fixed)
