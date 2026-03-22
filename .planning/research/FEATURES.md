# Feature Landscape

**Domain:** AI-assisted trading strategy development CLI (backtest-to-export pipeline)
**Researched:** 2026-03-22
**Milestone:** v1.1 Enhancement Features

## Table Stakes

Features users expect in a v1.1 of a tool that already has a working pipeline. These are polish items that feel like oversights if missing.

### Bayesian Optimization (Optuna Integration)

| Feature | Why Expected | Complexity | Depends On |
|---------|--------------|------------|------------|
| Optuna TPE sampler as optimization method | Grid/random search already exist. Any tool with 5+ parameters needs smarter search. Users who saw optuna in the dependency list expect it to work. TPE is the default Optuna sampler and the right choice -- it outperforms random search after ~20 trials and handles conditional parameter spaces natively. | Med | Existing execute.md iteration loop, plan.md method selection |
| `suggest_*` API for parameter proposals | Optuna's `trial.suggest_int()`, `trial.suggest_float()`, `trial.suggest_categorical()` replace manual parameter selection in execute Step 5f. The AI currently hand-picks next parameters; Optuna should propose them instead, with AI retaining veto/override power. | Med | Optuna study object persisted across iterations |
| Optuna study persistence (SQLite) | Studies must survive session interruptions. Optuna natively supports `optuna.create_study(storage="sqlite:///.pmf/phases/phase_N_execute/optuna_study.db")`. This enables `--resume` to work with Bayesian state, not just iteration artifacts. | Low | `--resume` flag in execute.md |
| Pruning unpromising trials | Optuna's `MedianPruner` (for random) or `HyperbandPruner` (for TPE) can stop bad parameter combos early. For backtesting: report intermediate Sharpe at 25%, 50%, 75% of data. If Sharpe at 50% is terrible, prune. Saves significant execution time on large parameter spaces. | Med | Optuna study, backtest engine reporting intermediate values |
| Multi-objective optimization support | Traders always optimize for multiple conflicting goals: high Sharpe AND low drawdown AND sufficient trades. Optuna supports multi-objective natively via `create_study(directions=["maximize", "minimize", "maximize"])`. Pareto-optimal solutions replace single-metric ranking. | High | Plan.md changes to define multiple objectives, verify.md to display Pareto front |
| Warm-starting from prior phases | When debug cycle opens Phase N+1, the Optuna study from Phase N should seed the new study. Optuna supports `enqueue_trial()` to inject known good parameters. This carries forward optimization knowledge across debug cycles. | Low | Debug cycle flow in verify.md |

### Diagnostic / Maintenance Commands

| Feature | Why Expected | Complexity | Depends On |
|---------|--------------|------------|------------|
| `/brrr:doctor` -- environment health check | Users hit install issues silently (wrong Python version, missing deps, broken venv). A doctor command is standard practice in CLI tools (homebrew doctor, npm doctor, flutter doctor). Should check: Python version >= 3.10, venv exists and activates, all pip deps importable, disk space, data source connectivity. | Low | Existing install script, requirements.txt |
| Auto version check (silent, once per session) | npm packages update frequently. Users running stale commands miss fixes. Check `npm view @print-money-factory/cli version` once per session, compare to installed, show one-line notice if outdated. Never block execution. | Low | npm registry, package.json version |
| Dependency version reporting in doctor | Show exact versions of critical deps (pandas, optuna, plotly, ccxt, yfinance) vs expected versions. Version mismatches cause subtle bugs (pandas 2.x vs 3.x column behavior). | Low | requirements.txt, pip list |
| Data source connectivity test | Doctor should attempt a tiny data fetch from each configured source (1 bar of BTC/USDT from ccxt, 1 day of SPY from yfinance) to verify API access. Report pass/fail per source. | Low | data_sources.py adapters |

### Debug Cycle Memory (Smarter Debug Cycles)

| Feature | Why Expected | Complexity | Depends On |
|---------|--------------|------------|------------|
| Failed approach registry | Current debug cycles carry forward via `debug_diagnosis.md`, but the discuss workflow only reads the LAST phase's diagnosis. It should read ALL prior diagnoses and maintain a structured "tried and failed" list. This prevents the AI from re-suggesting approaches that already failed. | Med | verify.md debug path, discuss.md debug-discuss mode |
| Cross-phase metric trajectory | Show a metric progression chart across ALL phases (not just within one phase's iterations). Phase 1 best Sharpe: 0.7, Phase 2: 1.1, Phase 3: 1.4 -- this trajectory reveals whether debug cycles are converging or stalling. | Low | STATE.md best metrics per phase |
| Automatic phase budget warning | If the milestone has gone through 3+ debug cycles without meeting targets, warn the user that the hypothesis may be fundamentally flawed. Suggest a new milestone with a different approach. Currently drift detection exists, but cycle count exhaustion does not. | Low | STATE.md phase count |
| Structured parameter changelog | Track which parameters changed between phases (not just between iterations). Phase 1 used EMA 10/50; Phase 2 added ADX filter; Phase 3 switched to SMA. This log helps the AI and user understand the strategy's evolution. | Low | phase_N_discuss.md files, plan artifacts |

### Equity PNG Bug Fix

| Feature | Why Expected | Complexity | Depends On |
|---------|--------------|------------|------------|
| Fix blank equity curve PNGs during execute | Currently broken. matplotlib renders blank graphs during `/brrr:execute` iterations. This is a critical bug -- visual iteration feedback is the primary way users track optimization progress. Most likely cause: matplotlib figure not receiving data before `savefig()`, or the equity curve array is empty/wrong type. | Low | execute.md Step 5d, matplotlib Agg backend |

## Differentiators

Features that would make v1.1 notably better than v1.0, beyond expected polish.

### Enhanced Export

| Feature | Value Proposition | Complexity | Depends On |
|---------|-------------------|------------|------------|
| MD-instruction bot-building guide | A new export file (`bot-building-guide.md`) that gives step-by-step instructions for implementing the strategy as a live trading bot. Covers: which platform/broker to use for the asset class, API setup, position sizing for real account size, risk management rules, monitoring checklist, and common gotchas. This bridges the gap between "backtest approved" and "actually trading." No competitor exports this. | Med | Existing export flow in verify.md Step 5a, strategy artifacts |
| Platform-specific implementation sections | The bot-building guide should have sections for the 2-3 most relevant platforms per asset class: crypto (ccxt + exchange API), stocks (Alpaca/IBKR API), forex (MT4/MT5 EA). Each section: "How to implement THIS strategy on THIS platform." | High | Asset class detection from STRATEGY.md |
| Claude Code prompt for bot building | Export a `.md` file that IS a Claude Code prompt -- the user can paste it into a new Claude Code session and say "build this bot" and it contains all the context needed. Strategy logic, parameters, risk rules, platform preferences. This is uniquely powerful because the tool runs IN Claude Code. | Med | All strategy artifacts, best_result.json |

### Advanced Optimization Features

| Feature | Value Proposition | Complexity | Depends On |
|---------|-------------------|------------|------------|
| Optuna visualization integration | Optuna has built-in visualization (`optuna.visualization.plot_optimization_history`, `plot_param_importances`, `plot_pareto_front`). Embed these in the HTML report alongside existing plotly charts. Shows which parameters matter most and how optimization progressed. | Med | Optuna study persistence, report_generator.py |
| CMA-ES sampler for continuous parameters | When all parameters are continuous (floats), CMA-ES outperforms TPE. Optuna supports it via `CmaEsSampler`. Auto-select based on parameter types in plan.md. | Low | Optuna, plan.md parameter type detection |
| Constrained optimization | Optuna supports constraints (e.g., "maximize Sharpe subject to drawdown < 15%"). Currently the execute loop checks constraints post-hoc. With Optuna constraints, bad regions are avoided entirely. | Med | Optuna study, plan.md constraint definitions |

## Anti-Features

Features to explicitly NOT build in v1.1.

| Anti-Feature | Why Avoid | What to Do Instead |
|--------------|-----------|-------------------|
| Full Optuna dashboard (web UI) | Optuna has a dashboard (`optuna-dashboard`) but it requires a running server. Violates the "no server" constraint. Would split attention from the CLI experience. | Embed Optuna visualizations as static plots in the HTML report. |
| Automatic strategy generation from Optuna | Using Optuna to generate strategy LOGIC (not just parameters) crosses into StrategyQuant territory. Produces overfitted garbage without human hypothesis guiding it. | Optuna optimizes parameters within a human-defined strategy. The human + AI hypothesis loop is the differentiator. |
| Real-time monitoring of live bots | The bot-building guide exports instructions, not a monitoring system. Building monitoring is scope creep into ops tooling. | Export checklist of what to monitor. User sets up monitoring on their platform. |
| Multi-strategy Optuna optimization | Optimizing a portfolio of strategies simultaneously is a different problem requiring correlation analysis, capital allocation, and rebalancing logic. | One strategy per milestone. Portfolio construction is a separate tool. |
| Custom Optuna samplers | OptunaHub has exotic samplers (VaR, GP-based). These add complexity without clear value for typical trading parameter spaces where TPE and CMA-ES cover 99% of use cases. | Stick to TPE (default), CMA-ES (continuous params), and random (baseline). |
| Dependency auto-repair in doctor | Doctor should DIAGNOSE, not FIX. Auto-repairing venvs or reinstalling deps risks breaking the user's setup worse. | Doctor reports what's wrong. User runs `/brrr:update` to fix. |

## Feature Dependencies

```
Optuna study creation --> Optuna TPE sampler (study required for any sampler)
Optuna study creation --> Optuna pruning (pruner attaches to study)
Optuna study creation --> Optuna persistence (SQLite storage)
Optuna study persistence --> Warm-starting from prior phases (need saved study to seed from)
Optuna study persistence --> --resume with Bayesian state
Optuna study creation --> Multi-objective optimization
Optuna study persistence --> Optuna visualization in report

Plan.md method selection --> Optuna integration (plan must offer "bayesian" as optimization method)
Execute.md iteration loop --> Optuna parameter suggestion (replaces manual Step 5f)

Failed approach registry --> Smarter discuss debug-discuss mode
Cross-phase metric trajectory --> STATUS command enhancement
Automatic phase budget warning --> STATE.md phase count tracking (already exists)

Existing export flow (verify Step 5a) --> MD-instruction bot-building guide (new export file)
STRATEGY.md asset class --> Platform-specific sections in guide

Equity PNG bug fix --> (standalone, no dependencies, should be done first)
Doctor command --> (standalone, no dependencies on other v1.1 features)
Auto version check --> (standalone, npm registry access only)
```

## Priority Recommendation

### Must-have for v1.1 (ship or it's not worth a release):

1. **Fix equity PNG bug** -- broken feature in v1.0, users see blank charts, zero dependencies, fix first
2. **Optuna TPE integration in execute loop** -- the headline feature. Replace manual AI parameter selection with Optuna suggestions + AI oversight. Study persistence via SQLite for resume support.
3. **`/brrr:doctor` diagnostic command** -- low effort, high user trust. Environment health check catches the silent failures that cause bad support experiences.
4. **Failed approach registry** -- the current debug cycle "forgets" too easily. A structured list of what was tried and why it failed prevents circular optimization.

### Should-have for v1.1 (significantly improves the release):

5. **Auto version check** -- trivial to implement, prevents stale installs
6. **MD-instruction bot-building guide export** -- the most valuable new export. Bridges backtest-to-live gap that every competitor ignores.
7. **Cross-phase metric trajectory** -- simple visualization that reveals whether debug cycles are converging
8. **Warm-starting Optuna from prior phases** -- makes debug cycles smarter without user effort

### Nice-to-have (defer if scope pressure):

9. **Optuna pruning** -- saves time on large parameter spaces but not critical for initial integration
10. **Multi-objective optimization** -- powerful but adds complexity to plan and verify workflows
11. **Optuna visualization in HTML report** -- enhancement to existing report, not blocking
12. **Platform-specific bot-building sections** -- high effort, narrow audience per section
13. **Claude Code prompt export** -- clever but low urgency

## Complexity Budget

| Feature Group | Estimated Effort | Files Modified |
|---------------|-----------------|----------------|
| Equity PNG fix | 1-2 hours | execute.md (Step 5d), possibly backtest_engine.py |
| Optuna core integration | 1-2 days | plan.md, execute.md (Steps 4, 5f), new optuna_optimizer.py |
| Doctor command | 0.5 day | new command doctor.md, new workflow doctor.md |
| Auto version check | 2-3 hours | All command preambles or shared preamble include |
| Debug cycle memory | 0.5-1 day | verify.md (Step 5b), discuss.md (Step 2-debug), STATE.md schema |
| Bot-building guide export | 0.5-1 day | verify.md (Step 5a, new sub-step), new template |
| Optuna advanced (pruning, multi-obj, viz) | 1-2 days | execute.md, report_generator.py, verify.md |

**Total estimated: 4-7 days of development**

## Sources

- [Optuna TPESampler docs](https://optuna.readthedocs.io/en/stable/reference/samplers/generated/optuna.samplers.TPESampler.html) - TPE sampler API and defaults
- [Optuna efficient optimization](https://optuna.readthedocs.io/en/stable/tutorial/10_key_features/003_efficient_optimization_algorithms.html) - Pruning and sampler selection
- [OptunaHub samplers](https://hub.optuna.org/samplers/) - Available samplers including CMA-ES
- [Optuna GitHub releases](https://github.com/optuna/optuna/releases) - v4.7.0+ features
- [Traderize - Debug Bot Best Practices](https://blog.traderize.com/posts/debug_bot/) - Diagnostic logging, health checks
- [3Commas - Backtesting Guide 2025](https://3commas.io/blog/comprehensive-2025-guide-to-backtesting-ai-trading) - Optimization workflow patterns
- [Petr Vojacek - Trading Bot Risks](https://petrvojacek.cz/en/blog/trading-bot-risks-and-tools/) - Overfitting detection, ongoing maintenance
- [Piotr Pomorski - Hyperparameter optimization with backtesting](https://piotrpomorski.substack.com/p/hyperparameter-optimisation-with) - Optuna + trading strategy integration pattern
- [LuxAlgo - Building Your First Trading Bot](https://www.luxalgo.com/blog/building-your-first-trading-bot-step-by-step-guide/) - Bot deployment best practices
