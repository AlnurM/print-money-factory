# Technology Stack: v1.1 Enhancement

**Project:** Print Money Factory v1.1
**Researched:** 2026-03-22
**Scope:** Stack additions/changes for Bayesian optimization, enhanced export, diagnostic commands, debug cycle memory, and equity PNG fix

## Executive Decision

**No new Python or npm dependencies are needed.** All v1.1 features can be built with the existing stack. Optuna is already in requirements.txt. The equity PNG bug is a code pattern issue, not a missing library. The doctor command and version check use stdlib/npm CLI. Debug cycle memory is a workflow data structure change. Enhanced export is a template change.

This is a workflow-and-pattern milestone, not a stack milestone.

---

## Feature-by-Feature Stack Analysis

### 1. Bayesian Optimization (Optuna Integration)

**Already installed:** `optuna>=4.7,<5` in requirements.txt
**Current stable:** Optuna 4.8.0 (confirmed via official docs)
**Confidence:** HIGH

| Component | What to Use | Why |
|-----------|------------|-----|
| Sampler | `optuna.samplers.TPESampler` | Default and best for single-objective. Tree-structured Parzen Estimator handles mixed parameter types well |
| Study | `optuna.create_study(sampler=TPESampler(), direction="maximize")` | Maximize Sharpe ratio as primary metric |
| Parameter suggestion | `trial.suggest_int()`, `trial.suggest_float()` | Maps directly to existing parameter space format from plan workflow |
| Pruning | `optuna.pruners.MedianPruner` | Early-stop unpromising trials. Reduces wasted compute on clearly bad parameter combos |

**Integration point:** The execute workflow currently supports 3 optimization methods (grid, random, walk-forward). Optuna becomes a 4th method: `bayesian`. The plan workflow's auto-selection rules need a new tier:

```
Current:
  < 1000 combos  -> grid search
  1000-10000     -> random search
  3+ params OR > 10000 -> walk-forward

New (replace walk-forward as default for large spaces):
  < 1000 combos  -> grid search
  1000-10000     -> random search
  3+ params OR > 10000 -> bayesian (optuna TPE)
  Walk-forward remains available as user override
```

**Key TPESampler settings for trading backtests:**

| Setting | Value | Rationale |
|---------|-------|-----------|
| `n_startup_trials` | 10 | Enough random samples before TPE kicks in. Default is 10, appropriate for 3-6 parameter strategies |
| `multivariate` | `True` | Trading strategy parameters are correlated (e.g., fast_period and slow_period). Joint sampling outperforms independent sampling per Optuna docs |
| `group` | `True` | Works with multivariate to decompose search space into related subgroups |
| `seed` | Fixed per study | Reproducibility across runs |

**Critical integration detail:** Optuna's `study.optimize()` runs all trials internally in a loop. But the execute workflow needs to generate per-iteration output (the "brrr..." formatted blocks, verdict JSONs, equity PNGs). Solution: run `study.optimize(objective, n_trials=1)` in a loop to maintain the existing iteration display pattern. Each call adds one trial to the study, and TPE uses all prior trials to inform the next suggestion.

**Code pattern:**

```python
import optuna
from optuna.samplers import TPESampler

def objective(trial):
    params = {
        'fast_period': trial.suggest_int('fast_period', 5, 50),
        'slow_period': trial.suggest_int('slow_period', 20, 200),
        # ... mapped from plan's parameter space
    }
    if params['fast_period'] >= params['slow_period']:
        return float('-inf')  # Invalid combo

    results = run_backtest(df_train, params)
    return results['sharpe_ratio']

sampler = TPESampler(multivariate=True, group=True, seed=42)
study = optuna.create_study(sampler=sampler, direction='maximize')

# Run one trial at a time for per-iteration output
for i in range(n_trials):
    study.optimize(objective, n_trials=1)
    trial = study.trials[-1]
    # Generate iteration artifacts (metrics JSON, params JSON, equity PNG)
    # Display formatted iteration block
```

**What NOT to add:**
- Do NOT add `optuna-dashboard` -- requires a server, violates CLI-only constraint
- Do NOT add `SQLAlchemy` for optuna storage -- in-memory storage is fine for 20-50 trials per phase
- Do NOT use `optuna.visualization` -- adds complexity; existing report generator handles visualization
- Do NOT use multi-objective optimization (NSGA-II) -- single-objective Sharpe + post-hoc OOS validation is simpler and proven

---

### 2. Enhanced Export: MD-Instruction Format

**Already installed:** `jinja2>=3.1,<4` in requirements.txt
**No new dependencies needed.**
**Confidence:** HIGH

| Component | What to Use | Why |
|-----------|------------|-----|
| Templating | Jinja2 (existing) | Already used for HTML report. Same engine, new template |
| Output format | Markdown (.md) | Universal, readable by any LLM or human |

This is purely a new template file and workflow change. The MD-instruction format is a structured guide that tells a developer (or another AI) how to implement the strategy as a live trading bot.

**What NOT to add:**
- Do NOT add a markdown-to-HTML converter -- the export IS markdown
- Do NOT add `mdformat` or markdown linting -- Claude generates clean markdown
- Do NOT add Pandoc for PDF conversion -- users asked for MD, not PDF

---

### 3. `/brrr:doctor` Diagnostic Command

**No new dependencies.** Uses Python stdlib and shell commands.
**Confidence:** HIGH

| Check | Implementation | Tool |
|-------|---------------|------|
| Python version | `~/.pmf/venv/bin/python --version` | Bash (workflow) |
| Venv exists | Check `~/.pmf/venv/` directory | Bash (workflow) |
| Venv health | `~/.pmf/venv/bin/python -c "import sys; print(sys.version)"` | Bash (workflow) |
| Dependencies installed | `~/.pmf/venv/bin/pip list --format=json` | Bash (workflow) |
| Missing packages | Compare pip list against requirements.txt | Claude reasoning |
| Commands installed | Check `~/.claude/commands/brrr/*.md` exists | Bash/Glob (workflow) |
| Workflows installed | Check `~/.pmf/workflows/*.md` exists | Bash/Glob (workflow) |
| References installed | Check `~/.pmf/references/*.py` exists | Bash/Glob (workflow) |
| Disk usage | `du -sh ~/.pmf/` | Bash (workflow) |

**Implementation:** New slash command (`.md`) + new workflow (`.md`). The workflow instructs Claude to run diagnostic Bash commands and format output using `tabulate` (already installed).

**What NOT to add:**
- Do NOT add `node-doctor` or any npm diagnostic package
- Do NOT write a standalone Python diagnostic script -- the workflow instructs Claude to run checks directly

---

### 4. Auto Version Check

**No new dependencies.** Uses `npm view` CLI command.
**Confidence:** HIGH

| Component | Implementation | Tool |
|-----------|---------------|------|
| Get latest version | `npm view @print-money-factory/cli version 2>/dev/null` | Bash (workflow preamble) |
| Get installed version | Read `~/.pmf/version.txt` (written by install script) | Read (workflow preamble) |
| Compare versions | String comparison | Claude reasoning |
| Rate limiting | Timestamp file `~/.pmf/.last_version_check` | Read/Write (workflow preamble) |

**Session tracking:** Write `~/.pmf/.last_version_check` with ISO timestamp. On each `/brrr:*` command, the preamble checks if this file is less than 24 hours old. If so, skip. If not, run the check.

**Output (only when update available):**
```
[UPDATE] print-money-factory v{new} available (you have v{current})
Run: npx print-money-factory install
```

**What NOT to add:**
- Do NOT add `semver` npm package -- version comparison for "0.4.0" vs "0.5.0" is trivial string logic
- Do NOT add `update-notifier` -- designed for CLI tools, not slash command workflows
- Do NOT hit registry.npmjs.org API directly -- `npm view` is simpler and already available

---

### 5. Smarter Debug Cycles (Failed Approach Memory)

**No new dependencies.** Workflow data structure change.
**Confidence:** HIGH

| Component | What to Use | Why |
|-----------|------------|-----|
| Storage format | JSON file per phase | Consistent with existing `iter_NN_verdict.json` pattern |
| Storage location | `.pmf/phases/phase_N_diagnosis.json` | Alongside other phase artifacts |
| Read pattern | Glob + Read in debug-discuss mode | Already done for other artifacts |

**New artifact: `phase_N_diagnosis.json`** -- written by verify workflow when verdict is "debug":

```json
{
  "phase": 1,
  "verdict": "debug",
  "approaches_tried": [
    {
      "description": "RSI oversold/overbought with SMA filter",
      "why_failed": "Too few trades (12 in 2 years). RSI(14) rarely hits 30/70 on BTC 4H",
      "metrics": {"sharpe": 0.4, "max_dd": -8.2, "trades": 12},
      "lesson": "Need faster indicator or lower thresholds for crypto volatility"
    }
  ],
  "parameter_ranges_exhausted": {
    "rsi_period": [7, 14, 21],
    "rsi_oversold": [20, 25, 30]
  },
  "suggested_next_direction": "Try MACD crossover or reduce RSI thresholds below 25/above 75"
}
```

**Written by:** verify workflow when verdict is "debug"
**Read by:** discuss workflow in debug-discuss mode (Step 2-debug, Step 1 context load)

**What NOT to add:**
- Do NOT add SQLite or any database for storing history -- JSON files are sufficient and human-inspectable
- Do NOT add vector embeddings for semantic search over past approaches -- overkill for 3-5 debug cycles

---

### 6. Fix Blank Equity PNG Bug

**No new dependencies.** Code pattern fix in execute workflow template.
**Confidence:** HIGH

**Root cause (from codebase review of execute.md lines 522-553):**

The equity curve PNG generation reconstructs the equity from trades instead of using the actual equity array from the backtest engine. This fails when:

1. **No trades generated** -- `results_is.get('trades', [])` returns empty list, equity becomes `[initial_capital]` (single point), matplotlib plots an invisible dot
2. **Lossy reconstruction** -- the trade-based reconstruction loses intra-trade equity movement (mark-to-market), producing a step function instead of the smooth curve the engine actually computed

**The fix** is a workflow template change (not a library change):

```python
# BEFORE (buggy - reconstructs from trades, loses intra-trade equity)
trades_is = results_is.get('trades', [])
equity = [initial_capital]
for t in trades_is:
    pnl = t.get('pnl', 0)
    equity.append(equity[-1] + pnl)

# AFTER (correct - uses actual bar-by-bar equity curve from engine)
equity_arr = np.array(results_is.get('equity_curve', [initial_capital]))
if len(equity_arr) <= 1:
    print("WARNING: No equity data to plot (no trades generated)")
else:
    fig, ax = plt.subplots(figsize=(12, 6))
    ax.plot(equity_arr, linewidth=1, color='#2196F3')
    # ... rest of existing plot code
```

**Additional safeguards to add to the template:**
- Guard against empty equity curve (skip PNG, log warning)
- Ensure `matplotlib.use('Agg')` is the FIRST matplotlib statement
- Keep existing `plt.close(fig)` + `plt.close('all')` for memory leak prevention

**Verification:** `compute_all_metrics()` in `metrics.py` receives `equity_curve` as a parameter and includes it in the return dict. The `run_backtest()` function in `backtest_engine.py` passes `np.array(equity)` to `compute_all_metrics()`. The data is already available -- the workflow template just needs to use it.

**What NOT to add:**
- Do NOT switch to plotly for iteration PNGs -- matplotlib Agg is correct (lighter, headless, no Chrome)
- Do NOT add Pillow for image verification -- the fix is in the data source, not image processing

---

## Stack Changes Summary

| Feature | New Dependencies | Change Type |
|---------|-----------------|-------------|
| Bayesian optimization | NONE (optuna already installed) | Workflow + code pattern |
| Enhanced export | NONE (jinja2 already installed) | New template file |
| `/brrr:doctor` | NONE | New command + workflow |
| Auto version check | NONE | Preamble addition to workflows |
| Debug cycle memory | NONE | New JSON artifact format |
| Equity PNG fix | NONE | Fix data source in execute template |

**Total new pip packages: 0**
**Total new npm packages: 0**
**requirements.txt changes: NONE**
**package.json changes: Version bump only (e.g., 0.5.0)**

---

## Existing Stack Confirmation

All currently installed packages are sufficient. No version bumps needed:

| Package | Current Pin | Needed For v1.1 | Status |
|---------|------------|-----------------|--------|
| optuna | >=4.7,<5 | Bayesian optimization (TPESampler) | Sufficient -- 4.8.0 stable is in range |
| matplotlib | >=3.10,<4 | Equity PNG fix (Agg backend) | Sufficient -- 3.10.8 stable |
| jinja2 | >=3.1,<4 | Enhanced export MD template | Sufficient |
| tabulate | >=0.9,<1 | Doctor command output formatting | Sufficient |
| plotly | >=6.5,<7 | Existing reports (unchanged) | Sufficient |
| pandas | >=3.0,<4 | Existing data handling (unchanged) | Sufficient |
| numpy | >=2.4,<3 | Existing computation (unchanged) | Sufficient |

---

## Alternatives Considered

| Feature | Considered | Why Not |
|---------|-----------|---------|
| Bayesian opt | Ax (Facebook) | Heavy -- pulls in PyTorch. Optuna is already installed |
| Bayesian opt | Hyperopt | Unmaintained since 2023. Optuna is the successor |
| Bayesian opt | optuna-dashboard | Requires server process. Violates CLI-only constraint |
| Bayesian opt | Multi-objective (NSGA-II) | Adds complexity. Single-objective + post-hoc OOS validation is proven |
| Version check | update-notifier npm package | Designed for CLI entry points, not slash command workflows |
| Version check | Direct registry.npmjs.org API | npm view already does this without HTTP client code |
| Version check | semver npm package | Version comparison for "0.4.0" vs "0.5.0" is trivial |
| Debug memory | SQLite database | JSON files are simpler, inspectable, consistent with existing artifact pattern |
| Debug memory | Vector embeddings | Massive overkill for 3-5 debug cycles |
| PNG fix | Plotly for iteration charts | Heavier, requires CDN or embedded JS. Matplotlib Agg is correct for headless PNGs |
| PNG fix | Pillow for image validation | Fix is in the data source, not image processing |
| Export format | Pandoc for MD-to-PDF | Users asked for MD, not PDF. Pandoc is a heavy system dep |

---

## Integration Points (for roadmap)

### Optuna in plan.md + execute.md

**plan.md changes:**
- Add `bayesian` as 4th optimization method option
- Update auto-selection: 3+ params OR >10000 combos -> bayesian (was walk-forward)
- Walk-forward remains as user override option

**execute.md changes:**
- New code path for `method == "bayesian"` in Step 5a (script generation)
- Build optuna study with TPESampler
- Map parameter space from plan artifact to `trial.suggest_*()` calls
- Run `study.optimize(objective, n_trials=1)` in a loop (preserves per-iteration output)
- Per-trial: generate artifacts (metrics JSON, params JSON, equity PNG, verdict JSON)
- Study best_params used for final OOS validation

### Version check preamble in all workflows

Add AFTER sequence validation, BEFORE context file scan. Must be non-blocking (network errors = silent skip). Rate-limited to once per 24 hours via timestamp file.

### Diagnosis JSON: verify writes, discuss reads

- **verify.md:** When verdict is "debug", compile `phase_N_diagnosis.json` from iteration verdicts before incrementing phase counter
- **discuss.md:** In debug-discuss mode (Step 1), Glob all `phase_*_diagnosis.json` files and build cumulative memory of what was tried

### Equity PNG fix in execute.md

- Change the Python script template in Step 5a to use `results_is['equity_curve']` instead of reconstructing from trades
- Add empty-data guard to skip PNG generation when no trades
- No changes to backtest_engine.py or metrics.py needed

---

## Sources

- [Optuna 4.8.0 TPESampler documentation](https://optuna.readthedocs.io/en/stable/reference/samplers/generated/optuna.samplers.TPESampler.html) - TPE sampler parameters, multivariate mode, constructor options
- [Optuna Study API docs](https://optuna.readthedocs.io/en/stable/reference/generated/optuna.study.Study.html) - create_study and optimize patterns
- [Matplotlib savefig blank image causes](https://pythonguides.com/matplotlib-savefig-blank-image/) - 5 common causes of blank PNGs with fixes
- [Matplotlib savefig API reference](https://matplotlib.org/stable/api/_as_gen/matplotlib.pyplot.savefig.html) - savefig parameters and backend behavior
- [npm view documentation](https://docs.npmjs.com/cli/v7/commands/npm-view/) - Registry version lookup via CLI
- [npm registry API guide](https://www.tutorialpedia.org/blog/get-versions-from-npm-registry-api/) - Programmatic version checking, rate limits
