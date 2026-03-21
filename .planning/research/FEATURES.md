# Feature Landscape

**Domain:** AI-assisted trading strategy development CLI (backtest-to-export pipeline)
**Researched:** 2026-03-21

## Table Stakes

Features users expect. Missing = product feels incomplete.

### Backtest Engine

| Feature | Why Expected | Complexity | Notes |
|---------|--------------|------------|-------|
| Core metrics suite (net P&L, win rate, profit factor, max drawdown, Sharpe ratio, Sortino ratio) | Every backtest tool reports these. Traders evaluate strategies on these numbers. Missing any = tool feels amateur. | Low | Compute from trade log. Sharpe/Sortino need daily returns series. |
| Equity curve visualization | Traders need to see account growth over time. The single most-looked-at chart. | Low | Per-iteration PNG during execute, interactive plotly in final report. Already in PROJECT.md. |
| Drawdown chart | Traders obsess over drawdown. Seeing peak-to-trough decline visually is non-negotiable. | Low | Plot alongside equity curve. Show max drawdown line. |
| Trade log with per-trade details | Traders audit individual trades: entry/exit time, price, size, P&L, holding period. Without this, results are a black box. | Low | DataFrame output from backtest engine. Include in HTML report as sortable table. |
| Commission and slippage modeling | Ignoring transaction costs produces fantasy results. Traders know this and distrust tools that skip it. | Low | Configurable per-trade commission (flat or %) and slippage (fixed or % of spread). Set during discuss phase. |
| Multiple timeframes of historical data | Strategies need sufficient data. At minimum: daily bars for stocks/crypto/forex. | Med | ccxt (crypto), yfinance (stocks/forex daily). Already planned. Key: handle gaps, timezone alignment. |
| Position sizing | Fixed lot, percentage of equity, and volatility-based (ATR) sizing are baseline expectations. | Low | Discussed in discuss phase, implemented in backtest code. |
| Stop-loss and take-profit | Every serious strategy has risk management. Entry-only strategies are toys. | Low | Fixed, trailing, ATR-based stops. Set during discuss phase. |
| Parameter optimization (grid search) | Traders expect to sweep parameter ranges and find best combinations. Grid search is the default everyone understands. | Med | Iterate parameter combos, track results, find best by target metric. |
| Out-of-sample / in-sample split | Testing on the same data you optimize on is the #1 beginner mistake. Tools must enforce train/test splits. | Low | Split data by date. Report both in-sample and out-of-sample metrics separately. |
| Overfitting detection warnings | Profit factor > 3.0, Sharpe > 3.0, or vastly different in-sample vs out-of-sample results = red flags. Tool should call these out. | Low | Heuristic checks on final metrics. AI analysis already planned for execute phase. |

### Workflow / CLI

| Feature | Why Expected | Complexity | Notes |
|---------|--------------|------------|-------|
| Clear phase progression (idea to results) | Users need to know where they are and what's next. Confusion = abandonment. | Low | STATUS command with ASCII tree. Already planned. |
| Persistent state between sessions | Strategy development spans days/weeks. Losing progress = dealbreaker. | Low | STATE.md and STRATEGY.md files. Already planned. |
| HTML report generation | Traders share results, review them outside terminal. Standalone HTML with embedded charts is the standard. | Med | Plotly-based. Already planned. Single file, no server needed. |
| Export to usable trading code | Backtest results without executable code are academic exercises. PineScript is the dominant retail format. | High | PineScript v5 generation is the hardest table-stakes feature. Must produce valid, runnable code. |
| Data source flexibility | Different asset classes need different data sources. Being locked to one = limited audience. | Med | Already planned: ccxt, yfinance, Dukascopy, polygon.io, CSV fallback. |
| Error recovery / resume | Backtest runs fail (API limits, bad data, Python errors). Users need to pick up where they left off, not restart. | Med | STATE.md tracks iteration progress. Execute phase should resume from last good iteration. |

## Differentiators

Features that set product apart. Not expected, but valued.

### AI-Driven (Unique to This Tool)

| Feature | Value Proposition | Complexity | Notes |
|---------|-------------------|------------|-------|
| AI-analyzed iteration loop | No other tool has AI look at backtest results, diagnose problems, adjust parameters, and re-run automatically. This is the core differentiator. Composer/Nvestiq do natural-language input but NOT iterative AI-driven optimization. | High | The execute phase loop: run backtest, AI reads metrics + equity curve, decides next parameter adjustment or stop condition. This is what makes PMF unique. |
| Natural language strategy input | Describe "fade failed breakouts at resistance" and the system understands. Competitors like Composer and Nvestiq offer this, but PMF does it through Claude Code which is more powerful for complex strategies. | Med | discuss phase converts natural language to formal strategy spec in STRATEGY.md. Claude's strength. |
| AI diagnosis on debug cycles | When verify produces --debug, AI reads the full report, identifies WHY the strategy underperformed, and suggests specific fixes. No competitor does post-mortem diagnosis. | Med | verify --debug triggers new phase cycle with AI diagnosis carried forward. Already planned. |
| Hypothesis drift protection | Detects when iterative tweaking has drifted so far from the original idea that it's a different strategy. Suggests opening a new milestone instead. | Low | Compare current parameters/logic to original STRATEGY.md. Already planned. |
| Context file understanding (images, PDFs) | Upload a chart screenshot or research paper, and the system incorporates it into strategy design. Unique to Claude Code's multimodal capabilities. | Med | .pmf/context/ directory. Already planned. Leverages Claude's vision. |

### Advanced Backtest Features

| Feature | Value Proposition | Complexity | Notes |
|---------|-------------------|------------|-------|
| Walk-forward analysis | The "gold standard" for strategy validation per industry consensus. Splits data into rolling in-sample/out-of-sample windows. Most retail tools skip this. | High | Computationally expensive. Plan phase should offer this as an optimization method. Worth implementing but flag as advanced. |
| Parameter heatmap visualization | 2D color grid showing how performance varies across two parameters. Immediately reveals whether a strategy is robust (broad plateau) or fragile (narrow spike). | Med | Already planned for HTML report. Use plotly heatmap. |
| Regime breakdown analysis | Show performance split by market regime (trending, ranging, volatile). Traders need to know WHEN their strategy works, not just IF. | Med | Classify periods by volatility or trend strength. Report metrics per regime. Already mentioned in PROJECT.md. |
| Bayesian optimization | Smarter than grid search for large parameter spaces. Finds good parameters in fewer iterations. | High | Optuna is already in the planned dependency list. Use TPE sampler. |
| Monte Carlo simulation | Randomize trade order to show range of possible equity curves. Reveals how much of the result is path-dependent luck. | Med | Shuffle trade returns, generate N equity curves, show confidence bands. Powerful for risk assessment. |
| Correlation to benchmark | Show strategy returns vs buy-and-hold or market index. Traders need to know if they're beating passive. | Low | Compute alpha, beta, correlation coefficient. Display on report. |

### Export / Delivery

| Feature | Value Proposition | Complexity | Notes |
|---------|-------------------|------------|-------|
| Trading rules document (plain English) | Machine-readable rules are great, but traders also need human-readable rules for discipline. | Low | Already planned (trading-rules.md). Claude generates from STRATEGY.md. |
| Live trading checklist | Step-by-step guide: which broker, what settings, position size for account X, what to monitor. Bridges the gap from backtest to live. | Low | Already planned (live-checklist.md). Template-driven. |
| Python backtest as reproducible artifact | Final backtest script that anyone can re-run to verify results. Transparency builds trust. | Low | Already planned (backtest_final.py). |
| Performance report (markdown) | Portable summary for sharing in forums, Discord, journals. | Low | Already planned (performance-report.md). |

## Anti-Features

Features to explicitly NOT build.

| Anti-Feature | Why Avoid | What to Do Instead |
|--------------|-----------|-------------------|
| Live trading execution | Massive liability, regulatory risk, scope creep. Live trading is a fundamentally different problem (connectivity, order management, risk controls, latency). Mixing it with backtesting produces bad backtesting AND bad live trading. | Export PineScript/Python. User connects to their own broker. Live trading is explicitly out of scope per PROJECT.md. |
| Real-time data streaming | Adds infrastructure complexity (websockets, rate limits, reconnection). Not needed for backtesting. | Use historical data downloads. Cache locally. |
| Web UI or dashboard | Splits development effort. Claude Code IS the interface. Building a web UI means maintaining two interfaces that drift apart. | Terminal-only via slash commands. HTML reports are read-only output, not interactive UI. |
| Multi-strategy portfolio backtesting | Exponentially more complex: correlation, capital allocation, rebalancing. Solving a different problem than single-strategy development. | One strategy per milestone. Portfolio construction is a separate tool. |
| Built-in indicator library | Maintaining 200+ indicators is a maintenance nightmare. Claude can implement any indicator on-the-fly from its training data. | Claude writes indicator calculations inline in the backtest code. Describe what you need, Claude codes it fresh. |
| Paper trading simulation | Different from backtesting (requires live data feed, order simulation, clock sync). Half-measure between backtest and live. | Export to TradingView for paper trading via PineScript. |
| User accounts / cloud storage | This is a local tool. Adding auth and cloud storage violates the zero-infrastructure principle. | Everything is local files. Git handles versioning. |
| Genetic/evolutionary strategy generation | StrategyQuant / Build Alpha territory. Generates thousands of random strategies and picks winners. Produces overfitted garbage without deep domain knowledge guiding it. | AI-guided iteration from a human hypothesis. The human + AI loop is the right approach. |
| Intraday tick-level simulation | Tick data is enormous, slow to process, and rarely available for free. Bar-level simulation is sufficient for 95% of retail strategies. | OHLCV bars at various timeframes. Minute bars are the finest practical resolution. |

## Feature Dependencies

```
Commission/slippage modeling --> Accurate metrics (all metrics depend on realistic cost modeling)
Data sourcing (ccxt/yfinance) --> Backtest execution (can't run without data)
Core metrics suite --> Equity curve + drawdown chart (computed from same data)
Core metrics suite --> Overfitting detection (heuristics on metric values)
Parameter optimization --> Parameter heatmap (heatmap is a visualization of optimization results)
In-sample/out-of-sample split --> Walk-forward analysis (WFA generalizes the split concept)
discuss phase (strategy spec) --> execute phase (backtest needs formal rules)
execute phase (backtest loop) --> verify phase (needs results to report on)
verify phase (report) --> export (needs approved strategy to export)
AI iteration loop --> Hypothesis drift protection (needs baseline + current to compare)
Bayesian optimization --> optuna dependency (already planned)
Regime breakdown --> Market regime classifier (volatility/trend detection)
```

## MVP Recommendation

Prioritize (Phase 1 - must ship for the tool to be usable):

1. **Core metrics suite** - Net P&L, win rate, profit factor, max drawdown, Sharpe, Sortino, expectancy, trade count
2. **Commission and slippage modeling** - Without this, all metrics are lies
3. **Equity curve + drawdown visualization** - Per-iteration PNG, plotly in final report
4. **Trade log** - Per-trade details in report
5. **In-sample / out-of-sample split** - Enforced by default
6. **Grid search optimization** - Simple, understandable parameter sweeping
7. **AI iteration loop** - THE differentiator. If this works well, the tool has a reason to exist
8. **HTML report generation** - Traders need a deliverable to review
9. **PineScript v5 export** - Bridge from backtest to live trading
10. **Single data source working** (ccxt for crypto OR yfinance for stocks) - Expand later

Defer to Phase 2:
- Walk-forward analysis: Valuable but complex. Grid search + in/out-of-sample is sufficient for v1.
- Bayesian optimization: Optuna integration after grid search proves the loop works.
- Monte Carlo simulation: Nice-to-have for risk assessment, not blocking.
- Regime breakdown: Requires market classifier. Add after core reporting works.
- Multiple data sources: Ship with one working source, add others incrementally.
- Parameter heatmap: Needs optimization data structure. Add after optimization is solid.
- Context file support (images/PDFs): Powerful but not blocking the core loop.

Defer indefinitely:
- Correlation to benchmark: Low effort but low priority. Add when someone asks.

## Competitive Landscape Context

| Competitor | Strengths | What PMF Does Better |
|------------|-----------|---------------------|
| TradingView Strategy Tester | Huge user base, built-in charting, PineScript ecosystem | PMF: AI-driven iteration, not manual tweak-and-retest cycles |
| QuantConnect | Multi-asset, cloud backtesting, institutional grade | PMF: Zero infrastructure, natural language input, no learning curve for quant libraries |
| Composer | Natural language strategy input, no-code | PMF: Deeper iteration loop, debug diagnosis, Claude handles complex strategies Composer can't express |
| Nvestiq | Natural language, one-click deployment | PMF: Full control over backtest code, export artifacts, transparent methodology |
| backtesting.py | Clean Python API, parameter optimization, heatmaps | PMF: AI writes the code, no Python knowledge needed from user |
| Build Alpha / StrategyQuant | Automated strategy generation, massive search | PMF: Human hypothesis + AI refinement vs. brute-force search. Better strategies, less overfitting. |

## Sources

- [FX Replay - 5 KPIs That Matter Most](https://www.fxreplay.com/learn/the-5-kpis-that-matter-most-in-backtesting-a-strategy) - Metrics baseline
- [TrendSpider - Basic Backtesting Metrics](https://trendspider.com/learning-center/basic-backtesting-metrics/) - Table stakes metrics
- [TrendSpider - Advanced Backtesting Metrics](https://trendspider.com/learning-center/advanced-backtesting-metrics/) - Advanced metrics
- [LuxAlgo - Top 7 Metrics](https://www.luxalgo.com/blog/top-7-metrics-for-backtesting-results/) - Metric priorities
- [Algo Strategy Analyzer - Advanced Trading Metrics 2026](https://algostrategyanalyzer.com/en/blog/advanced-trading-metrics/) - Sharpe, Sortino, Calmar, SQN
- [LuxAlgo - Backtesting Traps](https://www.luxalgo.com/blog/backtesting-traps-common-errors-to-avoid/) - Overfitting, lookahead bias
- [Interactive Brokers - Walk Forward Analysis](https://www.interactivebrokers.com/campus/ibkr-quant-news/the-future-of-backtesting-a-deep-dive-into-walk-forward-analysis/) - WFA as gold standard
- [backtesting.py - Parameter Heatmap](https://kernc.github.io/backtesting.py/doc/examples/Parameter%20Heatmap%20&%20Optimization.html) - Heatmap visualization patterns
- [QuantConnect - Backtest Analysis](https://www.quantconnect.com/docs/v2/research-environment/meta-analysis/backtest-analysis) - Report structure
- [Composer](https://www.composer.trade/) - Natural language strategy competitor
- [Capitalise.ai](https://capitalise.ai/) - Code-free automation competitor
- [newtrading.io - Backtesting Software 2026](https://www.newtrading.io/backtesting-software/) - Market overview
- [AnalystPrep - Problems in Backtesting](https://analystprep.com/study-notes/cfa-level-2/problems-in-backtesting/) - Academic pitfalls reference
