"""Shared pytest fixtures for metrics tests."""

import numpy as np
import pytest


@pytest.fixture
def sample_trades():
    """10 trades with known PnL values for deterministic metric testing.

    Total PnL: 100 + (-50) + 75 + (-25) + 150 + (-80) + 60 + (-30) + 200 + (-40) = 360
    Winners: 5 (100, 75, 150, 60, 200) = 585 gross profit
    Losers: 5 (-50, -25, -80, -30, -40) = -225 gross loss
    Win rate: 0.5
    Profit factor: 585 / 225 = 2.6
    Expectancy: 360 / 10 = 36.0
    """
    return [
        {"entry_time": "2024-01-01 09:00", "exit_time": "2024-01-01 10:00",
         "entry_price": 100.0, "exit_price": 101.0, "size": 100, "side": "long",
         "pnl": 100.0, "commission": 1.0},
        {"entry_time": "2024-01-02 09:00", "exit_time": "2024-01-02 10:00",
         "entry_price": 101.0, "exit_price": 100.5, "size": 100, "side": "long",
         "pnl": -50.0, "commission": 1.0},
        {"entry_time": "2024-01-03 09:00", "exit_time": "2024-01-03 10:00",
         "entry_price": 100.5, "exit_price": 101.25, "size": 100, "side": "long",
         "pnl": 75.0, "commission": 1.0},
        {"entry_time": "2024-01-04 09:00", "exit_time": "2024-01-04 10:00",
         "entry_price": 101.25, "exit_price": 101.0, "size": 100, "side": "long",
         "pnl": -25.0, "commission": 1.0},
        {"entry_time": "2024-01-05 09:00", "exit_time": "2024-01-05 10:00",
         "entry_price": 101.0, "exit_price": 102.5, "size": 100, "side": "long",
         "pnl": 150.0, "commission": 1.0},
        {"entry_time": "2024-01-08 09:00", "exit_time": "2024-01-08 10:00",
         "entry_price": 102.5, "exit_price": 101.7, "size": 100, "side": "long",
         "pnl": -80.0, "commission": 1.0},
        {"entry_time": "2024-01-09 09:00", "exit_time": "2024-01-09 10:00",
         "entry_price": 101.7, "exit_price": 102.3, "size": 100, "side": "long",
         "pnl": 60.0, "commission": 1.0},
        {"entry_time": "2024-01-10 09:00", "exit_time": "2024-01-10 10:00",
         "entry_price": 102.3, "exit_price": 102.0, "size": 100, "side": "long",
         "pnl": -30.0, "commission": 1.0},
        {"entry_time": "2024-01-11 09:00", "exit_time": "2024-01-11 10:00",
         "entry_price": 102.0, "exit_price": 104.0, "size": 100, "side": "long",
         "pnl": 200.0, "commission": 1.0},
        {"entry_time": "2024-01-12 09:00", "exit_time": "2024-01-12 10:00",
         "entry_price": 104.0, "exit_price": 103.6, "size": 100, "side": "long",
         "pnl": -40.0, "commission": 1.0},
    ]


@pytest.fixture
def sample_returns():
    """252-day numpy array with known statistical properties.

    Alternating +1% / -0.5% pattern for deterministic Sharpe/Sortino computation.
    Mean daily return: (+0.01 + (-0.005)) / 2 = 0.0025
    """
    rng = np.array([0.01, -0.005] * 126)
    return rng


@pytest.fixture
def sample_equity(sample_returns):
    """Equity curve derived from sample_returns starting at 10000."""
    return 10000.0 * np.cumprod(1.0 + sample_returns)
