# Print Money Factory

An npm package for [Claude Code](https://claude.ai/code) that provides a complete AI-driven trading strategy development pipeline via slash commands (`/brrr:*`). Describe a trading idea, and the system iteratively develops, backtests, optimizes, and exports it — from hypothesis to ready-to-trade PineScript and Python code.

## How It Works

```
/brrr:new-milestone  →  Define your strategy idea and scope
/brrr:discuss        →  Fix all decisions: entry/exit, stops, sizing, params
/brrr:research       →  Find implementations, pitfalls, lookahead traps
/brrr:plan           →  Design parameter space and optimization method
/brrr:execute        →  AI writes & runs backtests, analyzes, adjusts, repeats
/brrr:verify         →  Interactive HTML report, approve or debug
```

The core loop: **idea → backtest → AI analysis → parameter adjustment → repeat** until targets are hit or the strategy is diagnosed as unviable.

## Installation

```bash
npx @print-money-factory/cli install
```

**Requirements:** Python 3.10+ (the only prerequisite — everything else is installed automatically)

**What it does:**
- Copies 9 slash commands to `~/.claude/commands/brrr/`
- Creates a Python venv at `~/.pmf/venv/` with all dependencies
- Installs workflows, templates, and reference modules to `~/.pmf/`

After install, open Claude Code and type `/brrr:new-milestone` to start.

## Commands

| Command | What it does |
|---------|-------------|
| `/brrr:new-milestone` | Create a new strategy milestone with guided scoping |
| `/brrr:discuss` | Fix strategy decisions through conversation (entry/exit, stops, sizing, commissions, parameter ranges) |
| `/brrr:research` | Find known implementations, academic work, and lookahead traps for your strategy type |
| `/brrr:plan` | Design parameter space, select optimization method (grid/random/walk-forward/bayesian), set evaluation criteria |
| `/brrr:execute` | Run the AI backtest loop: load data → run backtest → compute metrics → AI analyzes → adjust params → repeat |
| `/brrr:verify` | Generate interactive HTML report with equity curve, drawdown, regime breakdown, benchmark comparison |
| `/brrr:status` | ASCII tree showing milestone progress, all phases, next step |
| `/brrr:doctor` | Diagnose installation health (Python, venv, dependencies, file integrity) |
| `/brrr:update` | Update to the latest version |

## The Pipeline

### 1. New Milestone (`/brrr:new-milestone`)

Define your trading idea and scope. The system guides you through:
- Strategy idea (e.g., "SMA crossover on BTC/USDT daily")
- Scope selection (strategy, backtest, tuning, risk management, exports)
- Success criteria (target Sharpe, max drawdown, min trades)
- Asset and data source selection

### 2. Discuss (`/brrr:discuss`)

Fix all strategy decisions before any code runs:
- Entry/exit logic, stop-loss, take-profit
- Position sizing and commission assumptions
- Parameter ranges for optimization
- `--auto` flag for reasonable defaults with minimal questions

**Debug mode:** When coming back from a failed verify, discuss starts from the AI diagnosis — not from scratch. It reads all prior failed approaches and avoids suggesting what already didn't work.

### 3. Research (`/brrr:research`)

Optional phase that investigates your strategy type:
- Known implementations and academic references
- Lookahead bias traps specific to your strategy
- `--deep` flag for extended web search

### 4. Plan (`/brrr:plan`)

Design the optimization approach:
- Define free parameters with ranges and step sizes
- Auto-selects optimization method:
  - **Grid search** for < 100 combinations
  - **Random search** for 100-500 combinations
  - **Bayesian (Optuna TPE/CMA-ES)** for 500+ combinations
  - **Walk-forward** as override option
- Set evaluation criteria, data period, train/test split
- Parameter budget enforcement to prevent overfitting

### 5. Execute (`/brrr:execute`)

The core AI backtest loop — fully autonomous:

1. Claude writes a Python backtest script from scratch based on your plan
2. Runs it against real market data (ccxt for crypto, yfinance for stocks)
3. Computes 9 metrics: Sharpe, Sortino, Calmar, Max DD, Win Rate, Profit Factor, Expectancy, Trade Count, Net PnL
4. AI analyzes results and equity curve PNG
5. Adjusts parameters and repeats

**Stop conditions:**
- **MINT** — All targets hit
- **PLATEAU** — 3 iterations without >5% improvement
- **REKT** — No edge found at any parameter combination
- **NO DATA** — Data loading failed

**Bayesian optimization:** When selected in the plan phase, uses Optuna's Ask-and-Tell API with TPE or CMA-ES sampler. Each iteration shows `[WARMUP]` or `[GUIDED]` mode. Studies persist to SQLite for `--resume`.

Per-iteration artifacts saved: params JSON, metrics JSON, equity curve PNG, verdict JSON.

### 6. Verify (`/brrr:verify`)

Generates a standalone interactive HTML report (Plotly, no server needed) with:

| Section | What it shows |
|---------|--------------|
| Metrics Summary | All 9 metrics vs targets with color coding |
| Equity Curve | Strategy vs buy-and-hold with zoom |
| Drawdown Chart | With max drawdown horizontal line |
| Iteration Table | All iterations with Sharpe evolution |
| Parameter Heatmap | If grid search was used |
| Trade List | Per-trade P&L with green/red coloring |
| Regime Breakdown | Bull/bear/sideways performance |
| Benchmark | Alpha, beta vs buy-and-hold |

**Three paths:**
- **`--approved`** — Closes the milestone and generates a complete export package (8 files)
- **`--debug`** — AI diagnoses what went wrong, writes a structured diagnosis JSON with "do NOT retry" entries, opens a new phase cycle
- **Interactive** — AI presents assessment, you choose

### Export Package (on `--approved`)

Generated in `.pmf/output/`:

| File | Purpose |
|------|---------|
| `pinescript_v5_strategy.pine` | TradingView strategy for backtesting |
| `pinescript_v5_indicator.pine` | TradingView indicator with alerts for live trading |
| `trading-rules.md` | Plain English entry/exit/sizing rules |
| `performance-report.md` | Portable metrics summary |
| `backtest_final.py` | Reproducible Python script, runs standalone |
| `live-checklist.md` | Step-by-step guide before real money |
| `bot-building-guide.md` | Platform-specific deployment instructions (crypto/stocks/forex) |
| `report_vN.html` | Interactive HTML report |

## Data Sources

| Source | Assets | Timeframes | API Key |
|--------|--------|------------|---------|
| **ccxt** | Crypto (100+ exchanges) | All | No |
| **yfinance** | Stocks, ETFs, Forex (daily) | Daily | No |
| **CSV** | Any asset | Any | No |
| polygon.io | Stocks (intraday) | Minute+ | Yes |

Data is validated for gaps and NaN before every backtest run. Local caching prevents re-downloading.

## Optimization Methods

| Method | When | How |
|--------|------|-----|
| **Grid Search** | < 100 combinations | Systematic sweep through all parameter combinations |
| **Random Search** | 100-500 combinations | Random sampling guided by AI analysis |
| **Bayesian (Optuna)** | 500+ combinations | TPE sampler (mixed params) or CMA-ES (continuous only), SQLite persistence for `--resume` |
| **Walk-Forward** | Time-series robustness | Rolling train/test windows |

## Debug Cycles

When a strategy doesn't meet targets, the debug cycle carries forward knowledge:

1. `/brrr:verify --debug` writes a structured `phase_N_diagnosis.json` with:
   - Failed parameter regions
   - Explicit "do NOT retry" entries
   - AI-generated analysis of what went wrong

2. `/brrr:discuss` in debug mode:
   - Reads ALL prior diagnosis files
   - Presents a "Prior Debug Cycles" failure summary table
   - Enforces do_not_retry constraints — the AI cannot suggest parameters that already failed
   - Starts from the diagnosis, not from scratch

3. Hypothesis drift protection detects when changes exceed the original strategy scope and offers to open a new milestone instead.

## Architecture

```
~/.claude/commands/brrr/    # 9 thin slash commands (markdown)
~/.pmf/
  workflows/                # 8 behavioral workflows (markdown prompts)
  references/               # Python modules (metrics, backtest engine, data sources, optuna bridge, report generator)
  templates/                # HTML report, PineScript, STATE.md, STRATEGY.md
  venv/                     # Isolated Python environment
  .version                  # Installed version info
```

Commands are thin markdown files that `@`-reference behavioral workflows. The workflows describe what Claude does step-by-step. Python modules are fixed reference code (not regenerated per strategy) with unit tests.

## Metrics

All 9 metrics computed per iteration with known-answer TDD tests:

| Metric | What it measures |
|--------|-----------------|
| Sharpe Ratio | Risk-adjusted return (annualized) |
| Sortino Ratio | Downside risk-adjusted return |
| Calmar Ratio | Return vs max drawdown |
| Max Drawdown | Largest peak-to-trough decline |
| Win Rate | Percentage of winning trades |
| Profit Factor | Gross profit / gross loss |
| Expectancy | Average profit per trade |
| Trade Count | Total number of trades |
| Net PnL | Total profit/loss |

## Updating

```bash
/brrr:update
```

Or manually:
```bash
npx @print-money-factory/cli@latest install
```

Every `/brrr:*` command silently checks for updates once per 24 hours.

## Diagnostics

```bash
/brrr:doctor
```

Checks: Python version (>=3.10), venv health, 10 library imports, command files, workflow files, reference files. Reports pass/fail per check with fix suggestions.

## Requirements

- **Python 3.10+** (tested on 3.10 through 3.14)
- **Claude Code** (the CLI tool from Anthropic)
- **Node.js 18+** (for the install script)

All Python dependencies are installed automatically in an isolated venv:
pandas, numpy, matplotlib, plotly, optuna, ccxt, yfinance, scipy, ta, jinja2, tabulate, requests, pyyaml, pytest

## Design Principles

- **One milestone at a time** — Keeps focus, prevents strategy confusion
- **Claude writes the backtest engine** — No framework constraints, maximum flexibility per strategy
- **Behavioral workflows** — Claude follows step-by-step markdown prompts, not code templates
- **Per-iteration artifacts** — Every iteration saves params, metrics, equity PNG, verdict JSON
- **Standalone outputs** — HTML reports work without a server, PineScript pastes directly into TradingView

## License

MIT
