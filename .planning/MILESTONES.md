# Milestones

## v1.1 Enhancement (Shipped: 2026-03-22)

**Phases completed:** 5 phases, 9 plans, 13 tasks

**Key accomplishments:**

- Fixed blank equity PNGs by returning equity_curve from run_backtest() and using it directly in execute.md PNG generation with zero-trade guard
- `/brrr:doctor` slash command with 6-category health check: Python version, venv, 10 library imports via actual `python -c import`, command/workflow/reference file integrity, and HEALTHY/NEEDS ATTENTION verdict
- Structured diagnosis JSON artifact in verify --debug with failed_approaches, do_not_retry entries, and append-only semantics
- Discuss workflow reads all diagnosis JSONs, presents Prior Debug Cycles failure table, and enforces do_not_retry constraints on AI suggestions
- Optuna bridge module with Ask-and-Tell lifecycle, TPE/CMA-ES auto-selection, composite scoring, and SQLite persistence
- Bayesian optimization added as fourth method in plan workflow Step 4 with auto-selection at >500 combinations, override prompt, and plan artifact fields
- Bayesian Ask-and-Tell branch integrated into execute workflow with warmup/guided display, SQLite resume, and CMA-ES sampler persistence
- Bot-building-guide.md generation step added to verify workflow with platform-specific deployment instructions for crypto (ccxt), stocks (alpaca/ib_async), and forex (oandapyV20/MT5)

---

## v1.0 MVP (Shipped: 2026-03-22)

**Phases completed:** 5 phases, 14 plans, 25 tasks

**Key accomplishments:**

- npm package with 8 thin slash commands, ESM install script handling Python 3.10+ venv creation, and 14 backtest dependencies
- 9 core financial metrics (Sharpe, Sortino, Calmar, MaxDD, win rate, profit factor, expectancy, trade count, net PnL) with 32 known-answer tests via TDD
- Backtest engine skeleton with anti-lookahead enforcement, 3 data source adapters, PineScript v5 templates/examples, and 7 workflow stubs
- Full install pipeline validated: 8 commands + 29 support files copied, Python 3.14 venv with 14 dependencies, 32 metrics tests passing, idempotent reinstall confirmed
- Full guided conversation workflow for milestone creation with context scanning, smart scope defaults, strategy-type success criteria, and sequence validation reference
- Full ASCII status tree workflow parsing STATE.md to display milestone progress, phase steps with [DONE]/[WIP]/[SKIP] icons, inline metrics, best results, and actionable next step
- Complete 512-line behavioral workflow for /brrr:discuss with three modes, drift detection hard gate, and 7-topic decision tracker
- Complete behavioral research workflow with training-data-first approach, pitfall cross-referencing, --deep mode web search via WebFetch, and auto-recommendation logic
- Complete /brrr:plan behavioral workflow with parameter space design, optimization method auto-selection, overfitting budget check, evaluation criteria, and train/test split configuration
- Fixed yfinance multi-level column bug in data_sources.py and replaced execute.md 10-line stub with 1067-line AI backtest optimization loop workflow covering all 19 EXEC/DATA requirements
- Human-verified the complete AI backtest loop: iteration display, artifact creation, stop conditions, and STATE.md updates all confirmed working
- Standalone HTML report template with 9 sections and Python generator module using SMA+ADX regime classification, scipy benchmark stats, and Jinja2 rendering
- Complete verify.md behavioral workflow (999 lines) with PineScript v5 syntax rules reference, covering report generation, AI assessment, 7-file export package on --approved, and diagnosis-driven debug cycles on --debug
- Install script confirmed to copy all Phase 5 files; /brrr:verify human-verified with working HTML report, interactive charts, and approval flow

---
