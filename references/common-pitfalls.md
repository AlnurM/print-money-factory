# Common Backtesting Pitfalls

> A catalog of known pitfalls in algorithmic trading backtests.
> Read this before designing or reviewing any backtest strategy.
> Each pitfall includes: what it is, an example of the mistake, how to detect it, and how to prevent it.

---

## 1. Lookahead Bias

**Description:**
The backtest uses information that would not have been available at the time of
the trading decision. This is the most dangerous pitfall because it produces
results that look excellent but are completely unreproducible in live trading.
Any backtest with lookahead bias is worthless.

**Example of the mistake:**
```python
# Computing a signal using the close price, then "executing" at that same close
df['signal'] = df['close'] > df['close'].rolling(20).mean()
df['entry_price'] = df['close']  # Can't execute at a price you just used to decide!
```

**How to detect it:**
- Sharpe ratio above 3.0 on any strategy (suspiciously high)
- Win rate above 70% on a trend-following strategy
- Equity curve with no significant drawdowns
- Strategy performs far better than published benchmarks for similar approaches
- Check that `calculate_signal()` only receives `history[:i+1]` (past + current bar)
- Check that execution uses next-bar open price, not current-bar close

**How to prevent it:**
- Use an event-loop architecture: process one bar at a time
- Signal function receives only data up to the current bar
- All trades execute at the NEXT bar's open price
- Never use `.shift(-1)` or access future indices in signal generation
- Compute all indicators on the history slice, not the full DataFrame

---

## 2. Survivorship Bias

**Description:**
Backtesting only on instruments (stocks, crypto tokens) that still exist today.
This ignores all the companies that went bankrupt, were delisted, or tokens that
went to zero during the backtest period. The result is an inflated performance
because you are only testing on "winners."

**Example of the mistake:**
```python
# Backtesting a stock-picking strategy on today's S&P 500 constituents
# over the last 20 years -- but the S&P 500 list has changed significantly
tickers = get_current_sp500_tickers()  # Missing all removed companies!
for ticker in tickers:
    backtest(ticker)
```

**How to detect it:**
- Portfolio strategy shows unrealistically high returns vs benchmarks
- No losing instruments in the backtest universe
- The instrument universe does not change over the backtest period
- All instruments in the test set are currently active/listed

**How to prevent it:**
- For single-instrument strategies (e.g., BTC/USDT), survivorship bias is minimal
- For multi-instrument strategies, use a historically accurate instrument list
- Document which biases apply in the backtest report limitations section
- Consider point-in-time data sources for portfolio strategies

---

## 3. Execution Price Bias

**Description:**
Using an unrealistic price for trade execution. The most common form is executing
at the close price of the bar where the signal was generated, when in reality
you can only execute at the next bar's open (or later). Even small timing
differences compound over hundreds of trades.

**Example of the mistake:**
```python
# Signal generated from bar's close, execution at the same close
if close > sma_20:
    buy(price=close)  # Impossible in practice -- you see close AFTER bar ends
```

**How to detect it:**
- Compare backtest results using close-price execution vs next-bar-open execution
- If results differ dramatically, execution price bias is present
- Check the code: does the execution price come from the same bar as the signal?

**How to prevent it:**
- Always execute at the next bar's open price: `execution_price = df.iloc[i]['open']`
- Consider adding slippage on top of the open price for more realism
- For limit orders, verify the limit price was actually reached during the bar

---

## 4. Over-Optimization (Curve Fitting)

**Description:**
Testing too many parameter combinations on the same dataset until finding one
that produces excellent metrics. The strategy is fit to historical noise rather
than genuine market patterns. It will fail in forward testing or live trading.

**Example of the mistake:**
```python
# Testing 10,000 combinations of 6 parameters on 2 years of data
for fast in range(5, 50):
    for slow in range(20, 200):
        for stop in [0.5, 1.0, 1.5, 2.0, 2.5]:
            for take in [1.0, 2.0, 3.0, 4.0]:
                for lookback in range(10, 100, 5):
                    for threshold in np.arange(0.1, 2.0, 0.1):
                        result = backtest(fast, slow, stop, take, lookback, threshold)
# With 10,000 tests, you WILL find something that looks great by chance
```

**How to detect it:**
- Out-of-sample performance drops more than 40% vs in-sample
- Optimal parameters are at extreme edges of the search range
- Small parameter changes cause large performance swings (fragile)
- More than 5-6 free parameters being optimized simultaneously
- Number of parameter combinations tested exceeds 100x the number of trades

**How to prevent it:**
- Mandatory train/test split: optimize on in-sample (e.g., 70%), validate on out-of-sample (30%)
- Cap optimization iterations (e.g., 50 max per phase)
- Use walk-forward validation: re-optimize on rolling windows
- Limit the number of free parameters (fewer is better)
- Track and display how many combinations were tested

---

## 5. Commission and Slippage Omission

**Description:**
Running backtests with zero transaction costs, zero slippage, and assumed
infinite liquidity. Strategies that trade frequently are most affected -- a
strategy with 0.01% average profit per trade is deeply unprofitable after
0.1% commission per side.

**Example of the mistake:**
```python
# Simple P&L without any cost deduction
pnl = exit_price - entry_price  # No commission, no slippage, no spread
equity += pnl * position_size
```

**How to detect it:**
- Trade log shows no commission line items
- Average profit per trade is smaller than typical spread/commission for the asset
- Strategy profitability inverts when transaction costs are doubled
- High-frequency strategy (>5 trades/day) shows consistent profits

**How to prevent it:**
- Make transaction costs MANDATORY in the backtest engine (never zero default)
- Default conservative estimates: 0.1% crypto, 0.01% stocks, 0.005% forex
- Include cost sensitivity analysis: show results at 1x, 2x, 3x assumed costs
- For high-frequency strategies, require explicit slippage justification

---

## 6. In-Sample / Out-of-Sample Confusion

**Description:**
Evaluating strategy performance on the same data used for optimization. This
guarantees the results look good (the optimizer found parameters that work on
this specific data) but says nothing about future performance.

**Example of the mistake:**
```python
# Optimize on full dataset, report metrics on full dataset
best_params = optimize(df, param_space)  # Optimized on ALL data
results = backtest(df, best_params)      # Evaluated on SAME data
print(f"Sharpe: {results['sharpe']}")    # Meaningless -- of course it looks good
```

**How to detect it:**
- No mention of train/test split in the methodology
- Same date range used for optimization and final evaluation
- Only one set of metrics reported (no IS vs OOS comparison)
- "Final" Sharpe ratio matches the "best" optimization Sharpe exactly

**How to prevent it:**
- Split data before optimization: first 70% for training, last 30% for testing
- Optimize ONLY on training data; evaluate ONCE on test data
- Report both in-sample and out-of-sample metrics side by side
- Never re-optimize after seeing out-of-sample results (that makes them in-sample)
- Consider walk-forward validation for more robust assessment

---

## Quick Reference

| Pitfall | Severity | Detection Difficulty | Primary Prevention |
|---------|----------|---------------------|--------------------|
| Lookahead bias | CRITICAL | Medium | Event-loop architecture |
| Survivorship bias | HIGH | Low | Documented limitations |
| Execution price bias | HIGH | Easy | Next-bar open execution |
| Over-optimization | HIGH | Medium | Train/test split |
| Commission omission | MEDIUM | Easy | Mandatory cost modeling |
| IS/OOS confusion | HIGH | Easy | Data split before optimization |

---

*This catalog should be reviewed before every backtest design and after every
backtest review. If any of these pitfalls are present, the results are unreliable.*
