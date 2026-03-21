<!-- GSD:project-start source:PROJECT.md -->
## Project

**Print Money Factory**

An npm package for Claude Code that provides a complete trading strategy development pipeline via slash commands (`/brrr:*`). Users describe a trading idea, and the system iteratively develops, backtests, optimizes, and exports it — from hypothesis to ready-to-trade PineScript and Python code. One active milestone at a time, with debug cycles that accumulate phases until the strategy meets its targets.

**Core Value:** The iterative backtest loop must work end-to-end: a user describes a strategy idea, the system backtests it, AI analyzes results, adjusts parameters, and repeats until targets are hit or the strategy is diagnosed as unviable.

### Constraints

- **Distribution**: Public npm package on npmjs.com — must work via `npx print-money-factory install`
- **Runtime**: Claude Code slash commands only — no standalone CLI, no server
- **Python**: All backtest code runs in a managed venv, not the system Python
- **Data**: Free data sources by default (ccxt, yfinance, Dukascopy). Paid sources (polygon.io, firstrate) optional with API keys
- **Reports**: Standalone HTML files (plotly embedded, no server needed)
- **Architecture**: Mirror GSD pattern — commands/, workflows/, templates/, references/ structure
<!-- GSD:project-end -->

<!-- GSD:stack-start source:research/STACK.md -->
## Technology Stack

## Overview
## Recommended Stack
### NPM Package Layer
| Technology | Version | Purpose | Why | Confidence |
|------------|---------|---------|-----|------------|
| Node.js | >=18 | Runtime for install script | LTS baseline, required by Claude Code itself | HIGH |
| npm (package.json) | -- | Package distribution | `npx print-money-factory install` is the install UX | HIGH |
| esbuild (via tsup) | tsup ^8.4 | Bundle install script only | Zero-config, fast, proven by GSD pattern. Only needed if install script is TypeScript | MEDIUM |
| shelljs or plain Node fs | ^0.8 | Install script file operations | Copy commands to `~/.claude/commands/brrr/`, create venv. No native deps | HIGH |
### Python Backtest Engine
| Technology | Version | Purpose | Why | Confidence |
|------------|---------|---------|-----|------------|
| Python | >=3.10 | Runtime | Minimum for all deps (dukascopy-python requires >=3.10, optuna requires >=3.9). 3.10 is safe floor | HIGH |
| pandas | ^3.0 | Data manipulation, OHLCV handling | Released Jan 2026. Industry standard for time series. Breaking changes from 2.x are minimal | HIGH |
| numpy | ^2.4 | Numerical computation | Required by pandas. Current stable is 2.4.3 (March 2026) | HIGH |
| matplotlib | ^3.10 | Per-iteration equity curve PNGs | Lightweight, headless-friendly (Agg backend), no Chrome dependency. Use for quick iteration PNGs, NOT for final reports | HIGH |
| plotly | ^6.5 | Interactive HTML reports | Standalone HTML with embedded JS. No server needed. Current stable is 6.5.2 (Jan 2026) | HIGH |
| kaleido | ^1.0 | Static image export from plotly | Required for plotly PNG export. v1.0+ requires Chrome installed on machine -- use matplotlib instead for iteration PNGs to avoid this dep | MEDIUM |
| optuna | ^4.7 | Bayesian optimization | Best-in-class for hyperparameter optimization. Supports TPE, GP, CMA-ES samplers. v4.7.0 (Jan 2026) | HIGH |
| ccxt | latest | Crypto exchange data | 100+ exchanges, actively maintained, frequent releases. Pin to specific version at install time | HIGH |
| yfinance | ^1.2 | Stock/forex daily data | v1.2.0 (Feb 2026). Unofficial Yahoo Finance API -- fragile but ubiquitous. No alternative with same coverage for free | MEDIUM |
| dukascopy-python | latest | Forex intraday data | Tick-level to daily. Free, no API key. Requires Python >=3.10 | MEDIUM |
| polygon-api-client | ^1.16 | Stocks intraday data (paid) | Use legacy package name, NOT `massive` (rebrand Oct 2025 is too fresh, users will search for "polygon"). Requires API key | MEDIUM |
| scipy | ^1.14 | Statistical functions | Used in metric calculations (Sharpe, Sortino, distribution fitting). Pulled in by optuna anyway | HIGH |
| ta | ^0.11 | Technical indicators | Lightweight, pandas-native. Alternative: ta-lib (faster but requires C compilation -- bad for venv portability) | MEDIUM |
### Infrastructure / Tooling
| Technology | Version | Purpose | Why | Confidence |
|------------|---------|---------|-----|------------|
| Python venv | stdlib | Isolation | Built into Python 3.10+. No additional deps. Created by install script | HIGH |
| pip | bundled | Package installation | Installed inside venv. Use `requirements.txt` with pinned versions | HIGH |
| Node.js child_process | stdlib | Invoke Python from commands if needed | Slash commands are markdown prompts, but install script needs to shell out to create venv | HIGH |
### Supporting Libraries (Python)
| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| jinja2 | ^3.1 | HTML report templating | Assembling the final plotly HTML report with multiple sections |
| tabulate | ^0.9 | ASCII table formatting | Status command output, terminal-friendly metric displays |
| requests | ^2.32 | HTTP fallback | CSV downloads, API fallbacks when primary libs fail |
| pyyaml | ^6.0 | Config parsing | If strategy configs or parameter spaces use YAML format |
## Alternatives Considered
| Category | Recommended | Alternative | Why Not |
|----------|-------------|-------------|---------|
| Backtest framework | Claude-written engine | vectorbt, backtesting.py, zipline | Project decision: max flexibility per strategy. Frameworks impose structure that constrains novel strategies |
| Optimization | optuna | scipy.optimize, hyperopt, Ax | Optuna has best API for iterative optimization, pruning, visualization. Hyperopt is unmaintained. Ax is heavy |
| Data viz (iterations) | matplotlib | plotly | Matplotlib is lighter, no Chrome dep for PNG, faster for simple equity curves |
| Data viz (reports) | plotly | bokeh, altair | Plotly HTML embeds are self-contained, interactive, well-documented. Bokeh requires more boilerplate |
| Technical indicators | ta | ta-lib, pandas-ta | ta-lib needs C compilation (portability nightmare). pandas-ta is less maintained. ta is pure Python, pandas-native |
| Forex data | dukascopy-python | FXCM, Oanda API | Dukascopy is free, no account needed, tick-level data. Others require accounts |
| Crypto data | ccxt | Individual exchange APIs | ccxt unifies 100+ exchanges behind one API. No reason to use individual clients |
| Stock data (free) | yfinance | alpha_vantage, quandl | yfinance has broadest coverage for free. Alpha Vantage has strict rate limits. Quandl is now Nasdaq Data Link (paid) |
| Stock data (paid) | polygon (massive) | IEX Cloud, Tiingo | Polygon has best intraday coverage and cleanest API. Use polygon-api-client (legacy name) |
| NPM bundler | tsup | rollup, webpack, unbundled | tsup is zero-config, esbuild-powered. Only needed for install script. GSD uses esbuild directly |
| Package format | ESM + CJS (tsup) | ESM only | Some Node.js tooling still expects CJS. Dual format avoids compatibility issues |
| HTML templating | jinja2 | mako, string templates | Jinja2 is the Python standard. Claude will know it. Mako adds nothing |
| PNG generation | matplotlib (Agg) | pillow, kaleido | Matplotlib is already needed. Agg backend works headless without Chrome. Kaleido v1 requires Chrome |
## Critical Decisions
### 1. matplotlib for iteration PNGs, plotly for final HTML reports
### 2. polygon-api-client, NOT massive
### 3. ta (pure Python) over ta-lib (C extension)
### 4. No pinescript transpiler library
### 5. Python >=3.10, not 3.12+
## Package Structure (npm side)
## Python venv Structure (created by install)
## Installation Flow
# User runs:
# Script does:
# 1. Copies commands/*.md -> ~/.claude/commands/brrr/
# 2. Copies workflows/, templates/, references/ -> ~/.pmf/
# 3. Detects python3 (>=3.10), creates ~/.pmf/venv/
# 4. pip install -r requirements.txt inside venv
# 5. Verifies installation (import test)
## requirements.txt (pinned)
## Version Pinning Strategy
## Sources
- [tsup npm package](https://www.npmjs.com/package/tsup) - npm bundling
- [Create a Modern npm Package in 2026](https://jsmanifest.com/create-modern-npm-package-2026) - npm best practices
- [ccxt GitHub](https://github.com/ccxt/ccxt) - crypto data
- [yfinance PyPI](https://pypi.org/project/yfinance/) - stock data, v1.2.0
- [optuna GitHub](https://github.com/optuna/optuna) - optimization, v4.7.0
- [plotly PyPI](https://pypi.org/project/plotly/) - visualization, v6.5.2
- [kaleido PyPI](https://pypi.org/project/kaleido/) - static image export, v1.0 Chrome requirement
- [Plotly static image generation changes](https://plotly.com/python/static-image-generation-changes/) - kaleido v1 breaking changes
- [pandas 3.0 release notes](https://pandas.pydata.org/docs/whatsnew/v3.0.0.html) - pandas 3.0
- [matplotlib PyPI](https://pypi.org/project/matplotlib/) - v3.10.8
- [dukascopy-python PyPI](https://pypi.org/project/dukascopy-python/) - forex data
- [polygon-api-client PyPI](https://pypi.org/project/polygon-api-client/) - stocks intraday, rebrand notice
- [Polygon.io -> Massive.com rebrand](https://github.com/polygon-io/client-python) - client-python rebrand details
- [get-shit-done-cc npm](https://www.npmjs.com/package/get-shit-done-cc) - GSD architecture pattern
- [Python venv docs](https://docs.python.org/3/library/venv.html) - stdlib venv
<!-- GSD:stack-end -->

<!-- GSD:conventions-start source:CONVENTIONS.md -->
## Conventions

Conventions not yet established. Will populate as patterns emerge during development.
<!-- GSD:conventions-end -->

<!-- GSD:architecture-start source:ARCHITECTURE.md -->
## Architecture

Architecture not yet mapped. Follow existing patterns found in the codebase.
<!-- GSD:architecture-end -->

<!-- GSD:workflow-start source:GSD defaults -->
## GSD Workflow Enforcement

Before using Edit, Write, or other file-changing tools, start work through a GSD command so planning artifacts and execution context stay in sync.

Use these entry points:
- `/gsd:quick` for small fixes, doc updates, and ad-hoc tasks
- `/gsd:debug` for investigation and bug fixing
- `/gsd:execute-phase` for planned phase work

Do not make direct repo edits outside a GSD workflow unless the user explicitly asks to bypass it.
<!-- GSD:workflow-end -->



<!-- GSD:profile-start -->
## Developer Profile

> Profile not yet configured. Run `/gsd:profile-user` to generate your developer profile.
> This section is managed by `generate-claude-profile` -- do not edit manually.
<!-- GSD:profile-end -->
