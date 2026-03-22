# Phase 5: Verify & Export - Context

**Gathered:** 2026-03-21
**Status:** Ready for planning

<domain>
## Phase Boundary

Implement `/brrr:verify` workflow — generates interactive HTML report, AI analyzes results, presents --approved/--debug choice. On --approved: close milestone, generate complete export package (PineScript, trading rules, performance report, backtest script, live checklist, HTML report) in output/. On --debug: AI diagnoses failure, opens new phase cycle. This is the final phase of the product pipeline.

</domain>

<decisions>
## Implementation Decisions

### HTML report
- **D-01:** Decision-first layout: metrics summary at top (is it good?), then equity curve (how it grew), then details (drawdown, iterations, heatmap, trades, regime, benchmark)
- **D-02:** Fill the existing `templates/report-template.html` template — inject plotly charts and data into placeholders. Template as structure, not generate from scratch.
- **D-03:** Regime classification is trend-based: SMA slope + ADX. Strong trend up = bull, strong down = bear, weak = sideways.
- **D-04:** Standalone HTML file with embedded plotly.js — no server needed, opens in any browser.
- **D-05:** Report includes all 7 sections: metrics summary, equity curve (vs buy & hold), drawdown chart, iteration table, parameter heatmap (if grid search), trade list with P&L coloring, regime breakdown, benchmark correlation (alpha/beta).

### Approval flow
- **D-06:** Always auto-analyze before presenting choice — Claude reads report data, formulates conclusion with specific metrics vs targets, then presents assessment before asking approved/debug.
- **D-07:** --debug triggers full diagnosis: equity curve shape, regime performance, losing trade clusters, parameter sensitivity. Specific hypothesis for the next phase cycle. Not just "metrics are bad."
- **D-08:** Allow force-approve — warn if targets not met, but allow --approved anyway. User decides what's "good enough."
- **D-09:** --debug opens new phase cycle: STATE.md updated, next /brrr:discuss starts from AI diagnosis.

### Export package (on --approved)
- **D-10:** trading-rules.md in practitioner tone: "Enter long when price sweeps below OB and closes back above. Stop: 1xATR below entry. Target: 2.5RR." Written for someone who trades.
- **D-11:** live-checklist.md with generic items (broker setup, position sizing calc) + strategy-specific items (which timeframe to watch, when signals appear).
- **D-12:** backtest_final.py is fully reproducible: data download, full backtest, metrics, equity plot. One file, zero deps beyond venv. Run once, get results.
- **D-13:** performance-report.md as portable markdown summary for sharing.
- **D-14:** All exports in `output/` directory.
- **D-15:** STATE.md updated to CLOSED with final metrics on --approved.

### PineScript generation
- **D-16:** Use template + examples + add a PineScript syntax rules reference for Claude to read before generating. Maximum reliability.
- **D-17:** Generate BOTH: strategy version (strategy() with entry/exit/stop/TP for TradingView backtesting) AND indicator version (indicator() with plotshape + alertcondition for live alerts).
- **D-18:** PineScript v5, with comment noting v6 migration path.
- **D-19:** Two files in output/: `pinescript_v5_strategy.pine` and `pinescript_v5_indicator.pine`.

### Claude's Discretion
- Exact plotly chart styling and colors
- How to format the metrics summary table
- Parameter heatmap color scheme
- Trade list sorting (chronological vs by P&L)
- Exact PineScript syntax rules doc content
- How to detect regime boundaries in the data

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Project spec
- `PROJECT.md` — Original spec with detailed verify phase: report sections, --approved/--debug flow, export file list, STATE.md update format

### Templates (Phase 1)
- `templates/report-template.html` — 211-line HTML template with plotly placeholders to fill
- `templates/pinescript-template.pine` — 40-line PineScript v5 structural template
- `references/pinescript-examples/trend-following.pine` — Complete trend strategy example
- `references/pinescript-examples/mean-reversion.pine` — Complete mean-reversion example
- `references/pinescript-examples/breakout.pine` — Complete breakout example

### Prior phase outputs
- `workflows/execute.md` — Execute workflow produces per-iteration artifacts and best_result.json that verify reads
- `.planning/phases/04-ai-backtest-loop/04-CONTEXT.md` — Phase 4 decisions: iteration artifacts (D-12), stop conditions (D-06..09)

### Existing stub
- `workflows/verify.md` — 10-line stub to replace with full implementation
- `commands/verify.md` — Command file that @-references workflow

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- `templates/report-template.html` (211 lines): HTML skeleton with plotly CDN, placeholder sections for charts
- `templates/pinescript-template.pine` (40 lines): `//@version=5`, strategy() declaration, input params structure
- 3 PineScript examples (trend, mean-rev, breakout): Complete working strategies for reference
- `references/metrics.py`: compute_all_metrics() output is what gets injected into the report

### Established Patterns
- Workflows are behavioral markdown (discuss=512, execute=1067, plan=532)
- Preamble: sequence validation → context scan → STATE.md read
- Phase artifacts in `.pmf/phases/phase_N_step/`
- Execute produces: `iter_NN_params.json`, `iter_NN_metrics.json`, `iter_NN_equity.png`, `iter_NN_verdict.json`, `phase_N_best_result.json`

### Integration Points
- `.pmf/phases/phase_N_execute/` → verify reads all iteration artifacts
- `.pmf/phases/phase_N_best_result.json` → best params and metrics for report
- `output/` → export directory created on --approved
- `.pmf/STATE.md` → mark CLOSED on --approved, update history on --debug
- `.pmf/STRATEGY.md` → read for trading rules and PineScript generation context

</code_context>

<specifics>
## Specific Ideas

- The HTML report should feel like a professional quant research report — clean, data-dense, with interactive plotly charts
- PineScript output should be paste-ready into TradingView — no manual editing needed
- Trading rules should be specific enough that another trader could follow them mechanically
- The AI analysis before approved/debug should feel like a senior quant reviewing your backtest: "Sharpe is above target, but notice the equity curve flattened in Q3 2023 — the strategy may struggle in sideways markets. Your regime breakdown confirms: 80% of profits came from the bull phase."
- Live checklist should prevent common mistakes: "Set TradingView alerts on 4H timeframe. Check spread before market open. Don't trade during news events if your strategy doesn't handle gaps."

</specifics>

<deferred>
## Deferred Ideas

None — discussion stayed within phase scope

</deferred>

---

*Phase: 05-verify-export*
*Context gathered: 2026-03-21*
