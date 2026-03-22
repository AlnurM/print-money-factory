# Architecture: v1.1 Integration Points

**Project:** Print Money Factory v1.1 Enhancement
**Researched:** 2026-03-22
**Focus:** How 5 new features integrate with the existing architecture

## Existing Architecture (Reference)

```
npm package (@print-money-factory/cli@0.4.0)
  bin/install.mjs          -> copies everything to ~/.claude/commands/brrr/ and ~/.pmf/
  commands/*.md             -> thin slash-command stubs (@-ref workflows)
  workflows/*.md            -> behavioral logic (discuss, plan, execute, verify, status, etc.)
  references/               -> fixed Python modules + engine docs
    backtest_engine.py        (9.5K, event-loop backtest, monkey-patched calculate_signal)
    metrics.py                (8K, 9 core metrics, compute_all_metrics)
    data_sources.py           (11K, ccxt/yfinance/CSV adapters)
    report_generator.py       (29.8K, plotly HTML report generation)
    backtest-engine.md        (anti-lookahead rules reference)
    pinescript-rules.md
    pinescript-examples/*.pine
  templates/
    STATE.md                  (milestone state tracker)
    STRATEGY.md               (strategy definition)
    report-template.html      (plotly HTML shell)
    pinescript-template.pine
  requirements.txt            (already includes optuna>=4.7)

Runtime data (.pmf/ in project dir):
  STATE.md                    (current milestone status)
  STRATEGY.md                 (strategy definition)
  cache/                      (OHLCV parquet cache)
  context/                    (user-dropped reference files)
  phases/
    phase_N_discuss.md
    phase_N_research.md
    phase_N_plan.md
    phase_N_execute/
      run_iter_NN.py          (per-iteration backtest script)
      iter_NN_params.json
      iter_NN_metrics.json
      iter_NN_oos_metrics.json
      iter_NN_equity.png
      iter_NN_verdict.json    (AI analysis + next param decisions)
    phase_N_best_result.json
    phase_N_verify/
      report_vN.html
      debug_diagnosis.md
  output/                     (export package on --approved)
```

## Feature 1: Bayesian Optimization (Optuna)

### Current State

The plan workflow (plan.md Step 4) auto-selects optimization method:
- <1000 combos: grid search
- 1000-10000: random search
- 3+ params OR >10000: walk-forward

The execute workflow (execute.md Step 5) implements the loop where Claude writes a new Python script per iteration, runs it, reads results, then decides next parameters via AI analysis (Step 5e-5f). Parameter selection is purely AI-driven -- Claude reads metrics and decides what to change.

Optuna is already in requirements.txt (`optuna>=4.7,<5`) but is never used.

### Integration Architecture

**Where it fits:** New optimization method option alongside grid/random/walk-forward. NOT a replacement for the existing AI-driven loop -- it replaces the parameter SELECTION logic in Step 5f while keeping the AI analysis in Step 5e.

**Key insight:** The current architecture has Claude write a complete Python script per iteration (Step 5a), execute it (Step 5b), then decide next params (Step 5f). Optuna integration should follow the same pattern -- Claude writes a script that uses Optuna's suggest API, not a standalone Optuna study that runs all trials internally. This preserves the per-iteration AI analysis and equity PNG generation.

#### Component Changes

| Component | Change Type | What Changes |
|-----------|-------------|--------------|
| `workflows/plan.md` | MODIFY Step 4 | Add "bayesian" as 4th optimization method option. Auto-select rule: 3+ free params AND >500 combos. Add Optuna-specific config: n_startup_trials (default 10), sampler (TPE default) |
| `workflows/execute.md` | MODIFY Step 5a, 5f | When method=bayesian: (1) Step 5a writes script that loads Optuna study, calls `trial.suggest_*()` for params instead of hardcoded values. (2) Step 5f saves trial result back to study via `study.tell()` or completes trial. AI analysis still happens in 5e. |
| `references/` | NEW file: `optuna_bridge.py` | Thin wrapper that manages Optuna study persistence. Functions: `get_or_create_study(study_name, storage_path, direction)`, `suggest_params(study, param_space)`, `report_result(study, trial, value)`. Storage: SQLite at `.pmf/phases/phase_N_execute/optuna_study.db` |

#### Data Flow (Bayesian Mode)

```
plan.md sets method=bayesian, param_space defined
    |
execute Step 4: create Optuna study (SQLite storage in phase_N_execute/)
    |
    v
execute Step 5a: write Python script that:
  1. imports optuna_bridge
  2. calls suggest_params() -> gets trial params from TPE sampler
  3. runs backtest with those params (same engine, same monkey-patch)
  4. saves IS/OOS metrics
  5. calls report_result() with Sharpe as objective value
  6. generates equity PNG (same as current)
    |
execute Step 5b: run script
execute Step 5c: read artifacts (unchanged)
execute Step 5e: AI analysis (unchanged -- Claude still reads metrics, analyzes equity)
execute Step 5f: SKIP manual param selection -- Optuna handles it via study
    |
    v (loop)
execute Step 6: finalize -- study.best_trial gives best params
```

#### optuna_bridge.py Design

```python
"""Optuna bridge for Bayesian optimization in PMF backtest loop.

Manages study lifecycle, parameter suggestion, and result reporting.
Stored in ~/.pmf/references/ alongside metrics.py and backtest_engine.py.
"""
import optuna
from pathlib import Path

def get_or_create_study(study_name: str, storage_dir: str, direction: str = "maximize") -> optuna.Study:
    """Load existing study or create new one with SQLite storage."""
    storage_path = Path(storage_dir) / "optuna_study.db"
    storage = f"sqlite:///{storage_path}"
    # Suppress Optuna's verbose logging
    optuna.logging.set_verbosity(optuna.logging.WARNING)
    return optuna.create_study(
        study_name=study_name,
        storage=storage,
        direction=direction,
        load_if_exists=True,
        sampler=optuna.samplers.TPESampler(
            n_startup_trials=10,
            multivariate=True,  # model param dependencies
        ),
    )

def suggest_params(study: optuna.Study, param_space: list[dict]) -> tuple:
    """Start a trial and suggest params from the space.

    param_space: list of dicts with keys: name, type, min, max, step
    Returns: (trial, params_dict)
    """
    trial = study.ask()
    params = {}
    for p in param_space:
        if p["type"] == "int":
            params[p["name"]] = trial.suggest_int(p["name"], p["min"], p["max"], step=p.get("step", 1))
        elif p["type"] == "float":
            params[p["name"]] = trial.suggest_float(p["name"], p["min"], p["max"], step=p.get("step"))
        elif p["type"] == "categorical":
            params[p["name"]] = trial.suggest_categorical(p["name"], p["choices"])
    return trial, params

def report_result(study: optuna.Study, trial, value: float):
    """Report the objective value (Sharpe ratio) for a completed trial."""
    study.tell(trial, value)
```

#### Why This Design

1. **Preserves AI analysis loop.** The current architecture's strength is that Claude analyzes results between iterations, catches overfitting, reads equity PNGs, and forms trading-domain hypotheses. A fully internal Optuna study would lose all of this. By using `study.ask()` / `study.tell()` (Optuna's ask-and-tell API), each trial is one iteration of the existing loop.

2. **SQLite persistence enables --resume.** The existing `--resume` flag scans for verdict JSONs. With Optuna, the study persists in SQLite, so resuming just loads the existing study and continues where it left off. The verdict JSON scan still works as a secondary check.

3. **No changes to backtest_engine.py or metrics.py.** The backtest engine and metrics modules remain untouched. Only the parameter selection mechanism changes.

4. **Gradual adoption.** Users can still use grid/random/walk-forward. Bayesian is an additional option, auto-selected for large parameter spaces.

### New Files

| File | Location | Size Estimate |
|------|----------|---------------|
| `references/optuna_bridge.py` | Shipped in npm package, copied to `~/.pmf/references/` | ~80 lines |

### Modified Files

| File | Sections Modified | Nature of Change |
|------|-------------------|------------------|
| `workflows/plan.md` | Step 4 (Select Optimization Method) | Add bayesian option to auto-selection rules and override menu |
| `workflows/execute.md` | Step 4 (init), Step 5a (write script), Step 5f (decide params) | Bayesian code path: use optuna_bridge instead of manual param selection |
| `bin/install.mjs` | None needed | `references/` already copied recursively |
| `package.json` | `files` array | No change needed -- `references/` already included |

### Constraints to Enforce

- Optuna study direction MUST be "maximize" (maximizing Sharpe)
- n_startup_trials MUST be >= 5 (need seed data before TPE kicks in)
- Parameter constraints (e.g., fast_period < slow_period) need Optuna's constraint handling or post-suggestion validation in optuna_bridge.py
- The plan artifact must record sampler choice and n_startup_trials for reproducibility

---

## Feature 2: Enhanced Export (MD-Instruction Format)

### Current State

The verify workflow (verify.md Step 5a) generates 7 export files in `.pmf/output/`:
- pinescript_v5_strategy.pine
- pinescript_v5_indicator.pine
- trading-rules.md
- performance-report.md
- backtest_final.py
- live-checklist.md
- report_vN.html

The STATE.md template already has `- [ ] MD instructions export` in its Scope section, suggesting this was planned from the start.

### Integration Architecture

**What it is:** A new export file `bot-building-guide.md` that provides step-by-step instructions for implementing the strategy as an automated bot on a specific platform (e.g., Freqtrade, CCXT raw, MetaTrader MQL5).

**Where it fits:** New step 5a.9 in verify.md, after 5a.8 (display export summary). Added to the export package alongside existing files.

#### Component Changes

| Component | Change Type | What Changes |
|-----------|-------------|--------------|
| `workflows/verify.md` | MODIFY Step 5a | Add Step 5a.9: generate `bot-building-guide.md`. Read discuss decisions + best params + strategy type. Write platform-specific implementation guide. |
| `workflows/verify.md` | MODIFY Step 5a.8 | Add `bot-building-guide.md` to the export summary display |
| `templates/` | OPTIONAL: `bot-guide-template.md` | Template with sections: Architecture, Data Pipeline, Signal Logic, Order Management, Risk Controls, Deployment. Could also be inline in workflow. |

#### Content Structure

```markdown
# Bot Building Guide: {strategy_name}

## Target Platform
{Auto-detected based on asset type:
  - Crypto: CCXT (direct exchange API)
  - Stocks: Alpaca/IBKR API
  - Forex: MetaTrader 5 / OANDA API}

## Architecture
{Component diagram: Data Feed -> Signal Engine -> Order Manager -> Risk Monitor}

## Implementation Steps

### 1. Data Pipeline
{How to get live OHLCV data. Code snippets for the detected platform.
Example: ccxt.fetch_ohlcv() with websocket fallback.}

### 2. Signal Calculation
{Direct translation of calculate_signal() to production code.
Include the exact indicator calculations from discuss decisions.
Highlight differences from backtest: live has partial bars, need to wait for bar close.}

### 3. Order Execution
{Platform-specific order placement. Market vs limit orders.
Slippage considerations. Commission handling.}

### 4. Position Management
{How to track open positions. Reconciliation with exchange state.
Stop-loss implementation: exchange-side stops vs polling.}

### 5. Risk Controls
{From live-checklist.md: daily loss limits, max drawdown kill switch.
Additional: connection loss handling, stale data detection.}

### 6. Deployment
{Where to run: VPS recommendations, cron vs daemon, logging, monitoring.}

### 7. Testing Checklist
{Paper trade validation steps. How to compare live vs backtest metrics.}
```

#### Why This Design

1. **Complements existing exports.** trading-rules.md tells a human trader what to do. bot-building-guide.md tells a developer how to automate it. Different audiences.
2. **No new Python modules needed.** This is purely a workflow markdown generation task -- Claude reads artifacts and writes markdown.
3. **Platform detection is simple.** Asset type from STRATEGY.md determines the platform: crypto = ccxt, stocks = broker API, forex = MT5/OANDA.

### New Files

| File | Location | Size Estimate |
|------|----------|---------------|
| None (generated at runtime) | `.pmf/output/bot-building-guide.md` | ~200-400 lines per generation |

### Modified Files

| File | Sections Modified |
|------|-------------------|
| `workflows/verify.md` | Step 5a (add 5a.9), Step 5a.8 (update summary) |

---

## Feature 3: /brrr:doctor Diagnostic Command

### Current State

No diagnostic tooling exists. If the venv breaks or dependencies are missing, users get cryptic Python tracebacks during `/brrr:execute`.

The install script (`bin/install.mjs`) already has detection logic for Python version and venv creation that could be partially reused.

### Integration Architecture

**What it is:** A new slash command `/brrr:doctor` that checks system health and reports issues.

**Where it fits:** New command + workflow pair, following the existing thin-command-refs-workflow pattern.

#### Component Architecture

```
commands/doctor.md          -> thin stub, @-refs workflows/doctor.md
workflows/doctor.md         -> behavioral logic (read-only checks)
```

#### Checks to Perform (in order)

| Check | How | Pass | Fail |
|-------|-----|------|------|
| Python version | `~/.pmf/venv/bin/python --version` | >= 3.10 | Missing or too old |
| Venv exists | Check `~/.pmf/venv/bin/python` exists | Exists | Missing -- suggest reinstall |
| Core deps importable | `python -c "import pandas, numpy, optuna, ccxt, plotly"` | All import | List which fail |
| Dep versions | `pip list --format=json` in venv, compare to requirements.txt | All meet minimums | List outdated |
| References intact | Check all 4 .py files exist in `~/.pmf/references/` | All present | List missing |
| Templates intact | Check all templates exist in `~/.pmf/templates/` | All present | List missing |
| Workflows intact | Check all 8 workflows in `~/.pmf/workflows/` | All present | List missing -- suggest /brrr:update |
| Disk space | Check `.pmf/` total size | < 1GB | Warn if cache is large |
| Active milestone | Check `.pmf/STATE.md` exists and parse status | Report status | No milestone (informational) |

#### Output Format

```
Print Money Factory -- Doctor

  System:
    [PASS] Python 3.14.0 (>= 3.10 required)
    [PASS] Venv: ~/.pmf/venv/
    [PASS] Core dependencies (6/6 importable)
    [WARN] optuna 4.7.0 -> 4.8.0 available
    [PASS] References: 4/4 files intact
    [PASS] Templates: 4/4 files intact
    [PASS] Workflows: 8/8 files intact

  Project:
    [PASS] Active milestone: v1 (Phase 2, step: execute)
    [INFO] Cache: 3 files, 12.4 MB
    [INFO] Phases: 2 phases, 14 iteration artifacts

  Result: All checks passed. System healthy.
```

#### Command Definition

```yaml
---
name: brrr:doctor
description: Check system health and diagnose issues
argument-hint: "[--fix]"
allowed-tools:
  - Read
  - Bash
  - Glob
---
```

Note: Read-only by default (no Write tool). The `--fix` flag could enable Write+Bash for auto-repair (reinstall venv, update deps), but that is a stretch goal.

### New Files

| File | Location | Size Estimate |
|------|----------|---------------|
| `commands/doctor.md` | Shipped in npm package | ~15 lines |
| `workflows/doctor.md` | Shipped in npm package | ~150 lines |

### Modified Files

None. New command + workflow pair, no changes to existing files.

---

## Feature 4: Auto Version Check

### Current State

No version checking. Users can be on an old version without knowing.

The `commands/update.md` command exists for manual updates (`npx print-money-factory install`), but there is no automatic check.

### Integration Architecture

**Where it fits:** Injected into every workflow's preamble section, before sequence validation. Runs once per session (tracked by a sentinel file).

#### Mechanism

Every workflow already has a "Preamble" section before the main logic. Add a new preamble section at the very top of each workflow:

```markdown
## Preamble: Version Check (silent)

1. Check if `.pmf/.version_checked` exists AND was modified today (compare file mtime to current date)
2. If already checked today: skip (silent, no output)
3. If NOT checked today:
   a. Read the installed version from `~/.pmf/package.json` (or a `.pmf/.version` file written during install)
   b. Run: `npm view @print-money-factory/cli version 2>/dev/null` (with 5-second timeout)
   c. If npm check fails (offline, timeout): skip silently, touch sentinel
   d. If installed < latest: display one line: "Update available: {installed} -> {latest}. Run /brrr:update"
   e. Touch `.pmf/.version_checked` sentinel file
```

#### Why NOT a Separate Command

A separate command would require users to remember to run it. By embedding in workflow preambles, it happens automatically. The sentinel file ensures it runs at most once per day (not per command).

#### Component Changes

| Component | Change Type | What Changes |
|-----------|-------------|--------------|
| `workflows/*.md` (all 8) | MODIFY preamble | Add Version Check preamble section at top |
| `bin/install.mjs` | MODIFY | Write `.pmf/.version` file during install with current package version |

#### Alternative: Single Include

Instead of duplicating the version check in all 8 workflows, add it to only the most commonly used ones: `execute.md`, `status.md`, `discuss.md`, `verify.md`. This reduces maintenance burden. The doctor command could also run the check.

**Recommendation:** Add to `status.md` and `doctor.md` only. Status is the natural "check things" command. Doctor is the natural "health check" command. Adding to all 8 workflows creates maintenance burden for minimal benefit.

### New Files

| File | Location | Size Estimate |
|------|----------|---------------|
| `.pmf/.version` | Written during install | 1 line (version string) |

### Modified Files

| File | Sections Modified |
|------|-------------------|
| `bin/install.mjs` | Write `.pmf/.version` during install |
| `workflows/status.md` | Add Version Check preamble |
| `workflows/doctor.md` | Include version check as one of its checks |

---

## Feature 5: Smarter Debug Cycles (Failed Approach Memory)

### Current State

The debug cycle works as follows:

1. `/brrr:verify --debug` writes `debug_diagnosis.md` with a hypothesis for the next cycle (Step 5b.1)
2. STATE.md is updated to Phase N+1 (Step 5b.2)
3. `/brrr:discuss` in debug-discuss mode reads ALL prior phase artifacts (Step 1, line 188-201):
   - Prior discuss artifacts: `phase_M_discuss.md` for all M < N
   - Prior research, plan artifacts
   - Last phase's `best_result.json`
   - Last phase's `debug_diagnosis.md`

**The problem:** The discuss workflow reads prior artifacts but has no structured way to track what parameter changes were tried across phases and WHY they failed. Claude reads everything but doesn't have a dedicated "what we've tried and what didn't work" summary. Across multiple debug cycles (Phase 3, 4, 5...), the context window fills up with repetitive artifacts, and Claude may suggest changes that were already tried in an earlier phase.

### Integration Architecture

**What it is:** A cumulative "debug memory" file that persists across phases, tracking: what was tried, what the result was, and why it failed. Each debug cycle appends to this file rather than requiring Claude to re-read all prior artifacts.

#### Design: `.pmf/DEBUG_MEMORY.md`

```markdown
# Debug Memory

Cumulative record of what has been tried across debug cycles.
Each entry records the hypothesis, parameters, result, and lesson learned.
This file is append-only -- do NOT edit previous entries.

## Phase 1 -> Phase 2

### What was tried
- Strategy: EMA crossover (fast=10, slow=50) with ATR stop-loss (multiplier=1.5)
- Parameters optimized: fast_period (5-20), slow_period (30-70), atr_mult (1.0-3.0)

### Result
- Best Sharpe: 0.72 (target: 1.5)
- Max DD: -28% (target: -15%)
- Stop reason: PLATEAU after 8 iterations
- 40% of losses clustered in sideways regime (ADX < 20)

### Diagnosis
- Hypothesis: Add ADX regime filter to avoid sideways markets
- Key insight: Strategy has edge in trending markets only

### Do NOT retry
- ATR multiplier 1.0-1.5 range: tested exhaustively, no improvement in drawdown

---

## Phase 2 -> Phase 3
...
```

#### Component Changes

| Component | Change Type | What Changes |
|-----------|-------------|--------------|
| `workflows/verify.md` | MODIFY Step 5b.1 | After writing `debug_diagnosis.md`, ALSO append to `.pmf/DEBUG_MEMORY.md`. Create file if it doesn't exist. Format: What was tried, Result (key metrics), Diagnosis (from debug_diagnosis.md), Do NOT retry (failed approaches). |
| `workflows/discuss.md` | MODIFY Step 1 | In debug-discuss mode, read `.pmf/DEBUG_MEMORY.md` FIRST, before reading individual phase artifacts. This gives Claude the cumulative context in one file. |
| `workflows/discuss.md` | MODIFY Step 2-debug | Add explicit check: before proposing parameter changes, scan DEBUG_MEMORY.md for "Do NOT retry" entries. If a proposed change matches something already tried, note it and explain why this time is different (or choose a different approach). |
| `workflows/execute.md` | MODIFY Step 5e | In AI analysis, reference DEBUG_MEMORY.md to avoid repeating past mistakes. If current iteration's params overlap with a "Do NOT retry" entry, flag it. |

#### Data Flow

```
Phase 1: execute -> verify --debug
  |
  v
verify writes:
  1. debug_diagnosis.md (per-phase, existing behavior)
  2. DEBUG_MEMORY.md (cumulative, NEW -- append entry for Phase 1)
  |
  v
Phase 2: discuss (debug mode)
  |
  reads DEBUG_MEMORY.md FIRST (single file, full history)
  reads debug_diagnosis.md (latest phase detail)
  |
  AI explicitly checks: "Have we tried this before?"
  |
  v
Phase 2: execute -> verify --debug
  |
  v
verify appends to DEBUG_MEMORY.md (Phase 2 entry added)
  |
  v
Phase 3: discuss reads updated DEBUG_MEMORY.md
  ...
```

#### Why a Separate File (Not Just STATE.md History)

STATE.md's History section is a brief log of events. It doesn't have enough detail to prevent repeating failed approaches. DEBUG_MEMORY.md is structured for AI consumption: specific parameters tried, specific results, specific "do not retry" instructions.

### New Files

| File | Location | Size Estimate |
|------|----------|---------------|
| `.pmf/DEBUG_MEMORY.md` | Created on first debug cycle | Grows ~20-30 lines per phase |

### Modified Files

| File | Sections Modified |
|------|-------------------|
| `workflows/verify.md` | Step 5b.1 (append to DEBUG_MEMORY.md) |
| `workflows/discuss.md` | Step 1 (load DEBUG_MEMORY.md), Step 2-debug (check against memory) |
| `workflows/execute.md` | Step 5e (reference DEBUG_MEMORY.md in analysis) |

---

## Feature 6: Fix Blank Equity PNG

### Current State

The equity PNG generation code is in execute.md Step 5a, item 8:

```python
# Reconstruct equity curve from IS trades
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
```

**The bug:** `compute_all_metrics()` does NOT return trades as a list in its output dict. Looking at `metrics.py` line 276-286, the return dict contains only metric values (sharpe_ratio, sortino_ratio, etc.), NOT the raw trade list. The workflow code does `results_is.get('trades', [])` but `results_is` is the output of `compute_all_metrics()`, which has no `trades` key. So `trades_is` is always `[]`, and the equity curve is always `[initial_capital]` -- a single point, which renders as a blank/dot PNG.

**Root cause in `backtest_engine.py`:** `run_backtest()` calls `compute_all_metrics(trades=trades, equity_curve=np.array(equity), ...)` and returns the result. But `compute_all_metrics()` does NOT pass through the trades list or equity curve in its return dict. The trades and equity data are consumed during metric computation but not included in the output.

### Fix Architecture

**Two possible fixes:**

#### Option A: Modify compute_all_metrics to include trades + equity (REJECTED)

Would require changing the fixed metrics.py module. This module is the "trust anchor" -- modifying it risks breaking the 32 existing unit tests and violates the architecture's principle that metrics.py is immutable reference code.

#### Option B: Modify run_backtest to include trades + equity in its return (RECOMMENDED)

`backtest_engine.py` calls `compute_all_metrics()` and returns its result. Instead, it should augment the result dict with the raw data:

```python
# In run_backtest(), replace the final return:
metrics = compute_all_metrics(
    trades=trades,
    equity_curve=np.array(equity),
    trading_days=trading_days,
)
metrics['trades'] = trades           # ADD: raw trade list
metrics['equity_curve'] = equity     # ADD: raw equity values (as list, not numpy)
return metrics
```

This is a ~3-line change to `backtest_engine.py`. The equity PNG code in execute.md then works as designed because `results_is.get('trades', [])` actually returns the trade list.

#### Additional Fix in execute.md Workflow

Even with the backtest_engine fix, the workflow's equity curve reconstruction uses trade PnLs (trade-by-trade), which gives a jagged stepped curve. Better to use the bar-by-bar equity curve that `run_backtest()` already computes:

```python
# Better: use the bar-by-bar equity curve directly
equity_arr = np.array(results_is.get('equity_curve', [initial_capital]))

if len(equity_arr) > 1:
    fig, ax = plt.subplots(figsize=(12, 6))
    ax.plot(equity_arr, linewidth=1, color='#2196F3')
    # ... rest of plotting code
```

This gives a smooth equity curve that matches what `report_generator.py` would show.

### Component Changes

| Component | Change Type | What Changes |
|-----------|-------------|--------------|
| `references/backtest_engine.py` | MODIFY `run_backtest()` return | Add `trades` and `equity_curve` keys to the returned dict |
| `workflows/execute.md` | MODIFY Step 5a item 8 | Use `results_is.get('equity_curve')` instead of reconstructing from trades. Add guard for empty equity curve. |
| `tests/` | ADD/MODIFY | Test that `run_backtest()` returns trades and equity_curve keys |

### New Files

None.

### Modified Files

| File | Lines Changed | Nature |
|------|---------------|--------|
| `references/backtest_engine.py` | ~3 lines at end of `run_backtest()` | Add trades + equity_curve to return dict |
| `workflows/execute.md` | ~15 lines in Step 5a | Use equity_curve from results instead of reconstructing |

---

## Build Order (Dependency-Aware)

Features should be built in this order based on dependencies and risk:

### Phase 1: Equity PNG Fix

**Why first:** Bug fix, zero new files, smallest change surface. Unblocks visual analysis that all other features depend on. The per-iteration equity PNG is consumed by Step 5c/5e of execute.md for AI visual analysis. If it's blank, AI analysis is degraded for all optimization methods including the new Bayesian mode.

**Touches:** backtest_engine.py (3 lines), execute.md (15 lines)
**Risk:** LOW -- unit tests exist for backtest_engine, verify fix doesn't break metrics output
**Test:** Run a backtest iteration, verify PNG has an actual curve plotted

### Phase 2: /brrr:doctor

**Why second:** Independent of all other features. Provides diagnostic tooling that helps debug issues during development of remaining features. Zero modifications to existing files.

**Touches:** NEW commands/doctor.md, NEW workflows/doctor.md
**Risk:** LOW -- additive only, no existing file modifications
**Test:** Run `/brrr:doctor` and verify all checks report correctly

### Phase 3: Smarter Debug Cycles (DEBUG_MEMORY.md)

**Why third:** Independent of Bayesian optimization. Improves the core debug loop that exists today. Should be in place before adding Bayesian mode (which might trigger more debug cycles).

**Touches:** verify.md (Step 5b.1), discuss.md (Step 1, Step 2-debug), execute.md (Step 5e)
**Risk:** MEDIUM -- modifies 3 core workflows, but changes are additive (append behavior, not replacing)
**Test:** Run a full debug cycle (execute -> verify --debug -> discuss), verify DEBUG_MEMORY.md is created and read

### Phase 4: Bayesian Optimization (Optuna)

**Why fourth:** Depends on equity PNG fix (Phase 1) for visual analysis. Benefits from doctor (Phase 2) for diagnosing optuna import issues. Benefits from debug memory (Phase 3) if Bayesian iterations trigger debug cycles.

**Touches:** NEW references/optuna_bridge.py, plan.md (Step 4), execute.md (Steps 4, 5a, 5f)
**Risk:** MEDIUM-HIGH -- modifies the core optimization loop, new Python module. Optuna's ask-and-tell API needs careful testing.
**Test:** Run plan with >500 combos, verify bayesian auto-selected. Run execute, verify Optuna suggests params and study persists across iterations.

### Phase 5: Enhanced Export + Auto Version Check

**Why last:** Purely additive. Enhanced export is a new step in verify.md's --approved path. Auto version check is a small preamble addition. Neither blocks other features.

**Touches:** verify.md (Step 5a.9), install.mjs (write .version), status.md (version preamble)
**Risk:** LOW -- additive changes to the export pipeline
**Test:** Run verify --approved, verify bot-building-guide.md appears in output/. Run status, verify version check appears (or silently passes).

---

## Cross-Cutting Concerns

### install.mjs Changes

The install script copies `references/` recursively. Adding `optuna_bridge.py` to `references/` requires no install.mjs changes -- the recursive copy handles it.

However, the `.pmf/.version` file for auto version check needs a small addition:

```javascript
// After all copies complete, write version file
const pkgVersion = JSON.parse(readFileSync(join(PKG_ROOT, 'package.json'), 'utf8')).version;
writeFileSync(join(PMF_DIR, '.version'), pkgVersion);
```

### requirements.txt

No changes needed. Optuna is already listed: `optuna>=4.7,<5`.

### Testing Strategy

| Feature | Test Type | What to Verify |
|---------|-----------|----------------|
| Equity PNG fix | Unit test | `run_backtest()` returns dict with `trades` and `equity_curve` keys |
| Equity PNG fix | Integration | Generated PNG has non-trivial content (file size > 5KB) |
| Doctor | Manual | Run `/brrr:doctor`, all checks pass |
| Debug memory | Integration | Full debug cycle creates/appends DEBUG_MEMORY.md |
| Bayesian | Unit test | `optuna_bridge.py` creates study, suggests params, reports results |
| Bayesian | Integration | Execute loop with method=bayesian completes, study.db exists |
| Enhanced export | Integration | verify --approved produces bot-building-guide.md |
| Version check | Manual | Installed old version, run status, see update message |

### Backward Compatibility

All changes are backward compatible:

- Bayesian is a new option, not a replacement. Existing grid/random/walk-forward unchanged.
- Enhanced export adds a file. Existing 7 files unchanged.
- Doctor is a new command. Existing 8 commands unchanged.
- Debug memory is append-only. Existing debug flow works without it (graceful degradation: if DEBUG_MEMORY.md doesn't exist, discuss reads individual artifacts as before).
- Equity PNG fix only adds data to the return dict. Existing consumers that don't use the new keys are unaffected.
- Version check silently skips on failure. Never blocks workflow execution.

## Sources

- [Optuna TPESampler v4.8 docs](https://optuna.readthedocs.io/en/stable/reference/samplers/generated/optuna.samplers.TPESampler.html)
- [Optuna ask-and-tell API](https://optuna.org/)
- Existing codebase: workflows/execute.md, workflows/verify.md, workflows/discuss.md, workflows/plan.md
- Existing codebase: references/backtest_engine.py, references/metrics.py
