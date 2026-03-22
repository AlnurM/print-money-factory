# Phase 9: Bayesian Optimization - Research

**Researched:** 2026-03-23
**Domain:** Optuna Bayesian optimization integration into existing iterative backtest loop
**Confidence:** HIGH

## Summary

Phase 9 integrates Optuna's Bayesian optimization into the existing execute workflow using the Ask-and-Tell API (`study.ask()` / `study.tell()`). This preserves the per-iteration architecture (script writing, equity PNGs, AI analysis, verdict JSONs) while replacing the manual "AI picks next params" step with Optuna's TPE or CMA-ES sampler suggestions.

The critical finding is that Optuna's SQLite storage does NOT persist sampler internal state -- but TPE rebuilds its probability model from stored trial history on each `study.ask()` call, so resume works correctly without pickle. CMA-ES, however, has internal covariance matrix state that IS lost on resume. For CMA-ES, the `optuna_bridge.py` module must pickle the sampler alongside the SQLite study. The second critical finding is that CMA-ES does not support `CategoricalDistribution` at all -- the auto-selection logic must check for categorical params, not just "non-continuous."

**Primary recommendation:** Create `references/optuna_bridge.py` as a thin helper module (~120 lines) that encapsulates study lifecycle, sampler auto-selection, parameter suggestion via Ask-and-Tell, result reporting, and param-space-change detection for `--resume`. Use the define-and-run approach (pass distributions dict to `study.ask()`) for cleaner separation between plan param space and Optuna distributions.

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions
- **D-01:** Use Optuna's Ask-and-Tell API (`study.ask()` then `study.tell(trial, value)`). Preserves existing per-iteration loop.
- **D-02:** AI analysis still runs between iterations. Claude reads metrics and equity PNG, writes analysis. Optuna replaces only the "pick next params" step.
- **D-03:** Display warmup vs guided mode: first N iterations show `[WARMUP]`, subsequent show `[GUIDED]`.
- **D-04:** Composite objective: `score = sharpe - max(0, abs(max_dd) - dd_target) * 2`. Single-objective only.
- **D-05:** Add `bayesian` as fourth optimization method in plan.md Step 4.
- **D-06:** Auto-recommendation: if total_combinations > 500, auto-select `bayesian`. If <= 500, keep current logic.
- **D-07:** Plan artifact gets `optimization_method: bayesian` with optional `sampler: auto`.
- **D-08:** Override prompt updated: `Override? (grid / random / walk-forward / bayesian / keep)`.
- **D-09:** If ALL free parameters are continuous (float with no step constraint), auto-select CMA-ES. Otherwise TPE with `multivariate=True`.
- **D-10:** Sampler selection happens at execute time, not plan time.
- **D-11:** Study persists to SQLite at `.pmf/phases/phase_N_execute/optuna_study.db`.
- **D-12:** On `--resume`, load existing study with `optuna.load_study()`. TPE probability model preserved via trial history.
- **D-13:** If param ranges change between runs, warn and offer: continue existing study or start fresh.
- **D-14:** Non-Bayesian `--resume` continues unchanged. SQLite only for bayesian method.

### Claude's Discretion
- Exact composite score formula weights (D-04 gives formula but weights are tunable)
- Whether to create `optuna_bridge.py` helper module or inline Optuna code
- TPE `n_startup_trials` parameter (default 10 is reasonable)
- Whether to display Optuna's internal trial number alongside PMF iteration number

### Deferred Ideas (OUT OF SCOPE)
- Multi-objective Optuna optimization (Pareto front for Sharpe vs Drawdown) -- deferred to v1.2
- Optuna visualization dashboard (parallel coordinate plots, importance) -- future enhancement
</user_constraints>

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|------------------|
| OPT-01 | `/brrr:execute` uses Optuna TPE sampler for Bayesian parameter optimization via Ask-and-Tell API | Ask-and-Tell API fully documented with code patterns. TPESampler with `multivariate=True, n_startup_trials=10`. Define-and-run approach via `study.ask(distributions)` for clean separation. |
| OPT-02 | Optuna auto-selects CMA-ES sampler when all parameters are continuous, TPE otherwise | CMA-ES does NOT support CategoricalDistribution. Check: all params are FloatDistribution without step, or IntDistribution. If any CategoricalDistribution exists, must use TPE. CMA-ES sampler state requires pickle for resume. |
| OPT-03 | Optuna study persists to SQLite so `--resume` preserves the Bayesian probability model | `optuna.create_study(storage="sqlite:///path.db", load_if_exists=True)` is the pattern. TPE rebuilds model from trial history -- no pickle needed. CMA-ES needs pickle. Param space change detection via `trial.distributions` comparison. |
| OPT-04 | `/brrr:plan` includes Bayesian as optimization method option alongside grid/random/walk-forward | Plan.md Step 4 needs new auto-selection rule (>500 combos = bayesian), new override option, and new plan artifact field `optimization_method: bayesian`. |
</phase_requirements>

## Standard Stack

### Core
| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| optuna | >=4.7,<5 (current: 4.8.0) | Bayesian optimization framework | Already in requirements.txt. Best-in-class for single-objective hyperparameter optimization. TPE and CMA-ES samplers cover all trading param types. |

### Supporting
| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| pickle (stdlib) | -- | Serialize CMA-ES sampler state | Only when CMA-ES sampler is selected AND study needs resume capability |
| sqlite3 (stdlib) | -- | Optuna study persistence backend | Automatic -- Optuna uses it internally when `storage="sqlite:///"` is specified |

### Alternatives Considered
| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| TPE + CMA-ES manual selection | `AutoSampler` from OptunaHub | AutoSampler requires `optunahub` + `cmaes` + `torch` + `scipy` as deps. Overkill -- we know the selection criteria (categorical = TPE, all continuous = CMA-ES). |
| `study.optimize(n_trials=1)` loop | Ask-and-Tell (`study.ask()` / `study.tell()`) | Ask-and-Tell is cleaner for our use case -- no objective function wrapping needed, trial lifecycle is explicit. Both work, but D-01 locks Ask-and-Tell. |
| Composite score function | Multi-objective (`directions=["maximize", "minimize"]`) | Multi-objective returns Pareto front, not single best -- breaks existing workflow. Deferred to v1.2. |

**Installation:**
```bash
# No installation needed -- optuna already in venv
```

## Architecture Patterns

### Recommended Project Structure
```
references/
  optuna_bridge.py        # NEW: Optuna study lifecycle, suggest, tell, resume
workflows/
  plan.md                 # MODIFY: Step 4 -- add bayesian method option
  execute.md              # MODIFY: Step 5a, 5f -- bayesian param selection branch
.pmf/phases/phase_N_execute/
  optuna_study.db          # NEW: SQLite study persistence (runtime artifact)
  optuna_sampler.pkl       # NEW: CMA-ES sampler pickle (only if CMA-ES selected)
```

### Pattern 1: Ask-and-Tell with Define-and-Run
**What:** Pre-define distributions dict from plan param space, pass to `study.ask(distributions)`, read suggested values from `trial.params`, run backtest externally, report back with `study.tell(trial, score)`.
**When to use:** Always for Bayesian optimization in this project. This is the locked decision (D-01).
**Example:**
```python
# Source: https://optuna.readthedocs.io/en/stable/tutorial/20_recipes/009_ask_and_tell.html
import optuna

# Convert plan param space to Optuna distributions (done once)
distributions = {
    "fast_period": optuna.distributions.IntDistribution(5, 50),
    "slow_period": optuna.distributions.IntDistribution(20, 200),
    "atr_mult": optuna.distributions.FloatDistribution(1.0, 3.0),
}

study = optuna.create_study(
    study_name="phase_1_bayesian",
    storage="sqlite:///.pmf/phases/phase_1_execute/optuna_study.db",
    direction="maximize",
    load_if_exists=True,
    sampler=optuna.samplers.TPESampler(
        n_startup_trials=10,
        multivariate=True,
    ),
)

# Per-iteration (called from execute loop)
trial = study.ask(distributions)  # Optuna suggests params
params = trial.params             # {"fast_period": 12, "slow_period": 85, "atr_mult": 1.7}

# ... run backtest with params, get metrics ...
score = compute_composite_score(metrics, dd_target)

study.tell(trial, score)          # Report result back

# Check if warmup or guided
is_warmup = len(study.trials) <= study.sampler._n_startup_trials
mode = "[WARMUP]" if is_warmup else "[GUIDED]"
```

### Pattern 2: Sampler Auto-Selection
**What:** Check param space types at execute time to select TPE or CMA-ES.
**When to use:** When plan specifies `sampler: auto` (default).
**Example:**
```python
# Source: https://optuna.readthedocs.io/en/stable/reference/samplers/generated/optuna.samplers.CmaEsSampler.html
def select_sampler(param_space: list[dict]) -> optuna.samplers.BaseSampler:
    """Auto-select CMA-ES for all-continuous, TPE otherwise.

    CMA-ES does NOT support CategoricalDistribution.
    CMA-ES works with FloatDistribution and IntDistribution.
    Per D-09: "continuous" means float with no step constraint.
    """
    all_continuous = all(
        p["type"] == "float" and p.get("step") is None
        for p in param_space
    )

    if all_continuous and len(param_space) >= 2:
        return optuna.samplers.CmaEsSampler(
            n_startup_trials=10,
            seed=42,
        )
    else:
        return optuna.samplers.TPESampler(
            n_startup_trials=10,
            multivariate=True,
            seed=42,
        )
```

### Pattern 3: Composite Objective Score
**What:** Combine Sharpe ratio and drawdown penalty into single scalar for `study.tell()`.
**When to use:** Every Bayesian iteration when reporting results.
**Example:**
```python
# Per D-04: score = sharpe - max(0, abs(max_dd) - dd_target) * 2
def compute_composite_score(metrics: dict, dd_target: float) -> float:
    """Compute single objective score for Optuna.

    Primary: Sharpe ratio (maximize)
    Penalty: Excess drawdown beyond target
    """
    sharpe = metrics.get('sharpe_ratio', 0.0)
    max_dd = abs(metrics.get('max_drawdown', 0.0))

    # Penalty kicks in only when drawdown exceeds target
    dd_penalty = max(0.0, max_dd - abs(dd_target)) * 2.0

    score = sharpe - dd_penalty

    # Handle edge cases
    if metrics.get('trade_count', 0) == 0:
        return float('-inf')  # No trades = worst possible score

    return score
```

### Pattern 4: Param Space Change Detection for --resume
**What:** Compare plan param space against distributions in stored study trials to detect changes.
**When to use:** On `--resume` with bayesian method before loading existing study.
**Example:**
```python
def detect_param_space_changes(
    study: optuna.Study,
    new_distributions: dict[str, optuna.distributions.BaseDistribution],
) -> list[str]:
    """Compare new param space against what the study has seen.

    Returns list of change descriptions. Empty = no changes.
    """
    changes = []
    if len(study.trials) == 0:
        return changes

    # Get distributions from most recent completed trial
    last_trial = study.trials[-1]
    old_distributions = last_trial.distributions

    for name, new_dist in new_distributions.items():
        if name not in old_distributions:
            changes.append(f"NEW param: {name}")
        elif old_distributions[name] != new_dist:
            changes.append(f"CHANGED: {name}: {old_distributions[name]} -> {new_dist}")

    for name in old_distributions:
        if name not in new_distributions:
            changes.append(f"REMOVED param: {name}")

    return changes
```

### Anti-Patterns to Avoid
- **Using `study.optimize(objective, n_trials=N)` directly:** Runs all trials in a single blocking call. Destroys per-iteration artifacts, AI analysis, equity PNGs, verdict JSONs, and resume capability. Use Ask-and-Tell instead.
- **In-memory study without SQLite:** Loses all TPE learning on session end. Resume wastes warmup trials.
- **Pickle-only persistence (no SQLite):** Pickle stores sampler state but NOT trial history. SQLite stores trial history. You need SQLite for TPE (rebuilds model from trials) and both SQLite + pickle for CMA-ES (needs covariance matrix state).
- **Setting max_iterations equal to n_startup_trials:** If both are 10, every single iteration is random sampling. TPE adds zero value. Enforce `max_iterations >= 2 * n_startup_trials` for bayesian mode.
- **Suggesting params inside the objective function:** With Ask-and-Tell, params are suggested via `trial = study.ask(distributions)` and accessed via `trial.params`. Do NOT call `trial.suggest_float()` inside a separate objective function -- this mixes define-by-run and define-and-run, causing confusion.

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Bayesian parameter suggestion | Custom probability model for param selection | `optuna.samplers.TPESampler` via `study.ask()` | TPE handles mixed param types, categorical, conditional spaces, multivariate correlations. Thousands of edge cases. |
| Study persistence | Custom JSON/pickle save/load for optimization state | `optuna.create_study(storage="sqlite:///...")` | Optuna handles trial versioning, concurrent access, partial writes, schema migrations. |
| CMA-ES covariance adaptation | Custom evolutionary strategy | `optuna.samplers.CmaEsSampler` | CMA-ES has >30 years of algorithmic refinement (Hansen 2001). Optuna's implementation handles boundary constraints, step sizes, population sizing. |
| Param space change detection | Manual JSON diff of param ranges | Compare `trial.distributions` from study vs new distributions | Optuna's distribution objects have proper `__eq__` implementations for exact comparison. |

**Key insight:** Optuna's value is not just the TPE algorithm -- it is the entire trial lifecycle: suggestion, evaluation, storage, resumption, and comparison. Hand-rolling any piece means maintaining it against Optuna's release cadence.

## Common Pitfalls

### Pitfall 1: TPE Warmup Makes First N Iterations Random
**What goes wrong:** TPE needs `n_startup_trials` (default 10) random trials before building its probability model. If `max_iterations` is 10, every iteration is random -- Bayesian optimization adds no value.
**Why it happens:** TPE fits a Gaussian Mixture Model to separate "good" vs "bad" parameter regions. Without enough data points, it cannot fit the model and falls back to random sampling.
**How to avoid:** When bayesian is selected in execute workflow, enforce `max_iterations >= 20` (or at minimum `2 * n_startup_trials`). Display `[WARMUP]` vs `[GUIDED]` per iteration so the user understands what is happening.
**Warning signs:** All iterations show random-looking parameter jumps with no convergence. No improvement trajectory despite 10+ iterations.

### Pitfall 2: CMA-ES Sampler State Lost on Resume
**What goes wrong:** Optuna's SQLite storage stores trial history but NOT sampler internal state. TPE rebuilds its model from trial history on each call, so this is fine for TPE. CMA-ES, however, maintains a covariance matrix that evolves across trials. On resume, a new CMA-ES sampler starts with a fresh covariance matrix, discarding learned parameter correlations.
**Why it happens:** Optuna's official docs explicitly state: "the storage doesn't store the state of the instance of samplers and pruners."
**How to avoid:** When CMA-ES is selected, pickle the sampler to `.pmf/phases/phase_N_execute/optuna_sampler.pkl` after each iteration. On resume, load the pickled sampler and pass it to `create_study(sampler=restored_sampler)`.
**Warning signs:** Resumed CMA-ES optimization shows reset exploration behavior instead of refining near the best region.

### Pitfall 3: CMA-ES with Categorical Params Crashes
**What goes wrong:** `CmaEsSampler` does not support `CategoricalDistribution`. If the param space includes a categorical parameter (e.g., `indicator_type: ["ema", "sma", "wma"]`), Optuna raises an error.
**Why it happens:** CMA-ES operates in continuous space -- it has no mechanism for discrete unordered categories. The Optuna docs explicitly state this limitation.
**How to avoid:** The auto-selection logic (Pattern 2) must check for ANY categorical params AND for integer params with step > 1 (which are effectively discrete). If found, use TPE. Only select CMA-ES when ALL params are `FloatDistribution` without step constraints.
**Warning signs:** Runtime error on first Bayesian iteration mentioning "CategoricalDistribution is not supported."

### Pitfall 4: Composite Score Dominates One Metric
**What goes wrong:** The formula `score = sharpe - max(0, abs(max_dd) - dd_target) * 2` can produce extreme negative scores when drawdown is far from target, causing Optuna to over-optimize for drawdown and ignore Sharpe. Example: Sharpe=2.5, max_dd=-40%, dd_target=15% yields `score = 2.5 - (40-15)*2 = 2.5 - 50 = -47.5`.
**Why it happens:** The penalty multiplier (2) amplifies drawdown violations linearly. Sharpe typically ranges 0-3, but the penalty can reach -50+.
**How to avoid:** Cap the penalty: `dd_penalty = min(max(0, excess_dd) * 2, 5.0)`. This prevents the penalty from exceeding 5 points, keeping it comparable to Sharpe's typical range. Alternatively, use a softer penalty: `excess_dd * 1.0` instead of `* 2.0`.
**Warning signs:** All "best" trials have drawdown exactly at target but mediocre Sharpe. Optuna converges to the drawdown boundary instead of exploring the full Sharpe landscape.

### Pitfall 5: study.ask() Returns Out-of-Range Values After Resume with Changed Params
**What goes wrong:** If a user changes param ranges between `--resume` runs (e.g., `fast_period` range changed from [5,50] to [10,30]), the TPE model was built on the old range. New suggestions may cluster near old-range boundaries rather than exploring the new range intelligently.
**Why it happens:** TPE's probability model is built from all historical trials. If those trials used a wider range, the model's learned density estimates may not align with the new narrower range.
**How to avoid:** Per D-13, detect param space changes and warn the user. Offer two options: (1) continue with existing study (may produce suboptimal early suggestions), or (2) start fresh study (loses all prior learning). For option 1, Optuna will clip suggestions to the new distribution bounds -- it won't suggest values outside the new range.
**Warning signs:** After resume with changed ranges, first few suggestions all cluster at the boundary of the new range.

## Code Examples

### Complete optuna_bridge.py Structure
```python
# Source: Optuna 4.8.0 official docs, verified patterns
"""Optuna bridge for Bayesian optimization in PMF backtest loop.

Manages study lifecycle, sampler auto-selection, parameter suggestion,
result reporting, and resume with param-space-change detection.

Stored in ~/.pmf/references/ alongside metrics.py and backtest_engine.py.
"""
import optuna
import pickle
from pathlib import Path

# Suppress Optuna's verbose logging
optuna.logging.set_verbosity(optuna.logging.WARNING)


def build_distributions(param_space: list[dict]) -> dict:
    """Convert plan param space to Optuna distribution dict.

    param_space format (from plan artifact):
    [
        {"name": "fast_period", "type": "int", "min": 5, "max": 50, "step": 1},
        {"name": "atr_mult", "type": "float", "min": 1.0, "max": 3.0},
        {"name": "ma_type", "type": "categorical", "choices": ["ema", "sma"]},
    ]
    """
    distributions = {}
    for p in param_space:
        name = p["name"]
        if p["type"] == "int":
            distributions[name] = optuna.distributions.IntDistribution(
                low=p["min"], high=p["max"], step=p.get("step", 1)
            )
        elif p["type"] == "float":
            step = p.get("step")
            distributions[name] = optuna.distributions.FloatDistribution(
                low=p["min"], high=p["max"],
                step=step,  # None = continuous, value = discrete float
                log=p.get("log", False),
            )
        elif p["type"] == "categorical":
            distributions[name] = optuna.distributions.CategoricalDistribution(
                choices=p["choices"]
            )
    return distributions


def select_sampler(param_space: list[dict], seed: int = 42):
    """Auto-select CMA-ES for all-continuous, TPE otherwise (per D-09)."""
    all_continuous = all(
        p["type"] == "float" and p.get("step") is None
        for p in param_space
    )

    if all_continuous and len(param_space) >= 2:
        sampler_name = "CMA-ES"
        sampler = optuna.samplers.CmaEsSampler(
            n_startup_trials=10,
            seed=seed,
        )
    else:
        sampler_name = "TPE"
        sampler = optuna.samplers.TPESampler(
            n_startup_trials=10,
            multivariate=True,
            seed=seed,
        )
    return sampler, sampler_name


def get_or_create_study(
    study_name: str,
    storage_dir: str,
    sampler,
    direction: str = "maximize",
) -> optuna.Study:
    """Create new study or load existing one with SQLite persistence."""
    storage_path = Path(storage_dir) / "optuna_study.db"
    storage_url = f"sqlite:///{storage_path}"
    return optuna.create_study(
        study_name=study_name,
        storage=storage_url,
        direction=direction,
        load_if_exists=True,
        sampler=sampler,
    )


def suggest_params(study, distributions):
    """Ask Optuna for next parameter suggestion (define-and-run)."""
    trial = study.ask(distributions)
    return trial, trial.params


def report_result(study, trial, value):
    """Report objective value for completed trial."""
    study.tell(trial, value)


def compute_composite_score(metrics, dd_target):
    """Composite objective: Sharpe with drawdown penalty (per D-04)."""
    sharpe = metrics.get('sharpe_ratio', 0.0)
    max_dd = abs(metrics.get('max_drawdown', 0.0))
    trade_count = metrics.get('trade_count', 0)

    if trade_count == 0:
        return float('-inf')

    excess_dd = max(0.0, max_dd - abs(dd_target))
    dd_penalty = min(excess_dd * 2.0, 5.0)  # Cap penalty at 5.0

    return sharpe - dd_penalty


def is_warmup(study, n_startup_trials=10):
    """Check if study is still in random warmup phase (per D-03)."""
    completed = len([t for t in study.trials
                     if t.state == optuna.trial.TrialState.COMPLETE])
    return completed < n_startup_trials


def detect_param_changes(study, new_distributions):
    """Detect if param space changed since last trial (per D-13)."""
    if len(study.trials) == 0:
        return []
    last_trial = study.trials[-1]
    old_dists = last_trial.distributions
    changes = []
    for name, new_dist in new_distributions.items():
        if name not in old_dists:
            changes.append(f"NEW param: {name}")
        elif old_dists[name] != new_dist:
            changes.append(f"CHANGED: {name}")
    for name in old_dists:
        if name not in new_distributions:
            changes.append(f"REMOVED: {name}")
    return changes


def save_sampler(study, storage_dir):
    """Pickle sampler state (needed for CMA-ES resume)."""
    pkl_path = Path(storage_dir) / "optuna_sampler.pkl"
    with open(pkl_path, "wb") as f:
        pickle.dump(study.sampler, f)


def load_sampler(storage_dir):
    """Load pickled sampler (for CMA-ES resume)."""
    pkl_path = Path(storage_dir) / "optuna_sampler.pkl"
    if pkl_path.exists():
        with open(pkl_path, "rb") as f:
            return pickle.load(f)
    return None
```

### Execute Workflow Bayesian Branch (Step 5f replacement)
```python
# Source: Pattern derived from Optuna Ask-and-Tell docs + project architecture
# This replaces the "Claude decides next params" logic in Step 5f when method=bayesian

# --- At loop start (Step 4, one-time setup) ---
from optuna_bridge import (
    build_distributions, select_sampler, get_or_create_study,
    suggest_params, report_result, compute_composite_score,
    is_warmup, detect_param_changes, save_sampler, load_sampler,
)

distributions = build_distributions(plan_param_space)
sampler, sampler_name = select_sampler(plan_param_space)

# On --resume with CMA-ES, try to restore sampler state
if resume_mode and sampler_name == "CMA-ES":
    restored = load_sampler(output_dir)
    if restored:
        sampler = restored

study = get_or_create_study(
    study_name=f"phase_{phase_num}_bayesian",
    storage_dir=output_dir,
    sampler=sampler,
)

# Check for param space changes on resume
if resume_mode and len(study.trials) > 0:
    changes = detect_param_changes(study, distributions)
    if changes:
        # Display warning to user, ask continue or fresh start
        pass

# --- Per iteration (in Step 5a/5f loop) ---
trial, suggested_params = suggest_params(study, distributions)
warmup = is_warmup(study)
mode_tag = "[WARMUP]" if warmup else "[GUIDED]"

# ... write backtest script with suggested_params ...
# ... run script, read metrics ...

score = compute_composite_score(metrics, dd_target)
report_result(study, trial, score)

# Save CMA-ES sampler state after each iteration
if sampler_name == "CMA-ES":
    save_sampler(study, output_dir)

# Display iteration with mode
print(f"Iteration {iteration}/{max_iterations} {mode_tag} ({sampler_name})")
```

### Plan Workflow Bayesian Addition (Step 4)
```markdown
# New auto-selection rules (replaces current Step 4 in plan.md)
- Total combinations <= 100: grid_search
- Total combinations 101-500: random_search
- Total combinations > 500: bayesian
- Walk-forward: available as user override for any size

# Override prompt (per D-08)
Override? (grid / random / walk-forward / bayesian / keep)

# Plan artifact fields when bayesian selected (per D-07)
optimization_method: bayesian
sampler: auto  # auto-selects TPE vs CMA-ES at execute time (per D-10)
```

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| `study.optimize(objective, n_trials=N)` | Ask-and-Tell: `study.ask()` / `study.tell()` | Optuna 2.4+ (2020) | Enables external loop control, per-trial artifacts |
| In-memory studies only | SQLite RDB backend | Optuna 1.0+ (2019) | Enables `--resume` with full trial history |
| TPE independent sampling | `TPESampler(multivariate=True)` | Optuna 2.x | Models parameter correlations, better for correlated trading params |
| Manual sampler selection | `AutoSampler` (OptunaHub) | 2024 | Automatic sampler selection -- but requires OptunaHub dep, not in core |
| `suggest_uniform/int/categorical` | `suggest_float/int/categorical` | Optuna 3.0 | Old APIs deprecated, new ones are current |

**Deprecated/outdated:**
- `trial.suggest_uniform()`, `trial.suggest_loguniform()`, `trial.suggest_discrete_uniform()` -- replaced by `trial.suggest_float()` with `log` and `step` params
- `optuna.distributions.UniformDistribution` -- replaced by `FloatDistribution`
- `optuna.distributions.IntUniformDistribution` -- replaced by `IntDistribution`

## Open Questions

1. **D-09 definition of "continuous" -- should IntDistribution with step=1 count?**
   - What we know: CMA-ES supports IntDistribution. D-09 says "float with no step constraint" = continuous.
   - What's unclear: An integer param (e.g., period=5..50, step=1) is technically discrete but CMA-ES handles it fine. The `with_margin` parameter prevents CMA-ES from converging to a single integer value.
   - Recommendation: Follow D-09 literally -- only use CMA-ES when ALL params are `float` without `step`. This is conservative but safe. Users who want CMA-ES with int params can override via plan.

2. **Should warmup count (n_startup_trials) be configurable in the plan artifact?**
   - What we know: Default 10 is reasonable for 3-6 param strategies. More params may benefit from higher warmup.
   - What's unclear: Whether to expose this as a plan field or keep it hardcoded.
   - Recommendation: Hardcode to 10 (Claude's discretion area). If needed later, add to plan artifact.

3. **What happens to existing walk-forward auto-selection users?**
   - What we know: Current rule is "3+ params OR >10000 combos -> walk-forward". New rule changes >500 combos to bayesian.
   - What's unclear: Whether users who relied on walk-forward auto-selection will be surprised.
   - Recommendation: Walk-forward remains available via override. The auto-selection change from walk-forward to bayesian for large spaces is an improvement -- bayesian is strictly better than walk-forward for parameter optimization (walk-forward is better for robustness testing, not parameter search).

## Validation Architecture

### Test Framework
| Property | Value |
|----------|-------|
| Framework | pytest (available in venv) |
| Config file | none -- see Wave 0 |
| Quick run command | `~/.pmf/venv/bin/python -m pytest tests/ -x --tb=short` |
| Full suite command | `~/.pmf/venv/bin/python -m pytest tests/ -v` |

### Phase Requirements to Test Map
| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|-------------|
| OPT-01 | optuna_bridge creates study, suggests params via ask, reports via tell | unit | `~/.pmf/venv/bin/python -m pytest tests/test_optuna_bridge.py::test_ask_tell_lifecycle -x` | No -- Wave 0 |
| OPT-01 | TPE sampler used by default, multivariate=True | unit | `~/.pmf/venv/bin/python -m pytest tests/test_optuna_bridge.py::test_tpe_default_sampler -x` | No -- Wave 0 |
| OPT-02 | CMA-ES selected when all params are continuous floats | unit | `~/.pmf/venv/bin/python -m pytest tests/test_optuna_bridge.py::test_cmaes_auto_selection -x` | No -- Wave 0 |
| OPT-02 | TPE selected when categorical or int params present | unit | `~/.pmf/venv/bin/python -m pytest tests/test_optuna_bridge.py::test_tpe_fallback_categorical -x` | No -- Wave 0 |
| OPT-03 | Study persists to SQLite and loads on resume | unit | `~/.pmf/venv/bin/python -m pytest tests/test_optuna_bridge.py::test_sqlite_persistence -x` | No -- Wave 0 |
| OPT-03 | Param space change detection on resume | unit | `~/.pmf/venv/bin/python -m pytest tests/test_optuna_bridge.py::test_param_change_detection -x` | No -- Wave 0 |
| OPT-04 | Plan workflow includes bayesian in auto-selection | manual-only | Run `/brrr:plan` with >500 combo param space, verify bayesian auto-selected | N/A |

### Sampling Rate
- **Per task commit:** `~/.pmf/venv/bin/python -m pytest tests/test_optuna_bridge.py -x --tb=short`
- **Per wave merge:** `~/.pmf/venv/bin/python -m pytest tests/ -v`
- **Phase gate:** Full suite green before `/gsd:verify-work`

### Wave 0 Gaps
- [ ] `tests/test_optuna_bridge.py` -- unit tests for optuna_bridge.py module
- [ ] `tests/conftest.py` -- shared fixtures (tmp dirs, sample param spaces)
- [ ] Framework config: none needed (pytest works without config file for simple cases)

## Sources

### Primary (HIGH confidence)
- [Optuna Ask-and-Tell Tutorial (4.6.0)](https://optuna.readthedocs.io/en/stable/tutorial/20_recipes/009_ask_and_tell.html) -- exact code patterns for study.ask(), study.tell(), define-and-run approach
- [Optuna create_study API (4.8.0)](https://optuna.readthedocs.io/en/stable/reference/generated/optuna.create_study.html) -- storage, sampler, direction, load_if_exists params
- [Optuna TPESampler (4.8.0)](https://optuna.readthedocs.io/en/stable/reference/samplers/generated/optuna.samplers.TPESampler.html) -- n_startup_trials, multivariate, group params
- [Optuna CmaEsSampler (4.8.0)](https://optuna.readthedocs.io/en/stable/reference/samplers/generated/optuna.samplers.CmaEsSampler.html) -- no CategoricalDistribution support, source_trials for warm-start
- [Optuna SQLite Persistence Tutorial (4.8.0)](https://optuna.readthedocs.io/en/stable/tutorial/20_recipes/001_rdb.html) -- storage URL format, sampler state NOT stored, pickle pattern
- [Optuna Study API (4.8.0)](https://optuna.readthedocs.io/en/stable/reference/generated/optuna.study.Study.html) -- trials, best_trial, best_params properties

### Secondary (MEDIUM confidence)
- [AutoSampler OptunaHub](https://hub.optuna.org/samplers/auto_sampler/) -- exists but requires optunahub dep, not used
- [Optuna GitHub Issue #1015](https://github.com/optuna/optuna/issues/1015) -- TPE handles trial states, rebuilds model from completed trials

### Tertiary (LOW confidence)
- None -- all critical claims verified against official Optuna documentation

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH -- optuna already installed, all APIs verified against 4.8.0 docs
- Architecture: HIGH -- Ask-and-Tell pattern is well-documented, integration points clearly identified in existing workflows
- Pitfalls: HIGH -- sampler state persistence, CMA-ES limitations, and warmup behavior all verified against official docs

**Research date:** 2026-03-23
**Valid until:** 2026-04-23 (Optuna is stable, low churn on core APIs)
