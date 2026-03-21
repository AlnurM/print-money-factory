# Pitfalls Research

**Domain:** AI-driven trading strategy backtesting CLI (Claude Code command package)
**Researched:** 2026-03-21
**Confidence:** HIGH (backtesting pitfalls are extensively documented; CLI distribution pitfalls verified against current Claude Code docs)

## Critical Pitfalls

### Pitfall 1: Lookahead Bias in Claude-Generated Backtest Code

**What goes wrong:**
Claude writes backtest code that accidentally uses future data. The most common form: using the current bar's close price to generate a signal and then "executing" at that same close price. Other forms include computing indicators over the full dataset before iterating (e.g., normalizing with min/max of the entire series), or using pandas operations like `.shift(-1)` that pull future values into the current row. Because Claude generates the backtest engine fresh each time, every single run is a new opportunity for this bug to appear.

**Why it happens:**
LLMs generate code that is syntactically correct and logically plausible but subtly wrong in domain-specific ways. Lookahead bias is invisible in code review unless you know exactly what to look for. A vectorized pandas operation like `df['signal'] = df['close'] > df['close'].rolling(20).mean()` followed by `df['entry_price'] = df['close']` looks perfectly reasonable but assumes you can act on information you only have after the bar closes.

**How to avoid:**
- The backtest engine template/workflow MUST enforce an event-loop architecture: process one bar at a time, generate signals using only data up to and including the current bar, execute trades at the NEXT bar's open (or with a configurable delay).
- Include a mandatory "lookahead audit" step in the execute workflow: after code generation, Claude must verify that no signal computation references future indices and that all trade executions use next-bar pricing.
- Build a reference snippet in `references/` showing the correct event-loop pattern that Claude must follow.

**Warning signs:**
- Backtest Sharpe ratio above 3.0 on any strategy
- Strategy performs dramatically better in backtest than any published benchmark for similar approaches
- Equity curve has no drawdowns or drawdowns are suspiciously shallow
- Win rate above 70% on a trend-following strategy

**Phase to address:**
Core backtest engine design (Phase 1). This must be baked into the engine template before any strategy is ever tested. The `references/` directory should contain a canonical event-loop pattern that all generated code must follow.

---

### Pitfall 2: Overfitting Through Excessive Parameter Optimization

**What goes wrong:**
The AI optimization loop (execute phase) tests hundreds or thousands of parameter combinations and finds one that produces excellent metrics on historical data. The strategy fails immediately in forward testing or live trading because it was tuned to noise, not signal. This is the single most common reason retail algo strategies fail.

**Why it happens:**
With automated optimization, it costs nothing to test thousands of combinations. Given enough parameters and enough iterations, you WILL find a combination that looks profitable on any random dataset. The AI loop makes this worse because Claude will keep adjusting parameters to "improve" metrics, not recognizing when improvements are just curve-fitting. Users see improving numbers and assume the strategy is getting better.

**How to avoid:**
- Enforce mandatory train/test split: optimize on in-sample data (e.g., 70%), validate on held-out out-of-sample data (30%). Never let the optimization loop see out-of-sample data.
- Cap the number of optimization iterations (e.g., 50 max per phase). The PLATEAU stop condition must trigger aggressively.
- Require walk-forward validation for any strategy that passes initial backtest: re-optimize on rolling windows and test on subsequent windows.
- Track and display the number of parameter combinations tested. If >100 combinations were tested and the best Sharpe is only marginally above 1.0, flag the strategy as likely overfit.
- Limit the number of free parameters. More than 5-6 tunable parameters on a single strategy is a red flag.

**Warning signs:**
- Out-of-sample performance drops more than 40% vs in-sample
- Optimal parameters are at extreme edges of the search range
- Small parameter changes cause large performance swings (fragile parameter landscape)
- Strategy requires very specific parameter values to be profitable

**Phase to address:**
Plan phase (parameter space design) and Execute phase (optimization loop). The plan phase must define the train/test split and parameter budget. The execute phase must enforce the budget and compute both in-sample and out-of-sample metrics.

---

### Pitfall 3: Claude Code Generates Silently Wrong Financial Calculations

**What goes wrong:**
Claude writes Python code with subtle mathematical errors: incorrect Sharpe ratio calculation (forgetting to annualize, using wrong risk-free rate), wrong drawdown computation (using returns instead of cumulative equity), incorrect position sizing (not accounting for existing positions), or broken commission/slippage modeling. The code runs without errors and produces numbers that look plausible but are wrong.

**Why it happens:**
LLMs generate code with high syntactic confidence but can hallucinate function signatures, use incorrect formulas, or make off-by-one errors in financial calculations. Financial math has many conventions (annualization factors differ for daily vs hourly data, Sharpe ratio has multiple valid formulations) and Claude may mix them or use the wrong one. Unlike a crash, a wrong number silently propagates.

**How to avoid:**
- Include a `references/metrics.py` file with verified, tested implementations of all core metrics: Sharpe ratio, Sortino ratio, max drawdown, CAGR, win rate, profit factor, Calmar ratio. Claude must import and use these rather than reimplementing them each time.
- Include unit tests for the metrics module with known-answer test cases (e.g., "given this equity curve, Sharpe should be exactly 1.23").
- The verify phase HTML report should display the raw equity curve data so users can sanity-check: "does the final equity match what I'd expect from the trade list?"

**Warning signs:**
- Sharpe ratio doesn't change when you change the timeframe (annualization is broken)
- Max drawdown is reported as a positive number or seems impossibly small
- Total return from equity curve doesn't match sum of individual trade P&Ls
- Commission impact is zero or negligible even with high-frequency strategies

**Phase to address:**
Core engine phase (Phase 1). The metrics module must be built and tested before any strategy runs. It should be a fixed, verified module -- not regenerated by Claude each time.

---

### Pitfall 4: Data Quality Failures Produce Garbage Backtests

**What goes wrong:**
Free data sources (yfinance, ccxt, Dukascopy) have gaps, incorrect values, split-unadjusted prices, survivorship bias, and inconsistent timestamps. A backtest runs on bad data and produces meaningless results. Crypto exchanges via ccxt frequently have missing candles for certain time periods. yfinance randomly returns NaN values or silently adjusts/unadjusts for splits mid-download.

**Why it happens:**
Free data is free for a reason. yfinance is an unofficial Yahoo Finance scraper that can break at any time. ccxt wraps exchange APIs that have inconsistent historical data availability. Users assume "I got data, therefore the data is correct." The backtest engine processes the data without validation and produces results that look legitimate.

**How to avoid:**
- Build a mandatory data validation step that runs before any backtest: check for NaN values, check for gaps larger than expected (weekends excluded for stocks, no gaps expected for 24/7 crypto), check for zero/negative prices, check for duplicate timestamps, check that OHLC relationships hold (High >= Open, Close, Low).
- Log data quality metrics: percentage of missing bars, number of gaps, date range covered. Display these in the verify report.
- For strategies sensitive to intraday data, warn users that free sources have significant quality limitations and suggest CSV fallback with premium data.
- Cache downloaded data locally so repeated backtests use the same data (reproducibility) and to avoid rate limiting.

**Warning signs:**
- Backtest period has fewer bars than expected for the timeframe
- Large price spikes or drops that don't correspond to real market events
- Strategy generates trades during periods where the market was actually closed
- Different backtest runs on the "same" data produce different results (data source returned different values)

**Phase to address:**
Data sourcing module (Phase 1 or early Phase 2). Data validation must be built before the optimization loop, because bad data + optimization = confidently wrong results.

---

### Pitfall 5: npm/npx Install Fails Silently or Partially

**What goes wrong:**
The `npx print-money-factory install` command needs to: copy slash command files to `~/.claude/commands/brrr/` (now `~/.claude/skills/brrr/`), create a Python venv, and install Python dependencies. Any of these steps can fail -- venv creation fails because Python 3.10+ isn't available, pip install fails due to network issues or compilation requirements (numpy/pandas wheels), the commands directory doesn't exist yet. The user thinks installation succeeded but the tool is broken.

**Why it happens:**
Postinstall scripts and install commands are notoriously fragile across platforms. macOS, Linux, and WSL have different Python paths, different compilation toolchains, and different permission models. Many users have `ignore-scripts` enabled for security (pnpm 10+ does this by default). The install script assumes a happy path that doesn't exist on many machines.

**How to avoid:**
- Do NOT use npm postinstall hooks. Use an explicit `npx print-money-factory install` command that the user runs intentionally.
- Make the install script idempotent -- running it twice should be safe and fix any partial state.
- Validate each step and report clearly: "Python 3.10+ found at /path", "venv created at /path", "dependencies installed (23/23)", "commands copied to ~/.claude/commands/brrr/ (8 files)". If any step fails, report exactly what failed and how to fix it.
- Check for Python 3.10+ BEFORE attempting venv creation. Provide a clear error message if not found.
- Use `--only-binary :all:` for pip installs where possible to avoid compilation failures.
- The update command must handle the migration from `commands/` to `skills/` directory structure as Claude Code evolves.

**Warning signs:**
- Users report "command not found" when trying `/brrr:*` commands
- Python errors about missing modules during execute phase
- Venv path hardcoded to a location that doesn't exist on the user's machine

**Phase to address:**
Installation/distribution phase (Phase 1). This must work reliably before anything else matters. Include a `brrr:doctor` diagnostic command that checks all prerequisites.

---

### Pitfall 6: Survivorship Bias in Stock/Crypto Backtests

**What goes wrong:**
Backtesting a stock-picking strategy using today's S&P 500 constituents ignores all the companies that were delisted, went bankrupt, or were removed from the index during the backtest period. This inflates returns because you're only testing on "winners." For crypto, testing on coins that still exist today ignores the thousands of tokens that went to zero.

**Why it happens:**
Free data sources only provide data for currently active instruments. yfinance can't easily retrieve data for delisted stocks. ccxt only connects to currently operating exchanges and currently listed pairs. Users don't realize their universe of instruments is biased.

**How to avoid:**
- Warn users explicitly during the plan phase when backtesting stock-selection or crypto-selection strategies that survivorship bias applies.
- For single-instrument strategies (e.g., "BTC/USDT mean reversion"), survivorship bias is less relevant -- document this distinction.
- For multi-instrument strategies, recommend using a fixed instrument list defined at the start of the backtest period, not today's list. Suggest premium point-in-time data sources if the strategy requires it.
- Include a "limitations" section in every backtest report that states which biases apply.

**Warning signs:**
- Portfolio strategy shows unrealistically high returns compared to benchmarks
- No losing instruments in the backtest universe
- Backtest universe size doesn't change over time (should shrink/grow as instruments list/delist)

**Phase to address:**
Research phase and Plan phase. The research workflow should flag survivorship bias risk for any multi-instrument strategy. The plan phase should document which biases apply and what mitigations are in place.

---

### Pitfall 7: Unrealistic Transaction Cost and Slippage Modeling

**What goes wrong:**
The backtest assumes zero commissions, zero slippage, and infinite liquidity. A strategy that trades 50 times per day with 0.01% average profit per trade looks amazing with zero costs but is deeply unprofitable with realistic costs (e.g., 0.1% per trade on crypto). High-frequency strategies are most affected but even swing trading strategies can be ruined by ignoring slippage on illiquid instruments.

**Why it happens:**
It's the simplest thing to omit from a backtest engine. Claude will generate a clean backtest loop that computes profit as `exit_price - entry_price` without any cost deduction unless explicitly instructed. Users see profitable results and don't question the assumptions.

**How to avoid:**
- Make transaction costs MANDATORY in the backtest engine. The plan phase must specify commission rate and slippage model. Default to conservative estimates: 0.1% for crypto, $0.005/share for US stocks, 1 pip for forex.
- Include a "cost sensitivity analysis" in the verify report: show strategy performance at 0x, 1x, 2x, and 3x the assumed transaction costs.
- For strategies with high trade frequency (>5 trades/day), require explicit slippage justification.

**Warning signs:**
- High-frequency strategy shows profit but no cost line items in trade log
- Average profit per trade is smaller than typical spread/commission
- Strategy profitability inverts when transaction costs are doubled

**Phase to address:**
Plan phase (cost assumptions) and Execute phase (cost enforcement in the engine). The backtest engine template must include cost deduction as a non-optional component.

---

## Technical Debt Patterns

| Shortcut | Immediate Benefit | Long-term Cost | When Acceptable |
|----------|-------------------|----------------|-----------------|
| Regenerating metrics code each run instead of using a fixed module | Less upfront work, Claude handles it | Inconsistent calculations across runs, subtle bugs | Never -- metrics must be fixed and tested |
| Storing all state in STATE.md as freeform text | Quick to implement | Parsing becomes fragile, state corruption on edge cases | MVP only, migrate to structured YAML/JSON early |
| Skipping data validation | Faster backtest execution | Garbage-in-garbage-out, impossible to debug results | Never -- even a minimal check (NaN count, date range) is essential |
| Hardcoding venv path | Works on developer's machine | Breaks on any different system | Never -- derive from project root or user home |
| Using Claude to generate PineScript without validation | Ships an export quickly | PineScript has strict syntax rules Claude may violate; user pastes broken code into TradingView | MVP only, add PineScript syntax validation in export phase |
| Embedding all plotly JS in HTML reports | Self-contained reports, no CDN dependency | HTML files are 3-4MB each, slow to open | Acceptable -- self-contained is more important for this use case |

## Integration Gotchas

| Integration | Common Mistake | Correct Approach |
|-------------|----------------|------------------|
| yfinance | Assuming data is always available and consistent; not handling the `auto_adjust` parameter correctly (changed defaults between versions) | Pin yfinance version, always validate returned DataFrame shape and content, handle empty returns gracefully, explicitly set `auto_adjust=True` |
| ccxt | Assuming all exchanges support the same timeframes and history depth; not handling rate limits | Check exchange capabilities before requesting data, implement retry with exponential backoff, cache fetched data locally, handle exchange-specific timestamp formats |
| Dukascopy | Assuming tick data is available for all pairs and all history; large downloads that time out | Download in chunks (month by month), validate downloaded data integrity, handle connection timeouts gracefully |
| plotly (HTML reports) | Generating HTML with external CDN references that break offline | Use `plotly.offline.plot()` with `include_plotlyjs=True` for self-contained HTML files |
| optuna (Bayesian optimization) | Letting optuna run indefinitely; not setting proper search space bounds | Set `n_trials` limit, define reasonable parameter bounds in plan phase, use `timeout` parameter as safety net |
| Claude Code slash commands | Assuming `$ARGUMENTS` parsing is robust for complex inputs; not handling missing arguments | Validate argument presence at the start of each workflow, provide clear error messages, use `argument-hint` in frontmatter |
| Python venv | Assuming `python3` exists and is 3.10+; venv creation failing silently on some Linux distros | Check Python version explicitly, test venv activation, use `python3 -m venv` not `virtualenv`, handle missing `ensurepip` on Debian-based systems |

## Performance Traps

| Trap | Symptoms | Prevention | When It Breaks |
|------|----------|------------|----------------|
| Loading entire dataset into memory for each optimization iteration | Slow optimization, high memory usage | Load data once, pass DataFrame reference to strategy function | Datasets > 1M rows (multi-year intraday data) |
| Generating a new PNG equity curve for every iteration | Disk fills up, matplotlib is slow | Only generate PNG for iterations that improve best metric; cap at ~20 PNGs per phase | > 50 iterations |
| Storing full trade log in STATE.md | STATE.md becomes huge, Claude struggles to parse it | Store summary metrics in STATE.md, keep full trade logs as separate CSV files | > 100 iterations with > 50 trades each |
| Running walk-forward optimization with too many windows | Optimization takes hours | Default to 5-10 walk-forward windows; let users increase if desired | > 20 windows with > 100 iterations each |
| Claude re-reading entire conversation history with each command | Context window fills up, responses slow down | Use `context: fork` for compute-heavy phases (execute, verify); keep conversation lean | > 10 iterations in a single session |

## Security Mistakes

| Mistake | Risk | Prevention |
|---------|------|------------|
| Storing API keys (polygon.io, exchange keys) in STATE.md or strategy files | Keys committed to git, exposed in reports | Store API keys in environment variables only; never write them to any project file; add `.env` to `.gitignore` template |
| Generated Python code executing arbitrary imports or system calls | Malicious or accidental system damage | The backtest Python code runs in a venv, but still has filesystem access. Limit imports in generated code to an allowlist (pandas, numpy, ccxt, yfinance, etc.) |
| Publishing npm package with test API keys or credentials | Public exposure of keys | Use `.npmignore` to exclude all dotfiles, test data, and local config; verify package contents with `npm pack --dry-run` before publishing |
| User's exchange API keys used in data fetching having trade permissions | Accidental trades if code bugs occur | Document that users should create read-only API keys for data fetching; warn in install flow |

## UX Pitfalls

| Pitfall | User Impact | Better Approach |
|---------|-------------|-----------------|
| Optimization loop runs for 30+ minutes with no progress indication | User thinks it's frozen, kills the process | Print iteration number, current best metric, and ETA after each iteration; use the per-iteration PNG as visual feedback |
| AI diagnosis in debug mode is vague ("try different parameters") | User gets no actionable next step | Require AI diagnosis to specify exact parameter changes, or flag specific issues (e.g., "entry condition triggers too rarely -- only 3 trades in 2 years") |
| Verify report HTML is only viewable in browser but user is SSH'd into a server | Report is inaccessible | Also generate a text-based summary that prints to terminal; HTML is supplementary |
| Strategy state lost when Claude session ends mid-execution | Hours of optimization lost | Write iteration results to disk after EACH iteration, not just at the end; resume from last completed iteration |
| Too many slash commands to remember | User doesn't know what to do next | The `brrr:status` command must clearly show the next recommended command and what it will do |

## "Looks Done But Isn't" Checklist

- [ ] **Backtest engine:** Does it use next-bar execution? Verify that signal generation and trade execution use different bars
- [ ] **Backtest engine:** Are transaction costs applied to every trade? Check the trade log shows cost deductions
- [ ] **Data module:** Does it validate data before passing to backtest? Check for NaN handling, gap detection, OHLC sanity
- [ ] **Optimization loop:** Does it hold out test data? Verify that out-of-sample metrics are computed and displayed
- [ ] **Metrics module:** Does Sharpe ratio annualize correctly for the data frequency? Test with known-answer cases
- [ ] **Install script:** Does it work on a clean machine with no prior setup? Test on fresh macOS AND Linux
- [ ] **PineScript export:** Does the generated code compile in TradingView? Paste-test before shipping
- [ ] **HTML report:** Does it open correctly when double-clicked from Finder/file manager? Test the file:// path
- [ ] **STATE.md:** Can the system resume after a session restart? Kill Claude mid-optimization and restart
- [ ] **Hypothesis protection:** Does it actually detect drift? Test by gradually changing the strategy idea during debug cycles

## Recovery Strategies

| Pitfall | Recovery Cost | Recovery Steps |
|---------|---------------|----------------|
| Lookahead bias in results | HIGH | All previous results are invalid. Must fix the engine and re-run all backtests from scratch. No partial recovery possible. |
| Overfitting discovered | MEDIUM | Re-run with walk-forward validation on the same strategy. If it fails walk-forward, the strategy concept may still be valid with fewer parameters. |
| Wrong metrics calculations | HIGH | Fix metrics module, re-run all backtests. Previous verify reports are misleading and should be discarded. |
| Bad data quality | MEDIUM | Re-download data with validation enabled. Re-run backtests. Previous results on clean portions of data may still be valid. |
| Partial npm install | LOW | Run `npx print-money-factory install` again (must be idempotent). Add a `brrr:doctor` command to diagnose issues. |
| Lost optimization state | MEDIUM | If per-iteration artifacts were saved to disk, resume from last iteration. If not, full re-run required. |
| PineScript export doesn't compile | LOW | Manual fix in TradingView editor. Add the specific syntax error to Claude's reference material for future strategies. |

## Pitfall-to-Phase Mapping

| Pitfall | Prevention Phase | Verification |
|---------|------------------|--------------|
| Lookahead bias | Phase 1: Core engine design | Unit test: strategy that peeks at future data should produce different results than event-loop version |
| Overfitting | Plan phase + Execute phase | Out-of-sample metrics displayed alongside in-sample; iteration count tracked and capped |
| Wrong metrics | Phase 1: Metrics module | Known-answer unit tests pass; metrics match a reference implementation (e.g., compare with empyrical or quantstats) |
| Data quality | Phase 1/2: Data module | Validation report generated before every backtest; NaN count and gap count logged |
| npm install failures | Phase 1: Distribution/install | Test matrix: macOS (Intel + ARM), Ubuntu, WSL. `brrr:doctor` command passes on all |
| Survivorship bias | Research + Plan phases | Limitations section in every verify report lists applicable biases |
| Unrealistic costs | Plan + Execute phases | Cost sensitivity table in verify report; default costs are non-zero |
| Silent state loss | Execute phase architecture | Iteration artifacts exist on disk after each iteration; resume tested |
| Claude hallucinated code | All phases (ongoing) | Reference files in `references/` for critical patterns; metrics module is fixed code not regenerated |
| Skills/commands directory migration | Install + Update phases | `brrr:update` detects old directory structure and migrates; works with both `.claude/commands/` and `.claude/skills/` |

## Sources

- [LuxAlgo: Backtesting Traps Common Errors](https://www.luxalgo.com/blog/backtesting-traps-common-errors-to-avoid/) - Comprehensive overview of backtesting biases
- [StarQube: Critical Pitfalls of Backtesting](https://starqube.com/backtesting-investment-strategies/) - Overfitting and lookahead analysis
- [FX Replay: Backtesting Biases](https://www.fxreplay.com/learn/backtesting-biases-how-traders-fool-themselves-without-knowing-it) - Survivorship and selection bias
- [The Hans India: Python Backtesting Pain Points](https://www.thehansindia.com/tech/python-backtesting-pain-points-data-execution-assumptions-and-evaluation-1057056) - Event-loop architecture, execution assumptions
- [Sling Academy: Handling Missing Data with yfinance](https://www.slingacademy.com/article/handling-missing-or-incomplete-data-with-yfinance/) - Data gap handling strategies
- [ccxt/ccxt Issue #24732: Missing Data](https://github.com/ccxt/ccxt/issues/24732) - Real-world ccxt data gap example
- [QuantInsti: Walk-Forward Optimization](https://blog.quantinsti.com/walk-forward-optimization-introduction/) - Walk-forward methodology and limitations
- [Unger Academy: Walk Forward Analysis Mistakes](https://ungeracademy.com/posts/how-to-use-walk-forward-analysis-you-may-be-doing-it-wrong) - Meta-overfitting through WFO
- [Claude Code Docs: Slash Commands / Skills](https://code.claude.com/docs/en/slash-commands) - Current skills system, frontmatter, allowed-tools
- [GitHub Issue #4637: Custom Command File Path Permissions](https://github.com/anthropics/claude-code/issues/4637) - Permission prompt friction for cross-directory access
- [npm Security Best Practices](https://github.com/lirantal/npm-security-best-practices) - Postinstall script risks
- [arxiv 2311.15548: LLM Deficiency in Finance](https://arxiv.org/abs/2311.15548) - LLM hallucination in financial tasks
- [arxiv 2601.19106: Hallucinations in LLM-Generated Code](https://arxiv.org/pdf/2601.19106) - Code-specific hallucination patterns

---
*Pitfalls research for: AI-driven trading strategy backtesting CLI (Claude Code command package)*
*Researched: 2026-03-21*
