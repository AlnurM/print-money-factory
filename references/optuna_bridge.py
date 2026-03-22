"""Optuna bridge for Bayesian optimization in PMF backtest loop.

Manages study lifecycle, sampler auto-selection, parameter suggestion,
result reporting, and resume with param-space-change detection.

Stored in ~/.pmf/references/ alongside metrics.py and backtest_engine.py.
"""

from __future__ import annotations

import pickle
from pathlib import Path

import optuna

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
                step=step,
                log=p.get("log", False),
            )
        elif p["type"] == "categorical":
            distributions[name] = optuna.distributions.CategoricalDistribution(
                choices=p["choices"]
            )
    return distributions


def select_sampler(
    param_space: list[dict], seed: int = 42
) -> tuple[optuna.samplers.BaseSampler, str]:
    """Auto-select CMA-ES for all-continuous floats, TPE otherwise (per D-09).

    CMA-ES requires:
    - ALL params are type="float" with no step constraint
    - At least 2 parameters

    Otherwise falls back to TPE with multivariate=True.
    """
    all_continuous = all(
        p["type"] == "float" and p.get("step") is None
        for p in param_space
    )

    if all_continuous and len(param_space) >= 2:
        sampler = optuna.samplers.CmaEsSampler(
            n_startup_trials=10,
            seed=seed,
        )
        return sampler, "CMA-ES"
    else:
        sampler = optuna.samplers.TPESampler(
            n_startup_trials=10,
            multivariate=True,
            seed=seed,
        )
        return sampler, "TPE"


def get_or_create_study(
    study_name: str,
    storage_dir: str,
    sampler: optuna.samplers.BaseSampler,
    direction: str = "maximize",
) -> optuna.Study:
    """Create new study or load existing one with SQLite persistence (per D-11)."""
    storage_path = Path(storage_dir) / "optuna_study.db"
    storage_url = f"sqlite:///{storage_path}"
    return optuna.create_study(
        study_name=study_name,
        storage=storage_url,
        direction=direction,
        load_if_exists=True,
        sampler=sampler,
    )


def suggest_params(
    study: optuna.Study, distributions: dict
) -> tuple[optuna.trial.FrozenTrial, dict]:
    """Ask Optuna for next parameter suggestion (define-and-run, per D-01)."""
    trial = study.ask(distributions)
    return trial, trial.params


def report_result(study: optuna.Study, trial, value: float) -> None:
    """Report objective value for completed trial."""
    study.tell(trial, value)


def compute_composite_score(metrics: dict, dd_target: float) -> float:
    """Composite objective: Sharpe with capped drawdown penalty (per D-04).

    score = sharpe - dd_penalty
    dd_penalty = min(max(0, abs(max_dd) - abs(dd_target)) * 2.0, 5.0)

    Returns -inf if trade_count == 0.
    """
    trade_count = metrics.get("trade_count", 0)
    if trade_count == 0:
        return float("-inf")

    sharpe = metrics.get("sharpe_ratio", 0.0)
    max_dd = abs(metrics.get("max_drawdown", 0.0))

    excess_dd = max(0.0, max_dd - abs(dd_target))
    dd_penalty = min(excess_dd * 2.0, 5.0)

    return sharpe - dd_penalty


def is_warmup(study: optuna.Study, n_startup_trials: int = 10) -> bool:
    """Check if study is still in random warmup phase (per D-03)."""
    completed = len([
        t for t in study.trials
        if t.state == optuna.trial.TrialState.COMPLETE
    ])
    return completed < n_startup_trials


def detect_param_changes(
    study: optuna.Study,
    new_distributions: dict[str, optuna.distributions.BaseDistribution],
) -> list[str]:
    """Detect if param space changed since last trial (per D-13).

    Returns list of change descriptions. Empty = no changes.
    """
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


def save_sampler(study: optuna.Study, storage_dir: str) -> None:
    """Pickle sampler state (needed for CMA-ES resume)."""
    pkl_path = Path(storage_dir) / "optuna_sampler.pkl"
    with open(pkl_path, "wb") as f:
        pickle.dump(study.sampler, f)


def load_sampler(storage_dir: str) -> optuna.samplers.BaseSampler | None:
    """Load pickled sampler (for CMA-ES resume). Returns None if not found."""
    pkl_path = Path(storage_dir) / "optuna_sampler.pkl"
    if pkl_path.exists():
        with open(pkl_path, "rb") as f:
            return pickle.load(f)
    return None
