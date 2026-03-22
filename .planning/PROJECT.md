# Print Money Factory

## What This Is

An npm package for Claude Code that provides a complete trading strategy development pipeline via slash commands (`/brrr:*`). Users describe a trading idea, and the system iteratively develops, backtests, optimizes, and exports it — from hypothesis to ready-to-trade PineScript and Python code. One active milestone at a time, with debug cycles that accumulate phases until the strategy meets its targets.

## Core Value

The iterative backtest loop must work end-to-end: a user describes a strategy idea, the system backtests it, AI analyzes results, adjusts parameters, and repeats until targets are hit or the strategy is diagnosed as unviable.

## Requirements

### Validated

- ✓ Install via `npx print-money-factory install` — v1.0
- ✓ Package architecture mirrors GSD — v1.0
- ✓ `/brrr:new-milestone` — guided scoping flow — v1.0
- ✓ `/brrr:status` — ASCII tree with step icons — v1.0
- ✓ STATE.md tracks milestone status — v1.0
- ✓ `/brrr:discuss` — guided conversation, --auto, drift detection — v1.0
- ✓ `/brrr:research` — implementations, pitfalls, --deep mode — v1.0
- ✓ `/brrr:plan` — parameter space, optimization method, train/test split — v1.0
- ✓ `/brrr:execute` — AI-driven backtest loop, 4 stop conditions — v1.0
- ✓ Data sourcing via ccxt, yfinance, CSV — v1.0
- ✓ `/brrr:verify` — interactive HTML report (plotly), 9 sections — v1.0
- ✓ Export package: PineScript v5, trading-rules, performance-report, backtest, live-checklist, HTML — v1.0
- ✓ `/brrr:update` — re-install from npm — v1.0
- ✓ Claude-generated Python backtest engine — v1.0
- ✓ Context file support — v1.0
- ✓ Hypothesis drift protection — v1.0
- ✓ Sequence validation — v1.0
- ✓ Equity PNG fix — visible curves, zero-trade guard — v1.1
- ✓ `/brrr:doctor` — 6-category diagnostic command — v1.1
- ✓ Auto version check preamble in all workflows — v1.1
- ✓ Debug cycle memory — diagnosis JSON, do_not_retry enforcement — v1.1
- ✓ Bayesian optimization — Optuna TPE/CMA-ES via Ask-and-Tell, SQLite persistence — v1.1
- ✓ Bot-building guide — platform-specific deployment instructions on --approved — v1.1

### Active

(None — next milestone requirements TBD via `/gsd:new-milestone`)

### Out of Scope

- Live trading bot (Binance/MetaTrader) — always a separate milestone after proven strategy
- Multiple simultaneous milestones — one active at a time by design
- Web UI or dashboard — CLI-only via Claude Code slash commands
- Mobile app — not applicable
- User authentication — local tool, no accounts
- Real-time market data streaming — backtesting only, no live feeds
- Multi-objective Optuna optimization — defer to v1.2

## Context

**v1.1 shipped 2026-03-22** — published as `@print-money-factory/cli@0.5.0` on npm.

- 9 slash commands: new-milestone, discuss, research, plan, execute, verify, status, update, doctor
- 8 behavioral workflows + version check preamble in all
- Python modules: metrics.py, data_sources.py, backtest_engine.py, report_generator.py, optuna_bridge.py (new)
- 32 metrics tests + 14 report/export tests + 23 optuna bridge tests = 69 tests passing
- Bayesian optimization via Optuna Ask-and-Tell with SQLite persistence
- Debug cycle memory with structured diagnosis JSON and do_not_retry enforcement

## Constraints

- **Distribution**: Public npm package on npmjs.com — must work via `npx print-money-factory install`
- **Runtime**: Claude Code slash commands only — no standalone CLI, no server
- **Python**: All backtest code runs in a managed venv, not the system Python
- **Data**: Free data sources by default (ccxt, yfinance). Paid sources (polygon.io) optional with API keys
- **Reports**: Standalone HTML files (plotly embedded, no server needed)
- **Architecture**: Mirror GSD pattern — commands/, workflows/, templates/, references/ structure

## Key Decisions

| Decision | Rationale | Outcome |
|----------|-----------|---------|
| Claude writes backtest engine (not vectorbt/backtesting.py) | Maximum flexibility per strategy | ✓ Good |
| Python venv managed by install script | Zero-friction setup | ✓ Good |
| One milestone at a time | Keeps focus | ✓ Good |
| GSD-mirror architecture | Proven pattern | ✓ Good |
| Per-iteration PNGs + final HTML | Visual feedback + polished report | ✓ Good |
| SMA slope + ADX for regime classification | Simple, no lookahead | ✓ Good |
| PineScript v5 with migration comment | v5 universal in TradingView | ✓ Good |
| Both strategy() and indicator() exports | Different use cases | ✓ Good |
| Standalone HTML (no kaleido) | Portability | ✓ Good |
| Optuna Ask-and-Tell (not study.optimize) | Preserves per-iteration AI analysis loop | ✓ Good |
| CMA-ES for all-continuous, TPE otherwise | CMA-ES doesn't support categorical | ✓ Good |
| Composite score with capped penalty | Prevents drawdown domination | ✓ Good |
| Diagnosis JSON (not just markdown) | Machine-readable for discuss workflow | ✓ Good |
| ib_async (not ib_insync) in bot guide | ib_insync is archived | ✓ Good |

## Evolution

This document evolves at phase transitions and milestone boundaries.

**After each phase transition:**
1. Requirements invalidated? → Move to Out of Scope with reason
2. Requirements validated? → Move to Validated with milestone reference
3. New requirements emerged? → Add to Active
4. Decisions to log? → Add to Key Decisions
5. "What This Is" still accurate? → Update if drifted

**After each milestone:**
1. Full review of all sections
2. Core Value check — still the right priority?
3. Audit Out of Scope — reasons still valid?
4. Update Context with current state

---
*Last updated: 2026-03-22 after v1.1 milestone completion*
