# Print Money Factory

## What This Is

An npm package for Claude Code that provides a complete trading strategy development pipeline via slash commands (`/brrr:*`). Users describe a trading idea, and the system iteratively develops, backtests, optimizes, and exports it — from hypothesis to ready-to-trade PineScript and Python code. One active milestone at a time, with debug cycles that accumulate phases until the strategy meets its targets.

## Core Value

The iterative backtest loop must work end-to-end: a user describes a strategy idea, the system backtests it, AI analyzes results, adjusts parameters, and repeats until targets are hit or the strategy is diagnosed as unviable.

## Requirements

### Validated

- ✓ Install via `npx print-money-factory install` — copies commands to `~/.claude/commands/brrr/`, creates Python venv with all backtest dependencies — v1.0
- ✓ Package architecture mirrors GSD: commands/, workflows/, templates/, references/ with fixed metrics module and reference backtest patterns — v1.0
- ✓ `/brrr:new-milestone` — guided scoping flow with context file scanning, smart scope defaults, strategy-type criteria — v1.0
- ✓ `/brrr:status` — ASCII tree with step icons, best metrics, next step recommendation — v1.0
- ✓ STATE.md tracks milestone status, all phases, best metrics per phase — v1.0
- ✓ `/brrr:discuss` — guided conversation for strategy decisions, --auto mode, debug discuss with full context, drift detection hard gate — v1.0
- ✓ `/brrr:research` — find implementations, pitfalls, lookahead traps. --deep mode. Auto-recommendation — v1.0
- ✓ `/brrr:plan` — parameter space, optimization method auto-select, train/test split, parameter budget enforcement — v1.0
- ✓ `/brrr:execute` — AI-driven backtest loop with holistic analysis, adaptive param changes, 4 stop conditions, per-iteration artifacts — v1.0
- ✓ Data sourcing via ccxt, yfinance, CSV with validation and caching — v1.0
- ✓ `/brrr:verify` — interactive HTML report (plotly) with equity curve, drawdown, iteration table, parameter heatmap, trade list, regime breakdown, benchmark comparison, metrics summary — v1.0
- ✓ Export package on `--approved`: PineScript v5 (strategy + indicator), trading-rules.md, performance-report.md, backtest_final.py, live-checklist.md, report HTML — v1.0
- ✓ `/brrr:update` — re-install from npm to update commands and workflows — v1.0
- ✓ Claude-generated Python backtest engine — no external backtest library — v1.0
- ✓ Context file support — `.pmf/context/` accepts images, PDFs, screenshots — v1.0
- ✓ Hypothesis drift protection — detect scope drift during debug, offer new milestone — v1.0
- ✓ Per-iteration equity PNG generation during execute phase — v1.0
- ✓ Sequence validation — commands enforce correct order — v1.0

### Active

(None — next milestone requirements TBD via `/gsd:new-milestone`)

### Out of Scope

- Live trading bot (Binance/MetaTrader) — always a separate milestone after proven strategy
- Multiple simultaneous milestones — one active at a time by design
- Web UI or dashboard — CLI-only via Claude Code slash commands
- Mobile app — not applicable
- User authentication — local tool, no accounts
- Real-time market data streaming — backtesting only, no live feeds

## Context

**v1.0 shipped 2026-03-22** — published as `@print-money-factory/cli@0.4.0` on npm.

- 8 slash commands: new-milestone, discuss, research, plan, execute, verify, status, update
- 7 behavioral workflows (discuss 512 lines, execute 1067 lines, verify 999 lines)
- Python modules: metrics.py (8K), data_sources.py (11K), backtest_engine.py (9.5K), report_generator.py (29.8K)
- 32 metrics unit tests + 14 report/export tests passing
- Architecture mirrors GSD: commands/, workflows/, templates/, references/, bin/

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
| Claude writes backtest engine (not vectorbt/backtesting.py) | Maximum flexibility per strategy — no framework constraints | ✓ Good — enables novel strategies without framework constraints |
| Python venv managed by install script | Zero-friction setup, isolated from user's system Python | ✓ Good — works on Python 3.10-3.14, idempotent |
| One milestone at a time | Keeps focus, prevents strategy confusion | ✓ Good — clean lifecycle |
| GSD-mirror architecture | Proven pattern for Claude Code command packages | ✓ Good — 8 thin commands, 7 behavioral workflows |
| Per-iteration PNGs + final HTML | Visual feedback during optimization + polished final report | ✓ Good — matplotlib for speed, plotly for interactivity |
| SMA slope + ADX for regime classification | Simple, no lookahead, interpretable | ✓ Good — per D-03 |
| PineScript v5 (not v6) with migration comment | v6 too new, v5 universal in TradingView | ✓ Good — per D-18 |
| Both strategy() and indicator() PineScript exports | Different use cases (backtesting vs live alerts) | ✓ Good — per D-17 |
| Standalone HTML (no kaleido/Chrome dependency) | Portability — works on any machine with a browser | ✓ Good — CDN plotly.js |

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
*Last updated: 2026-03-22 after v1.0 milestone completion*
