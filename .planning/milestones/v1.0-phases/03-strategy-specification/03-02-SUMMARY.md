---
phase: 03-strategy-specification
plan: 02
subsystem: workflows
tags: [research, pitfalls, webfetch, backtesting, strategy-analysis]

# Dependency graph
requires:
  - phase: 01-package-foundation
    provides: "Stub workflows, references/common-pitfalls.md, references/backtest-engine.md"
  - phase: 02-milestone-lifecycle-state
    provides: "new-milestone.md canonical workflow pattern, STATE.md tracking"
provides:
  - "Complete behavioral workflow for /brrr:research command"
  - "Pitfall cross-reference pattern for strategy-specific risk assessment"
  - "Web search integration via WebFetch for extended research"
affects: [03-plan-workflow, 04-execute-phase, strategy-research]

# Tech tracking
tech-stack:
  added: [WebFetch]
  patterns: [pitfall-cross-reference, research-recommendation-auto-detect, deep-mode-extended-search]

key-files:
  created: []
  modified:
    - workflows/research.md

key-decisions:
  - "Followed new-milestone.md structural pattern for consistency across all workflows"
  - "Research always proceeds after recommendation (informational only since user already invoked command)"
  - "Standard mode skips web search if training data is sufficient; deep mode always searches 3-5 sources"

patterns-established:
  - "Pitfall cross-reference: each of 6 pitfalls rated HIGH/MEDIUM/LOW RISK with strategy-specific explanation"
  - "Research recommendation: auto-detect based on strategy complexity criteria"

requirements-completed: [RSCH-01, RSCH-02, RSCH-03, RSCH-04, RSCH-05]

# Metrics
duration: 2min
completed: 2026-03-21
---

# Phase 03 Plan 02: Research Workflow Summary

**Complete behavioral research workflow with training-data-first approach, pitfall cross-referencing, --deep mode web search via WebFetch, and auto-recommendation logic**

## Performance

- **Duration:** 2 min
- **Started:** 2026-03-21T14:46:40Z
- **Completed:** 2026-03-21T14:49:00Z
- **Tasks:** 1
- **Files modified:** 1

## Accomplishments
- Replaced 11-line stub with 411-line complete behavioral workflow
- 9-step workflow: validation, context scan, load context, recommendation, training data research, pitfall cross-reference, web search, compile findings, write artifact, update STATE, confirmation
- Cross-references all 6 pitfalls from common-pitfalls.md with strategy-specific risk ratings (HIGH/MEDIUM/LOW)
- --deep mode searches 3-5 sources with per-source reliability rating
- Auto-recommends whether research is needed based on strategy complexity

## Task Commits

Each task was committed atomically:

1. **Task 1: Replace research workflow stub with full behavioral workflow** - `d2501e8` (feat)

## Files Created/Modified
- `workflows/research.md` - Complete behavioral workflow for /brrr:research command (411 lines)

## Decisions Made
- Followed new-milestone.md structural pattern (preamble sections, numbered steps, footer) for consistency
- Research recommendation is informational only -- always proceeds since user already invoked the command
- Standard mode skips web search entirely if Claude's training data is sufficient; deep mode always searches 3-5 sources
- Pitfall assessment uses three-tier rating (HIGH/MEDIUM/LOW RISK) with strategy-specific explanations

## Deviations from Plan

None - plan executed exactly as written.

## Issues Encountered
None

## User Setup Required
None - no external service configuration required.

## Next Phase Readiness
- Research workflow ready for use via /brrr:research
- Plan workflow (03-03) can now reference research output artifact pattern (phase_N_research.md)
- Pitfall cross-reference pattern established for reuse in plan and execute phases

## Self-Check: PASSED

All files exist. All commits verified.

---
*Phase: 03-strategy-specification*
*Completed: 2026-03-21*
