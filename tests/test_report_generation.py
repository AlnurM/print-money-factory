"""Tests for report_generator.py -- regime classification, benchmark stats, data formatting.

Covers VRFY-02 through VRFY-09.
"""
import pytest
import sys
import os
import numpy as np
import pandas as pd

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'references'))
from report_generator import (
    classify_regimes, compute_benchmark_stats, format_metrics_cards,
    format_trades_table, sanitize_for_json, compute_regime_stats
)


# ---------------------------------------------------------------------------
# Mock fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def mock_ohlcv_df():
    """~100 rows of OHLCV with realistic movement: uptrend -> downtrend -> sideways."""
    np.random.seed(42)
    dates = pd.date_range('2023-01-01', periods=100, freq='D')

    # Build a price path: up 35 bars, down 35 bars, sideways 30 bars
    up = np.linspace(100, 130, 35) + np.random.normal(0, 0.5, 35)
    down = np.linspace(130, 105, 35) + np.random.normal(0, 0.5, 35)
    side = np.linspace(105, 107, 30) + np.random.normal(0, 0.5, 30)
    close = np.concatenate([up, down, side])

    high = close + np.abs(np.random.normal(0.5, 0.3, 100))
    low = close - np.abs(np.random.normal(0.5, 0.3, 100))
    opn = close + np.random.normal(0, 0.3, 100)
    volume = np.random.randint(1000, 5000, 100).astype(float)

    df = pd.DataFrame({
        'open': opn,
        'high': high,
        'low': low,
        'close': close,
        'volume': volume,
    }, index=dates)
    df.index.name = 'timestamp'
    return df


@pytest.fixture
def mock_iteration_artifacts():
    """3 iteration verdict dicts."""
    return [
        {
            'iteration': 1,
            'params': {'fast': 10, 'slow': 30},
            'metrics': {
                'sharpe_ratio': 1.2, 'max_drawdown': -0.10, 'win_rate': 0.55,
                'profit_factor': 1.4, 'total_trades': 42, 'net_pnl': 3200.0,
                'sortino_ratio': 1.8, 'calmar_ratio': 1.1,
            },
            'hypothesis': 'Initial parameter set',
            'verdict': 'exploring',
        },
        {
            'iteration': 2,
            'params': {'fast': 8, 'slow': 25},
            'metrics': {
                'sharpe_ratio': 1.6, 'max_drawdown': -0.12, 'win_rate': 0.60,
                'profit_factor': 1.9, 'total_trades': 38, 'net_pnl': 5100.0,
                'sortino_ratio': 2.2, 'calmar_ratio': 1.5,
            },
            'hypothesis': 'Tighter fast period',
            'verdict': 'MINT',
        },
        {
            'iteration': 3,
            'params': {'fast': 12, 'slow': 35},
            'metrics': {
                'sharpe_ratio': 1.0, 'max_drawdown': -0.18, 'win_rate': 0.50,
                'profit_factor': 1.1, 'total_trades': 55, 'net_pnl': 1200.0,
                'sortino_ratio': 1.3, 'calmar_ratio': 0.7,
            },
            'hypothesis': 'Wider parameters',
            'verdict': 'PLATEAU',
        },
    ]


@pytest.fixture
def mock_best_result():
    """Best result dict."""
    return {
        'best_params': {'fast': 8, 'slow': 25},
        'is_metrics': {
            'sharpe_ratio': 1.6, 'max_drawdown': -0.12, 'win_rate': 0.60,
            'profit_factor': 1.9, 'total_trades': 38, 'net_pnl': 5100.0,
            'sortino_ratio': 2.2, 'calmar_ratio': 1.5,
        },
        'oos_metrics': {
            'sharpe_ratio': 1.3, 'max_drawdown': -0.14,
        },
        'stop_reason': 'MINT',
    }


@pytest.fixture
def mock_trades():
    """5 trade dicts."""
    return [
        {'entry_date': '2023-02-15', 'exit_date': '2023-03-01', 'direction': 'long',
         'entry_price': 105.0, 'exit_price': 112.0, 'pnl': 700.0, 'pnl_pct': 6.67, 'duration': 14},
        {'entry_date': '2023-01-10', 'exit_date': '2023-01-20', 'direction': 'long',
         'entry_price': 101.0, 'exit_price': 108.0, 'pnl': 700.0, 'pnl_pct': 6.93, 'duration': 10},
        {'entry_date': '2023-04-01', 'exit_date': '2023-04-10', 'direction': 'short',
         'entry_price': 120.0, 'exit_price': 115.0, 'pnl': 500.0, 'pnl_pct': 4.17, 'duration': 9},
        {'entry_date': '2023-03-10', 'exit_date': '2023-03-20', 'direction': 'long',
         'entry_price': 118.0, 'exit_price': 115.0, 'pnl': -300.0, 'pnl_pct': -2.54, 'duration': 10},
        {'entry_date': '2023-05-01', 'exit_date': '2023-05-15', 'direction': 'long',
         'entry_price': 106.0, 'exit_price': 107.0, 'pnl': 100.0, 'pnl_pct': 0.94, 'duration': 14},
    ]


@pytest.fixture
def mock_targets():
    """Target metrics."""
    return {'sharpe_ratio': 1.5, 'max_drawdown': -0.15}


# ---------------------------------------------------------------------------
# Tests -- regime classification
# ---------------------------------------------------------------------------

def test_classify_regimes_returns_valid_labels(mock_ohlcv_df):
    result = classify_regimes(mock_ohlcv_df)
    assert isinstance(result, pd.Series)
    valid_labels = {'bull', 'bear', 'sideways'}
    assert set(result.unique()).issubset(valid_labels), f"Unexpected labels: {set(result.unique()) - valid_labels}"
    assert len(result) == len(mock_ohlcv_df)


def test_classify_regimes_no_nan(mock_ohlcv_df):
    result = classify_regimes(mock_ohlcv_df)
    assert result.isna().sum() == 0, "Regime series should have no NaN (warmup bars filled with 'sideways')"


# ---------------------------------------------------------------------------
# Tests -- benchmark stats
# ---------------------------------------------------------------------------

def test_compute_benchmark_stats_returns_alpha_beta_r2():
    # Two equity curves: strategy slightly outperforms
    strategy_equity = np.array([10000, 10100, 10250, 10200, 10400, 10500])
    buyhold_equity = np.array([10000, 10050, 10100, 10080, 10200, 10250])
    result = compute_benchmark_stats(strategy_equity, buyhold_equity)
    assert 'alpha' in result
    assert 'beta' in result
    assert 'r_squared' in result
    assert isinstance(result['alpha'], float)
    assert isinstance(result['beta'], float)
    assert isinstance(result['r_squared'], float)


# ---------------------------------------------------------------------------
# Tests -- metrics card formatting
# ---------------------------------------------------------------------------

def test_format_metrics_cards_color_coding(mock_targets):
    metrics = {
        'sharpe_ratio': 1.6,   # meets target 1.5 -> green
        'max_drawdown': -0.20, # misses target -0.15 -> red (more negative is worse)
        'win_rate': 0.58,      # no target -> default
    }
    cards = format_metrics_cards(metrics, mock_targets)
    card_map = {c['label']: c for c in cards}

    assert card_map['SHARPE RATIO']['color'] == '#16a34a'
    assert card_map['MAX DRAWDOWN']['color'] == '#dc2626'
    assert card_map['WIN RATE']['color'] == '#333333'


def test_format_metrics_cards_formatting(mock_targets):
    metrics = {
        'sharpe_ratio': 1.4567,
        'max_drawdown': -0.123,
        'net_pnl': 12450.0,
    }
    cards = format_metrics_cards(metrics, mock_targets)
    card_map = {c['label']: c for c in cards}

    assert card_map['SHARPE RATIO']['value'] == '1.46'
    assert '%' in card_map['MAX DRAWDOWN']['value']
    assert '$' in card_map['NET P&L']['value']


# ---------------------------------------------------------------------------
# Tests -- trades table formatting
# ---------------------------------------------------------------------------

def test_format_trades_table_chronological(mock_trades):
    result = format_trades_table(mock_trades)
    dates = [t['entry_date'] for t in result]
    assert dates == sorted(dates), "Trades should be sorted chronologically by entry_date"


def test_format_trades_table_pnl_fields(mock_trades):
    result = format_trades_table(mock_trades)
    for trade in result:
        assert isinstance(trade['pnl'], (int, float)), "pnl should be a raw float"
        assert isinstance(trade['pnl_pct'], (int, float)), "pnl_pct should be a raw float"
        assert isinstance(trade['pnl_formatted'], str), "pnl_formatted should be a string"
        assert isinstance(trade['pnl_pct_formatted'], str), "pnl_pct_formatted should be a string"


# ---------------------------------------------------------------------------
# Tests -- JSON sanitization
# ---------------------------------------------------------------------------

def test_sanitize_for_json_numpy_types():
    data = {
        'int_val': np.int64(42),
        'float_val': np.float64(3.14),
        'array_val': np.array([1, 2, 3]),
    }
    result = sanitize_for_json(data)
    assert isinstance(result['int_val'], int)
    assert isinstance(result['float_val'], float)
    assert isinstance(result['array_val'], list)


# ---------------------------------------------------------------------------
# Tests -- regime stats
# ---------------------------------------------------------------------------

def test_regime_stats_per_regime_metrics(mock_trades, mock_ohlcv_df):
    regimes = classify_regimes(mock_ohlcv_df)
    result = compute_regime_stats(mock_trades, regimes, mock_ohlcv_df)

    for regime_dict in result:
        for key in ('name', 'bars', 'trades', 'win_rate', 'avg_pnl', 'total_pnl', 'contribution', 'color'):
            assert key in regime_dict, f"Regime dict missing key '{key}'"
