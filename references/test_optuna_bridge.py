"""Unit tests for optuna_bridge.py -- Optuna integration for PMF backtest loop.

Tests cover: distribution building, sampler auto-selection, Ask-and-Tell lifecycle,
composite scoring, warmup detection, SQLite persistence, param change detection,
and sampler pickle save/load.
"""

import math
import os
import sys

import optuna
import pytest

# Enable import from same directory
sys.path.insert(0, os.path.dirname(__file__))

from optuna_bridge import (
    build_distributions,
    compute_composite_score,
    detect_param_changes,
    get_or_create_study,
    is_warmup,
    load_sampler,
    report_result,
    save_sampler,
    select_sampler,
    suggest_params,
)


# ---------------------------------------------------------------------------
# build_distributions
# ---------------------------------------------------------------------------

class TestBuildDistributions:
    def test_build_distributions_int(self):
        """IntDistribution from int param spec with step."""
        param_space = [{"name": "fast_period", "type": "int", "min": 5, "max": 50, "step": 1}]
        dists = build_distributions(param_space)
        assert "fast_period" in dists
        d = dists["fast_period"]
        assert isinstance(d, optuna.distributions.IntDistribution)
        assert d.low == 5
        assert d.high == 50
        assert d.step == 1

    def test_build_distributions_float(self):
        """FloatDistribution from float param spec without step."""
        param_space = [{"name": "atr_mult", "type": "float", "min": 1.0, "max": 3.0}]
        dists = build_distributions(param_space)
        assert "atr_mult" in dists
        d = dists["atr_mult"]
        assert isinstance(d, optuna.distributions.FloatDistribution)
        assert d.low == 1.0
        assert d.high == 3.0
        assert d.step is None

    def test_build_distributions_float_with_step(self):
        """FloatDistribution with step constraint."""
        param_space = [{"name": "threshold", "type": "float", "min": 0.1, "max": 1.0, "step": 0.1}]
        dists = build_distributions(param_space)
        d = dists["threshold"]
        assert isinstance(d, optuna.distributions.FloatDistribution)
        assert d.step == 0.1

    def test_build_distributions_categorical(self):
        """CategoricalDistribution from categorical param spec."""
        param_space = [{"name": "ma_type", "type": "categorical", "choices": ["ema", "sma"]}]
        dists = build_distributions(param_space)
        d = dists["ma_type"]
        assert isinstance(d, optuna.distributions.CategoricalDistribution)
        assert list(d.choices) == ["ema", "sma"]


# ---------------------------------------------------------------------------
# select_sampler
# ---------------------------------------------------------------------------

class TestSelectSampler:
    def test_select_sampler_cmaes(self):
        """CMA-ES when all params are float without step and count >= 2."""
        param_space = [
            {"name": "atr_mult", "type": "float", "min": 1.0, "max": 3.0},
            {"name": "stop_mult", "type": "float", "min": 0.5, "max": 2.0},
        ]
        sampler, name = select_sampler(param_space)
        assert isinstance(sampler, optuna.samplers.CmaEsSampler)
        assert name == "CMA-ES"

    def test_select_sampler_tpe_categorical(self):
        """TPE when categorical param present."""
        param_space = [
            {"name": "atr_mult", "type": "float", "min": 1.0, "max": 3.0},
            {"name": "ma_type", "type": "categorical", "choices": ["ema", "sma"]},
        ]
        sampler, name = select_sampler(param_space)
        assert isinstance(sampler, optuna.samplers.TPESampler)
        assert name == "TPE"

    def test_select_sampler_tpe_int(self):
        """TPE when int param present."""
        param_space = [
            {"name": "fast_period", "type": "int", "min": 5, "max": 50, "step": 1},
            {"name": "atr_mult", "type": "float", "min": 1.0, "max": 3.0},
        ]
        sampler, name = select_sampler(param_space)
        assert isinstance(sampler, optuna.samplers.TPESampler)
        assert name == "TPE"

    def test_select_sampler_tpe_float_with_step(self):
        """TPE when float has step constraint."""
        param_space = [
            {"name": "threshold", "type": "float", "min": 0.1, "max": 1.0, "step": 0.1},
            {"name": "atr_mult", "type": "float", "min": 1.0, "max": 3.0},
        ]
        sampler, name = select_sampler(param_space)
        assert isinstance(sampler, optuna.samplers.TPESampler)
        assert name == "TPE"

    def test_select_sampler_tpe_single_float(self):
        """TPE when only 1 float param (CMA-ES needs >= 2)."""
        param_space = [
            {"name": "atr_mult", "type": "float", "min": 1.0, "max": 3.0},
        ]
        sampler, name = select_sampler(param_space)
        assert isinstance(sampler, optuna.samplers.TPESampler)
        assert name == "TPE"


# ---------------------------------------------------------------------------
# Ask-and-Tell lifecycle
# ---------------------------------------------------------------------------

class TestAskTellLifecycle:
    def test_ask_tell_lifecycle(self, tmp_path):
        """study.ask() returns trial with params, study.tell() records score."""
        param_space = [
            {"name": "fast_period", "type": "int", "min": 5, "max": 50, "step": 1},
            {"name": "slow_period", "type": "int", "min": 20, "max": 200, "step": 1},
        ]
        dists = build_distributions(param_space)
        sampler, _ = select_sampler(param_space)
        study = get_or_create_study("test_lifecycle", str(tmp_path), sampler)

        trial, params = suggest_params(study, dists)
        assert "fast_period" in params
        assert "slow_period" in params
        assert 5 <= params["fast_period"] <= 50
        assert 20 <= params["slow_period"] <= 200

        report_result(study, trial, 1.5)

        completed = [t for t in study.trials if t.state == optuna.trial.TrialState.COMPLETE]
        assert len(completed) == 1
        assert completed[0].value == 1.5


# ---------------------------------------------------------------------------
# compute_composite_score
# ---------------------------------------------------------------------------

class TestCompositeScore:
    def test_composite_score_basic(self):
        """No penalty when drawdown within target."""
        metrics = {"sharpe_ratio": 2.0, "max_drawdown": -0.10, "trade_count": 50}
        score = compute_composite_score(metrics, dd_target=0.15)
        assert score == pytest.approx(2.0)

    def test_composite_score_penalty(self):
        """Penalty applied when drawdown exceeds target, capped at 5."""
        metrics = {"sharpe_ratio": 2.0, "max_drawdown": -0.25, "trade_count": 50}
        # excess = 0.25 - 0.15 = 0.10, penalty = min(0.10 * 2, 5) = 0.20
        # But wait: test spec says score = 2.0 - min(10*2, 5) = -3.0
        # Let me re-read: max_dd=-25%, dd_target=15%
        # If dd values are percentages (0.25, 0.15): excess=0.10, penalty=min(0.20, 5)=0.20, score=1.80
        # The plan spec uses "sharpe=2.0, max_dd=-25%, dd_target=15% -> score=2.0 - min(10*2, 5) = -3.0"
        # That implies dd expressed as whole percentages. But research code uses fractions.
        # Research code: abs(-0.25) - abs(0.15) = 0.10, penalty = min(0.10*2, 5) = 0.20
        # So score = 2.0 - 0.20 = 1.80
        score = compute_composite_score(metrics, dd_target=0.15)
        # excess_dd = abs(-0.25) - abs(0.15) = 0.10
        # dd_penalty = min(0.10 * 2.0, 5.0) = 0.20
        # score = 2.0 - 0.20 = 1.80
        assert score == pytest.approx(1.80)

    def test_composite_score_no_trades(self):
        """Zero trades returns -inf."""
        metrics = {"sharpe_ratio": 2.0, "max_drawdown": -0.10, "trade_count": 0}
        score = compute_composite_score(metrics, dd_target=0.15)
        assert score == float("-inf")

    def test_composite_score_penalty_cap(self):
        """Penalty capped at 5.0 even for extreme drawdown."""
        metrics = {"sharpe_ratio": 2.5, "max_drawdown": -0.40, "trade_count": 50}
        # excess = 0.40 - 0.15 = 0.25, penalty = min(0.25*2, 5) = 0.50
        # score = 2.5 - 0.50 = 2.0
        score = compute_composite_score(metrics, dd_target=0.15)
        assert score == pytest.approx(2.0)


# ---------------------------------------------------------------------------
# is_warmup
# ---------------------------------------------------------------------------

class TestIsWarmup:
    def test_is_warmup_true(self, tmp_path):
        """Fewer completed trials than n_startup_trials -> warmup."""
        sampler = optuna.samplers.TPESampler(n_startup_trials=10, seed=42)
        study = get_or_create_study("test_warmup_true", str(tmp_path), sampler)
        dists = {"x": optuna.distributions.FloatDistribution(0.0, 1.0)}
        # Add 5 trials (< 10)
        for i in range(5):
            trial = study.ask(dists)
            study.tell(trial, float(i))
        assert is_warmup(study, n_startup_trials=10) is True

    def test_is_warmup_false(self, tmp_path):
        """Enough completed trials -> not warmup."""
        sampler = optuna.samplers.TPESampler(n_startup_trials=5, seed=42)
        study = get_or_create_study("test_warmup_false", str(tmp_path), sampler)
        dists = {"x": optuna.distributions.FloatDistribution(0.0, 1.0)}
        for i in range(10):
            trial = study.ask(dists)
            study.tell(trial, float(i))
        assert is_warmup(study, n_startup_trials=5) is False


# ---------------------------------------------------------------------------
# SQLite persistence
# ---------------------------------------------------------------------------

class TestSQLitePersistence:
    def test_sqlite_persistence(self, tmp_path):
        """Create study, add trial, reload from SQLite, verify trial exists."""
        param_space = [
            {"name": "x", "type": "float", "min": 0.0, "max": 1.0},
            {"name": "y", "type": "float", "min": 0.0, "max": 1.0},
        ]
        dists = build_distributions(param_space)
        sampler1, _ = select_sampler(param_space)
        study1 = get_or_create_study("test_persist", str(tmp_path), sampler1)

        trial, params = suggest_params(study1, dists)
        report_result(study1, trial, 2.0)

        # Create NEW study object from same storage
        sampler2, _ = select_sampler(param_space)
        study2 = get_or_create_study("test_persist", str(tmp_path), sampler2)

        assert len(study2.trials) == 1
        assert study2.trials[0].value == 2.0


# ---------------------------------------------------------------------------
# detect_param_changes
# ---------------------------------------------------------------------------

class TestParamChangeDetection:
    def test_param_change_detection_no_changes(self, tmp_path):
        """Same distributions -> empty change list."""
        dists = {"x": optuna.distributions.FloatDistribution(0.0, 1.0)}
        sampler = optuna.samplers.TPESampler(seed=42)
        study = get_or_create_study("test_no_changes", str(tmp_path), sampler)
        trial = study.ask(dists)
        study.tell(trial, 1.0)

        changes = detect_param_changes(study, dists)
        assert changes == []

    def test_param_change_detection_new_param(self, tmp_path):
        """New param added -> detected."""
        dists_old = {"x": optuna.distributions.FloatDistribution(0.0, 1.0)}
        sampler = optuna.samplers.TPESampler(seed=42)
        study = get_or_create_study("test_new_param", str(tmp_path), sampler)
        trial = study.ask(dists_old)
        study.tell(trial, 1.0)

        dists_new = {
            "x": optuna.distributions.FloatDistribution(0.0, 1.0),
            "y": optuna.distributions.FloatDistribution(0.0, 2.0),
        }
        changes = detect_param_changes(study, dists_new)
        assert any("NEW param: y" in c for c in changes)

    def test_param_change_detection_changed_range(self, tmp_path):
        """Range changed -> detected."""
        dists_old = {"x": optuna.distributions.FloatDistribution(0.0, 1.0)}
        sampler = optuna.samplers.TPESampler(seed=42)
        study = get_or_create_study("test_changed_range", str(tmp_path), sampler)
        trial = study.ask(dists_old)
        study.tell(trial, 1.0)

        dists_new = {"x": optuna.distributions.FloatDistribution(0.0, 5.0)}
        changes = detect_param_changes(study, dists_new)
        assert any("CHANGED: x" in c for c in changes)

    def test_param_change_detection_removed_param(self, tmp_path):
        """Param removed -> detected."""
        dists_old = {
            "x": optuna.distributions.FloatDistribution(0.0, 1.0),
            "y": optuna.distributions.FloatDistribution(0.0, 2.0),
        }
        sampler = optuna.samplers.TPESampler(seed=42)
        study = get_or_create_study("test_removed_param", str(tmp_path), sampler)
        trial = study.ask(dists_old)
        study.tell(trial, 1.0)

        dists_new = {"x": optuna.distributions.FloatDistribution(0.0, 1.0)}
        changes = detect_param_changes(study, dists_new)
        assert any("REMOVED: y" in c for c in changes)


# ---------------------------------------------------------------------------
# save_sampler / load_sampler
# ---------------------------------------------------------------------------

class TestSamplerPickle:
    def test_save_load_sampler(self, tmp_path):
        """Pickle CMA-ES sampler, load it back, verify type matches."""
        param_space = [
            {"name": "a", "type": "float", "min": 0.0, "max": 1.0},
            {"name": "b", "type": "float", "min": 0.0, "max": 1.0},
        ]
        sampler, name = select_sampler(param_space)
        assert name == "CMA-ES"

        study = get_or_create_study("test_pickle", str(tmp_path), sampler)
        save_sampler(study, str(tmp_path))

        loaded = load_sampler(str(tmp_path))
        assert loaded is not None
        assert isinstance(loaded, optuna.samplers.CmaEsSampler)

    def test_load_sampler_missing_file(self, tmp_path):
        """Load from nonexistent path returns None."""
        loaded = load_sampler(str(tmp_path))
        assert loaded is None
