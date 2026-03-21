"""
Data source adapters -- ready-to-use, tested.
Claude calls these functions, does not rewrite them.

Usage:
    from data_sources import load_ccxt, load_yfinance, load_csv
    df = load_yfinance('AAPL', '2020-01-01', '2024-01-01', '1d')
"""
import pandas as pd
import numpy as np
import logging
from pathlib import Path

logger = logging.getLogger(__name__)


def validate_ohlcv(df: pd.DataFrame, source: str = "unknown") -> pd.DataFrame:
    """
    Validate and clean an OHLCV DataFrame.

    Checks for:
    - NaN values (logs warning, drops rows)
    - Duplicate timestamps (drops duplicates, keeps first)
    - Ascending sort by timestamp
    - Numeric types for OHLCV columns

    Args:
        df:     DataFrame with DatetimeIndex and columns: open, high, low, close, volume.
        source: Name of the data source (for log messages).

    Returns:
        Cleaned DataFrame with valid OHLCV data.

    Raises:
        ValueError: If required columns are missing or DataFrame is empty after cleaning.
    """
    required_columns = ['open', 'high', 'low', 'close']

    # Check required columns exist
    missing = [c for c in required_columns if c not in df.columns]
    if missing:
        raise ValueError(
            f"[{source}] Missing required columns: {missing}. "
            f"Available columns: {list(df.columns)}"
        )

    # Ensure OHLCV columns are numeric
    for col in required_columns + (['volume'] if 'volume' in df.columns else []):
        if not pd.api.types.is_numeric_dtype(df[col]):
            logger.warning(f"[{source}] Column '{col}' is not numeric. Attempting conversion.")
            df[col] = pd.to_numeric(df[col], errors='coerce')

    # Check for NaN values in OHLCV
    ohlcv_cols = [c for c in required_columns + ['volume'] if c in df.columns]
    nan_count = df[ohlcv_cols].isna().sum().sum()
    if nan_count > 0:
        nan_rows = df[ohlcv_cols].isna().any(axis=1).sum()
        logger.warning(
            f"[{source}] Found {nan_count} NaN values across {nan_rows} rows. "
            f"Dropping affected rows."
        )
        df = df.dropna(subset=ohlcv_cols)

    # Check for duplicate timestamps
    if df.index.duplicated().any():
        dup_count = df.index.duplicated().sum()
        logger.warning(
            f"[{source}] Found {dup_count} duplicate timestamps. Keeping first occurrence."
        )
        df = df[~df.index.duplicated(keep='first')]

    # Ensure ascending sort
    if not df.index.is_monotonic_increasing:
        logger.warning(f"[{source}] Data not sorted ascending by timestamp. Sorting.")
        df = df.sort_index()

    # Final check -- not empty
    if len(df) == 0:
        raise ValueError(f"[{source}] DataFrame is empty after cleaning.")

    logger.info(f"[{source}] Validated: {len(df)} rows, {df.index[0]} to {df.index[-1]}")
    return df


def load_ccxt(
    exchange: str,
    symbol: str,
    timeframe: str,
    since: str,
    limit: int = 1000,
) -> pd.DataFrame:
    """
    Fetch OHLCV data from a cryptocurrency exchange via ccxt.

    Handles pagination automatically for requests larger than the exchange's
    per-call limit (typically ~1000 candles).

    Args:
        exchange:  Exchange name (e.g., 'binance', 'coinbase', 'kraken').
        symbol:    Trading pair (e.g., 'BTC/USDT', 'ETH/BTC').
        timeframe: Candle timeframe (e.g., '1m', '5m', '1h', '4h', '1d').
        since:     Start date as ISO string (e.g., '2023-01-01').
        limit:     Maximum number of candles to fetch. Default 1000.
                   Set higher to auto-paginate.

    Returns:
        DataFrame with DatetimeIndex and columns: open, high, low, close, volume.

    Raises:
        ImportError: If ccxt is not installed.
        ValueError: If exchange or symbol is not found, or data is empty.
    """
    try:
        import ccxt
    except ImportError:
        raise ImportError(
            "ccxt is not installed. Run: pip install ccxt\n"
            "Or use the PMF venv: ~/.pmf/venv/bin/pip install ccxt"
        )

    # Initialize exchange
    exchange_id = exchange.lower()
    if exchange_id not in ccxt.exchanges:
        raise ValueError(
            f"Exchange '{exchange}' not found in ccxt. "
            f"Available exchanges include: {', '.join(sorted(ccxt.exchanges)[:10])}..."
        )

    exchange_class = getattr(ccxt, exchange_id)
    ex = exchange_class({'enableRateLimit': True})

    # Load markets to validate symbol
    try:
        ex.load_markets()
    except Exception as e:
        raise ValueError(f"Failed to load markets from {exchange}: {e}")

    if symbol not in ex.symbols:
        raise ValueError(
            f"Symbol '{symbol}' not found on {exchange}. "
            f"Available symbols include: {', '.join(sorted(ex.symbols)[:10])}..."
        )

    # Parse since date to millisecond timestamp
    since_ms = int(pd.Timestamp(since).timestamp() * 1000)

    # Paginate: fetch in chunks
    all_candles = []
    fetched = 0
    current_since = since_ms
    per_call = min(limit, 1000)

    while fetched < limit:
        try:
            batch_limit = min(per_call, limit - fetched)
            candles = ex.fetch_ohlcv(symbol, timeframe, since=current_since, limit=batch_limit)
        except ccxt.RateLimitExceeded:
            logger.warning(f"[ccxt:{exchange}] Rate limited. Waiting and retrying...")
            import time
            time.sleep(ex.rateLimit / 1000)
            continue
        except Exception as e:
            raise ValueError(f"[ccxt:{exchange}] Failed to fetch OHLCV: {e}")

        if not candles:
            break

        all_candles.extend(candles)
        fetched += len(candles)

        if len(candles) < batch_limit:
            break  # No more data available

        # Move since to after the last candle
        current_since = candles[-1][0] + 1

    if not all_candles:
        raise ValueError(
            f"[ccxt:{exchange}] No data returned for {symbol} {timeframe} since {since}."
        )

    # Convert to DataFrame
    df = pd.DataFrame(all_candles, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
    df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
    df = df.set_index('timestamp')

    return validate_ohlcv(df, source=f"ccxt:{exchange}:{symbol}")


def load_yfinance(
    ticker: str,
    start: str,
    end: str,
    interval: str = '1d',
) -> pd.DataFrame:
    """
    Fetch OHLCV data from Yahoo Finance via yfinance.

    Args:
        ticker:   Ticker symbol (e.g., 'AAPL', 'MSFT', 'BTC-USD', 'EURUSD=X').
        start:    Start date as ISO string (e.g., '2020-01-01').
        end:      End date as ISO string (e.g., '2024-01-01').
        interval: Data interval. One of: '1m', '2m', '5m', '15m', '30m',
                  '60m', '90m', '1h', '1d', '5d', '1wk', '1mo', '3mo'.
                  Intraday intervals limited to last 60-730 days by Yahoo.

    Returns:
        DataFrame with DatetimeIndex and columns: open, high, low, close, volume.

    Raises:
        ImportError: If yfinance is not installed.
        ValueError: If ticker not found, date range invalid, or data is empty.
    """
    try:
        import yfinance as yf
    except ImportError:
        raise ImportError(
            "yfinance is not installed. Run: pip install yfinance\n"
            "Or use the PMF venv: ~/.pmf/venv/bin/pip install yfinance"
        )

    logger.info(f"[yfinance] Fetching {ticker} {interval} from {start} to {end}")

    try:
        data = yf.download(
            ticker,
            start=start,
            end=end,
            interval=interval,
            auto_adjust=True,
            progress=False,
        )
    except Exception as e:
        raise ValueError(f"[yfinance] Failed to download {ticker}: {e}")

    if data is None or len(data) == 0:
        raise ValueError(
            f"[yfinance] No data returned for {ticker} from {start} to {end} "
            f"with interval {interval}. Check that the ticker exists and the "
            f"date range is valid (intraday data limited to recent history)."
        )

    # Rename columns to lowercase
    data.columns = [c.lower() for c in data.columns]

    # Handle multi-level columns from yfinance (when downloading single ticker)
    if isinstance(data.columns, pd.MultiIndex):
        data.columns = data.columns.get_level_values(0)
        data.columns = [c.lower() for c in data.columns]

    # Keep only OHLCV columns
    keep_cols = ['open', 'high', 'low', 'close', 'volume']
    available = [c for c in keep_cols if c in data.columns]
    data = data[available]

    # Name the index for consistency
    data.index.name = 'timestamp'

    return validate_ohlcv(data, source=f"yfinance:{ticker}")


def load_csv(
    filepath: str,
    date_column: str = 'date',
    date_format: str = None,
) -> pd.DataFrame:
    """
    Load OHLCV data from a CSV file.

    Args:
        filepath:    Path to CSV file.
        date_column: Name of the date/timestamp column. Default 'date'.
                     Case-insensitive matching is attempted.
        date_format: Optional strftime format string for date parsing
                     (e.g., '%Y-%m-%d %H:%M:%S'). If None, pandas infers.

    Returns:
        DataFrame with DatetimeIndex and columns: open, high, low, close, volume.

    Raises:
        FileNotFoundError: If the CSV file does not exist.
        ValueError: If required columns are missing or data is empty.
    """
    path = Path(filepath)
    if not path.exists():
        raise FileNotFoundError(
            f"CSV file not found: {filepath}\n"
            f"Checked absolute path: {path.resolve()}"
        )

    logger.info(f"[csv] Loading {filepath}")

    df = pd.read_csv(filepath)

    # Normalize all column names to lowercase
    df.columns = [c.strip().lower() for c in df.columns]

    # Find the date column (case-insensitive)
    date_col_lower = date_column.lower()
    date_col_actual = None
    for col in df.columns:
        if col == date_col_lower:
            date_col_actual = col
            break

    # Try common date column names if specified one not found
    if date_col_actual is None:
        for candidate in ['date', 'datetime', 'timestamp', 'time']:
            if candidate in df.columns:
                date_col_actual = candidate
                logger.warning(
                    f"[csv] Column '{date_column}' not found. "
                    f"Using '{candidate}' instead."
                )
                break

    if date_col_actual is None:
        raise ValueError(
            f"[csv] Date column '{date_column}' not found. "
            f"Available columns: {list(df.columns)}. "
            f"Specify the correct column name with date_column parameter."
        )

    # Parse dates and set as index
    if date_format:
        df[date_col_actual] = pd.to_datetime(df[date_col_actual], format=date_format)
    else:
        df[date_col_actual] = pd.to_datetime(df[date_col_actual], infer_datetime_format=True)

    df = df.set_index(date_col_actual)
    df.index.name = 'timestamp'

    return validate_ohlcv(df, source=f"csv:{Path(filepath).name}")
