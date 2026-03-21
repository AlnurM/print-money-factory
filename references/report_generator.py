"""Report generator for /brrr:verify -- reads execute-phase artifacts,
computes regime/benchmark analytics, renders standalone HTML report.

This is a REFERENCE file (like metrics.py, backtest_engine.py) that gets
copied to ~/.pmf/ during install. It is imported and called by the verify
workflow's Python script.

Usage:
    from report_generator import generate_report
    generate_report(phase_dir, strategy_name, targets, output_path, template_path)
"""

import json
import glob
import os
import sys
import re
from pathlib import Path

import pandas as pd
import numpy as np
from jinja2 import Template

try:
    import plotly.graph_objects as go
except ImportError:
    go = None

try:
    from scipy.stats import linregress
except ImportError:
    linregress = None

try:
    import ta
except ImportError:
    ta = None


# ---------------------------------------------------------------------------
# JSON serialization safety
# ---------------------------------------------------------------------------

def sanitize_for_json(obj):
    """Recursively convert numpy types to native Python types."""
    if isinstance(obj, dict):
        return {k: sanitize_for_json(v) for k, v in obj.items()}
    elif isinstance(obj, (list, tuple)):
        return [sanitize_for_json(item) for item in obj]
    elif isinstance(obj, np.integer):
        return int(obj)
    elif isinstance(obj, np.floating):
        return float(obj)
    elif isinstance(obj, np.ndarray):
        return obj.tolist()
    elif isinstance(obj, np.bool_):
        return bool(obj)
    elif isinstance(obj, (pd.Timestamp,)):
        return obj.isoformat()
    return obj


# ---------------------------------------------------------------------------
# Data loading
# ---------------------------------------------------------------------------

def load_iteration_artifacts(phase_dir, phase_num=None):
    """Load all iteration artifacts from a phase execute directory.

    Args:
        phase_dir: Path to .pmf/phases/ (contains phase_N_execute/ subdirs).
        phase_num: Phase number. If None, auto-detect from directory contents.

    Returns:
        List of iteration dicts sorted by iteration number.

    Raises:
        ValueError: If no iteration artifacts found.
    """
    phase_dir = Path(phase_dir)

    # Auto-detect phase number if not provided
    if phase_num is None:
        exec_dirs = sorted(phase_dir.glob('phase_*_execute'))
        if not exec_dirs:
            raise ValueError(
                "No iteration artifacts found in .pmf/phases/. "
                "Run /brrr:execute first."
            )
        # Extract phase number from first execute dir
        match = re.search(r'phase_(\d+)_execute', exec_dirs[-1].name)
        if match:
            phase_num = int(match.group(1))
        else:
            raise ValueError(
                "No iteration artifacts found in .pmf/phases/. "
                "Run /brrr:execute first."
            )

    exec_dir = phase_dir / f'phase_{phase_num}_execute'
    if not exec_dir.exists():
        raise ValueError(
            "No iteration artifacts found in .pmf/phases/. "
            "Run /brrr:execute first."
        )

    # Load verdict files (primary) or fall back to params+metrics files
    verdict_files = sorted(exec_dir.glob('iter_*_verdict.json'))
    iterations = []

    if verdict_files:
        for vf in verdict_files:
            with open(vf) as f:
                verdict = json.load(f)

            iter_num = verdict.get('iteration', 0)
            if iter_num == 0:
                # Extract from filename
                match = re.search(r'iter_(\d+)_', vf.name)
                if match:
                    iter_num = int(match.group(1))

            # Try to load OOS metrics
            oos_file = exec_dir / f'iter_{iter_num:02d}_oos_metrics.json'
            oos_metrics = {}
            if oos_file.exists():
                with open(oos_file) as f:
                    oos_metrics = json.load(f)

            iterations.append({
                'iteration': iter_num,
                'params': verdict.get('params', {}),
                'metrics': verdict.get('metrics', {}),
                'oos_metrics': oos_metrics,
                'hypothesis': verdict.get('hypothesis', ''),
                'verdict': verdict.get('verdict', 'exploring'),
            })
    else:
        # Fallback: load params + metrics files
        param_files = sorted(exec_dir.glob('iter_*_params.json'))
        if not param_files:
            raise ValueError(
                "No iteration artifacts found in .pmf/phases/. "
                "Run /brrr:execute first."
            )

        for pf in param_files:
            match = re.search(r'iter_(\d+)_', pf.name)
            if not match:
                continue
            iter_num = int(match.group(1))

            with open(pf) as f:
                params = json.load(f)

            metrics_file = exec_dir / f'iter_{iter_num:02d}_metrics.json'
            metrics = {}
            if metrics_file.exists():
                with open(metrics_file) as f:
                    metrics = json.load(f)

            iterations.append({
                'iteration': iter_num,
                'params': params,
                'metrics': metrics,
                'oos_metrics': {},
                'hypothesis': '',
                'verdict': 'exploring',
            })

    if not iterations:
        raise ValueError(
            "No iteration artifacts found in .pmf/phases/. "
            "Run /brrr:execute first."
        )

    iterations.sort(key=lambda x: x['iteration'])
    return iterations


def load_best_result(phase_dir, phase_num):
    """Load best result JSON from phase directory.

    Args:
        phase_dir: Path to .pmf/phases/.
        phase_num: Phase number.

    Returns:
        Dict with best_params, is_metrics, oos_metrics, stop_reason.
        Returns None if file not found.
    """
    best_file = Path(phase_dir) / f'phase_{phase_num}_best_result.json'
    if not best_file.exists():
        return None

    with open(best_file) as f:
        return json.load(f)


# ---------------------------------------------------------------------------
# Analytics computation
# ---------------------------------------------------------------------------

def compute_equity_curve(best_result, ohlcv_df=None, initial_capital=10000.0):
    """Compute equity and buy-hold curves from best result metrics.

    If ohlcv_df is provided, computes buy & hold from close prices.
    Otherwise returns only strategy equity from metrics.

    Returns:
        Tuple of (equity_dict, buyhold_dict) where each is
        {'x': [dates], 'y': [values]} or None for buyhold if no ohlcv.
    """
    is_metrics = best_result.get('is_metrics', {})

    # If we have OHLCV data, compute buy & hold
    buyhold = None
    if ohlcv_df is not None and len(ohlcv_df) > 0:
        close = ohlcv_df['close'].values
        bh_equity = initial_capital * (close / close[0])
        dates = [d.isoformat() if hasattr(d, 'isoformat') else str(d)
                 for d in ohlcv_df.index]
        buyhold = {
            'x': dates,
            'y': bh_equity.tolist(),
        }

    # For strategy equity, we use a simple approximation from net_pnl
    # In production, the verify workflow would re-run the backtest
    # and capture the bar-level equity; here we provide a fallback
    net = is_metrics.get('net_pnl', 0)
    trade_count = is_metrics.get('trade_count', is_metrics.get('total_trades', 0))

    if ohlcv_df is not None and len(ohlcv_df) > 0:
        # Distribute equity growth linearly across bars as a placeholder
        n_bars = len(ohlcv_df)
        equity_values = np.linspace(initial_capital, initial_capital + net, n_bars)
        dates = [d.isoformat() if hasattr(d, 'isoformat') else str(d)
                 for d in ohlcv_df.index]
        equity = {
            'x': dates,
            'y': equity_values.tolist(),
        }
    else:
        # Minimal 2-point equity curve
        equity = {
            'x': ['start', 'end'],
            'y': [initial_capital, initial_capital + net],
        }

    return equity, buyhold


def compute_drawdown_series(equity_values):
    """Compute drawdown series from equity values.

    Args:
        equity_values: List or array of equity values.

    Returns:
        Tuple of (drawdown_values_list, max_drawdown_pct).
        drawdown_values are negative percentages.
    """
    eq = np.array(equity_values, dtype=float)
    running_max = np.maximum.accumulate(eq)

    # Avoid division by zero
    with np.errstate(divide='ignore', invalid='ignore'):
        drawdown = np.where(running_max > 0, (eq - running_max) / running_max * 100, 0.0)

    max_dd_pct = float(np.min(drawdown))
    return drawdown.tolist(), max_dd_pct


def classify_regimes(ohlcv_df, sma_period=50, adx_period=14, adx_threshold=25):
    """Classify each bar as bull, bear, or sideways using SMA slope + ADX.

    Per D-03: SMA slope + ADX classification.
    - Bull: SMA slope > 0 AND ADX > threshold
    - Bear: SMA slope < 0 AND ADX > threshold
    - Sideways: ADX <= threshold

    NaN warmup bars are filled with 'sideways' (per Research pitfall 4).

    Args:
        ohlcv_df: DataFrame with 'close' column.
        sma_period: SMA lookback period.
        adx_period: ADX indicator period.
        adx_threshold: ADX threshold for trending vs sideways.

    Returns:
        pd.Series with values 'bull', 'bear', 'sideways'.
    """
    close = ohlcv_df['close']

    # SMA and its slope
    sma = close.rolling(window=sma_period).mean()
    sma_slope = sma.diff()

    # ADX using ta library
    if ta is not None:
        adx_indicator = ta.trend.ADXIndicator(
            high=ohlcv_df['high'],
            low=ohlcv_df['low'],
            close=ohlcv_df['close'],
            window=adx_period,
        )
        adx = adx_indicator.adx()
    else:
        # Fallback: use simple volatility proxy if ta not available
        adx = close.rolling(window=adx_period).std() / close * 100
        adx = adx.fillna(0)

    # Classify
    regimes = pd.Series('sideways', index=ohlcv_df.index)
    bull_mask = (sma_slope > 0) & (adx > adx_threshold)
    bear_mask = (sma_slope < 0) & (adx > adx_threshold)

    regimes[bull_mask] = 'bull'
    regimes[bear_mask] = 'bear'

    # Fill NaN (warmup bars) with 'sideways'
    regimes = regimes.fillna('sideways')

    return regimes


def compute_regime_stats(trades, regimes_series, ohlcv_df):
    """Compute per-regime statistics.

    Args:
        trades: List of trade dicts with entry_date and pnl.
        regimes_series: pd.Series from classify_regimes().
        ohlcv_df: DataFrame with DatetimeIndex.

    Returns:
        List of regime stat dicts with: name, bars, trades, win_rate,
        avg_pnl, total_pnl, contribution, color.
    """
    regime_colors = {
        'bull': '#16a34a',
        'bear': '#dc2626',
        'sideways': '#f59e0b',
    }

    # Count bars per regime
    regime_bar_counts = regimes_series.value_counts()

    # Assign each trade to a regime by entry date
    regime_trades = {'bull': [], 'bear': [], 'sideways': []}

    for trade in trades:
        entry_date = trade.get('entry_date', trade.get('entry_time', ''))
        if isinstance(entry_date, str):
            try:
                entry_date = pd.Timestamp(entry_date)
            except (ValueError, TypeError):
                continue

        # Find the closest date in the regime series
        if entry_date in regimes_series.index:
            regime = regimes_series[entry_date]
        else:
            # Find nearest date
            try:
                idx = regimes_series.index.get_indexer([entry_date], method='nearest')[0]
                if idx >= 0:
                    regime = regimes_series.iloc[idx]
                else:
                    regime = 'sideways'
            except (KeyError, IndexError):
                regime = 'sideways'

        if regime in regime_trades:
            regime_trades[regime].append(trade)

    # Total PnL across all trades for contribution calculation
    total_pnl_all = sum(t.get('pnl', 0) for t in trades) if trades else 1.0
    if total_pnl_all == 0:
        total_pnl_all = 1.0  # Avoid division by zero

    result = []
    for regime_name in ['bull', 'bear', 'sideways']:
        r_trades = regime_trades.get(regime_name, [])
        n_trades = len(r_trades)
        bars = int(regime_bar_counts.get(regime_name, 0))

        if n_trades > 0:
            pnls = [t.get('pnl', 0) for t in r_trades]
            wins = sum(1 for p in pnls if p > 0)
            wr = f"{wins / n_trades * 100:.1f}%"
            avg = sum(pnls) / n_trades
            total = sum(pnls)
            contrib = total / abs(total_pnl_all) * 100
        else:
            wr = "0.0%"
            avg = 0.0
            total = 0.0
            contrib = 0.0

        result.append({
            'name': regime_name.capitalize(),
            'bars': bars,
            'trades': n_trades,
            'win_rate': wr,
            'avg_pnl': f"${avg:,.2f}",
            'total_pnl': f"${total:,.2f}",
            'contribution': f"{contrib:.1f}%",
            'color': regime_colors.get(regime_name, '#333333'),
        })

    return result


def compute_benchmark_stats(strategy_equity, buyhold_equity):
    """Compute alpha, beta, R-squared from strategy vs buy-and-hold.

    Args:
        strategy_equity: Array of strategy equity values.
        buyhold_equity: Array of buy-and-hold equity values.

    Returns:
        Dict with alpha (annualized), beta, r_squared.
    """
    strat_eq = np.array(strategy_equity, dtype=float)
    bh_eq = np.array(buyhold_equity, dtype=float)

    # Compute daily returns
    strat_returns = np.diff(strat_eq) / strat_eq[:-1]
    bh_returns = np.diff(bh_eq) / bh_eq[:-1]

    # Ensure same length
    min_len = min(len(strat_returns), len(bh_returns))
    strat_returns = strat_returns[:min_len]
    bh_returns = bh_returns[:min_len]

    if linregress is not None and len(strat_returns) > 1:
        result = linregress(bh_returns, strat_returns)
        alpha = float(result.intercept * 252)  # Annualize
        beta = float(result.slope)
        r_squared = float(result.rvalue ** 2)
    else:
        # Fallback: simple correlation-based estimate
        if len(strat_returns) > 1:
            corr = np.corrcoef(strat_returns, bh_returns)[0, 1]
            beta = corr * (np.std(strat_returns) / max(np.std(bh_returns), 1e-12))
            alpha = float((np.mean(strat_returns) - beta * np.mean(bh_returns)) * 252)
            r_squared = float(corr ** 2)
        else:
            alpha = 0.0
            beta = 1.0
            r_squared = 0.0

    return {
        'alpha': alpha,
        'beta': beta,
        'r_squared': r_squared,
    }


# ---------------------------------------------------------------------------
# Data formatting helpers
# ---------------------------------------------------------------------------

def format_metrics_cards(metrics, targets):
    """Format metrics for display as cards with color coding.

    Args:
        metrics: Dict of metric_name -> value.
        targets: Dict of metric_name -> target_value.

    Returns:
        List of card dicts: {label, value, color}.
    """
    # Define label mapping and formatting rules
    formats = {
        'sharpe_ratio': ('SHARPE RATIO', lambda v: f"{v:.2f}"),
        'sortino_ratio': ('SORTINO RATIO', lambda v: f"{v:.2f}"),
        'calmar_ratio': ('CALMAR RATIO', lambda v: f"{v:.2f}"),
        'max_drawdown': ('MAX DRAWDOWN', lambda v: f"{v * 100:.1f}%"),
        'win_rate': ('WIN RATE', lambda v: f"{v * 100:.1f}%"),
        'profit_factor': ('PROFIT FACTOR', lambda v: f"{v:.2f}"),
        'total_trades': ('TOTAL TRADES', lambda v: f"{int(v)}"),
        'trade_count': ('TOTAL TRADES', lambda v: f"{int(v)}"),
        'net_pnl': ('NET P&L', lambda v: f"+${v:,.0f}" if v >= 0 else f"-${abs(v):,.0f}"),
        'expectancy': ('EXPECTANCY', lambda v: f"${v:,.2f}"),
    }

    # Higher-is-better metrics vs lower-is-better
    # For max_drawdown, the target is a threshold (e.g. -0.15 means dd must be >= -0.15, i.e. less negative)
    higher_is_better = {
        'sharpe_ratio', 'sortino_ratio', 'calmar_ratio', 'win_rate',
        'profit_factor', 'total_trades', 'trade_count', 'net_pnl', 'expectancy',
    }

    cards = []
    for key, value in metrics.items():
        if key not in formats:
            continue

        label, fmt_fn = formats[key]

        # Skip duplicate total_trades / trade_count
        existing_labels = [c['label'] for c in cards]
        if label in existing_labels:
            continue

        try:
            formatted = fmt_fn(value)
        except (TypeError, ValueError):
            formatted = str(value)

        # Determine color based on target
        color = '#333333'  # default: no target
        if key in targets:
            target = targets[key]
            if key in higher_is_better:
                color = '#16a34a' if value >= target else '#dc2626'
            else:
                # Lower-is-better (e.g. max_drawdown: -0.10 is better than -0.15)
                # Target is like -0.15, value must be >= target (less negative)
                color = '#16a34a' if value >= target else '#dc2626'

        cards.append({
            'label': label,
            'value': formatted,
            'color': color,
        })

    return cards


def format_trades_table(trades):
    """Format trades for HTML table display.

    Sorts chronologically by entry date and adds formatted P&L strings.

    Args:
        trades: List of trade dicts.

    Returns:
        List of formatted trade dicts sorted by entry_date.
    """
    # Sort chronologically
    sorted_trades = sorted(trades, key=lambda t: str(t.get('entry_date', t.get('entry_time', ''))))

    result = []
    for i, trade in enumerate(sorted_trades, 1):
        pnl = trade.get('pnl', 0)
        pnl_pct = trade.get('pnl_pct', 0)

        # Format P&L
        if pnl >= 0:
            pnl_formatted = f"+${pnl:,.2f}"
        else:
            pnl_formatted = f"-${abs(pnl):,.2f}"

        if pnl_pct >= 0:
            pnl_pct_formatted = f"+{pnl_pct:.2f}%"
        else:
            pnl_pct_formatted = f"{pnl_pct:.2f}%"

        result.append({
            'number': i,
            'entry_date': trade.get('entry_date', trade.get('entry_time', '')),
            'exit_date': trade.get('exit_date', trade.get('exit_time', '')),
            'direction': trade.get('direction', trade.get('side', '')),
            'entry_price': trade.get('entry_price', ''),
            'exit_price': trade.get('exit_price', ''),
            'pnl': float(pnl),
            'pnl_pct': float(pnl_pct),
            'pnl_formatted': pnl_formatted,
            'pnl_pct_formatted': pnl_pct_formatted,
            'duration': trade.get('duration', ''),
        })

    return result


def format_iterations_table(iterations, best_iter_num=None):
    """Format iteration artifacts for HTML table display.

    Args:
        iterations: List of iteration dicts from load_iteration_artifacts.
        best_iter_num: Iteration number to mark as best.

    Returns:
        List of formatted iteration dicts.
    """
    result = []
    for it in iterations:
        iter_num = it.get('iteration', 0)
        params = it.get('params', {})
        metrics = it.get('metrics', {})
        oos = it.get('oos_metrics', {})

        # Compact params string
        params_str = ', '.join(f"{k}={v}" for k, v in params.items()
                              if k not in ('initial_capital', 'commission', 'position_size', 'trading_days'))

        sharpe_is = metrics.get('sharpe_ratio', '')
        if isinstance(sharpe_is, (int, float)):
            sharpe_is = f"{sharpe_is:.2f}"

        sharpe_oos = oos.get('sharpe_ratio', '')
        if isinstance(sharpe_oos, (int, float)):
            sharpe_oos = f"{sharpe_oos:.2f}"

        max_dd = metrics.get('max_drawdown', '')
        if isinstance(max_dd, (int, float)):
            max_dd = f"{max_dd * 100:.1f}%"

        trades_count = metrics.get('total_trades', metrics.get('trade_count', ''))

        result.append({
            'number': iter_num,
            'params': params_str,
            'sharpe_is': sharpe_is,
            'sharpe_oos': sharpe_oos,
            'max_dd': max_dd,
            'trades': trades_count,
            'verdict': it.get('verdict', 'exploring'),
            'is_best': iter_num == best_iter_num,
        })

    return result


def detect_grid_search(plan_path):
    """Detect if the optimization method was grid search.

    Args:
        plan_path: Path to phase plan file.

    Returns:
        Boolean indicating grid search was used.
    """
    if plan_path is None:
        return False

    plan_path = Path(plan_path)
    if not plan_path.exists():
        return False

    try:
        content = plan_path.read_text().lower()
        return 'grid' in content and 'search' in content
    except (OSError, IOError):
        return False


def build_heatmap_html(iterations, param_names=None):
    """Build a plotly heatmap HTML fragment for parameter sensitivity.

    Only called if grid search was detected.

    Args:
        iterations: List of iteration dicts.
        param_names: List of two parameter names for x/y axes.

    Returns:
        HTML string of the plotly heatmap, or empty string on error.
    """
    if go is None:
        return ''

    if not iterations or len(iterations) < 2:
        return ''

    # Auto-detect parameter names if not provided
    if param_names is None:
        all_params = set()
        for it in iterations:
            params = it.get('params', {})
            for k in params:
                if k not in ('initial_capital', 'commission', 'position_size', 'trading_days'):
                    all_params.add(k)
        param_names = sorted(all_params)[:2]

    if len(param_names) < 2:
        return ''

    p1, p2 = param_names[0], param_names[1]

    # Build 2D grid
    x_vals = sorted(set(it['params'].get(p1) for it in iterations if p1 in it.get('params', {})))
    y_vals = sorted(set(it['params'].get(p2) for it in iterations if p2 in it.get('params', {})))

    if not x_vals or not y_vals:
        return ''

    z = np.full((len(y_vals), len(x_vals)), np.nan)

    for it in iterations:
        params = it.get('params', {})
        metrics = it.get('metrics', {})
        if p1 in params and p2 in params:
            xi = x_vals.index(params[p1]) if params[p1] in x_vals else -1
            yi = y_vals.index(params[p2]) if params[p2] in y_vals else -1
            if xi >= 0 and yi >= 0:
                z[yi][xi] = metrics.get('sharpe_ratio', np.nan)

    fig = go.Figure(data=go.Heatmap(
        x=[str(v) for v in x_vals],
        y=[str(v) for v in y_vals],
        z=z.tolist(),
        colorscale='RdYlGn',
        colorbar=dict(title='Sharpe Ratio'),
        hovertemplate=f'{p1}: %{{x}}, {p2}: %{{y}}, Sharpe: %{{z:.2f}}<extra></extra>',
    ))

    fig.update_layout(
        margin=dict(t=10, r=30, b=40, l=60),
        xaxis_title=p1,
        yaxis_title=p2,
    )

    return fig.to_html(full_html=False, include_plotlyjs=False)


# ---------------------------------------------------------------------------
# Template rendering
# ---------------------------------------------------------------------------

def render_report(template_path, output_path, **data):
    """Render the HTML report template with provided data.

    Args:
        template_path: Path to report-template.html.
        output_path: Where to write the rendered HTML.
        **data: Template variables.

    Returns:
        output_path string.
    """
    template_text = Path(template_path).read_text()
    template = Template(template_text)

    # Sanitize all data for JSON safety
    safe_data = sanitize_for_json(data)

    rendered = template.render(**safe_data)
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    Path(output_path).write_text(rendered)

    return str(output_path)


# ---------------------------------------------------------------------------
# Main entry point
# ---------------------------------------------------------------------------

def generate_report(
    phase_dir,
    strategy_name,
    targets,
    output_path,
    template_path,
    cache_dir=None,
    plan_path=None,
    phase_num=None,
):
    """Generate the standalone HTML backtest report.

    Args:
        phase_dir: Path to .pmf/phases/ directory.
        strategy_name: Strategy name for report title.
        targets: Dict of target metrics (e.g., {"sharpe_ratio": 1.5}).
        output_path: Where to write the HTML file.
        template_path: Path to report-template.html.
        cache_dir: Path to .pmf/cache/ for OHLCV data (optional).
        plan_path: Path to phase plan file (optional, for grid search detection).
        phase_num: Phase number (optional, auto-detected if None).

    Returns:
        Output path string.

    Raises:
        ValueError: If no iteration artifacts found.
    """
    # Load iteration artifacts
    iterations = load_iteration_artifacts(phase_dir, phase_num)

    # Load best result
    if phase_num is None:
        # Re-detect phase number from iterations
        exec_dirs = sorted(Path(phase_dir).glob('phase_*_execute'))
        if exec_dirs:
            match = re.search(r'phase_(\d+)_execute', exec_dirs[-1].name)
            if match:
                phase_num = int(match.group(1))

    best_result = None
    if phase_num is not None:
        best_result = load_best_result(phase_dir, phase_num)

    if best_result is None:
        # Synthesize from best iteration
        best_iter = max(iterations, key=lambda x: x.get('metrics', {}).get('sharpe_ratio', -999))
        best_result = {
            'best_params': best_iter.get('params', {}),
            'is_metrics': best_iter.get('metrics', {}),
            'oos_metrics': best_iter.get('oos_metrics', {}),
            'stop_reason': best_iter.get('verdict', 'unknown'),
        }

    is_metrics = best_result.get('is_metrics', {})
    best_iter_num = None
    best_sharpe = -999
    for it in iterations:
        s = it.get('metrics', {}).get('sharpe_ratio', -999)
        if s > best_sharpe:
            best_sharpe = s
            best_iter_num = it.get('iteration')

    # Load OHLCV data if cache_dir provided
    ohlcv_df = None
    if cache_dir is not None:
        cache_path = Path(cache_dir)
        parquet_files = list(cache_path.glob('*.parquet'))
        if parquet_files:
            try:
                ohlcv_df = pd.read_parquet(parquet_files[0])
            except Exception:
                print(f"Warning: Cached data file not found at {parquet_files[0]}. "
                      "Regime breakdown and benchmark stats will be skipped.")

    # Compute equity curve and buy & hold
    equity_data, buyhold_data = compute_equity_curve(best_result, ohlcv_df)

    # Compute drawdown
    drawdown_values, max_dd_pct = compute_drawdown_series(equity_data['y'])
    drawdown_data = {
        'x': equity_data['x'],
        'y': drawdown_values,
    }

    # Format metrics cards
    metrics_cards = format_metrics_cards(is_metrics, targets or {})

    # Format iterations table
    iterations_table = format_iterations_table(iterations, best_iter_num)

    # Format trades table (extract from best result if available)
    trades_list = best_result.get('trades', [])
    trades_table = format_trades_table(trades_list)

    # Regime classification and stats (only if we have OHLCV data)
    has_regime_data = False
    regimes_data = []
    if ohlcv_df is not None and len(ohlcv_df) > 0:
        try:
            regimes = classify_regimes(ohlcv_df)
            regimes_data = compute_regime_stats(trades_list, regimes, ohlcv_df)
            has_regime_data = True
        except Exception as e:
            print(f"Warning: Regime classification failed: {e}")

    # Benchmark stats (only if we have buy & hold data)
    has_benchmark = False
    benchmark_cards = []
    if buyhold_data is not None and len(equity_data['y']) > 2:
        try:
            bench = compute_benchmark_stats(equity_data['y'], buyhold_data['y'])
            benchmark_cards = [
                {'label': 'ALPHA', 'value': f"{bench['alpha']:.2f}"},
                {'label': 'BETA', 'value': f"{bench['beta']:.2f}"},
                {'label': 'R-SQUARED', 'value': f"{bench['r_squared']:.2f}"},
            ]
            has_benchmark = True
        except Exception as e:
            print(f"Warning: Benchmark computation failed: {e}")

    # Parameter heatmap (only if grid search)
    has_heatmap = detect_grid_search(plan_path)
    heatmap_html = ''
    if has_heatmap and go is not None:
        heatmap_html = build_heatmap_html(iterations)
        if not heatmap_html:
            has_heatmap = False

    # Buyhold data default
    if buyhold_data is None:
        buyhold_data = {'x': [], 'y': []}

    # Render the report
    return render_report(
        template_path=template_path,
        output_path=output_path,
        title=f"{strategy_name}",
        metrics=metrics_cards,
        equity_data=json.dumps(sanitize_for_json(equity_data)),
        buyhold_data=json.dumps(sanitize_for_json(buyhold_data)),
        drawdown_data=json.dumps(sanitize_for_json(drawdown_data)),
        max_drawdown_pct=max_dd_pct,
        iterations=iterations_table,
        trades=trades_table,
        has_heatmap=has_heatmap,
        heatmap_chart_html=heatmap_html,
        has_regime_data=has_regime_data,
        regimes=regimes_data,
        has_benchmark=has_benchmark,
        benchmark_stats=benchmark_cards,
    )
