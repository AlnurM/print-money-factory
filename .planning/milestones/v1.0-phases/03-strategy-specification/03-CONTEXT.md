# Phase 3: Strategy Specification - Context

**Gathered:** 2026-03-21
**Status:** Ready for planning

<domain>
## Phase Boundary

Implement `/brrr:discuss`, `/brrr:research`, and `/brrr:plan` workflows. These three commands take a user from a vague trading idea to a complete, formal backtest specification. Discuss collects strategy decisions through conversation, research finds implementations and pitfalls, plan designs the parameter space and optimization method. All three produce phase artifacts in `.pmf/phases/`.

</domain>

<decisions>
## Implementation Decisions

### Discuss workflow (/brrr:discuss)
- **D-01:** Follow-the-thread conversation style — start open ("describe your strategy"), then follow what the user emphasizes. Fill gaps at the end, don't follow a fixed topic checklist.
- **D-02:** Must cover by end: entry/exit logic, stops/TP, position sizing, commission assumptions, parameter ranges (which are fixed, which to optimize). Ensure all are captured before outputting artifact.
- **D-03:** `--auto` flag: detect strategy type from STRATEGY.md, apply type-specific defaults (stops, sizing, commission, param ranges), then override with any specifics from STRATEGY.md context. Minimal questions.
- **D-04:** Debug discuss reads EVERYTHING: all prior phase artifacts (discuss, plan, execute results, verify report). Full context for AI diagnosis. Starts with diagnosis, not from scratch.
- **D-05:** Outputs `phase_N_discuss.md` with all decisions fixed and organized.
- **D-06:** Reads and re-reads STRATEGY.md before starting to anchor the conversation to the original hypothesis.

### Research workflow (/brrr:research)
- **D-07:** Sources: Claude's training data for common strategies + web search for recent/niche topics. Training data first, web search to supplement.
- **D-08:** `--deep` flag: both more sources (3-5 instead of 1-2, including academic papers and forums) AND deeper analysis per source (extract code patterns, compare approaches, rate reliability).
- **D-09:** Recommendation logic: Claude auto-detects from discuss output whether strategy is well-formalized or needs research. Non-standard/complex = recommended, classic/well-defined = optional.
- **D-10:** Must warn about known lookahead traps specific to the strategy type (from research or training data).
- **D-11:** Outputs `phase_N_research.md` with implementations found, pitfalls identified, formalization alternatives if applicable.

### Plan workflow (/brrr:plan)
- **D-12:** Optimization method auto-selected by parameter count: < 1000 combos = grid search, medium space = random search, 3+ free params = walk-forward. User can override.
- **D-13:** Parameter budget: warn + explain specific overfitting risk if too many free params vs data size, recommend reducing, but allow user override.
- **D-14:** Train/test split: plan sets rules (percentage like 70/30, method = chronological), execute calculates exact dates from actual data.
- **D-15:** Plan defines: all free parameters with ranges and step sizes, all fixed parameters with values, constraints between params (e.g., fast < slow), evaluation criteria (primary + secondary metrics), minimum trade count.
- **D-16:** Outputs `phase_N_plan.md` with complete optimization spec.

### Drift protection
- **D-17:** Drift = new indicators/signals not in original STRATEGY.md OR fundamentally changed entry/exit logic, but only if changes affect >50% of the strategy. Minor tweaks (filter adjustments, parameter range changes) are fine.
- **D-18:** When drift detected: HARD GATE — stop and force a choice: stay within current scope OR open new milestone. No soft suggestions, no "continue anyway".
- **D-19:** Drift detection happens during debug discuss by comparing proposed changes against original STRATEGY.md hypothesis.

### Claude's Discretion
- Exact question wording and conversation flow in discuss
- How to present research findings (structure, depth)
- Parameter range suggestions when user doesn't specify
- How to format the plan output
- Web search queries for research

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Project spec
- `PROJECT.md` — Original spec with detailed discuss, research, and plan phase descriptions
- `.planning/phases/02-milestone-lifecycle-state/02-CONTEXT.md` — Phase 2 decisions: state tracking (D-09..14), context files (D-15..18), artifact naming (D-11)

### Existing stubs (Phase 1 outputs to replace)
- `workflows/discuss.md` — 10-line stub to replace with full implementation
- `workflows/research.md` — 10-line stub to replace with full implementation
- `workflows/plan.md` — 10-line stub to replace with full implementation

### Reference patterns (Phase 1 outputs)
- `references/backtest_engine.py` — Anti-lookahead event loop pattern that plan must design parameters for
- `references/backtest-engine.md` — Pattern guide with rules the plan must respect
- `references/common-pitfalls.md` — Pitfalls catalog that research should cross-reference

### Commands
- `commands/discuss.md` — Thin command that @-references workflow
- `commands/research.md` — Thin command that @-references workflow
- `commands/plan.md` — Thin command that @-references workflow

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- `workflows/new-milestone.md` (351 lines): Established pattern for guided conversation workflows — context scan preamble, STATE.md read/update, structured output
- `templates/STRATEGY.md`: Strategy template with hypothesis, asset, scope, criteria — discuss reads and anchors to this
- `templates/STATE.md`: State template with phase tracking — all three commands update current step

### Established Patterns
- Workflows are behavioral markdown that Claude reads and follows
- Every command starts with: context file scan → STATE.md validation → sequence check
- Phase artifacts named `phase_N_step.md` in `.pmf/phases/`
- STATE.md updated after each command (current step, history)
- All output in English

### Integration Points
- `.pmf/STRATEGY.md` — discuss reads hypothesis, drift detection compares against it
- `.pmf/STATE.md` — all three commands read current step, update after completion
- `.pmf/phases/phase_N_discuss.md` → input for research and plan
- `.pmf/phases/phase_N_research.md` → input for plan
- `.pmf/phases/phase_N_plan.md` → input for execute (Phase 4)
- `~/.pmf/references/backtest_engine.py` — plan must design params that fit this engine pattern

</code_context>

<specifics>
## Specific Ideas

- Discuss should feel like a trading strategy brainstorming session, not a questionnaire
- Research should be like asking an experienced quant "what are the gotchas with this type of strategy?"
- Plan should feel like an engineer designing an experiment — methodical, with clear justification for each choice
- The debug discuss AI diagnosis should be specific and actionable: "your strategy broke in Q3 2023 because..." not "consider adjusting parameters"
- Drift detection hard gate should quote the original hypothesis from STRATEGY.md so the user sees the comparison

</specifics>

<deferred>
## Deferred Ideas

None — discussion stayed within phase scope

</deferred>

---

*Phase: 03-strategy-specification*
*Context gathered: 2026-03-21*
