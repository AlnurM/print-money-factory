# Phase 4: AI Backtest Loop - Context

**Gathered:** 2026-03-21
**Status:** Ready for planning

<domain>
## Phase Boundary

Implement `/brrr:execute` workflow — the core AI-driven backtest optimization loop. Claude loads market data, writes a custom Python backtest engine per strategy, runs iterative optimization with AI analysis between iterations, and stops when targets are hit or the strategy is diagnosed as unviable. Per-iteration artifacts (params, metrics, equity PNG, verdict) persist. This is the most complex phase and the product's core differentiator.

</domain>

<decisions>
## Implementation Decisions

### AI iteration loop
- **D-01:** Holistic analysis per iteration — Claude reads ALL artifacts (metrics JSON + equity PNG + trade list + prior iterations' verdicts). Forms a hypothesis about what's not working. Not just metric-driven rules.
- **D-02:** Adaptive change rate — start with 1-2 parameter changes per iteration, increase to 3-4 if plateau detected. Accelerate when stuck.
- **D-03:** Always explain reasoning — each iteration: "I'm changing X because Y, expecting Z". User learns and can redirect. No silent parameter tweaks.
- **D-04:** Claude writes Python backtest from scratch each time, adapting the reference skeleton (`~/.pmf/references/backtest_engine.py`) to the specific strategy. Uses fixed data adapters (`data_sources.py`) and fixed metrics module (`metrics.py`).
- **D-05:** Walk-forward, grid search, or random search per plan phase decision. Execute follows the method selected in plan.

### Stop conditions
- **D-06:** MINT — targets hit. Stop, save best result, suggest: "targets hit — run more iterations to improve?" User decides whether to continue.
- **D-07:** PLATEAU — configurable in plan phase (default: 3 iterations without >5% improvement). Plan defines threshold, execute enforces.
- **D-08:** REKT — no edge at any params. Diagnose cause: distinguish "strategy logic has no edge" vs "asset/timeframe wrong for this strategy". Different fix paths for each.
- **D-09:** NO DATA — insufficient data, API error, delisting. Report clearly with what went wrong.

### Terminal display
- **D-10:** Match spec format exactly: header with milestone/pair/method, then per-iteration block with params, metrics, AI commentary, "brrr..."
- **D-11:** Equity PNG saved to `.pmf/phases/phase_N_execute/iter_NN_equity.png` and mentioned in output: "equity curve saved to iter_03_equity.png". Not displayed inline.
- **D-12:** Per-iteration artifacts: `iter_NN_params.json`, `iter_NN_metrics.json`, `iter_NN_equity.png`, `iter_NN_verdict.json` — all in phase_N_execute/ directory.
- **D-13:** `--iterations N` (default 10), `--fast` (skip PNG generation), `--resume` (continue from last saved iteration).

### Data handling
- **D-14:** Data source from STRATEGY.md — user specified exchange/source in new-milestone. Execute reads it and calls the appropriate adapter. No re-asking.
- **D-15:** Data cache in `.pmf/cache/` — project-local, persists across iterations. Clear manually or on new milestone.
- **D-16:** Data validation: auto-fix small gaps (<5 bars via forward-fill), drop NaN rows, warn user what was fixed. Refuse if >10% of data affected.
- **D-17:** ccxt for crypto (use exchange from STRATEGY.md), yfinance for stocks/forex daily, CSV fallback for any asset.

### Overfitting detection
- **D-18:** Compare in-sample vs out-of-sample metrics each iteration. Warn when they diverge significantly (e.g., IS Sharpe > 2x OOS Sharpe).
- **D-19:** Warn when metrics look "too good" (Sharpe > 3.0, Profit Factor > 5.0, Win Rate > 80%).

### Claude's Discretion
- Exact Python code structure per strategy (within backtest_engine.py constraints)
- How to interpret equity curve visual patterns
- When to try radically different parameters vs incremental adjustments
- Error handling for Python execution failures
- How to format iteration verdict JSON

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Project spec
- `PROJECT.md` — Original spec with detailed execute phase flow, iteration format, stop conditions, terminal display

### Reference code (Phase 1 — the foundation execute depends on)
- `references/backtest_engine.py` — Anti-lookahead event loop skeleton that Claude adapts per strategy
- `references/backtest-engine.md` — Pattern guide with rules (next-bar execution, no lookahead)
- `references/data_sources.py` — Ready-to-use data adapters: `load_ccxt()`, `load_yfinance()`, `load_csv()`, `validate_ohlcv()`
- `references/metrics.py` — Fixed metrics module: Sharpe, Sortino, Calmar, Max DD, Win Rate, PF, expectancy, trade count, net P&L
- `references/common-pitfalls.md` — 6 backtesting pitfalls to guard against

### Prior phase outputs
- `workflows/plan.md` — Plan workflow defines parameter space, optimization method, train/test split that execute must follow
- `workflows/discuss.md` — Discuss output defines strategy logic that execute must implement
- `.planning/phases/03-strategy-specification/03-CONTEXT.md` — Phase 3 decisions: plan sets split rules (D-14), optimization method auto-select (D-12)

### Existing stub
- `workflows/execute.md` — 10-line stub to replace with full implementation
- `commands/execute.md` — Command file that @-references workflow

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- `references/backtest_engine.py` (240 lines): Complete event-loop skeleton with anti-lookahead. Claude adapts `calculate_signal()` per strategy.
- `references/data_sources.py` (333 lines): Tested adapters for ccxt, yfinance, CSV with `validate_ohlcv()` helper.
- `references/metrics.py` (286 lines): Fixed module with `compute_all_metrics()` accepting trade log or returns series.
- `references/conftest.py` + `references/test_metrics.py`: Test fixtures and 32 known-answer tests.

### Established Patterns
- Workflows are behavioral markdown (512 lines for discuss, 532 for plan)
- Preamble: sequence validation → context scan → STATE.md read
- Python execution via `~/.pmf/venv/bin/python`
- Artifacts in `.pmf/phases/phase_N_step/`

### Integration Points
- `.pmf/phases/phase_N_plan.md` → execute reads parameter space, optimization method, split rules
- `.pmf/phases/phase_N_discuss.md` → execute reads strategy logic decisions
- `.pmf/phases/phase_N_execute/` → directory for iteration artifacts
- `.pmf/STATE.md` → update current step, record best metrics in history
- `.pmf/phases/phase_N_best_result.json` → final output with best params and metrics

</code_context>

<specifics>
## Specific Ideas

- The execute workflow should feel like watching an AI trader optimize in real-time — each iteration tells a story
- The "brrr..." in the terminal display is part of the brand — keep it
- AI reasoning should be specific and trading-domain: "Sharpe improved but DD worsened — the wider stop is letting winners run but also increasing drawdowns. Trying a tighter stop with higher TP ratio." Not generic "adjusting parameters."
- REKT diagnosis should be genuinely useful: "Your SMC strategy assumes trending markets but BTC has been ranging since Q3 2023. Consider: (1) add regime filter, (2) switch to 1H timeframe, (3) test on a trending asset like SOL."
- The holistic analysis should look at the equity curve image (via multimodal) to detect visual patterns like regime shifts, clustered losses, etc.

</specifics>

<deferred>
## Deferred Ideas

None — discussion stayed within phase scope

</deferred>

---

*Phase: 04-ai-backtest-loop*
*Context gathered: 2026-03-21*
