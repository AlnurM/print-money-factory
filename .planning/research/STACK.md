# Technology Stack

**Project:** Print Money Factory
**Researched:** 2026-03-21

## Overview

This project has two distinct technology surfaces: (1) an npm package that installs Claude Code slash commands, and (2) a Python backtest engine that runs inside a managed venv. The npm side is a thin distribution layer -- markdown files plus a Node.js install script. The Python side is where all computation happens.

## Recommended Stack

### NPM Package Layer

| Technology | Version | Purpose | Why | Confidence |
|------------|---------|---------|-----|------------|
| Node.js | >=18 | Runtime for install script | LTS baseline, required by Claude Code itself | HIGH |
| npm (package.json) | -- | Package distribution | `npx print-money-factory install` is the install UX | HIGH |
| esbuild (via tsup) | tsup ^8.4 | Bundle install script only | Zero-config, fast, proven by GSD pattern. Only needed if install script is TypeScript | MEDIUM |
| shelljs or plain Node fs | ^0.8 | Install script file operations | Copy commands to `~/.claude/commands/brrr/`, create venv. No native deps | HIGH |

**Note on build complexity:** The GSD package publishes most files as-is (commands/, workflows/, templates/ are just markdown). Only the install script and any hooks need bundling. Do NOT over-engineer the npm side -- it is a file copier, not an application.

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

**Rationale:** Kaleido v1.0 (required by plotly for static image export) now requires Chrome installed on the machine. This is an unacceptable dependency for a CLI tool that runs in diverse environments. Use matplotlib with the Agg backend for per-iteration equity PNGs (fast, headless, zero external deps). Use plotly only for the final interactive HTML report where its strengths (hover, zoom, pan) justify the heavier library.

### 2. polygon-api-client, NOT massive

**Rationale:** Polygon.io rebranded to Massive.com in October 2025. The Python client was renamed from `polygon-api-client` to `massive`. However, every tutorial, StackOverflow answer, and documentation resource still references "polygon." The legacy package (v1.16.3) remains available and `api.polygon.io` continues to work. Using the legacy name reduces user confusion. Migrate to `massive` in a future version when the ecosystem catches up.

### 3. ta (pure Python) over ta-lib (C extension)

**Rationale:** ta-lib requires compiling C extensions, which fails frequently in venv setups across platforms (especially macOS ARM). The `ta` library is pure Python, installs cleanly everywhere, and covers all standard indicators (RSI, MACD, Bollinger, ATR, etc.). The performance difference is irrelevant for backtesting (not real-time).

### 4. No pinescript transpiler library

**Rationale:** PineScript v5 export will be done by Claude generating the PineScript code from the strategy description and parameters -- not by transpiling Python to PineScript. Libraries like `pynescript` parse PineScript INTO Python (wrong direction). Claude is better at generating idiomatic PineScript than any transpiler.

### 5. Python >=3.10, not 3.12+

**Rationale:** 3.10 is the highest minimum that satisfies all deps (dukascopy-python requires >=3.10). Going higher (3.12+) would exclude users on older systems without adding value. The backtest engine uses no 3.11+ features (match statements, ExceptionGroup, etc. are not needed).

## Package Structure (npm side)

```
print-money-factory/
  package.json            # name, version, bin, files
  bin/
    install.mjs           # npx entry point: copies commands, creates venv
    update.mjs            # version check + update
  commands/               # .md files -> ~/.claude/commands/brrr/
    new-milestone.md
    discuss.md
    research.md
    plan.md
    execute.md
    verify.md
    status.md
    update.md
  workflows/              # multi-step workflow definitions
  templates/              # Python templates (backtest runner, report)
    backtest_runner.py    # skeleton that Claude fills in
    report_template.html  # jinja2 template for plotly report
  references/             # strategy patterns, indicator docs
  requirements.txt        # pinned Python deps for venv
```

## Python venv Structure (created by install)

```
~/.pmf/
  venv/                   # Python virtual environment
    bin/python
    bin/pip
    lib/python3.x/site-packages/
  data/                   # cached market data
  config.yaml             # API keys (polygon, etc.)
```

## Installation Flow

```bash
# User runs:
npx print-money-factory install

# Script does:
# 1. Copies commands/*.md -> ~/.claude/commands/brrr/
# 2. Copies workflows/, templates/, references/ -> ~/.pmf/
# 3. Detects python3 (>=3.10), creates ~/.pmf/venv/
# 4. pip install -r requirements.txt inside venv
# 5. Verifies installation (import test)
```

## requirements.txt (pinned)

```
pandas>=3.0,<4
numpy>=2.4,<3
matplotlib>=3.10,<4
plotly>=6.5,<7
optuna>=4.7,<5
ccxt>=4.0
yfinance>=1.2,<2
dukascopy-python>=0.3
polygon-api-client>=1.16,<2
scipy>=1.14,<2
ta>=0.11,<1
jinja2>=3.1,<4
tabulate>=0.9,<1
requests>=2.32,<3
pyyaml>=6.0,<7
```

## Version Pinning Strategy

Use **compatible release ranges** (>=X.Y,<next-major) in requirements.txt. This allows patch updates while preventing breaking changes. The install script runs `pip install -r requirements.txt` which resolves latest compatible versions at install time.

Do NOT use exact pins (==) -- they cause conflicts when users have other Python projects. Do NOT use unpinned (no upper bound) -- major version bumps break things.

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
