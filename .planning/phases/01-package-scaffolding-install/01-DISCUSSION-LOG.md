# Phase 1: Package Scaffolding & Install - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-03-21
**Phase:** 01-package-scaffolding-install
**Areas discussed:** Install location, Venv management, Metrics module, Reference patterns

---

## Install Location

### Where should workflows, templates, and references live after install?

| Option | Description | Selected |
|--------|-------------|----------|
| All in commands/ | Everything under ~/.claude/commands/brrr/ — simple, one location, but commands dir gets big | |
| Split: ~/.pmf/ | Commands in ~/.claude/commands/brrr/, everything else in ~/.pmf/ (workflows, templates, references, bin) — mirrors GSD's separation | ✓ |

**User's choice:** Split: ~/.pmf/

### How should /brrr:update handle the update?

| Option | Description | Selected |
|--------|-------------|----------|
| Git pull + recopy | Clone repo to temp, copy updated files to install locations. Clean and simple. | |
| npx reinstall | Just run npx print-money-factory install again — idempotent install IS the update | ✓ |

**User's choice:** npx reinstall

### Should the install script also create .pmf/ in the user's project directory?

| Option | Description | Selected |
|--------|-------------|----------|
| No, on first use | /brrr:new-milestone creates .pmf/ when first run — install only sets up global files | ✓ |
| Yes, scaffold it | Install creates .pmf/ with context/ and phases/ subdirs ready to go | |

**User's choice:** No, on first use

---

## Venv Management

### Where should the Python venv live?

| Option | Description | Selected |
|--------|-------------|----------|
| ~/.pmf/venv/ | Inside the ~/.pmf/ directory — keeps everything together, one place to nuke | ✓ |
| ~/.pmf-venv/ | Separate from ~/.pmf/ — can delete config without losing venv and vice versa | |

**User's choice:** ~/.pmf/venv/

### How should install handle an existing venv with different deps?

| Option | Description | Selected |
|--------|-------------|----------|
| pip install --upgrade | Upgrade existing packages in-place — fast, preserves user additions | ✓ |
| Recreate venv | Delete and rebuild fresh — clean but slower, loses user additions | |

**User's choice:** pip install --upgrade

### Should the venv activation be transparent to the user?

| Option | Description | Selected |
|--------|-------------|----------|
| Full path always | Commands use ~/.pmf/venv/bin/python directly — no activation needed, just works | ✓ |
| Activate in shell | Workflows activate the venv before running Python — more standard but adds a step | |

**User's choice:** Full path always

---

## Metrics Module

### What format should the fixed metrics module accept?

| Option | Description | Selected |
|--------|-------------|----------|
| Trade log CSV/JSON | List of trades with entry/exit time, price, size, side — module computes everything from raw trades | |
| Daily returns series | Pandas-style series of daily portfolio returns — simpler input, module computes risk metrics | |
| Both formats | Accept either — trade log for trade-level stats, returns series for portfolio-level risk metrics | ✓ |

**User's choice:** Both formats

### Which metrics are in the fixed module vs computed by Claude per-strategy?

| Option | Description | Selected |
|--------|-------------|----------|
| All core in module | Sharpe, Sortino, Calmar, MaxDD, WinRate, PF, expectancy, trade count, net P&L — all fixed, all tested | ✓ |
| Risk metrics fixed | Sharpe/Sortino/Calmar/MaxDD fixed. Trade stats (WinRate, PF) computed inline since they're simpler | |

**User's choice:** All core in module

### Should the metrics module also handle IS/OOS splitting and overfitting detection?

| Option | Description | Selected |
|--------|-------------|----------|
| Yes, all in module | Metrics module handles splits, computes both sets, flags divergence — single source of truth | |
| No, separate | Metrics module just computes numbers. Split logic and overfitting detection are in the backtest workflow | ✓ |

**User's choice:** No, separate

---

## Reference Patterns

### How structured should the canonical backtest engine pattern be?

| Option | Description | Selected |
|--------|-------------|----------|
| Full skeleton | Complete backtest_engine.py with event loop, position management, metrics integration — Claude fills in strategy logic only | |
| Pattern guide | Markdown doc with rules (next-bar execution, no lookahead, etc.) + code snippets — Claude writes full engine following rules | |
| Both | Pattern guide for rules + skeleton for structure. Claude reads both. | ✓ |

**User's choice:** Both

### Should references include data source adapters as ready-to-use code?

| Option | Description | Selected |
|--------|-------------|----------|
| Ready-to-use Python | data_sources.py with functions: load_ccxt(), load_yfinance(), load_csv() — tested, Claude calls them | ✓ |
| Pattern doc only | Markdown describing how to use each API — Claude writes the loader code each time | |

**User's choice:** Ready-to-use Python

### PineScript template — how detailed?

| Option | Description | Selected |
|--------|-------------|----------|
| Structural template | Template with version header, input params, strategy() call structure — Claude fills in logic | |
| Full examples | Multiple complete PineScript examples by strategy type (trend, mean-reversion, etc.) as reference | |
| Both | Structural template + example library | ✓ |

**User's choice:** Both

---

## Claude's Discretion

- npm package.json structure and scripts
- install.js implementation details
- Unit test framework choice for Python metrics
- Internal file organization within ~/.pmf/
- requirements.txt exact version pins

## Deferred Ideas

None — discussion stayed within phase scope
