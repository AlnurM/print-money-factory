# Phase 5: Verify & Export - Research

**Researched:** 2026-03-21
**Domain:** Interactive HTML reporting, PineScript code generation, approval/debug workflow orchestration
**Confidence:** HIGH

## Summary

Phase 5 implements `/brrr:verify` -- the final phase in the product pipeline. It has three distinct domains: (1) generating a standalone interactive HTML report from execute-phase artifacts, (2) an AI-driven approval/debug decision flow, and (3) a complete export package on approval including PineScript v5 code. The report template already exists (211 lines) with Jinja2 placeholders and a plotly CDN script tag, but needs extension for regime breakdown, benchmark comparison, and parameter heatmap sections. PineScript generation requires both a strategy version and an indicator version per D-17/D-19.

The workflow is a behavioral markdown file (~800-1000 lines estimated) following the established pattern: preamble validation, context scan, argument parsing, then the core logic sections. It reads execute-phase artifacts (iteration JSONs, best_result.json, cached OHLCV data) and produces either the report + export package (--approved) or a diagnosis document + new phase cycle (--debug).

**Primary recommendation:** Build the workflow in three logical waves: (1) report generation pipeline (Python script that reads artifacts, computes regime/benchmark data, fills the HTML template via Jinja2), (2) AI analysis and approval/debug flow (workflow behavioral sections), (3) export package generation (PineScript templates, markdown documents, final packaging).

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions
- **D-01:** Decision-first layout: metrics summary at top (is it good?), then equity curve (how it grew), then details (drawdown, iterations, heatmap, trades, regime, benchmark)
- **D-02:** Fill the existing `templates/report-template.html` template -- inject plotly charts and data into placeholders. Template as structure, not generate from scratch.
- **D-03:** Regime classification is trend-based: SMA slope + ADX. Strong trend up = bull, strong down = bear, weak = sideways.
- **D-04:** Standalone HTML file with embedded plotly.js -- no server needed, opens in any browser.
- **D-05:** Report includes all 7 sections: metrics summary, equity curve (vs buy & hold), drawdown chart, iteration table, parameter heatmap (if grid search), trade list with P&L coloring, regime breakdown, benchmark correlation (alpha/beta).
- **D-06:** Always auto-analyze before presenting choice -- Claude reads report data, formulates conclusion with specific metrics vs targets, then presents assessment before asking approved/debug.
- **D-07:** --debug triggers full diagnosis: equity curve shape, regime performance, losing trade clusters, parameter sensitivity. Specific hypothesis for the next phase cycle. Not just "metrics are bad."
- **D-08:** Allow force-approve -- warn if targets not met, but allow --approved anyway. User decides what's "good enough."
- **D-09:** --debug opens new phase cycle: STATE.md updated, next /brrr:discuss starts from AI diagnosis.
- **D-10:** trading-rules.md in practitioner tone: "Enter long when price sweeps below OB and closes back above. Stop: 1xATR below entry. Target: 2.5RR."
- **D-11:** live-checklist.md with generic items (broker setup, position sizing calc) + strategy-specific items (which timeframe to watch, when signals appear).
- **D-12:** backtest_final.py is fully reproducible: data download, full backtest, metrics, equity plot. One file, zero deps beyond venv.
- **D-13:** performance-report.md as portable markdown summary for sharing.
- **D-14:** All exports in `output/` directory.
- **D-15:** STATE.md updated to CLOSED with final metrics on --approved.
- **D-16:** Use template + examples + add a PineScript syntax rules reference for Claude to read before generating. Maximum reliability.
- **D-17:** Generate BOTH: strategy version (strategy() with entry/exit/stop/TP for TradingView backtesting) AND indicator version (indicator() with plotshape + alertcondition for live alerts).
- **D-18:** PineScript v5, with comment noting v6 migration path.
- **D-19:** Two files in output/: `pinescript_v5_strategy.pine` and `pinescript_v5_indicator.pine`.

### Claude's Discretion
- Exact plotly chart styling and colors
- How to format the metrics summary table
- Parameter heatmap color scheme
- Trade list sorting (chronological vs by P&L)
- Exact PineScript syntax rules doc content
- How to detect regime boundaries in the data

### Deferred Ideas (OUT OF SCOPE)
None -- discussion stayed within phase scope
</user_constraints>

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|------------------|
| VRFY-01 | Interactive standalone HTML report (plotly, no server) | Plotly `to_html(full_html=False, include_plotlyjs=False)` into existing Jinja2 template that already has CDN script tag |
| VRFY-02 | Equity curve (strategy vs buy & hold) with zoom | Plotly scatter traces -- two lines on same chart, plotly has built-in zoom |
| VRFY-03 | Drawdown chart with max drawdown line | Already in template; add horizontal line at max DD value using `add_hshape` |
| VRFY-04 | Iteration table -- all iterations with params and Sharpe evolution | Read all `iter_NN_verdict.json` files, render as HTML table or plotly Table trace |
| VRFY-05 | Parameter heatmap (if grid search) | `plotly.graph_objects.Heatmap` -- 2D array of parameter combos vs metric value |
| VRFY-06 | Trade list with per-trade P&L coloring | HTML table with `.positive`/`.negative` CSS classes already in template |
| VRFY-07 | Regime breakdown -- performance in bull/bear/sideways | SMA slope + ADX classification per D-03; compute metrics per regime segment |
| VRFY-08 | Benchmark correlation -- alpha, beta vs buy-and-hold | Linear regression of strategy returns vs buy-and-hold returns; alpha = intercept * 252, beta = slope |
| VRFY-09 | Metrics summary table -- all metrics vs targets | Read best_result.json metrics + targets from STRATEGY.md, render metric cards |
| VRFY-10 | AI analyzes full report and formulates conclusion | Workflow behavioral section -- Claude reads all data and writes assessment |
| VRFY-11 | --approved closes milestone, triggers export | Workflow flow control + STATE.md update to CLOSED |
| VRFY-12 | --debug keeps milestone open, AI diagnoses failure | Workflow flow control + diagnosis document + new phase cycle in STATE.md |
| EXPT-01 | PineScript v5 code -- valid strategy | Template + examples + syntax rules reference; generate strategy() version |
| EXPT-02 | trading-rules.md -- plain English entry/exit/sizing | Claude reads STRATEGY.md + discuss artifacts, writes practitioner-tone rules |
| EXPT-03 | performance-report.md -- portable metrics summary | Template from best_result.json metrics |
| EXPT-04 | backtest_final.py -- reproducible Python script | Combine data loading + backtest engine + best params into single file |
| EXPT-05 | live-checklist.md -- step-by-step guide | Generic + strategy-specific checklist items |
| EXPT-06 | report_vN.html -- copy of final HTML report | Copy generated report to output/ |
| EXPT-07 | All exports in output/ directory | mkdir output/, write all files there |
</phase_requirements>

## Standard Stack

### Core (already installed in venv)
| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| plotly | ^6.5 | Interactive charts in HTML report | Already in requirements.txt. `to_html(full_html=False)` for Jinja2 injection. CDN tag already in template |
| jinja2 | ^3.1 | HTML template rendering | Already in requirements.txt. Fills `{{ variable }}` placeholders in report-template.html |
| pandas | ^3.0 | Data manipulation for regime/benchmark | Already available. OHLCV data from parquet cache |
| numpy | ^2.4 | Numerical computation for alpha/beta | Already available. Linear regression for benchmark stats |
| matplotlib | ^3.10 | NOT used in this phase | Per CLAUDE.md: matplotlib for iteration PNGs, plotly for final reports |

### Supporting (already installed)
| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| ta | ^0.11 | ADX indicator for regime classification | Regime breakdown computation (D-03) |
| scipy | ^1.14 | Linear regression for alpha/beta | `scipy.stats.linregress` for benchmark correlation |

### No New Dependencies
All libraries needed are already in the venv from Phase 1 install. No new pip installs required.

## Architecture Patterns

### Report Generation Pipeline

The report is generated by a Python script that the verify workflow writes and executes, following the same pattern as execute-phase iteration scripts.

```
Python report script flow:
1. Read all iteration artifacts (iter_NN_*.json)
2. Read best_result.json
3. Read cached OHLCV data (.pmf/cache/*.parquet)
4. Compute additional analytics:
   - Buy & hold equity curve (for comparison)
   - Drawdown series from equity curve
   - Regime classification (SMA slope + ADX)
   - Benchmark stats (alpha, beta via linregress)
5. Build plotly figures (to_html with full_html=False)
6. Render Jinja2 template with all data injected
7. Write standalone HTML file
```

### Template Extension Pattern

The existing `templates/report-template.html` has 5 sections (metrics, equity, drawdown, iterations, trades). It needs extension for:
- Parameter heatmap section (conditional -- only if grid search)
- Regime breakdown section
- Benchmark correlation section

**Pattern:** Add new `<div class="section">` blocks to the template with new Jinja2 variables. The Python script computes the data and passes it to `jinja2.Template.render()`.

**Critical detail:** The template already includes plotly CDN (`<script src="https://cdn.plot.ly/plotly-2.35.2.min.js">`). When generating chart HTML with `fig.to_html()`, use `full_html=False, include_plotlyjs=False` so plotly.js is NOT duplicated.

### Workflow Structure (behavioral markdown)

Follow the established pattern from execute.md (1067 lines) and discuss.md (543 lines):

```
workflows/verify.md (~800-1000 lines estimated)
  Preamble: Sequence Validation (execute must be done)
  Preamble: Context File Scan (same as other workflows)
  Preamble: Parse Arguments (--approved, --debug)
  Step 1: Load Inputs (best_result.json, STRATEGY.md, iteration artifacts)
  Step 2: Generate Report (write + run Python script)
  Step 3: AI Analysis (Claude reads report data, formulates assessment)
  Step 4: Present Assessment & Choice (display to user)
  Step 5a: --approved path (export package generation)
  Step 5b: --debug path (diagnosis + new phase cycle)
  Step 6: Update STATE.md
  Step 7: Confirmation
  Appendix: Requirement Coverage
```

### Export Package Structure

```
output/
  pinescript_v5_strategy.pine    # strategy() version for TradingView backtesting
  pinescript_v5_indicator.pine   # indicator() version with alertcondition for live
  trading-rules.md               # Practitioner-tone entry/exit/sizing rules
  performance-report.md          # Portable metrics summary
  backtest_final.py              # Fully reproducible single-file backtest
  live-checklist.md              # Step-by-step before real money
  report_v{N}.html               # Copy of interactive HTML report
```

### PineScript Generation Pattern

Per D-16: Claude reads template + examples + syntax rules reference before generating.

**Strategy version (`strategy()`):**
- Uses `strategy()` declaration (already in template)
- `strategy.entry()` / `strategy.close()` / `strategy.exit()` for trades
- Stop loss via `strategy.exit()` with `stop=` parameter
- Take profit via `strategy.exit()` with `limit=` parameter
- All params as `input.int()` / `input.float()` for TradingView UI

**Indicator version (`indicator()`):**
- Uses `indicator()` declaration instead of `strategy()`
- `plotshape()` for visual entry/exit signals on chart
- `alert()` function (modern replacement for `alertcondition()`) for notifications
- Note: PineScript v5 supports both `alert()` and `alertcondition()`; use `alert()` as it is more flexible
- Same logic, different execution model

**PineScript v5 vs v6 migration note (per D-18):**
- v6 released late 2024; main changes: dynamic requests, `int`/`float` no longer implicitly cast to `bool`, `when` parameter removed from strategy functions, 9000-trade limit removed
- v5 is stable and broadly supported; v6 adoption is early
- Add comment: `// Note: This is PineScript v5. For v6 migration, see TradingView migration guide.`
- Key v6 change affecting strategies: `when` parameter removed from `strategy.entry()` etc. -- use `if` blocks instead (our templates already do this correctly)

### Regime Classification Pattern (D-03)

```python
# SMA slope + ADX regime classification
# Using ta library (already in venv)
import ta

def classify_regimes(df, sma_period=50, adx_period=14, adx_threshold=25):
    """
    Classify each bar as bull, bear, or sideways.

    Bull:     SMA slope > 0 AND ADX > threshold (strong uptrend)
    Bear:     SMA slope < 0 AND ADX > threshold (strong downtrend)
    Sideways: ADX <= threshold (weak trend regardless of direction)
    """
    sma = df['close'].rolling(sma_period).mean()
    sma_slope = sma.diff()  # positive = up, negative = down

    adx = ta.trend.ADXIndicator(df['high'], df['low'], df['close'], window=adx_period)
    adx_values = adx.adx()

    regimes = pd.Series('sideways', index=df.index)
    regimes[(sma_slope > 0) & (adx_values > adx_threshold)] = 'bull'
    regimes[(sma_slope < 0) & (adx_values > adx_threshold)] = 'bear'

    return regimes
```

### Benchmark Alpha/Beta Computation

```python
from scipy.stats import linregress

def compute_benchmark_stats(strategy_returns, benchmark_returns, trading_days=252):
    """
    Compute alpha and beta vs buy-and-hold benchmark.

    beta = slope of regression(strategy_returns ~ benchmark_returns)
    alpha = annualized intercept
    """
    # Align returns
    aligned = pd.DataFrame({
        'strategy': strategy_returns,
        'benchmark': benchmark_returns
    }).dropna()

    slope, intercept, r_value, p_value, std_err = linregress(
        aligned['benchmark'], aligned['strategy']
    )

    beta = slope
    alpha = intercept * trading_days  # annualize daily alpha
    r_squared = r_value ** 2

    return {'alpha': alpha, 'beta': beta, 'r_squared': r_squared}
```

### Anti-Patterns to Avoid
- **Generating HTML from scratch instead of filling the template:** D-02 explicitly locks to filling `templates/report-template.html`. Extend it, do not replace it.
- **Using `include_plotlyjs=True` in `to_html()`:** The template already has the CDN script tag. Using True would embed ~3MB of plotly.js inline AND duplicate with the CDN tag.
- **Putting report generation logic in the workflow markdown:** The workflow should write a Python script, execute it, and read the output -- same pattern as execute.md. Do not try to generate plotly charts from markdown instructions alone.
- **Using `alertcondition()` without `alert()` in PineScript indicator:** `alertcondition()` is older and more limited. Use `alert()` function for flexibility, but include both for compatibility since `alert()` fires during chart execution while `alertcondition()` is user-configurable.

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| ADX calculation | Manual ADX formula | `ta.trend.ADXIndicator` | ADX has a complex smoothing algorithm; edge cases in early bars |
| Linear regression for alpha/beta | Manual matrix math | `scipy.stats.linregress` | One-liner, handles edge cases, returns r-value and p-value |
| HTML template rendering | String concatenation / f-strings | `jinja2.Template.render()` | Proper escaping, clean separation of data from layout |
| Plotly chart HTML fragments | Manual JS generation | `fig.to_html(full_html=False, include_plotlyjs=False)` | Handles all JS dependencies, data serialization, responsive layout |
| Drawdown series computation | Custom loop | numpy vectorized (already in metrics.py pattern) | `max_drawdown()` exists; extend pattern for full series |

**Key insight:** The report generation is a Python data pipeline, not a markdown-generation task. The workflow writes a Python script, runs it, and gets an HTML file. All complex computation (regime, benchmark, drawdown series) happens in Python where pandas/numpy/scipy are available.

## Common Pitfalls

### Pitfall 1: Plotly CDN Duplication
**What goes wrong:** Report HTML loads plotly.js twice -- once from CDN tag in template, once embedded by `to_html()`.
**Why it happens:** Default `to_html()` includes full plotly.js (~3MB).
**How to avoid:** Always use `fig.to_html(full_html=False, include_plotlyjs=False)`.
**Warning signs:** Report HTML file is >3MB; browser console shows plotly loaded twice.

### Pitfall 2: JSON Serialization of numpy Types
**What goes wrong:** `json.dumps()` fails on numpy int64, float64, ndarray types when injecting data into Jinja2 template.
**Why it happens:** Jinja2 template expects `{{ metrics_json }}` to be valid JSON, but Python dicts may contain numpy types.
**How to avoid:** Use a JSON serializer that handles numpy types. The execute workflow already has this pattern -- convert numpy types before serialization.
**Warning signs:** `TypeError: Object of type int64 is not JSON serializable`.

### Pitfall 3: Equity Curve from Trades vs Daily
**What goes wrong:** Equity curve looks jagged/wrong because it's plotted per-trade instead of per-bar.
**Why it happens:** The backtest engine returns trades (with entry/exit times) and a bar-level equity array. The trades-based equity reconstruction in execute.md skips bars between trades.
**How to avoid:** Use the bar-level equity curve from `run_backtest()` return value (the `equity_curve` key from `compute_all_metrics`). However, note that `compute_all_metrics` does NOT include the raw equity curve in its return dict by default. The verify script needs to either (a) re-run the best iteration's backtest to capture the full equity curve, or (b) reconstruct from trades with proper date alignment against the OHLCV index.
**Warning signs:** Equity curve has fewer points than expected; dates don't align with OHLCV data.

### Pitfall 4: Regime Classification on Insufficient Data
**What goes wrong:** SMA and ADX need warmup bars (50+ for SMA-50, 14+ for ADX). First N bars get NaN, classified incorrectly.
**Why it happens:** Rolling calculations produce NaN for the first `window` bars.
**How to avoid:** Fill NaN regime values with 'sideways' (default assumption for insufficient data).
**Warning signs:** First N trades always classified as 'sideways' regardless of actual market condition.

### Pitfall 5: PineScript strategy() vs indicator() Declaration Conflicts
**What goes wrong:** `strategy.entry()` calls in an `indicator()` script cause compilation errors in TradingView.
**Why it happens:** Strategy functions (`strategy.*`) are only available in `strategy()` scripts, not `indicator()` scripts.
**How to avoid:** The indicator version must use completely different execution logic: `plotshape()` for visual signals, `alert()` for notifications. No `strategy.*` calls.
**Warning signs:** "Cannot call 'strategy.entry' in indicator script" error in Pine Editor.

### Pitfall 6: backtest_final.py Data Source Dependency
**What goes wrong:** `backtest_final.py` fails when run later because data source API changed or is rate-limited.
**Why it happens:** The script downloads fresh data on each run.
**How to avoid:** Include both paths: (1) try to download fresh data, (2) fall back to a bundled CSV or the cached parquet. Per D-12, it should be "zero deps beyond venv" but still needs data.
**Warning signs:** Script fails months later with API errors.

### Pitfall 7: --debug New Phase Cycle Numbering
**What goes wrong:** Debug opens Phase N+1 but discuss workflow looks for different artifact paths.
**Why it happens:** Phase numbering in STATE.md drives all artifact paths. New phase cycle means incrementing the phase number and creating new artifact directories.
**How to avoid:** Follow the exact STATE.md update pattern from the template. New phase = increment phase number, add new Phase N+1 checklist section, update "Current Phase" field.
**Warning signs:** Next `/brrr:discuss` can't find its inputs or writes to wrong directory.

## Code Examples

### Plotly Chart Injection into Jinja2 Template

```python
# Source: Plotly official docs (plotly.com/python/interactive-html-export/)
import plotly.graph_objects as go
from jinja2 import Template

# Create equity curve figure
fig = go.Figure()
fig.add_trace(go.Scatter(x=dates, y=strategy_equity, name='Strategy',
                          line=dict(color='#2563eb', width=2)))
fig.add_trace(go.Scatter(x=dates, y=buyhold_equity, name='Buy & Hold',
                          line=dict(color='#9ca3af', width=1, dash='dash')))
fig.update_layout(margin=dict(t=10, r=30, b=40, l=60),
                   xaxis_title='Date', yaxis_title='Equity ($)',
                   hovermode='x unified')

# Get HTML div only (template already has plotly CDN)
equity_html = fig.to_html(full_html=False, include_plotlyjs=False)

# Render template
with open('templates/report-template.html') as f:
    template = Template(f.read())

html = template.render(
    title=strategy_name,
    equity_chart_html=equity_html,
    drawdown_chart_html=drawdown_html,
    metrics_json=json.dumps(metrics_data),
    # ... other variables
)

with open(output_path, 'w') as f:
    f.write(html)
```

### Parameter Heatmap (Grid Search Only)

```python
# Source: Plotly heatmap docs (plotly.com/python/heatmaps/)
import plotly.graph_objects as go

# Build 2D grid from iteration results
# x = param1 values, y = param2 values, z = sharpe values
fig = go.Figure(data=go.Heatmap(
    x=param1_values,
    y=param2_values,
    z=sharpe_grid,  # 2D array
    colorscale='RdYlGn',  # Red (bad) -> Yellow -> Green (good)
    colorbar=dict(title='Sharpe Ratio'),
    hovertemplate='%{x}<br>%{y}<br>Sharpe: %{z:.2f}<extra></extra>'
))
fig.update_layout(
    xaxis_title=param1_name,
    yaxis_title=param2_name,
    margin=dict(t=10, r=30, b=40, l=60)
)
```

### PineScript v5 Indicator Version Pattern

```pine
//@version=5
indicator("{{STRATEGY_NAME}} Signals", overlay=true)

// === INPUTS ===
// Same parameters as strategy version
fastLength = input.int(10, "Fast Period", minval=1)
slowLength = input.int(50, "Slow Period", minval=1)

// === INDICATORS ===
fastMA = ta.ema(close, fastLength)
slowMA = ta.ema(close, slowLength)

// === SIGNALS ===
longCondition = ta.crossover(fastMA, slowMA)
shortCondition = ta.crossunder(fastMA, slowMA)

// === VISUAL SIGNALS ===
plotshape(longCondition, title="Long Entry", location=location.belowbar,
          color=color.green, style=shape.triangleup, size=size.small)
plotshape(shortCondition, title="Short Entry / Long Exit", location=location.abovebar,
          color=color.red, style=shape.triangledown, size=size.small)

// === ALERTS ===
// alert() fires during script execution (v4+)
if longCondition
    alert("Long entry signal on " + syminfo.tickerid, alert.freq_once_per_bar)
if shortCondition
    alert("Short/exit signal on " + syminfo.tickerid, alert.freq_once_per_bar)

// alertcondition() creates user-configurable alerts (legacy but widely used)
alertcondition(longCondition, "Long Entry", "Long entry signal")
alertcondition(shortCondition, "Short/Exit", "Short or exit signal")

// === PLOTTING ===
plot(fastMA, "Fast MA", color=color.blue, linewidth=2)
plot(slowMA, "Slow MA", color=color.red, linewidth=2)

// Note: This is PineScript v5. For v6 migration, see:
// https://www.tradingview.com/pine-script-docs/migration-guides/to-pine-version-6/
// Key v6 change: int/float no longer implicitly cast to bool
```

### Debug Diagnosis Document Pattern

```markdown
# Phase {N} Debug Diagnosis

## Assessment
{AI's specific assessment of what went wrong, with metrics vs targets}

## Equity Curve Analysis
{Shape description: "Equity was flat from X to Y, suggesting the strategy
doesn't perform in sideways markets"}

## Regime Performance
| Regime | Trades | Win Rate | Avg P&L | Contribution |
|--------|--------|----------|---------|--------------|
| Bull   | {n}    | {wr}%    | ${avg}  | {pct}%       |
| Bear   | {n}    | {wr}%    | ${avg}  | {pct}%       |
| Sideways | {n}  | {wr}%    | ${avg}  | {pct}%       |

## Losing Trade Clusters
{Analysis of where losses concentrate -- time periods, market conditions}

## Parameter Sensitivity
{Which parameters matter most, which are insensitive}

## Hypothesis for Next Cycle
{Specific, actionable hypothesis: "Add a regime filter to avoid sideways markets"
or "Widen stop loss to reduce whipsaws during volatile periods"}

## Recommended Changes
1. {Specific change 1}
2. {Specific change 2}
```

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| `alertcondition()` only | `alert()` function + `alertcondition()` | PineScript v4+ | `alert()` is more flexible, fires during execution. Use both for compatibility |
| PineScript v5 | PineScript v6 available | Late 2024 | v6 removes `when` param, changes bool casting. v5 still fully supported. Use v5 per D-18 |
| Plotly `write_html()` | `to_html(full_html=False)` + Jinja2 | Current best practice | Separates chart generation from page layout; enables multi-chart pages |
| kaleido for static images | matplotlib Agg backend | kaleido v1.0 (Chrome dependency) | Per CLAUDE.md: use matplotlib for PNGs, plotly for HTML only |

## Template Extension Plan

The existing `templates/report-template.html` needs these additions:

### New Sections to Add
1. **Parameter Heatmap section** (conditional, after Iteration History):
   - `<div class="section" id="param-heatmap">` with `{{ heatmap_chart_html }}`
   - Only rendered if grid search was used (`{% if has_heatmap %}`)

2. **Regime Breakdown section** (after Trade Log):
   - `<div class="section" id="regime-breakdown">` with regime performance table and optional bar chart
   - `{{ regime_table_html }}` and `{{ regime_chart_html }}`

3. **Benchmark Correlation section** (after Regime Breakdown):
   - `<div class="section" id="benchmark">` with alpha/beta/R-squared stats
   - `{{ benchmark_stats_html }}` and optional scatter plot of returns

### Template Variable Changes
Current template uses raw JSON injection (`{{ equity_data }}`) with inline JavaScript. For consistency, the report Python script should either:
- **Option A:** Keep the current pattern (inject JSON, render with inline JS) for existing sections AND use `to_html()` for new chart sections
- **Option B:** Convert all charts to `to_html()` pattern for consistency

**Recommendation:** Option A -- keep existing sections working, add new ones with `to_html()`. Minimizes changes to working code. The equity and drawdown charts use the template's inline JS; new charts (heatmap, regime, benchmark) use plotly `to_html()` injection.

### Buy & Hold Overlay on Equity Chart
The existing template renders a single equity line. To add buy & hold comparison (VRFY-02):
- Modify the template's equity chart JS to accept a second trace: `var buyholdData = {{ buyhold_data }};`
- Add the buy & hold trace to the `Plotly.newPlot()` call

## Integration Points with Prior Phases

### Artifacts Consumed from Execute Phase
| Artifact | Path | Content | Used For |
|----------|------|---------|----------|
| Best result | `.pmf/phases/phase_N_best_result.json` | Best params, IS/OOS metrics, stop reason | Report metrics, export params |
| Iteration verdicts | `.pmf/phases/phase_N_execute/iter_NN_verdict.json` | Per-iteration metrics, AI hypothesis, params | Iteration table, parameter sensitivity |
| Iteration params | `.pmf/phases/phase_N_execute/iter_NN_params.json` | Parameters per iteration | Heatmap data, parameter evolution |
| Iteration metrics | `.pmf/phases/phase_N_execute/iter_NN_metrics.json` | IS metrics per iteration | Iteration table |
| OOS metrics | `.pmf/phases/phase_N_execute/iter_NN_oos_metrics.json` | OOS metrics per iteration | IS vs OOS comparison |
| Cached OHLCV | `.pmf/cache/{asset}_{source}_{timeframe}.parquet` | Raw market data | Regime classification, benchmark computation, equity curve reconstruction |
| Strategy spec | `.pmf/STRATEGY.md` | Strategy type, asset, targets | PineScript generation, report title, target comparison |
| Discuss decisions | `.pmf/phases/phase_N_discuss.md` | Entry/exit logic, indicators | PineScript logic, trading rules |
| Plan decisions | `.pmf/phases/phase_N_plan.md` | Parameter space, optimization method | Heatmap (grid search check), parameter ranges |

### State Updates
| Action | STATE.md Change |
|--------|----------------|
| --approved | Status = APPROVED, mark Verify [x], add Best Results row, add History entry, update Last Updated |
| --debug | Keep IN PROGRESS, increment phase N to N+1, add new Phase N+1 checklist, add History entry with diagnosis summary |

## Open Questions

1. **Equity Curve Reconstruction for Report**
   - What we know: `run_backtest()` returns `compute_all_metrics()` output which includes trades but NOT the raw bar-level equity array (it's computed internally but not returned in the dict)
   - What's unclear: The verify report needs the full bar-level equity curve with dates for a proper time-series plotly chart. The execute phase stores per-iteration equity PNGs but not the raw equity data.
   - Recommendation: The verify report Python script should re-run the best iteration's backtest (using best params from best_result.json) to capture the full equity curve. This is fast since data is cached. Alternatively, modify `compute_all_metrics` to return the equity array -- but that modifies a fixed reference file. **Re-running is safer.**

2. **Template Modification vs New Template**
   - What we know: D-02 says "fill the existing template." But the template needs new sections (heatmap, regime, benchmark) and modifications (buy & hold overlay).
   - What's unclear: Does "fill" mean only inject data into existing placeholders, or can we extend the template structure?
   - Recommendation: Extend the template with new sections. D-02's intent is "use the template as structure, not generate from scratch." Adding sections to the existing template is consistent with this intent.

## Validation Architecture

### Test Framework
| Property | Value |
|----------|-------|
| Framework | pytest (already installed in venv) |
| Config file | None -- see Wave 0 |
| Quick run command | `~/.pmf/venv/bin/python -m pytest tests/ -x -q` |
| Full suite command | `~/.pmf/venv/bin/python -m pytest tests/ -v` |

### Phase Requirements -> Test Map
| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|-------------|
| VRFY-01 | HTML report is standalone, contains plotly | smoke | Manual: open generated HTML in browser | N/A manual |
| VRFY-02 | Equity curve has strategy + buy&hold traces | unit | Test report generation script outputs both traces | Wave 0 |
| VRFY-03 | Drawdown chart with max DD line | unit | Test drawdown computation and chart data | Wave 0 |
| VRFY-04 | Iteration table from verdict JSONs | unit | Test iteration data loading and table rendering | Wave 0 |
| VRFY-05 | Parameter heatmap for grid search | unit | Test heatmap data construction from params | Wave 0 |
| VRFY-06 | Trade list with P&L coloring | unit | Test trade data formatting | Wave 0 |
| VRFY-07 | Regime breakdown | unit | Test regime classification function | Wave 0 |
| VRFY-08 | Benchmark alpha/beta | unit | Test benchmark stats computation | Wave 0 |
| VRFY-09 | Metrics vs targets table | unit | Test metrics comparison formatting | Wave 0 |
| VRFY-10 | AI analysis formulates conclusion | manual-only | Requires Claude reading data | N/A |
| VRFY-11 | --approved closes milestone | integration | Test STATE.md update | Wave 0 |
| VRFY-12 | --debug opens new phase cycle | integration | Test STATE.md phase increment | Wave 0 |
| EXPT-01 | Valid PineScript v5 strategy | manual-only | Paste into TradingView Pine Editor | N/A |
| EXPT-02 | trading-rules.md content | manual-only | Review for practitioner tone | N/A |
| EXPT-03 | performance-report.md content | unit | Test markdown generation | Wave 0 |
| EXPT-04 | backtest_final.py runs standalone | smoke | Execute script with cached data | Wave 0 |
| EXPT-05 | live-checklist.md content | manual-only | Review for completeness | N/A |
| EXPT-06 | Report HTML copied to output/ | unit | Test file copy | Wave 0 |
| EXPT-07 | All exports in output/ | integration | Check all expected files exist | Wave 0 |

### Sampling Rate
- **Per task commit:** `~/.pmf/venv/bin/python -m pytest tests/ -x -q`
- **Per wave merge:** `~/.pmf/venv/bin/python -m pytest tests/ -v`
- **Phase gate:** Full suite green before `/gsd:verify-work`

### Wave 0 Gaps
- [ ] `tests/test_report_generation.py` -- covers VRFY-02 through VRFY-09 (regime classification, benchmark stats, data formatting)
- [ ] `tests/test_export_package.py` -- covers EXPT-03, EXPT-04, EXPT-06, EXPT-07 (file generation and completeness)
- [ ] Test fixtures: mock iteration artifacts (verdict JSONs, metrics JSONs, params JSONs, best_result.json)

*(Note: Many requirements are manual-only (PineScript validation, AI analysis, practitioner tone review) -- these require human verification via the workflow itself)*

## Sources

### Primary (HIGH confidence)
- [Plotly interactive HTML export](https://plotly.com/python/interactive-html-export/) -- `to_html()`, `full_html`, `include_plotlyjs` parameters
- [Plotly `to_html` API reference](https://plotly.com/python-api-reference/generated/plotly.io.to_html.html) -- parameter documentation for v6.6.0
- [Plotly heatmaps](https://plotly.com/python/heatmaps/) -- `go.Heatmap` for parameter heatmap
- [TradingView PineScript v5/v6 migration guide](https://www.tradingview.com/pine-script-docs/migration-guides/to-pine-version-6/) -- v5 vs v6 differences
- [TradingView alerts documentation](https://www.tradingview.com/pine-script-docs/concepts/alerts/) -- `alert()` vs `alertcondition()`
- Existing codebase: `templates/report-template.html`, `templates/pinescript-template.pine`, `references/pinescript-examples/*.pine`, `references/metrics.py`, `references/backtest_engine.py`, `workflows/execute.md`

### Secondary (MEDIUM confidence)
- [Pine Script v5 vs v6 comparison (traderspost.io)](https://blog.traderspost.io/article/pine-script-v5-vs-v6-comparison) -- v6 feature summary
- [Plotly Jinja2 community thread](https://community.plotly.com/t/how-to-render-graphs-in-jinja-template/35541) -- community pattern for Jinja2 integration
- [Pineify alertcondition guide](https://pineify.app/resources/blog/pine-script-alertcondition-complete-guide-to-creating-custom-tradingview-alerts) -- alertcondition syntax and limitations

### Tertiary (LOW confidence)
- None -- all findings verified against official sources

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH -- all libraries already installed, APIs verified against official docs
- Architecture: HIGH -- follows established patterns from execute.md, template already exists
- Pitfalls: HIGH -- based on known plotly/Jinja2 integration issues and PineScript syntax rules
- Report generation: HIGH -- plotly `to_html()` pattern well-documented
- PineScript generation: MEDIUM -- Claude generates code from templates + examples, no automated validation possible (only TradingView Pine Editor can validate)
- Regime/benchmark computation: HIGH -- standard financial computation using scipy/pandas/ta

**Research date:** 2026-03-21
**Valid until:** 2026-04-21 (stable domain -- plotly, PineScript v5, jinja2 are mature)
