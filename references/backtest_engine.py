"""
Backtest Engine Skeleton -- Claude fills in calculate_signal() only.
DO NOT modify: event loop, position management, or metrics integration.

Usage:
    from backtest_engine import run_backtest
    results = run_backtest(df, params)
"""
import pandas as pd
import numpy as np
from pathlib import Path
import sys
import json

# Import fixed metrics module
sys.path.insert(0, str(Path.home() / '.pmf' / 'references'))
from metrics import compute_all_metrics


def calculate_signal(history: pd.DataFrame, params: dict) -> str:
    """
    Generate a trading signal based on historical data.

    Claude replaces this function per strategy. The rest of the engine
    MUST NOT be modified.

    Args:
        history: DataFrame with OHLCV data up to and including current bar.
                 Columns: open, high, low, close, volume (all lowercase).
                 Index: DatetimeIndex sorted ascending.
        params:  Strategy parameters dict (e.g., {'fast_period': 10, 'slow_period': 50}).

    Returns:
        One of: 'long', 'short', 'close', 'hold'
        - 'long':  Open a long position (or do nothing if already long)
        - 'short': Open a short position (or do nothing if already short)
        - 'close': Close the current position
        - 'hold':  Do nothing

    RULE 3: No future data in calculate_signal()
    This function receives only history[:i+1]. It MUST NOT access any data
    beyond what is passed in. Do not use global DataFrames, do not reference
    indices beyond len(history)-1.
    """
    return 'hold'


def run_backtest(df: pd.DataFrame, params: dict) -> dict:
    """
    Event-loop backtest engine with anti-lookahead enforcement.

    Processes one bar at a time, generates signals using only past + current
    data, and executes trades at the next bar's open price.

    Args:
        df:     Full OHLCV DataFrame. Columns: open, high, low, close, volume.
                Index: DatetimeIndex sorted ascending.
        params: Dict with strategy parameters plus engine config:
                - initial_capital (float): Starting equity. Default 10000.
                - commission (float): Commission as fraction of trade value. Default 0.001 (0.1%).
                - trading_days (int): Trading days per year for annualization. Default 252.
                - position_size (float): Fraction of equity per trade. Default 1.0 (100%).
                Plus any strategy-specific parameters for calculate_signal().

    Returns:
        dict: Output of compute_all_metrics() with trades, equity curve, and all metrics.
    """
    initial_capital = params.get('initial_capital', 10000)
    commission_rate = params.get('commission', 0.001)
    position_size_frac = params.get('position_size', 1.0)
    trading_days = params.get('trading_days', 252)

    equity = [initial_capital]
    trades = []
    position = None  # None, or dict with: side, entry_price, entry_time, size

    for i in range(1, len(df)):
        # RULE 1: history[:i+1] -- signal sees only past and current bar
        # The signal function receives data from bar 0 through bar i (inclusive).
        # It CANNOT see bar i+1 or any future bar.
        history = df.iloc[:i + 1]

        signal = calculate_signal(history, params)

        # RULE 2: execution at df.iloc[i]['open'] -- next bar's open price
        # The signal was generated using data up to bar i-1's close (bar i is
        # the "current" bar whose open we use for execution). This simulates
        # the real-world flow: analyze after bar closes -> place order ->
        # order fills at next bar's open.
        execution_price = df.iloc[i]['open']
        current_time = df.index[i]

        current_equity = equity[-1]

        # --- Position Management ---

        # Close position on 'close' signal or opposite signal
        if position is not None:
            should_close = False

            if signal == 'close':
                should_close = True
            elif signal == 'long' and position['side'] == 'short':
                should_close = True
            elif signal == 'short' and position['side'] == 'long':
                should_close = True

            if should_close:
                # Calculate P&L
                if position['side'] == 'long':
                    pnl = (execution_price - position['entry_price']) * position['size']
                else:  # short
                    pnl = (position['entry_price'] - execution_price) * position['size']

                # Deduct exit commission
                exit_commission = abs(position['size'] * execution_price) * commission_rate

                net_pnl = pnl - position['entry_commission'] - exit_commission

                trades.append({
                    'entry_time': position['entry_time'],
                    'exit_time': current_time,
                    'entry_price': position['entry_price'],
                    'exit_price': execution_price,
                    'size': position['size'],
                    'side': position['side'],
                    'pnl': net_pnl,
                    'commission': position['entry_commission'] + exit_commission,
                })

                current_equity += net_pnl
                position = None

        # Open new position on 'long' or 'short' signal (if flat)
        if position is None and signal in ('long', 'short'):
            # Calculate position size based on current equity
            trade_value = current_equity * position_size_frac
            size = trade_value / execution_price

            # Deduct entry commission (stored, applied on close)
            entry_commission = abs(size * execution_price) * commission_rate

            position = {
                'side': signal,
                'entry_price': execution_price,
                'entry_time': current_time,
                'size': size,
                'entry_commission': entry_commission,
            }

        # Track equity after each bar
        # If in position, mark-to-market using current bar's close
        if position is not None:
            close_price = df.iloc[i]['close']
            if position['side'] == 'long':
                unrealized = (close_price - position['entry_price']) * position['size']
            else:
                unrealized = (position['entry_price'] - close_price) * position['size']
            equity.append(current_equity + unrealized - position['entry_commission'])
        else:
            equity.append(current_equity)

    # Close any remaining position at last bar's close
    if position is not None:
        final_price = df.iloc[-1]['close']
        if position['side'] == 'long':
            pnl = (final_price - position['entry_price']) * position['size']
        else:
            pnl = (position['entry_price'] - final_price) * position['size']

        exit_commission = abs(position['size'] * final_price) * commission_rate
        net_pnl = pnl - position['entry_commission'] - exit_commission

        trades.append({
            'entry_time': position['entry_time'],
            'exit_time': df.index[-1],
            'entry_price': position['entry_price'],
            'exit_price': final_price,
            'size': position['size'],
            'side': position['side'],
            'pnl': net_pnl,
            'commission': position['entry_commission'] + exit_commission,
        })
        equity[-1] = current_equity + net_pnl

    return compute_all_metrics(
        trades=trades,
        equity_curve=np.array(equity),
        trading_days=trading_days,
    )


def save_iteration_artifacts(results: dict, params: dict, iteration: int, output_dir: str):
    """
    Save backtest iteration artifacts to disk.

    Creates two files per iteration:
      - iter_{N}_params.json: The parameters used for this iteration
      - iter_{N}_metrics.json: The computed metrics from compute_all_metrics()

    Args:
        results:   Output dict from run_backtest() / compute_all_metrics().
        params:    The parameter dict used for this iteration.
        iteration: Iteration number (1-indexed).
        output_dir: Directory to save artifacts into.
    """
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    # Save parameters
    params_file = output_path / f"iter_{iteration:02d}_params.json"
    # Convert any non-serializable values
    serializable_params = {}
    for k, v in params.items():
        if isinstance(v, (int, float, str, bool, list, dict, type(None))):
            serializable_params[k] = v
        else:
            serializable_params[k] = str(v)

    with open(params_file, 'w') as f:
        json.dump(serializable_params, f, indent=2)

    # Save metrics (exclude non-serializable items like full equity curve)
    metrics_file = output_path / f"iter_{iteration:02d}_metrics.json"
    serializable_metrics = {}
    for k, v in results.items():
        if isinstance(v, (int, float, str, bool, type(None))):
            serializable_metrics[k] = v
        elif isinstance(v, (list, dict)):
            serializable_metrics[k] = v
        elif isinstance(v, np.ndarray):
            serializable_metrics[k] = v.tolist()
        elif isinstance(v, (np.integer,)):
            serializable_metrics[k] = int(v)
        elif isinstance(v, (np.floating,)):
            serializable_metrics[k] = float(v)
        # Skip non-serializable items silently

    with open(metrics_file, 'w') as f:
        json.dump(serializable_metrics, f, indent=2, default=str)
