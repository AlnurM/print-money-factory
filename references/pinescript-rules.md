# PineScript v5 Syntax Rules

> Reference for Claude when generating PineScript output. Read this before writing any .pine files.
> Also read: templates/pinescript-template.pine and references/pinescript-examples/*.pine

---

## 1. Version Declaration

Always start every PineScript file with:

```pine
//@version=5
```

This project generates **PineScript v5**, NOT v6. Include this comment in every generated file:

```pine
// Note: This is PineScript v5. For v6 migration, see:
// https://www.tradingview.com/pine-script-docs/migration-guides/to-pine-version-6/
```

---

## 2. Strategy vs Indicator -- TWO Versions Required

Every strategy MUST produce **two separate PineScript files**:

| File | Declaration | Purpose |
|------|-------------|---------|
| `pinescript_v5_strategy.pine` | `strategy()` | TradingView Strategy Tester backtesting |
| `pinescript_v5_indicator.pine` | `indicator()` | Live chart signals + alerts |

### CRITICAL Rule

**`strategy.*` functions are ONLY available in `strategy()` scripts.**

NEVER call `strategy.entry()`, `strategy.close()`, or `strategy.exit()` in an `indicator()` script. This is the #1 PineScript generation error. TradingView will reject it with: "Cannot call 'strategy.entry' in indicator script."

- **Strategy version** uses: `strategy.entry()`, `strategy.close()`, `strategy.exit()`
- **Indicator version** uses: `plotshape()`, `alert()`, `alertcondition()`

### Strategy Declaration

```pine
//@version=5
strategy("Strategy Name", overlay=true, initial_capital=10000,
         default_qty_type=strategy.percent_of_equity, default_qty_value=100,
         commission_type=strategy.commission.percent, commission_value=0.1)
```

Key parameters:
- `overlay=true` -- plot on price chart (most strategies). Use `false` for oscillator-only strategies
- `initial_capital` -- set to the backtest's initial capital
- `default_qty_type` -- `strategy.percent_of_equity` (percentage) or `strategy.fixed` (fixed qty)
- `commission_type` -- `strategy.commission.percent` for percentage-based commissions
- `commission_value` -- commission rate (e.g., 0.1 for 0.1%)

### Indicator Declaration

```pine
//@version=5
indicator("Strategy Name Signals", overlay=true)
```

- Same `overlay` setting as the strategy version
- Title should include "Signals" to distinguish from the strategy version

---

## 3. Input Functions

All strategy parameters should be `input()` calls so users can adjust them in the TradingView UI. Use the optimized best parameter values as defaults.

| Function | Usage | Example |
|----------|-------|---------|
| `input.int(defval, title, minval, maxval)` | Integer parameters | `fastLength = input.int(10, "Fast Period", minval=1, maxval=200)` |
| `input.float(defval, title, minval, maxval, step)` | Float parameters | `stopPct = input.float(2.0, "Stop Loss %", minval=0.1, maxval=20.0, step=0.1)` |
| `input.bool(defval, title)` | Boolean flags | `useTrend = input.bool(true, "Use Trend Filter")` |
| `input.string(defval, title, options)` | String selections | `maType = input.string("EMA", "MA Type", options=["EMA", "SMA", "WMA"])` |

**Rule:** Set `defval` to the best parameter values from the optimization. Set `minval`/`maxval` to the parameter space boundaries from the plan.

---

## 4. Common Indicator Functions (ta namespace)

### Moving Averages
- `ta.ema(source, length)` -- Exponential Moving Average
- `ta.sma(source, length)` -- Simple Moving Average
- `ta.wma(source, length)` -- Weighted Moving Average
- `ta.vwma(source, length)` -- Volume-Weighted Moving Average

### Oscillators
- `ta.rsi(source, length)` -- Relative Strength Index (0-100)
- `ta.stoch(close, high, low, length)` -- Stochastic %K (0-100)
- `ta.macd(source, fastLength, slowLength, signalLength)` -- returns `[macdLine, signalLine, histogram]`
- `ta.cci(source, length)` -- Commodity Channel Index
- `ta.mfi(series, length)` -- Money Flow Index

### Volatility
- `ta.atr(length)` -- Average True Range
- `ta.bb(source, length, mult)` -- Bollinger Bands, returns `[middle, upper, lower]`

### Crossovers
- `ta.crossover(a, b)` -- returns `true` when `a` crosses ABOVE `b`
- `ta.crossunder(a, b)` -- returns `true` when `a` crosses BELOW `b`

### Range
- `ta.highest(source, length)` -- Highest value over N bars
- `ta.lowest(source, length)` -- Lowest value over N bars
- `ta.highestbars(source, length)` -- Bars since highest value

### Trend
- `ta.supertrend(factor, atrPeriod)` -- returns `[supertrend, direction]`
- `ta.pivothigh(source, leftbars, rightbars)` -- Pivot high detection
- `ta.pivotlow(source, leftbars, rightbars)` -- Pivot low detection

---

## 5. Strategy Execution Functions

These functions are **ONLY valid in `strategy()` scripts**. Never use them in `indicator()` scripts.

### Entry

```pine
strategy.entry(id, direction)
```

- `id` -- String identifier for the entry (e.g., `"Long"`, `"Short"`)
- `direction` -- `strategy.long` or `strategy.short`

### Close

```pine
strategy.close(id)
```

- Closes the position opened by the entry with matching `id`

### Exit (Stop Loss / Take Profit)

```pine
strategy.exit(id, from_entry, stop, limit)
```

- `id` -- Unique identifier for this exit order
- `from_entry` -- The entry `id` this exit applies to
- `stop` -- Stop loss price level
- `limit` -- Take profit price level

### Conditional Execution Pattern

Always use `if` blocks for conditional entries:

```pine
if longCondition
    strategy.entry("Long", strategy.long)

if exitCondition
    strategy.close("Long")
```

**Do NOT use the `when` parameter** (deprecated in v6):

```pine
// WRONG (deprecated):
strategy.entry("Long", strategy.long, when=longCondition)

// RIGHT:
if longCondition
    strategy.entry("Long", strategy.long)
```

### Position Information

- `strategy.position_size` -- Current position size (positive = long, negative = short, 0 = flat)
- `strategy.position_avg_price` -- Average entry price of current position

---

## 6. Indicator Signal Functions

These functions are used in `indicator()` scripts to display signals and create alerts. They replace the `strategy.*` functions.

### Visual Signals

```pine
plotshape(condition, title, location, color, style, size)
```

Parameters:
- `condition` -- Boolean series (when `true`, shape is plotted)
- `title` -- Label for the shape in the legend
- `location` -- Where to draw:
  - `location.belowbar` -- Below the price bar (for buy signals)
  - `location.abovebar` -- Above the price bar (for sell signals)
  - `location.absolute` -- At a specific price level
- `color` -- Shape color (e.g., `color.green`, `color.red`)
- `style` -- Shape type:
  - `shape.triangleup` -- Up triangle (buy)
  - `shape.triangledown` -- Down triangle (sell)
  - `shape.circle` -- Circle
  - `shape.cross` -- Cross
  - `shape.diamond` -- Diamond
  - `shape.flag` -- Flag
- `size` -- `size.small`, `size.normal`, `size.large`, `size.tiny`, `size.huge`

### Alerts

**Use BOTH `alert()` and `alertcondition()` for maximum compatibility:**

#### alert() -- Modern (v4+)

```pine
if longCondition
    alert("Long entry signal on " + syminfo.tickerid, alert.freq_once_per_bar)
```

Fires during script execution. Frequency options:
- `alert.freq_once_per_bar` -- Once per bar (most common)
- `alert.freq_once_per_bar_close` -- Only on bar close (avoids intra-bar noise)
- `alert.freq_all` -- Every time condition is true

#### alertcondition() -- Legacy but widely used

```pine
alertcondition(longCondition, "Long Entry", "Long entry signal")
alertcondition(shortCondition, "Short/Exit", "Short or exit signal")
```

Creates user-configurable alerts in the TradingView Alerts dialog. Users can customize delivery (email, webhook, push notification). More limited than `alert()` but supported in all v5 scripts.

**Include BOTH** -- `alert()` for flexibility, `alertcondition()` for user-configurable alerts.

---

## 7. Plotting Functions

```pine
plot(series, title, color, linewidth)
```

- Plot a line on the chart (e.g., moving averages, indicator values)

```pine
bgcolor(color)
```

- Set background color for the current bar

```pine
barcolor(color)
```

- Set bar color for the current bar

### Colors

Built-in colors:
- `color.red`, `color.green`, `color.blue`, `color.orange`, `color.yellow`
- `color.purple`, `color.gray`, `color.white`, `color.black`
- `color.aqua`, `color.fuchsia`, `color.lime`, `color.maroon`, `color.navy`

Transparency:
- `color.new(color, transparency)` -- transparency from 0 (opaque) to 100 (invisible)
- Example: `color.new(color.green, 90)` -- very transparent green for backgrounds

Hex colors:
- `color.rgb(r, g, b, transp)` -- custom RGB color

---

## 8. Common Strategy Patterns

### Trailing Stop

```pine
// Track highest price since entry, set stop at highest - N*ATR
var float trailHigh = na
if strategy.position_size > 0
    trailHigh := math.max(nz(trailHigh), high)
    trailStop = trailHigh - ta.atr(14) * 2.0
    strategy.exit("Trail", "Long", stop=trailStop)
else
    trailHigh := na
```

### Breakout Entry

```pine
// N-bar high breakout
breakoutLevel = ta.highest(high, 20)[1]  // [1] to avoid lookahead
longCondition = close > breakoutLevel
```

### Mean Reversion

```pine
// RSI oversold with Bollinger Band confirmation
[bbMiddle, bbUpper, bbLower] = ta.bb(close, 20, 2.0)
rsiValue = ta.rsi(close, 14)
longCondition = rsiValue < 30 and close <= bbLower
exitCondition = close >= bbMiddle
```

### Trend Following with Filter

```pine
// MA crossover with ADX filter
fastMA = ta.ema(close, 10)
slowMA = ta.ema(close, 50)
[diPlus, diMinus, adxValue] = ta.dmi(14, 14)
longCondition = ta.crossover(fastMA, slowMA) and adxValue > 25
```

### Risk-Reward Exit

```pine
// Fixed R:R with ATR-based stop
atrVal = ta.atr(14)
if longCondition
    strategy.entry("Long", strategy.long)
    stopPrice = close - atrVal * 1.5
    targetPrice = close + atrVal * 3.0  // 2:1 R:R
    strategy.exit("Exit", "Long", stop=stopPrice, limit=targetPrice)
```

---

## 9. Built-in Variables

| Variable | Description |
|----------|-------------|
| `open`, `high`, `low`, `close` | Current bar OHLC prices |
| `volume` | Current bar volume |
| `time` | Current bar time (Unix timestamp) |
| `bar_index` | Current bar number (0-based) |
| `syminfo.tickerid` | Current symbol ticker |
| `syminfo.timezone` | Exchange timezone |
| `timeframe.period` | Current chart timeframe |
| `na` | Not-a-number (Pine equivalent of null/NaN) |

---

## 10. v5 vs v6 Migration Notes

This project generates PineScript v5. Here are the key differences for future v6 migration:

| Change | v5 Behavior | v6 Behavior |
|--------|-------------|-------------|
| `when` parameter | `strategy.entry("Long", strategy.long, when=cond)` works | `when` parameter removed -- use `if` blocks |
| Bool casting | `int`/`float` implicitly cast to `bool` (0 = false, non-zero = true) | Explicit comparisons required (`x != 0` instead of `x`) |
| Trade limit | 9000-trade limit per backtest | Limit removed |
| Dynamic requests | Not available | `request.security_lower_tf()` and similar new functions |
| Method syntax | Limited | More OOP-style method calls on types |

**Recommendation:** Generate v5 code. v5 is stable, broadly supported, and compatible with all TradingView accounts. Our templates already use `if` blocks (not `when`), so the main migration concern is bool casting.

Always include this comment in generated files:

```pine
// Note: This is PineScript v5. For v6 migration, see:
// https://www.tradingview.com/pine-script-docs/migration-guides/to-pine-version-6/
// Key v6 change: int/float no longer implicitly cast to bool -- use explicit comparisons.
```

---

## 11. File Naming Convention

Output files in the export package:

| File | Purpose |
|------|---------|
| `pinescript_v5_strategy.pine` | Strategy version for TradingView backtesting |
| `pinescript_v5_indicator.pine` | Indicator version with plotshape + alerts for live trading |

Both files go in the `output/` directory.

---

## 12. Generation Checklist

Before generating PineScript, verify:

- [ ] Read this reference (`references/pinescript-rules.md`)
- [ ] Read the template (`templates/pinescript-template.pine`)
- [ ] Read at least one example from `references/pinescript-examples/`
- [ ] Read `STRATEGY.md` for entry/exit logic and parameters
- [ ] Read `best_result.json` for optimized parameter values
- [ ] Read `phase_N_discuss.md` for detailed strategy logic

When generating:

- [ ] `//@version=5` is the first line
- [ ] v6 migration comment is included
- [ ] All parameters use `input.*()` with best values as defaults
- [ ] Strategy version uses ONLY `strategy.*` functions
- [ ] Indicator version uses ONLY `plotshape()` / `alert()` / `alertcondition()`
- [ ] Both versions have identical signal logic
- [ ] Stop loss and take profit are implemented
- [ ] Indicators are plotted for visual confirmation
- [ ] `if` blocks used for conditional execution (not `when` parameter)
