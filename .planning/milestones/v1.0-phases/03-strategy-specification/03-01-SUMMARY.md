---
phase: 03-strategy-specification
plan: 01
subsystem: workflow
tags: [discuss, strategy, conversation, drift-detection, auto-mode]

# Dependency graph
requires:
  - phase: 02-milestone-lifecycle-state
    provides: new-milestone.md workflow pattern, STATE.md template, STRATEGY.md template
provides:
  - Complete behavioral workflow for /brrr:discuss command
  - Three discussion modes (first-discuss, auto, debug-discuss)
  - Drift detection hard gate for debug cycles
  - phase_N_discuss.md output artifact format
affects: [03-strategy-specification, 04-execute-engine]

# Tech tracking
tech-stack:
  added: []
  patterns: [follow-the-thread conversation, type-specific defaults, drift detection hard gate]

key-files:
  created: []
  modified:
    - workflows/discuss.md

key-decisions:
  - "Followed new-milestone.md structural pattern exactly: preamble sections, numbered steps, behavioral instructions, footer"
  - "Three-mode detection (first-discuss, auto, debug-discuss) based on --auto flag and phase number"
  - "Drift detection compares >50% strategy change threshold before hard-gating"

patterns-established:
  - "Mode detection preamble: check flags and state to determine workflow variant"
  - "7-topic tracker for ensuring complete decision coverage"
  - "Type-specific defaults table for auto mode (trend-following, mean-reversion, breakout, custom)"

requirements-completed: [DISC-01, DISC-02, DISC-03, DISC-04, DISC-05, DISC-06]

# Metrics
duration: 3min
completed: 2026-03-21
---

# Phase 03 Plan 01: Discuss Workflow Summary

**Complete 512-line behavioral workflow for /brrr:discuss with three modes, drift detection hard gate, and 7-topic decision tracker**

## Performance

- **Duration:** 3 min
- **Started:** 2026-03-21T14:46:39Z
- **Completed:** 2026-03-21T14:49:00Z
- **Tasks:** 1
- **Files modified:** 1

## Accomplishments
- Replaced 11-line discuss workflow stub with 512-line complete behavioral workflow
- Implemented three discussion modes: first-discuss (guided follow-the-thread conversation), auto (type-specific defaults with one confirmation), debug-discuss (AI diagnosis of prior phase failures)
- Built drift detection hard gate that quotes original hypothesis and forces binary choice (stay in scope or new milestone)
- Added sequence validation preamble, context file scan preamble, and mode detection preamble matching new-milestone.md pattern

## Task Commits

Each task was committed atomically:

1. **Task 1: Replace discuss workflow stub with full behavioral workflow** - `8fdffc7` (feat)

## Files Created/Modified
- `workflows/discuss.md` - Complete behavioral workflow for /brrr:discuss command (512 lines, was 11)

## Decisions Made
- Followed new-milestone.md structural pattern exactly: preamble sections, numbered steps, behavioral instructions, footer with requirement coverage
- Used follow-the-thread conversation pattern per D-01 instead of fixed topic checklist
- Applied >50% threshold for drift detection per D-17 -- minor tweaks do not trigger the gate
- Commission defaults by asset class: 0.1% crypto, 0.01% stocks, 0.005% forex per D-02/common-pitfalls.md

## Deviations from Plan

None - plan executed exactly as written.

## Issues Encountered
None

## User Setup Required
None - no external service configuration required.

## Next Phase Readiness
- discuss.md workflow is complete and ready for use via /brrr:discuss
- Provides the foundation artifact (phase_N_discuss.md) that research and plan workflows will consume
- Research workflow (03-02) and plan workflow (03-03) can now be implemented

---
*Phase: 03-strategy-specification*
*Completed: 2026-03-21*
