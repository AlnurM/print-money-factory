# Phase 8: Debug Cycle Memory - Context

**Gathered:** 2026-03-22
**Status:** Ready for planning

<domain>
## Phase Boundary

Add structured failed-approach tracking so debug cycles carry forward knowledge of what was tried and why it failed. Verify `--debug` writes a diagnosis artifact. Discuss in debug mode reads it and presents failures before gathering new decisions. Memory is phase-scoped and size-capped.

</domain>

<decisions>
## Implementation Decisions

### Diagnosis artifact format
- **D-01:** `/brrr:verify --debug` writes a `phase_N_diagnosis.json` to the phase directory (`.pmf/phases/`) alongside existing iteration artifacts. This is a new artifact — currently verify --debug only opens a new phase cycle without structured output.
- **D-02:** JSON structure:
  ```json
  {
    "phase": 2,
    "timestamp": "ISO-8601",
    "strategy_type": "SMA crossover",
    "best_metrics": { "sharpe": 0.8, "max_dd": -0.15, ... },
    "targets": { "sharpe": 1.5, "max_dd": -0.10 },
    "failed_approaches": [
      {
        "iteration_range": "1-10",
        "params_tried": { "fast_period": [5,10,15], "slow_period": [20,30,50] },
        "best_result": { "sharpe": 0.8, "trades": 45 },
        "diagnosis": "Entries too frequent in sideways markets, stops too tight for volatility",
        "do_not_retry": ["fast_period < 10 with slow_period < 30", "stop_loss < 1.5%"]
      }
    ],
    "overall_diagnosis": "Strategy shows edge in trending markets but gives back gains in choppy periods. Need wider stops or regime filter.",
    "suggested_changes": ["Widen stop-loss to 2-3%", "Add ADX filter for trend strength", "Consider longer timeframes"]
  }
  ```
- **D-03:** Each `failed_approaches` entry includes `do_not_retry` — explicit parameter regions or approaches the AI must avoid in the next cycle.
- **D-04:** The AI formulates the diagnosis from the iteration artifacts (metrics JSONs, verdict JSONs, equity PNGs) — it's an AI-generated analysis, not a mechanical dump of data.

### How discuss reads it
- **D-05:** In debug-discuss mode, discuss reads ALL `phase_*_diagnosis.json` files (not just the latest) to build cumulative failure knowledge.
- **D-06:** Present failures as a summary table before the conversation begins:
  ```
  ## Prior Debug Cycles

  | Phase | Best Sharpe | Diagnosis | Do NOT Retry |
  |-------|-------------|-----------|--------------|
  | 1     | 0.4         | No edge found at any params | fast_period < 10 |
  | 2     | 0.8         | Edge in trends, gives back in chop | stop_loss < 1.5% |

  Suggested starting point for Phase 3: [AI synthesis of all prior failures]
  ```
- **D-07:** The AI uses the cumulative `do_not_retry` list to constrain its suggestions — it must NOT propose parameter ranges that overlap with any prior `do_not_retry` entry.

### Memory size/scope rules
- **D-08:** Memory is scoped per milestone — all `phase_*_diagnosis.json` files within the current `.pmf/phases/` directory are in scope. Starting a new milestone (via `/brrr:new-milestone`) resets the memory.
- **D-09:** Cap at 50 `failed_approaches` entries across all diagnosis files combined. If total entries exceed 50, the AI should summarize the oldest entries into a compact "early failures summary" line rather than dropping them (merge, don't evict).
- **D-10:** Each diagnosis file is append-only within its phase — a phase that runs multiple debug cycles appends to the same `phase_N_diagnosis.json` rather than overwriting.

### Claude's Discretion
- Exact wording of the "Prior Debug Cycles" presentation in discuss
- How to synthesize multiple diagnosis files into a starting hypothesis
- Whether to include equity curve shape observations in the diagnosis (nice-to-have)
- Format of the merged "early failures summary" when cap is hit

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Verify workflow (debug path)
- `workflows/verify.md` — Step 5b handles `--debug` flow. Currently opens new phase cycle and updates STATE.md but does NOT write a structured diagnosis artifact. This is the primary file to modify.

### Discuss workflow (debug-discuss mode)
- `workflows/discuss.md` — Step 2-debug at line 354. Currently reads all prior phase artifacts (discuss, research, plan, best_result) and presents AI diagnosis. Needs to also read `phase_*_diagnosis.json` files and present the failure summary table.

### Research findings
- `.planning/research/FEATURES.md` — Debug cycle memory section with gap analysis
- `.planning/research/ARCHITECTURE.md` — DEBUG_MEMORY.md vs JSON approach analysis
- `.planning/research/PITFALLS.md` — Pitfall on context explosion and size-capping

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- Verify workflow already reads all iteration artifacts (metrics JSON, verdict JSON, equity PNG) — diagnosis generation can reuse this data
- Discuss workflow already has debug-discuss mode with prior artifact scanning — just needs to add diagnosis JSON to the scan

### Established Patterns
- Phase artifacts follow `phase_N_*.json` naming convention in `.pmf/phases/`
- Verdict JSON (`iter_NN_verdict.json`) is the existing per-iteration completion marker — diagnosis JSON follows the same pattern at phase level
- AI analysis in verify.md already produces specific metric-vs-target assessment — diagnosis extends this

### Integration Points
- `workflows/verify.md` Step 5b: add diagnosis JSON write after opening new phase cycle
- `workflows/discuss.md` Step 1 (Load Strategy Context): add diagnosis JSON glob and read
- `workflows/discuss.md` Step 2-debug: add failure summary table presentation before conversation

</code_context>

<specifics>
## Specific Ideas

No specific requirements — research covered this well.

</specifics>

<deferred>
## Deferred Ideas

None — discussion stayed within phase scope

</deferred>

---

*Phase: 08-debug-cycle-memory*
*Context gathered: 2026-03-22*
