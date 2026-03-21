# Backtest Engine Pattern Guide

> This document defines the rules and patterns for Claude-generated backtest code.
> Read this BEFORE writing any backtest logic. Violations of these rules produce
> invalid results that cannot be recovered -- all backtests must be re-run.

## Anti-Lookahead Rules

Lookahead bias is the #1 risk in algorithmic backtesting. It occurs when the
backtest uses information that would not have been available at the time of the
trading decision. **Any backtest with lookahead bias produces meaningless results.**

### Rule 1: Signal sees only past and current bar

```python
# CORRECT -- signal sees bars 0 through i (inclusive)
history = df.iloc[:i + 1]
signal = calculate_signal(history, params)

# WRONG -- signal sees the entire dataset
signal = calculate_signal(df, params)  # LOOKAHEAD!

# WRONG -- signal sees one bar ahead
history = df.iloc[:i + 2]  # LOOKAHEAD!
signal = calculate_signal(history, params)
```

The `calculate_signal()` function receives a DataFrame slice containing only
bars from the start of the dataset up to and including the current bar. It
must not access any global DataFrames or external data sources.

### Rule 2: Execution at next bar's open price

```python
# CORRECT -- trade executes at the open of bar i (signal was from bar i-1)
execution_price = df.iloc[i]['open']

# WRONG -- executing at the close of the bar where signal was generated
execution_price = df.iloc[i-1]['close']  # LOOKAHEAD! Can't act on close you just saw

# WRONG -- using the current bar's close for execution
execution_price = df.iloc[i]['close']  # LOOKAHEAD! Close isn't known until bar ends
```

The real-world sequence is:
1. Bar N closes -> you see the close price
2. You generate a signal based on bar N's data
3. You place an order
4. The order fills at bar N+1's open price

### Rule 3: No future data in indicator calculations

```python
# CORRECT -- rolling calculation on the history slice
sma = history['close'].rolling(20).mean().iloc[-1]

# WRONG -- normalizing with full dataset min/max
normalized = (df['close'] - df['close'].min()) / (df['close'].max() - df['close'].min())  # LOOKAHEAD!

# WRONG -- using shift(-1) to look forward
df['next_close'] = df['close'].shift(-1)  # LOOKAHEAD!

# WRONG -- computing Z-score over entire dataset
z_score = (df['close'] - df['close'].mean()) / df['close'].std()  # LOOKAHEAD!
```

All indicators must be computed on the `history` slice (data up to current bar),
not on the full DataFrame.

### Timing Diagram

```
Bar:    |  N-2  |  N-1  |   N   |  N+1  |  N+2  |
        |-------|-------|-------|-------|-------|
Signal:           ^--- signal generated here (using data up to N-1)
Execution:                 ^--- order fills at N's open
```

When the loop is at index `i`:
- `history = df.iloc[:i+1]` provides data up to bar i
- `signal = calculate_signal(history, params)` generates signal
- `execution_price = df.iloc[i]['open']` is where the trade fills
- This means the signal effectively uses data through bar i-1's close,
  and the trade fills at bar i's open (the next available price)

## Position Management Patterns

### Long-Only Strategy

```python
def calculate_signal(history, params):
    # ... compute indicators on history ...
    if entry_condition:
        return 'long'
    elif exit_condition:
        return 'close'
    return 'hold'
```

### Short-Only Strategy

```python
def calculate_signal(history, params):
    # ... compute indicators on history ...
    if entry_condition:
        return 'short'
    elif exit_condition:
        return 'close'
    return 'hold'
```

### Long-Short Strategy

```python
def calculate_signal(history, params):
    # ... compute indicators on history ...
    if long_condition:
        return 'long'    # Opens long OR closes short and opens long
    elif short_condition:
        return 'short'   # Opens short OR closes long and opens short
    elif flat_condition:
        return 'close'
    return 'hold'
```

The engine handles position flipping automatically: if you return 'long' while
in a short position, the engine closes the short first, then opens the long.

## Commission Modeling

The engine supports percentage-based commission as a fraction of trade value:

```python
params = {
    'commission': 0.001,  # 0.1% per trade (applied on entry AND exit)
}
```

Default commission rates by asset class:
- **Crypto:** 0.001 (0.1%) -- typical exchange taker fee
- **US Stocks:** 0.0001 (0.01%) -- most brokers are near-zero
- **Forex:** 0.00005 (0.005%) -- spread cost approximation

Commission is deducted from each trade's P&L. Both entry and exit commissions
are tracked and reported in the trade log.

## What Claude MUST NOT Modify

The following parts of `backtest_engine.py` are fixed infrastructure:

1. **The event loop structure** -- `for i in range(1, len(df)):` with history slicing
2. **Position management logic** -- open/close/flip logic in `run_backtest()`
3. **Equity tracking** -- mark-to-market and commission deduction
4. **Metrics integration** -- `compute_all_metrics()` call at the end
5. **Artifact saving** -- `save_iteration_artifacts()` function

## What Claude Fills In

Claude replaces ONLY the `calculate_signal()` function body:

1. Compute indicators from `history` DataFrame
2. Apply entry/exit logic using those indicators
3. Return one of: 'long', 'short', 'close', 'hold'

Everything else remains untouched.

## Common Mistakes

### Mistake 1: Using close price for execution

```python
# WRONG
execution_price = df.iloc[i]['close']
```

You cannot know the close price until the bar is complete. By then, you cannot
execute at that price. Always use the next bar's open.

### Mistake 2: Forward-looking in signal function

```python
# WRONG -- accessing future index
def calculate_signal(history, params):
    future_close = df.iloc[len(history) + 1]['close']  # LOOKAHEAD!
```

### Mistake 3: Using .shift(-1) for signal generation

```python
# WRONG -- shift(-1) pulls future values into current row
df['signal'] = df['close'].shift(-1) > df['close']  # LOOKAHEAD!
```

### Mistake 4: Vectorized operations on full DataFrame

```python
# WRONG -- computing signals for all bars at once using full dataset
df['sma'] = df['close'].rolling(20).mean()
df['signal'] = df['close'] > df['sma']
# This is fine for the indicator, but the normalization/z-score variants
# that use the full series stats are NOT fine.
```

### Mistake 5: Computing indicators inside the loop on full df

```python
# WRONG -- passing the full df instead of the history slice
for i in range(1, len(df)):
    sma = df['close'].rolling(20).mean().iloc[i]  # Uses all data for rolling!
    # The rolling itself is fine, but other operations on full df are not
```

Always compute indicators on `history = df.iloc[:i+1]`, never on `df`.

### Mistake 6: Not accounting for existing position

```python
# WRONG -- opening a new position while already in one
# The engine handles this, but your signal should be aware:
# Returning 'long' when already long = no action (engine ignores duplicate)
# Returning 'long' when short = engine closes short THEN opens long
```

---

*This guide is authoritative. If the generated backtest code violates any rule
above, the backtest results are invalid and must be discarded.*
