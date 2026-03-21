# Project Research Summary

**Project:** Print Money Factory
**Domain:** AI-driven trading strategy development CLI (Claude Code slash-command npm package)
**Researched:** 2026-03-21
**Confidence:** HIGH

## Executive Summary

Print Money Factory is a Claude Code slash-command package that guides users through an AI-driven backtest-to-export pipeline for trading strategies. The product has two distinct technical surfaces: a thin npm distribution layer (file copier + install script) and a Python computation engine (backtest, optimization, reporting) running in an isolated venv. The right mental model is not "build a backtesting framework" — it is "build reference patterns that Claude uses to write custom Python per strategy." Every strategy gets fresh, tailored code; the package ships the patterns and plumbing, not a generic library. This is the architectural choice that separates this tool from competitors like backtesting.py and vectorbt.

The recommended approach is straightforward: lean on the GSD (get-shit-done) pattern for the npm/command side, use a thin command → fat workflow delegation structure, and make STATE.md the single router for the milestone lifecycle. On the Python side, ship a verified metrics module and canonical event-loop backtest pattern in references/, then let Claude compose those building blocks into strategy-specific code at runtime. Use matplotlib for iteration PNGs (headless, no Chrome dep), plotly for the final interactive HTML report, and optuna for Bayesian optimization once grid search is proven. The AI-driven iteration loop — where Claude reads metrics + equity curves, diagnoses problems, and adjusts parameters automatically — is the core differentiator and must work well before anything else matters.

The highest-risk areas are lookahead bias in Claude-generated backtest code, overfitting through excessive parameter optimization, and silent failures in financial metric calculations. All three have HIGH recovery costs (requires discarding and re-running all previous results). These must be addressed in Phase 1 by shipping a fixed, tested metrics module and a canonical event-loop pattern in references/ that all generated code must follow. The npm install reliability is also critical — a failed silent install means users never reach the value proposition.

## Key Findings

### Recommended Stack

The npm layer is deliberately thin: Node.js >=18, plain `fs` operations to copy command files, and a Node.js install script that creates the Python venv. No framework needed — it is a file copier. The Python layer is where all computation happens: Python >=3.10 (floor set by dukascopy-python), pandas ^3.0, numpy ^2.4, matplotlib ^3.10 for iteration PNGs, plotly ^6.5 for HTML reports, optuna ^4.7 for Bayesian optimization, and data sources (ccxt, yfinance, dukascopy-python, polygon-api-client). Three critical version decisions stand out: use `polygon-api-client` (not `massive` — the rebrand is too recent for ecosystem adoption), use `ta` (pure Python indicators) not `ta-lib` (C extension that fails on macOS ARM), and use matplotlib Agg backend for PNGs (kaleido v1.0 now requires Chrome, which is unacceptable for a CLI tool).

**Core technologies:**
- Node.js >=18 / npm: distribution layer — npx install UX, file copying, venv creation
- Python >=3.10 + venv: computation isolation — all backtest, optimization, and reporting runs here
- pandas ^3.0 + numpy ^2.4: data manipulation — industry standard for OHLCV time series
- matplotlib ^3.10 (Agg): iteration equity PNGs — headless, no Chrome dep
- plotly ^6.5: final HTML reports — self-contained interactive files, no server needed
- optuna ^4.7: Bayesian optimization — TPE sampler, pruning, best-in-class API
- ccxt + yfinance + dukascopy-python + polygon-api-client: data sources — crypto/stocks/forex coverage
- ta ^0.11: technical indicators — pure Python, pandas-native, no C compilation
- jinja2 ^3.1: HTML report templating — Python standard, Claude knows it well

### Expected Features

**Must have (table stakes):**
- Core metrics suite (net P&L, win rate, profit factor, max drawdown, Sharpe, Sortino) — traders evaluate strategies on these; missing any = amateur
- Commission and slippage modeling — without this, all metrics are lies
- Equity curve + drawdown visualization — per-iteration PNG during execute, plotly in final report
- Trade log with per-trade details — traders audit individual trades; black-box results = distrust
- In-sample / out-of-sample split — enforced by default; testing on optimization data is the #1 beginner mistake
- Grid search parameter optimization — simple, understandable; baseline expectation
- AI-driven iteration loop — THE differentiator; Claude reads metrics, diagnoses, adjusts, re-runs
- HTML report generation — traders need a shareable deliverable
- PineScript v5 export — bridge from backtest to live trading; table stakes for retail traders
- At least one working data source (ccxt or yfinance) — can't run without data

**Should have (competitive differentiators):**
- AI post-mortem diagnosis on debug cycles — no competitor does this
- Walk-forward analysis — gold standard validation; most retail tools skip it
- Bayesian optimization via optuna — smarter than grid search for large parameter spaces
- Parameter heatmap in HTML report — instantly reveals robustness vs fragility
- Regime breakdown analysis — shows WHEN a strategy works, not just IF
- Monte Carlo simulation — reveals path-dependent luck in results
- Hypothesis drift protection — detects when iterative tweaking has diverged from original idea
- Context file support (images/PDFs in .pmf/context/) — leverages Claude's multimodal capability

**Defer (v2+):**
- Multiple data sources beyond the first working one — ship one, expand incrementally
- Correlation to benchmark — low effort, low priority; add when users ask
- Paper trading bridge — out of scope; direct users to TradingView PineScript for paper trading

**Explicit anti-features (never build):**
- Live trading execution — liability, regulatory risk, scope creep
- Web UI or dashboard — Claude Code IS the interface
- Multi-strategy portfolio backtesting — exponentially more complex, different problem
- Built-in indicator library — maintenance nightmare; Claude writes indicators inline

### Architecture Approach

The system mirrors the GSD architecture pattern: thin command markdown files (5-15 lines + YAML frontmatter) delegate to fat workflow markdown files (hundreds of lines) via `@` references. STATE.md is the single router — every command reads it first to validate position and refuse out-of-order execution. The Python backtest engine is NOT a fixed library; `references/backtest-engine.md` ships canonical patterns, and Claude composes custom code per strategy at runtime. Phase artifacts are append-only (debug cycles create phase_2, phase_3... not overwrites), preserving full history for AI diagnosis. The Python execution bridge is simple: Claude writes a .py file, runs it via `~/.pmf-venv/bin/python`, reads back JSON + PNG results.

**Major components:**
1. commands/ — thin entry points for Claude Code slash commands (`/brrr:*`)
2. workflows/ — full behavioral prompts with decision trees and output formats
3. references/ — read-only knowledge: backtest engine patterns, metrics formulas, data source configs, pitfall catalog
4. templates/ — scaffolding: STRATEGY.md, STATE.md, report-template.html, pinescript-template.pine
5. scripts/install.js — copies commands to `~/.claude/commands/brrr/`, creates Python venv at `~/.pmf-venv/`
6. bin/pmf-tools.cjs — version check, venv helpers
7. .pmf/ (user project) — per-project state: STRATEGY.md, STATE.md, phases/, context/
8. output/ (user project) — final deliverables on milestone close: PineScript, reports, clean Python

**Key patterns:**
- Thin command / fat workflow delegation (mirroring GSD)
- State-driven command routing via STATE.md
- Claude-generated Python from reference patterns (not a fixed library)
- Accumulated phase history (append-only, never overwrite)

### Critical Pitfalls

1. **Lookahead bias in Claude-generated backtest code** — use a canonical event-loop pattern in references/ (signal at bar N, execute at bar N+1 open); include a mandatory lookahead audit step in the execute workflow; any Sharpe > 3.0 is a red flag requiring investigation. Recovery cost: HIGH (all results invalid, must re-run from scratch).

2. **Overfitting through excessive parameter optimization** — enforce mandatory train/test split (70/30 default); cap iterations at ~50 per phase; require out-of-sample metrics alongside in-sample; limit free parameters to 5-6 max. Recovery cost: MEDIUM (walk-forward validation can salvage valid strategy concepts).

3. **Silent wrong financial calculations** — ship a fixed, tested `references/metrics.py` with verified implementations of Sharpe, Sortino, max drawdown, CAGR, profit factor; include known-answer unit tests; Claude imports from this module rather than reimplementing each time. Recovery cost: HIGH (all previous verify reports are misleading, must re-run).

4. **Data quality failures from free sources** — build mandatory data validation before any backtest: check NaN count, gap detection, OHLC sanity, duplicate timestamps; log data quality metrics in the verify report; cache downloaded data locally for reproducibility. Recovery cost: MEDIUM (re-download with validation, re-run on affected date ranges).

5. **npm/npx install fails silently or partially** — use explicit `npx print-money-factory install` (not postinstall hook); make install idempotent; validate and report each step clearly; check Python 3.10+ before venv creation; include a `brrr:doctor` diagnostic command; test on macOS Intel/ARM + Ubuntu + WSL. Recovery cost: LOW (re-run install).

## Implications for Roadmap

Based on combined research, the dependency chain is clear: install must work before anything else, the metrics module and event-loop pattern must be solid before any optimization runs, and the AI iteration loop (the core differentiator) must prove itself before adding advanced features. This suggests 5 phases.

### Phase 1: Foundation + Install + Core Engine

**Rationale:** Three critical pitfalls (lookahead bias, wrong metrics, install failures) all require Phase 1 solutions. Nothing else is valid until the metrics are correct and the install works. Architecture research explicitly recommends this build order: package scaffolding → references → install → state management.
**Delivers:** Working `npx print-money-factory install`, fixed metrics module, canonical event-loop backtest pattern, STATE.md schema, STRATEGY.md schema, `/brrr:new-milestone`, `/brrr:status`, `brrr:doctor`
**Addresses:** Core metrics suite, commission/slippage modeling, data validation (even minimal), install reliability
**Avoids:** Lookahead bias (canonical pattern in references/), wrong metric calculations (fixed tested module), silent install failures (validation + doctor command)
**Needs research:** No — install patterns, Python venv, and npm distribution are well-documented

### Phase 2: Strategy Discussion + Planning Commands

**Rationale:** The "thinking" commands (discuss, plan) don't require Python execution and establish the spec that execute depends on. Building them before execute means execute has solid inputs when we get there. Natural language → formal spec is Claude's core strength and requires careful prompt engineering.
**Delivers:** `/brrr:discuss` (strategy decision gathering, natural language to STRATEGY spec), `/brrr:plan` (parameter space design, optimization method selection, train/test split definition)
**Addresses:** Out-of-sample split enforcement (plan phase mandates it), position sizing, stop-loss/take-profit, commission assumptions
**Avoids:** Overfitting through pre-defining parameter budget and split in plan phase before any optimization runs
**Needs research:** No — prompt engineering for structured output is well-understood; plan workflow design follows GSD patterns

### Phase 3: Execute Phase (AI Backtest Loop)

**Rationale:** This is the hardest component and the core differentiator. It depends on: working install (Phase 1), solid references/backtest-engine.md (Phase 1), and clear plan output (Phase 2). Building it third gives it the best foundation. The Python execution bridge (write → run → read JSON/PNG) is the key integration to get right.
**Delivers:** `/brrr:execute` with full AI iteration loop: Claude writes custom backtest.py from plan, runs it, reads metrics.json + equity.png, diagnoses, adjusts parameters, stops on MINT/PLATEAU/REKT; per-iteration artifact files; grid search optimization; data loading from at least one source (start with ccxt or yfinance)
**Addresses:** AI-driven iteration loop (the differentiator), equity curve + drawdown visualization, trade log, data sourcing
**Avoids:** Lookahead bias (canonical event-loop reference enforced), overfitting (iteration cap + OOS metrics), data quality failures (validation before each run)
**Needs research:** YES — data source API integration (ccxt rate limits, yfinance edge cases), Python execution bridge reliability across platforms

### Phase 4: Verify + Export

**Rationale:** Depends entirely on execute producing real artifacts to verify against. Can't be built without real iteration data to generate reports from. PineScript export is the highest-complexity table-stakes feature and needs its own focus.
**Delivers:** `/brrr:verify` with plotly HTML report generation (equity curve, drawdown, parameter heatmap, trade log table, cost sensitivity analysis, bias limitations section), `--approved` flow (generates output/ package: PineScript v5, trading-rules.md, performance-report.md, live-checklist.md, backtest_final.py), `--debug` flow (AI post-mortem diagnosis, new phase cycle)
**Addresses:** HTML report generation, PineScript v5 export, overfitting detection warnings, survivorship bias warnings, regime breakdown (basic)
**Avoids:** Unrealistic cost modeling (cost sensitivity table in report), hypothesis drift (comparison to original STRATEGY.md)
**Needs research:** YES — PineScript v5 syntax validation approach (need to define what "valid export" means before shipping)

### Phase 5: Research + Advanced Features + Polish

**Rationale:** Enhancement features that add value but aren't on the critical path. `/brrr:research` is useful but optional (Claude can use WebSearch inline). Bayesian optimization (optuna) can be added after grid search proves the loop. `/brrr:update` is infrastructure polish.
**Delivers:** `/brrr:research` (WebSearch for strategy implementations and pitfalls), Bayesian optimization via optuna (replaces grid search when plan selects it), walk-forward analysis option, Monte Carlo simulation in verify report, `/brrr:update` (version check + file migration), context file support (.pmf/context/ images/PDFs), hypothesis drift protection
**Addresses:** Walk-forward analysis (gold standard validation), Bayesian optimization (smarter parameter search), context file understanding (multimodal differentiator)
**Avoids:** Meta-overfitting through walk-forward (cap windows, document limitations)
**Needs research:** YES — walk-forward analysis implementation patterns (rolling window design, WFO meta-overfitting); optuna integration with custom backtest loop

### Phase Ordering Rationale

- **Foundation first:** All three HIGH-cost pitfalls (lookahead bias, wrong metrics, install failures) must be solved in Phase 1. No results are trustworthy until these are solid.
- **No execution without specification:** The discuss → plan → execute dependency chain is hard. Skipping straight to execute produces an execute workflow with no clear inputs.
- **AI loop before export:** There is nothing to export until execute produces approved results. The verify/export phase can only be validated against real iteration data.
- **Enhancements last:** Bayesian optimization, walk-forward, Monte Carlo are genuinely valuable but none of them are blocking. Grid search + in/out-of-sample split is sufficient for v1 to be useful.

### Research Flags

Phases needing deeper research during planning:
- **Phase 3 (Execute):** Data source API integration has known edge cases (ccxt rate limits per exchange, yfinance `auto_adjust` parameter changes, Dukascopy chunked downloads). Need concrete tested patterns before building the execute workflow's data loading section.
- **Phase 4 (Verify/Export):** PineScript v5 syntax validation — determine whether to paste-test manually, use TradingView's API, or rely on Claude's training knowledge plus a comprehensive test suite. This decision affects how confidently the export can be shipped.
- **Phase 5 (Advanced):** Walk-forward analysis implementation — the rolling window design has subtle choices (anchored vs rolling, how many windows, WFO meta-overfitting risk). QuantInsti and IBKR research exists but implementation patterns need validation.

Phases with standard patterns (skip research-phase):
- **Phase 1 (Foundation):** Python venv, npm distribution, Node.js file operations — all well-documented, no novel patterns
- **Phase 2 (Discuss/Plan):** Prompt engineering for structured output follows established GSD patterns; no external APIs involved
- **Phase 4 (HTML Reports):** plotly `to_html()` with `include_plotlyjs=True` is documented and straightforward

## Confidence Assessment

| Area | Confidence | Notes |
|------|------------|-------|
| Stack | HIGH | All libraries verified on PyPI with current versions as of 2026-03-21; kaleido Chrome dep confirmed from official plotly docs; polygon rebrand confirmed from GitHub |
| Features | HIGH | Backtesting metrics and table stakes verified against multiple independent trading education sources; competitive landscape researched directly |
| Architecture | HIGH | Direct inspection of GSD package architecture; Claude Code slash command system inspected directly; well-established npm/venv patterns |
| Pitfalls | HIGH | Backtesting pitfalls extensively documented in academic and practitioner sources; Claude Code CLI pitfalls verified against current docs; LLM code hallucination research cited |

**Overall confidence:** HIGH

### Gaps to Address

- **PineScript v5 syntax validation strategy:** Research didn't resolve whether Claude-generated PineScript can be validated programmatically before delivery, or whether it requires paste-testing in TradingView. This decision affects Phase 4 scope. Recommendation: start with Claude generating PineScript from a validated skeleton template and treat v1 as "best effort with known limitations." Add syntax errors encountered during testing to references/.

- **ccxt exchange compatibility matrix:** ccxt covers 100+ exchanges but historical data availability varies wildly. The execute workflow needs to handle "exchange X doesn't support timeframe Y" gracefully. Recommendation: ship with a tested default exchange (Binance for crypto) and add exchange-specific handling incrementally.

- **Claude Code skills vs commands directory evolution:** PITFALLS.md notes that Claude Code may migrate from `~/.claude/commands/` to `~/.claude/skills/`. The install and update commands must handle both paths. This is a moving target — monitor Claude Code release notes during development.

- **State corruption recovery:** If STATE.md gets corrupted mid-optimization, the current design has no hard recovery path beyond `/brrr:status` attempting a rebuild from phase artifacts. This edge case should be designed into the status workflow explicitly.

## Sources

### Primary (HIGH confidence)
- GSD (`~/.claude/get-shit-done/`) — direct inspection of command/workflow/template/reference pattern
- Claude Code slash command system — direct inspection of `~/.claude/commands/gsd/` for frontmatter and `@` reference patterns
- [pandas 3.0 release notes](https://pandas.pydata.org/docs/whatsnew/v3.0.0.html) — version requirements
- [Plotly static image generation changes](https://plotly.com/python/static-image-generation-changes/) — kaleido v1 Chrome requirement confirmed
- [polygon-api-client PyPI](https://pypi.org/project/polygon-api-client/) / [GitHub rebrand](https://github.com/polygon-io/client-python) — legacy package name decision
- [optuna GitHub](https://github.com/optuna/optuna) — v4.7.0, sampler options
- [Python venv docs](https://docs.python.org/3/library/venv.html) — stdlib venv patterns

### Secondary (MEDIUM confidence)
- [Interactive Brokers: Walk Forward Analysis](https://www.interactivebrokers.com/campus/ibkr-quant-news/the-future-of-backtesting-a-deep-dive-into-walk-forward-analysis/) — WFA as gold standard
- [LuxAlgo: Backtesting Traps](https://www.luxalgo.com/blog/backtesting-traps-common-errors-to-avoid/) — pitfall catalog
- [QuantInsti: Walk-Forward Optimization](https://blog.quantinsti.com/walk-forward-optimization-introduction/) — implementation methodology
- [Claude Code Docs: Slash Commands / Skills](https://code.claude.com/docs/en/slash-commands) — current skills system
- [npm Security Best Practices](https://github.com/lirantal/npm-security-best-practices) — postinstall risks
- [FX Replay: 5 KPIs That Matter Most](https://www.fxreplay.com/learn/the-5-kpis-that-matter-most-in-backtesting-a-strategy) — metrics baseline

### Tertiary (LOW confidence / needs validation during implementation)
- [arxiv 2311.15548: LLM Deficiency in Finance](https://arxiv.org/abs/2311.15548) — LLM hallucination in financial tasks (informs pitfall severity but not implementation)
- yfinance `auto_adjust` behavior — documented in multiple community sources but behavior has changed between versions; validate during Phase 3 implementation
- dukascopy-python reliability — limited documentation; validate during Phase 3 data integration

---
*Research completed: 2026-03-21*
*Ready for roadmap: yes*
