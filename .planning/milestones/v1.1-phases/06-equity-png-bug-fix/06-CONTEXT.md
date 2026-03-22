# Phase 6: Equity PNG Bug Fix - Context

**Gathered:** 2026-03-22
**Status:** Ready for planning

<domain>
## Phase Boundary

Fix blank equity curve PNGs generated during `/brrr:execute` iterations. The matplotlib PNG file is created but shows no data — a single-point array renders as an empty chart.

</domain>

<decisions>
## Implementation Decisions

### Fix approach
- **D-01:** Modify `run_backtest()` in `backtest_engine.py` to include `trades` and `equity_curve` in its return dict alongside the 9 metrics from `compute_all_metrics()`. This is the minimal fix — 3 lines changed in one file.
- **D-02:** Update the execute.md workflow template to use the returned `equity_curve` array directly instead of reconstructing from trades. Remove the reconstruction fallback code (lines 531-542 in execute.md).

### Zero-trade handling
- **D-03:** When an iteration produces zero trades, skip PNG generation and log a warning: "No trades generated — equity PNG skipped". Do not render a blank or flat-line image.
- **D-04:** The execute.md template should check `len(trades) > 0` before attempting matplotlib rendering.

### Claude's Discretion
- Whether to also return `dates` array for x-axis labeling (nice-to-have, not required)
- Exact warning message format for zero-trade case
- Whether to add a guard in `compute_all_metrics()` or only in `run_backtest()` return

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Backtest engine
- `references/backtest_engine.py` — `run_backtest()` at line 48, returns `compute_all_metrics()` at line 186. The equity array is computed at line 188 but discarded.

### Metrics module
- `references/metrics.py` — `compute_all_metrics()` at line 203, return dict at line 276. Returns 9 metrics, does NOT include `trades` or `equity_curve`.

### Execute workflow
- `workflows/execute.md` — PNG generation template at lines 524-554. Tries to reconstruct equity from trades but falls back to `[initial_capital]` since trades aren't in the return dict.

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- `backtest_engine.py` already computes `equity` array (list → np.array at line 188) and `trades` list — they just need to be included in the return value
- matplotlib Agg backend pattern already established in execute.md template

### Established Patterns
- `run_backtest()` returns a dict — adding keys to an existing dict is non-breaking
- Execute workflow template uses f-string interpolation for the Python script
- `plt.close(fig)` + `plt.close('all')` pattern for memory leak prevention

### Integration Points
- `run_backtest()` return dict is consumed by the execute.md workflow template
- Equity PNG is saved to `{output_dir}/iter_{N:02d}_equity.png`
- AI analysis step reads the PNG via multimodal vision (line 610)
- Report generator in Phase 5 reconstructs equity from the best iteration — this fix also benefits that path

</code_context>

<specifics>
## Specific Ideas

No specific requirements — the fix is well-defined from root cause analysis.

</specifics>

<deferred>
## Deferred Ideas

None — discussion stayed within phase scope

</deferred>

---

*Phase: 06-equity-png-bug-fix*
*Context gathered: 2026-03-22*
