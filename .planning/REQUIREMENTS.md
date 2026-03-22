# Requirements: Print Money Factory

**Defined:** 2026-03-22
**Core Value:** The iterative backtest loop must work end-to-end: idea -> backtest -> AI analysis -> adjustment -> repeat until targets hit or strategy diagnosed unviable.

## v1.1 Requirements

### Bug Fixes

- [x] **BFIX-01**: Equity PNG shows actual equity curve data during `/brrr:execute` iterations (not blank)

### Optimization

- [ ] **OPT-01**: `/brrr:execute` uses Optuna TPE sampler for Bayesian parameter optimization via Ask-and-Tell API
- [ ] **OPT-02**: Optuna auto-selects CMA-ES sampler when all parameters are continuous, TPE otherwise
- [ ] **OPT-03**: Optuna study persists to SQLite so `--resume` preserves the Bayesian probability model
- [x] **OPT-04**: `/brrr:plan` includes Bayesian as an optimization method option alongside grid/random/walk-forward

### Debug Cycles

- [x] **DBUG-01**: `/brrr:verify --debug` writes a structured diagnosis JSON with failed approaches, parameter regions, and explicit "do NOT retry" entries
- [x] **DBUG-02**: `/brrr:discuss` in debug mode reads all prior diagnosis artifacts and presents them as context before gathering new decisions
- [x] **DBUG-03**: Debug memory is phase-scoped and size-capped (max 50 entries) to prevent context explosion

### Maintenance

- [x] **MANT-01**: `/brrr:doctor` checks Python version, venv existence, dependency imports, command file integrity, and reports pass/fail per check
- [x] **MANT-02**: Every `/brrr:*` command silently checks for new npm version (once per session via timestamp file) and displays update notice if available

### Export

- [ ] **EXPT-08**: `/brrr:verify --approved` generates a `bot-building-guide.md` with platform-specific step-by-step instructions for going live

## v2 Requirements

### Advanced Optimization

- **OPT-05**: Monte Carlo simulation -- randomize trade order to show equity curve confidence bands

### Additional Data Sources

- **DATA-06**: polygon.io integration for stocks intraday (requires API key)
- **DATA-07**: Dukascopy integration for forex intraday tick data
- **DATA-08**: cryptodatadownload.com CSV integration
- **DATA-09**: Kraken bulk CSV integration

## Out of Scope

| Feature | Reason |
|---------|--------|
| Live trading bot (Binance/MetaTrader) | Separate domain -- always a separate milestone after proven strategy |
| Real-time data streaming | Not needed for backtesting, adds infrastructure complexity |
| Web UI / dashboard | Claude Code IS the interface; HTML reports are read-only output |
| Multi-strategy portfolio backtesting | Different problem -- correlation, allocation, rebalancing |
| Multi-objective Optuna optimization | Adds plan.md/verify.md complexity -- defer to v1.2 |
| Full runnable bot code in export | Bot-building guide stays at "code pattern" level, not full bot |

## Traceability

| Requirement | Phase | Status |
|-------------|-------|--------|
| BFIX-01 | Phase 6 | Complete |
| OPT-01 | Phase 9 | Pending |
| OPT-02 | Phase 9 | Pending |
| OPT-03 | Phase 9 | Pending |
| OPT-04 | Phase 9 | Complete |
| DBUG-01 | Phase 8 | Complete |
| DBUG-02 | Phase 8 | Complete |
| DBUG-03 | Phase 8 | Complete |
| MANT-01 | Phase 7 | Complete |
| MANT-02 | Phase 7 | Complete |
| EXPT-08 | Phase 10 | Pending |

**Coverage:**
- v1.1 requirements: 11 total
- Mapped to phases: 11
- Unmapped: 0

---
*Requirements defined: 2026-03-22*
*Last updated: 2026-03-22 after roadmap creation*
