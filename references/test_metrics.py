"""Known-answer unit tests for all 9 financial metrics + edge cases."""

import math

import numpy as np
import pytest

from metrics import (
    calmar_ratio,
    compute_all_metrics,
    expectancy,
    max_drawdown,
    net_pnl,
    profit_factor,
    sharpe_ratio,
    sortino_ratio,
    trade_count,
    win_rate,
)


# ---------------------------------------------------------------------------
# sharpe_ratio
# ---------------------------------------------------------------------------

class TestSharpeRatio:
    def test_known_answer_alternating(self, sample_returns):
        """252 days of +1%/-0.5% -> Sharpe between 3.5 and 4.0."""
        result = sharpe_ratio(sample_returns)
        assert 3.5 <= result <= 4.0, f"Sharpe {result} not in [3.5, 4.0]"

    def test_constant_returns_nan(self):
        """Constant returns (zero std) -> NaN."""
        returns = np.array([0.01] * 100)
        result = sharpe_ratio(returns)
        assert math.isnan(result)

    def test_empty_returns_nan(self):
        """Empty array -> NaN."""
        result = sharpe_ratio(np.array([]))
        assert math.isnan(result)

    def test_single_element_nan(self):
        """Single element -> NaN."""
        result = sharpe_ratio(np.array([0.05]))
        assert math.isnan(result)


# ---------------------------------------------------------------------------
# sortino_ratio
# ---------------------------------------------------------------------------

class TestSortinoRatio:
    def test_known_answer_greater_than_sharpe(self, sample_returns):
        """With alternating +1%/-0.5%, Sortino > Sharpe (less downside volatility)."""
        s = sharpe_ratio(sample_returns)
        result = sortino_ratio(sample_returns)
        assert result > s, f"Sortino {result} should be > Sharpe {s}"

    def test_all_positive_nan(self):
        """All positive returns (no downside) -> NaN."""
        returns = np.array([0.01, 0.02, 0.005, 0.015, 0.01])
        result = sortino_ratio(returns)
        assert math.isnan(result)

    def test_empty_returns_nan(self):
        """Empty array -> NaN."""
        result = sortino_ratio(np.array([]))
        assert math.isnan(result)


# ---------------------------------------------------------------------------
# calmar_ratio
# ---------------------------------------------------------------------------

class TestCalmarRatio:
    def test_known_answer(self, sample_returns, sample_equity):
        """Calmar = annualized_return / abs(max_drawdown)."""
        result = calmar_ratio(sample_returns, sample_equity)
        assert result > 0, f"Calmar {result} should be positive for profitable returns"
        # Sanity: should be finite
        assert math.isfinite(result)

    def test_no_drawdown_nan(self):
        """Monotonically increasing equity -> NaN (no drawdown)."""
        returns = np.array([0.01, 0.02, 0.01, 0.03, 0.01])
        equity = 10000.0 * np.cumprod(1.0 + returns)
        result = calmar_ratio(returns, equity)
        assert math.isnan(result)

    def test_empty_nan(self):
        """Empty inputs -> NaN."""
        result = calmar_ratio(np.array([]), np.array([]))
        assert math.isnan(result)


# ---------------------------------------------------------------------------
# max_drawdown
# ---------------------------------------------------------------------------

class TestMaxDrawdown:
    def test_known_answer(self):
        """[100, 120, 90, 110] -> -0.25 (25% drop from 120 peak)."""
        equity = np.array([100.0, 120.0, 90.0, 110.0])
        result = max_drawdown(equity)
        assert result == pytest.approx(-0.25)

    def test_monotonically_increasing(self):
        """Monotonically increasing -> 0.0."""
        equity = np.array([100.0, 110.0, 120.0, 130.0])
        result = max_drawdown(equity)
        assert result == pytest.approx(0.0)

    def test_single_value(self):
        """Single value -> 0.0."""
        equity = np.array([100.0])
        result = max_drawdown(equity)
        assert result == pytest.approx(0.0)

    def test_empty(self):
        """Empty array -> 0.0."""
        equity = np.array([])
        result = max_drawdown(equity)
        assert result == pytest.approx(0.0)


# ---------------------------------------------------------------------------
# win_rate
# ---------------------------------------------------------------------------

class TestWinRate:
    def test_known_answer(self):
        """2 winners, 2 losers -> 0.5."""
        trades = [{"pnl": 100.0}, {"pnl": -50.0}, {"pnl": 75.0}, {"pnl": -25.0}]
        result = win_rate(trades)
        assert result == pytest.approx(0.5)

    def test_empty_trades(self):
        """Empty trades -> 0.0."""
        result = win_rate([])
        assert result == pytest.approx(0.0)

    def test_all_winners(self):
        """All winners -> 1.0."""
        trades = [{"pnl": 100.0}, {"pnl": 50.0}, {"pnl": 75.0}]
        result = win_rate(trades)
        assert result == pytest.approx(1.0)

    def test_all_losers(self):
        """All losers -> 0.0."""
        trades = [{"pnl": -100.0}, {"pnl": -50.0}]
        result = win_rate(trades)
        assert result == pytest.approx(0.0)


# ---------------------------------------------------------------------------
# profit_factor
# ---------------------------------------------------------------------------

class TestProfitFactor:
    def test_known_answer(self):
        """Gross profit=200, gross loss=100 -> 2.0."""
        trades = [{"pnl": 150.0}, {"pnl": -60.0}, {"pnl": 50.0}, {"pnl": -40.0}]
        result = profit_factor(trades)
        assert result == pytest.approx(2.0)

    def test_no_losers_inf(self):
        """No losers with profit -> inf."""
        trades = [{"pnl": 100.0}, {"pnl": 50.0}]
        result = profit_factor(trades)
        assert result == float("inf")

    def test_no_winners_zero(self):
        """No winners -> 0.0."""
        trades = [{"pnl": -100.0}, {"pnl": -50.0}]
        result = profit_factor(trades)
        assert result == pytest.approx(0.0)

    def test_empty_trades(self):
        """Empty trades -> 0.0."""
        result = profit_factor([])
        assert result == pytest.approx(0.0)


# ---------------------------------------------------------------------------
# expectancy
# ---------------------------------------------------------------------------

class TestExpectancy:
    def test_known_answer(self):
        """Trades with pnl [100, -50, 75, -25] -> 25.0."""
        trades = [{"pnl": 100.0}, {"pnl": -50.0}, {"pnl": 75.0}, {"pnl": -25.0}]
        result = expectancy(trades)
        assert result == pytest.approx(25.0)

    def test_empty_trades(self):
        """Empty trades -> 0.0."""
        result = expectancy([])
        assert result == pytest.approx(0.0)


# ---------------------------------------------------------------------------
# trade_count
# ---------------------------------------------------------------------------

class TestTradeCount:
    def test_count(self):
        """Returns len(trades)."""
        trades = [{"pnl": 1.0}, {"pnl": 2.0}, {"pnl": 3.0}]
        assert trade_count(trades) == 3

    def test_empty(self):
        """Empty trades -> 0."""
        assert trade_count([]) == 0


# ---------------------------------------------------------------------------
# net_pnl
# ---------------------------------------------------------------------------

class TestNetPnl:
    def test_known_answer(self):
        """Sum of pnl values."""
        trades = [{"pnl": 100.0}, {"pnl": -50.0}, {"pnl": 75.0}, {"pnl": -25.0}]
        result = net_pnl(trades)
        assert result == pytest.approx(100.0)

    def test_empty_trades(self):
        """Empty trades -> 0.0."""
        result = net_pnl([])
        assert result == pytest.approx(0.0)


# ---------------------------------------------------------------------------
# compute_all_metrics (integration)
# ---------------------------------------------------------------------------

class TestComputeAllMetrics:
    def test_with_trade_log(self, sample_trades):
        """compute_all_metrics with trades returns dict with all 9 keys."""
        result = compute_all_metrics(trades=sample_trades)
        expected_keys = {
            "sharpe_ratio", "sortino_ratio", "calmar_ratio", "max_drawdown",
            "win_rate", "profit_factor", "expectancy", "trade_count", "net_pnl",
        }
        assert set(result.keys()) == expected_keys
        # Trade-based metrics should have real values
        assert result["trade_count"] == 10
        assert result["net_pnl"] == pytest.approx(360.0)
        assert result["win_rate"] == pytest.approx(0.5)
        assert result["profit_factor"] == pytest.approx(585.0 / 225.0)
        assert result["expectancy"] == pytest.approx(36.0)

    def test_with_daily_returns(self, sample_returns):
        """compute_all_metrics with daily_returns returns ratio metrics, NaN/0 for trade metrics."""
        result = compute_all_metrics(daily_returns=sample_returns)
        expected_keys = {
            "sharpe_ratio", "sortino_ratio", "calmar_ratio", "max_drawdown",
            "win_rate", "profit_factor", "expectancy", "trade_count", "net_pnl",
        }
        assert set(result.keys()) == expected_keys
        # Ratio metrics should be computed
        assert math.isfinite(result["sharpe_ratio"])
        assert math.isfinite(result["sortino_ratio"])
        # Trade-based metrics should be 0 or NaN
        assert result["trade_count"] == 0

    def test_returns_dict(self, sample_trades):
        """Return type is dict."""
        result = compute_all_metrics(trades=sample_trades)
        assert isinstance(result, dict)

    def test_no_input_raises_or_returns_nans(self):
        """No trades or returns -> should handle gracefully."""
        result = compute_all_metrics()
        assert isinstance(result, dict)
        # All values should be NaN or 0
        for key, val in result.items():
            assert math.isnan(val) or val == 0, f"{key}={val} should be NaN or 0"
