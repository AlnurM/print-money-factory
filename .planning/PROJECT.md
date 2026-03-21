# Print Money Factory

## What This Is

An npm package for Claude Code that provides a complete trading strategy development pipeline via slash commands (`/brrr:*`). Users describe a trading idea, and the system iteratively develops, backtests, optimizes, and exports it — from hypothesis to ready-to-trade PineScript and Python code. One active milestone at a time, with debug cycles that accumulate phases until the strategy meets its targets.

## Core Value

The iterative backtest loop must work end-to-end: a user describes a strategy idea, the system backtests it, AI analyzes results, adjusts parameters, and repeats until targets are hit or the strategy is diagnosed as unviable.

## Requirements

### Validated

- ✓ Install via `npx print-money-factory install` — copies commands to `~/.claude/commands/brrr/`, creates Python venv with all backtest dependencies — Phase 1
- ✓ Package architecture mirrors GSD: commands/, workflows/, templates/, references/ with fixed metrics module and reference backtest patterns — Phase 1
- ✓ `/brrr:new-milestone` — guided scoping flow with context file scanning, smart scope defaults, strategy-type criteria — Phase 2
- ✓ `/brrr:status` — ASCII tree with step icons, best metrics, next step recommendation — Phase 2
- ✓ STATE.md tracks milestone status, all phases, best metrics per phase — Phase 2
- ✓ `/brrr:discuss` — guided conversation for strategy decisions, --auto mode, debug discuss with full context, drift detection hard gate — Phase 3
- ✓ `/brrr:research` — find implementations, pitfalls, lookahead traps. --deep mode. Auto-recommendation — Phase 3
- ✓ `/brrr:plan` — parameter space, optimization method auto-select, train/test split, parameter budget enforcement — Phase 3
- ✓ `/brrr:execute` — AI-driven backtest loop with holistic analysis, adaptive param changes, 4 stop conditions, per-iteration artifacts — Phase 4
- ✓ Data sourcing via ccxt, yfinance, CSV with validation and caching — Phase 4

### Active
- [ ] `/brrr:new-milestone` — scoping flow: parse context files, collect strategy idea, define scope (strategy/backtest/tuning/exports), set success criteria, output STRATEGY.md and STATE.md
- [ ] `/brrr:discuss` — fix all strategy decisions before code: entry/exit logic, stops, position sizing, commissions, parameter ranges. Debug mode starts from previous verify diagnosis
- [ ] `/brrr:research` — optional phase: find implementations, academic work, lookahead traps, formalization alternatives for the strategy type
- [ ] `/brrr:plan` — design parameter space, optimization method (grid/random/walk-forward/bayesian), evaluation criteria, data period
- [ ] `/brrr:execute` — AI-driven backtest loop: load data → run backtest → compute metrics → AI analyzes → adjust params → repeat. Stop conditions: MINT/PLATEAU/REKT/NO DATA. Per-iteration artifacts (params, metrics, equity PNG, verdict)
- [ ] `/brrr:verify` — generate interactive HTML report (plotly): equity curve, drawdown, iteration table, parameter heatmap, trade list, regime breakdown, metrics summary. Accept `--approved` (close milestone, generate exports) or `--debug` (open new phase cycle with AI diagnosis)
- [ ] `/brrr:status` — ASCII tree showing milestone progress, all phases, next step
- [ ] `/brrr:update` — check GitHub for new version, show changelog, update commands and workflows
- [ ] Claude-generated Python backtest engine — no external backtest library, Claude writes the strategy logic and backtest runner from scratch each time
- [ ] Data sourcing via ccxt (crypto), yfinance (stocks daily, forex daily), polygon.io (stocks intraday), Dukascopy (forex intraday), with CSV fallbacks
- [ ] Context file support — `.pmf/context/` accepts images, PDFs, screenshots; system parses and confirms understanding before incorporating
- [ ] Export package on `--approved`: PineScript v5, trading-rules.md, performance-report.md, backtest_final.py, live-checklist.md, report HTML
- [ ] Hypothesis protection — detect when user drifts from original idea during debug, offer to open new milestone instead
- [ ] Per-iteration equity PNG generation during execute phase
- [ ] STATE.md tracks milestone status, all phases, best metrics per phase

### Out of Scope

- Live trading bot (Binance/MetaTrader) — always a separate milestone after proven strategy
- Multiple simultaneous milestones — one active at a time by design
- Web UI or dashboard — CLI-only via Claude Code slash commands
- Mobile app — not applicable
- User authentication — local tool, no accounts
- Real-time market data streaming — backtesting only, no live feeds

## Context

- Architecture mirrors GSD (get-shit-done): commands/, workflows/, templates/, references/, bin/ with tooling layer
- Install script copies slash commands to `~/.claude/commands/brrr/` and creates a Python venv with all dependencies (pandas, numpy, ccxt, yfinance, plotly, optuna, etc.)
- Python 3.10+ is the only user prerequisite — everything else is installed into venv
- The backtest engine is not a fixed library — Claude writes the Python backtest code fresh for each strategy based on the plan phase decisions
- The project document (PROJECT.md in repo root) serves as the original spec/vision document, separate from this planning artifact

## Constraints

- **Distribution**: Public npm package on npmjs.com — must work via `npx print-money-factory install`
- **Runtime**: Claude Code slash commands only — no standalone CLI, no server
- **Python**: All backtest code runs in a managed venv, not the system Python
- **Data**: Free data sources by default (ccxt, yfinance, Dukascopy). Paid sources (polygon.io, firstrate) optional with API keys
- **Reports**: Standalone HTML files (plotly embedded, no server needed)
- **Architecture**: Mirror GSD pattern — commands/, workflows/, templates/, references/ structure

## Key Decisions

| Decision | Rationale | Outcome |
|----------|-----------|---------|
| Claude writes backtest engine (not vectorbt/backtesting.py) | Maximum flexibility per strategy — no framework constraints | — Pending |
| Python venv managed by install script | Zero-friction setup, isolated from user's system Python | — Pending |
| One milestone at a time | Keeps focus, prevents strategy confusion | — Pending |
| GSD-mirror architecture | Proven pattern for Claude Code command packages | — Pending |
| Per-iteration PNGs + final HTML | Visual feedback during optimization + polished final report | — Pending |

## Evolution

This document evolves at phase transitions and milestone boundaries.

**After each phase transition** (via `/gsd:transition`):
1. Requirements invalidated? → Move to Out of Scope with reason
2. Requirements validated? → Move to Validated with phase reference
3. New requirements emerged? → Add to Active
4. Decisions to log? → Add to Key Decisions
5. "What This Is" still accurate? → Update if drifted

**After each milestone** (via `/gsd:complete-milestone`):
1. Full review of all sections
2. Core Value check — still the right priority?
3. Audit Out of Scope — reasons still valid?
4. Update Context with current state

---
*Last updated: 2026-03-21 after Phase 4 completion*
