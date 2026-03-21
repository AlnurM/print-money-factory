# Requirements: Print Money Factory

**Defined:** 2026-03-21
**Core Value:** The iterative backtest loop must work end-to-end: idea -> backtest -> AI analysis -> adjustment -> repeat until targets hit or strategy diagnosed unviable.

## v1 Requirements

### Installation & Setup

- [x] **INST-01**: User can install via `npx print-money-factory install` -- copies commands to `~/.claude/commands/brrr/`
- [x] **INST-02**: Install creates isolated Python venv with all backtest dependencies (pandas, numpy, ccxt, yfinance, plotly, ta, matplotlib, optuna)
- [x] **INST-03**: Install detects Python 3.10+ and fails gracefully with clear error if missing
- [x] **INST-04**: Install is idempotent -- running twice doesn't break anything
- [x] **INST-05**: `/brrr:update` checks GitHub for new version, shows changelog, updates commands and workflows

### Milestone Management

- [ ] **MILE-01**: `/brrr:new-milestone` creates milestone with strategy idea, scope selection, asset/data source, and success criteria
- [ ] **MILE-02**: Scope selection includes: strategy, backtest, tuning, risk management, PineScript export, MD instructions export
- [ ] **MILE-03**: System recommends scope splitting when selection is too large
- [ ] **MILE-04**: One active milestone at a time -- new milestone only after current is approved
- [ ] **MILE-05**: `/brrr:status` shows ASCII tree of milestone progress, all phases, next step

### Context Files

- [ ] **CTXT-01**: System checks `.pmf/context/` at start of each command for new files (images, PDFs, screenshots)
- [ ] **CTXT-02**: System parses and describes what it sees in context files, asks user for confirmation before incorporating
- [ ] **CTXT-03**: Context files are included in subsequent phase artifacts after confirmation

### Discuss Phase

- [ ] **DISC-01**: `/brrr:discuss` collects all strategy decisions: entry/exit logic, stops, take-profit, position sizing, commission assumptions, parameter ranges
- [ ] **DISC-02**: First discuss builds strategy spec from scratch via guided conversation
- [ ] **DISC-03**: Debug discuss starts from previous verify diagnosis -- AI reads full milestone context and formulates starting hypothesis
- [ ] **DISC-04**: Hypothesis drift protection -- detects when user changes exceed original strategy scope, offers new milestone
- [ ] **DISC-05**: `--auto` flag lets Claude choose reasonable defaults with minimal questions
- [ ] **DISC-06**: Outputs `phase_N_discuss.md` with all decisions fixed

### Research Phase

- [ ] **RSCH-01**: `/brrr:research` finds known implementations, academic work, and formalization alternatives for the strategy type
- [ ] **RSCH-02**: Warns about known lookahead traps specific to the strategy type
- [ ] **RSCH-03**: Recommends when research is needed (non-standard strategies) vs optional (classic strategies)
- [ ] **RSCH-04**: `--deep` flag for extended search across multiple sources
- [ ] **RSCH-05**: Outputs `phase_N_research.md`

### Plan Phase

- [ ] **PLAN-01**: `/brrr:plan` defines parameter space -- fixed params and free params with ranges and step sizes
- [ ] **PLAN-02**: Defines constraints between parameters (e.g., fast_period < slow_period)
- [ ] **PLAN-03**: Selects optimization method: grid search (< 1000 combos), random search, walk-forward (3+ free params, recommended)
- [ ] **PLAN-04**: Sets evaluation criteria: primary metric (Sharpe), secondary metrics (Max DD, Win Rate, Profit Factor)
- [ ] **PLAN-05**: Enforces minimum trade count threshold (default 30)
- [ ] **PLAN-06**: Defines data period, timeframe, and train/test split
- [ ] **PLAN-07**: Enforces parameter budget to prevent overfitting (limits on number of free parameters vs data size)
- [ ] **PLAN-08**: Outputs `phase_N_plan.md`

### Execute Phase

- [ ] **EXEC-01**: `/brrr:execute` runs AI-driven backtest loop: load data -> run backtest -> compute metrics -> AI analyzes -> adjust params -> repeat
- [ ] **EXEC-02**: Claude writes Python backtest engine from scratch based on plan phase decisions -- no fixed library
- [ ] **EXEC-03**: Data sourcing via ccxt (crypto exchanges), yfinance (stocks daily, forex daily), with CSV fallback
- [ ] **EXEC-04**: Core metrics computed per iteration: Sharpe, Sortino, Calmar, Max DD, Win Rate, Profit Factor, expectancy, trade count, net P&L
- [ ] **EXEC-05**: Commission and slippage modeling included from first iteration -- configurable per-trade flat or percentage
- [ ] **EXEC-06**: In-sample / out-of-sample split enforced -- metrics reported separately for both
- [ ] **EXEC-07**: Walk-forward analysis available as optimization method -- rolling train/test windows
- [ ] **EXEC-08**: Stop conditions: MINT (targets hit), PLATEAU (3 iterations without >5% improvement), REKT (no edge at any params), NO DATA
- [ ] **EXEC-09**: AI reads metrics and equity curve each iteration, diagnoses what's working/not, decides next parameter adjustment
- [ ] **EXEC-10**: Per-iteration artifacts saved: params JSON, metrics JSON, equity PNG (matplotlib), verdict JSON
- [ ] **EXEC-11**: Real-time terminal display showing iteration progress, current params, metrics, AI commentary
- [ ] **EXEC-12**: `--iterations N` flag (default 10), `--fast` (no charts), `--resume` (continue from last iteration)
- [ ] **EXEC-13**: Overfitting detection -- warns when in-sample/out-of-sample diverge significantly or metrics look too good
- [ ] **EXEC-14**: Outputs `phase_N_best_result.json`

### Verify Phase

- [ ] **VRFY-01**: `/brrr:verify` generates interactive standalone HTML report (plotly, no server)
- [ ] **VRFY-02**: Report includes equity curve (strategy vs buy & hold) with zoom
- [ ] **VRFY-03**: Report includes drawdown chart with max drawdown line
- [ ] **VRFY-04**: Report includes iteration table -- all iterations with params and how Sharpe evolved
- [ ] **VRFY-05**: Report includes parameter heatmap (if grid search was used)
- [ ] **VRFY-06**: Report includes trade list with per-trade P&L coloring
- [ ] **VRFY-07**: Report includes regime breakdown -- performance in bull/bear/sideways
- [ ] **VRFY-08**: Report includes benchmark correlation -- alpha, beta vs buy-and-hold
- [ ] **VRFY-09**: Report includes metrics summary table -- all metrics vs targets
- [ ] **VRFY-10**: AI analyzes full report and formulates conclusion with specific assessment
- [ ] **VRFY-11**: `--approved` closes milestone, triggers export package generation
- [ ] **VRFY-12**: `--debug` keeps milestone open, AI diagnoses failure, opens new phase cycle with diagnosis as starting point

### Export (on --approved)

- [ ] **EXPT-01**: PineScript v5 code -- valid, runnable TradingView strategy
- [ ] **EXPT-02**: `trading-rules.md` -- plain English entry/exit/sizing rules
- [ ] **EXPT-03**: `performance-report.md` -- portable metrics summary for sharing
- [ ] **EXPT-04**: `backtest_final.py` -- reproducible Python script, runs standalone
- [ ] **EXPT-05**: `live-checklist.md` -- step-by-step guide before real money
- [ ] **EXPT-06**: `report_vN.html` -- copy of the final interactive HTML report
- [ ] **EXPT-07**: All exports in `output/` directory

### State Management

- [ ] **STAT-01**: STATE.md tracks current milestone, status, all phases with step completion
- [ ] **STAT-02**: STATE.md records best metrics per phase (Sharpe, DD, trades)
- [ ] **STAT-03**: Commands validate sequence -- cannot run execute without plan, verify without execute
- [ ] **STAT-04**: STRATEGY.md captures original hypothesis and scope from new-milestone
- [ ] **STAT-05**: Phase artifacts are append-only -- history never overwritten

### Data Sources

- [ ] **DATA-01**: ccxt integration for crypto -- auto-detect exchange from user's trading exchange for data fidelity
- [ ] **DATA-02**: yfinance integration for stocks (daily) and forex (daily)
- [ ] **DATA-03**: CSV fallback for any asset -- user provides historical data file
- [ ] **DATA-04**: Data validation before every backtest -- check for gaps, NaN values, timezone issues
- [ ] **DATA-05**: Local data caching to avoid re-downloading

### Package Architecture

- [x] **ARCH-01**: npm package structure mirrors GSD: commands/, workflows/, templates/, references/
- [x] **ARCH-02**: Commands are thin markdown files that @-reference workflow files
- [x] **ARCH-03**: Fixed metrics module (not regenerated by Claude) with unit tests for financial calculations
- [ ] **ARCH-04**: Reference backtest engine patterns for Claude to adapt per strategy
- [ ] **ARCH-05**: Template files: STRATEGY.md, STATE.md, pinescript-template.pine, report-template.html

## v2 Requirements

### Advanced Optimization

- **OPT-01**: Bayesian optimization via optuna for large parameter spaces
- **OPT-02**: Monte Carlo simulation -- randomize trade order to show equity curve confidence bands

### Additional Data Sources

- **DATA-06**: polygon.io integration for stocks intraday (requires API key)
- **DATA-07**: Dukascopy integration for forex intraday tick data
- **DATA-08**: cryptodatadownload.com CSV integration
- **DATA-09**: Kraken bulk CSV integration

### Enhanced Export

- **EXPT-08**: MD-instruction format -- detailed bot-building guide for user's preferred language/platform

### Maintenance

- **MAINT-01**: `/brrr:doctor` diagnostic command -- checks Python version, venv health, dependencies, command installation
- **MAINT-02**: Auto version check on every `/brrr:*` command (silent, once per session)

## Out of Scope

| Feature | Reason |
|---------|--------|
| Live trading bot (Binance/MetaTrader) | Separate domain -- always a separate milestone after proven strategy |
| Real-time data streaming | Not needed for backtesting, adds infrastructure complexity |
| Web UI / dashboard | Claude Code IS the interface; HTML reports are read-only output |
| Multi-strategy portfolio backtesting | Different problem -- correlation, allocation, rebalancing |
| Built-in indicator library | Claude writes indicators inline per strategy from training data |
| Paper trading simulation | Different from backtesting -- export to TradingView for paper trading |
| User accounts / cloud storage | Local tool, zero-infrastructure principle |
| Genetic/evolutionary strategy generation | Produces overfitted garbage without human hypothesis guiding it |
| Intraday tick-level simulation | Bar-level (OHLCV) sufficient for retail; tick data is enormous and rarely free |
| Multiple simultaneous milestones | One at a time by design -- prevents strategy confusion |

## Traceability

| Requirement | Phase | Status |
|-------------|-------|--------|
| INST-01 | Phase 1 | Complete |
| INST-02 | Phase 1 | Complete |
| INST-03 | Phase 1 | Complete |
| INST-04 | Phase 1 | Complete |
| INST-05 | Phase 1 | Complete |
| MILE-01 | Phase 2 | Pending |
| MILE-02 | Phase 2 | Pending |
| MILE-03 | Phase 2 | Pending |
| MILE-04 | Phase 2 | Pending |
| MILE-05 | Phase 2 | Pending |
| CTXT-01 | Phase 2 | Pending |
| CTXT-02 | Phase 2 | Pending |
| CTXT-03 | Phase 2 | Pending |
| DISC-01 | Phase 3 | Pending |
| DISC-02 | Phase 3 | Pending |
| DISC-03 | Phase 3 | Pending |
| DISC-04 | Phase 3 | Pending |
| DISC-05 | Phase 3 | Pending |
| DISC-06 | Phase 3 | Pending |
| RSCH-01 | Phase 3 | Pending |
| RSCH-02 | Phase 3 | Pending |
| RSCH-03 | Phase 3 | Pending |
| RSCH-04 | Phase 3 | Pending |
| RSCH-05 | Phase 3 | Pending |
| PLAN-01 | Phase 3 | Pending |
| PLAN-02 | Phase 3 | Pending |
| PLAN-03 | Phase 3 | Pending |
| PLAN-04 | Phase 3 | Pending |
| PLAN-05 | Phase 3 | Pending |
| PLAN-06 | Phase 3 | Pending |
| PLAN-07 | Phase 3 | Pending |
| PLAN-08 | Phase 3 | Pending |
| EXEC-01 | Phase 4 | Pending |
| EXEC-02 | Phase 4 | Pending |
| EXEC-03 | Phase 4 | Pending |
| EXEC-04 | Phase 4 | Pending |
| EXEC-05 | Phase 4 | Pending |
| EXEC-06 | Phase 4 | Pending |
| EXEC-07 | Phase 4 | Pending |
| EXEC-08 | Phase 4 | Pending |
| EXEC-09 | Phase 4 | Pending |
| EXEC-10 | Phase 4 | Pending |
| EXEC-11 | Phase 4 | Pending |
| EXEC-12 | Phase 4 | Pending |
| EXEC-13 | Phase 4 | Pending |
| EXEC-14 | Phase 4 | Pending |
| VRFY-01 | Phase 5 | Pending |
| VRFY-02 | Phase 5 | Pending |
| VRFY-03 | Phase 5 | Pending |
| VRFY-04 | Phase 5 | Pending |
| VRFY-05 | Phase 5 | Pending |
| VRFY-06 | Phase 5 | Pending |
| VRFY-07 | Phase 5 | Pending |
| VRFY-08 | Phase 5 | Pending |
| VRFY-09 | Phase 5 | Pending |
| VRFY-10 | Phase 5 | Pending |
| VRFY-11 | Phase 5 | Pending |
| VRFY-12 | Phase 5 | Pending |
| EXPT-01 | Phase 5 | Pending |
| EXPT-02 | Phase 5 | Pending |
| EXPT-03 | Phase 5 | Pending |
| EXPT-04 | Phase 5 | Pending |
| EXPT-05 | Phase 5 | Pending |
| EXPT-06 | Phase 5 | Pending |
| EXPT-07 | Phase 5 | Pending |
| STAT-01 | Phase 2 | Pending |
| STAT-02 | Phase 2 | Pending |
| STAT-03 | Phase 2 | Pending |
| STAT-04 | Phase 2 | Pending |
| STAT-05 | Phase 2 | Pending |
| DATA-01 | Phase 4 | Pending |
| DATA-02 | Phase 4 | Pending |
| DATA-03 | Phase 4 | Pending |
| DATA-04 | Phase 4 | Pending |
| DATA-05 | Phase 4 | Pending |
| ARCH-01 | Phase 1 | Complete |
| ARCH-02 | Phase 1 | Complete |
| ARCH-03 | Phase 1 | Complete |
| ARCH-04 | Phase 1 | Pending |
| ARCH-05 | Phase 1 | Pending |

**Coverage:**
- v1 requirements: 80 total
- Mapped to phases: 80
- Unmapped: 0

---
*Requirements defined: 2026-03-21*
*Last updated: 2026-03-21 after roadmap creation*
