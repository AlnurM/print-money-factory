---
phase: 08-debug-cycle-memory
plan: 02
subsystem: workflows
tags: [debug-memory, diagnosis-json, do-not-retry, discuss-workflow]

# Dependency graph
requires:
  - phase: 08-debug-cycle-memory plan 01
    provides: diagnosis JSON write in verify --debug flow
provides:
  - debug memory consumption in discuss workflow
  - Prior Debug Cycles failure table in debug-discuss mode
  - do_not_retry constraint enforcement on AI suggestions
  - 50-entry cap with merge-not-evict semantics
affects: [discuss, debug-cycles, verify]

# Tech tracking
tech-stack:
  added: []
  patterns: [diagnosis-json-consumption, do-not-retry-constraints, merge-not-evict-cap]

key-files:
  created: []
  modified: [workflows/discuss.md]

key-decisions:
  - "Diagnosis file references use phase_*_diagnosis.json glob pattern for milestone-scoped reads"
  - "50-entry cap merges oldest entries down to 45, leaving room for growth"

patterns-established:
  - "Debug memory consumption: read all diagnosis JSONs in Step 1, present in Step 2-debug"
  - "Constraint enforcement: AI must not propose parameters overlapping do_not_retry entries"

requirements-completed: [DBUG-02, DBUG-03]

# Metrics
duration: 2min
completed: 2026-03-22
---

# Phase 08 Plan 02: Debug Memory in Discuss Summary

**Discuss workflow reads all diagnosis JSONs, presents Prior Debug Cycles failure table, and enforces do_not_retry constraints on AI suggestions**

## Performance

- **Duration:** 2 min
- **Started:** 2026-03-22T18:49:44Z
- **Completed:** 2026-03-22T18:51:41Z
- **Tasks:** 1
- **Files modified:** 1

## Accomplishments
- Step 1 reads all `phase_*_diagnosis.json` files and collects failed approaches, do_not_retry entries, and latest diagnosis
- Step 1 enforces 50-entry cap with merge-not-evict semantics (DBUG-03)
- Step 2-debug presents Prior Debug Cycles table with phase, iterations, best sharpe, diagnosis, and do-not-retry columns
- CRITICAL CONSTRAINT block prevents AI from proposing parameters in do_not_retry regions (DBUG-02)
- User override warning when proposing retrying a previously failed approach

## Task Commits

Each task was committed atomically:

1. **Task 1: Add diagnosis JSON reading to discuss.md Step 1 and failure table to Step 2-debug** - `aadaf52` (feat)

## Files Created/Modified
- `workflows/discuss.md` - Added diagnosis JSON reading in Step 1, Prior Debug Cycles table and constraint enforcement in Step 2-debug

## Decisions Made
- Used `phase_*_diagnosis.json` glob pattern consistently for milestone-scoped memory reads
- 50-entry cap merges oldest entries to 45 (not 50) to leave room for growth before next merge

## Deviations from Plan

None - plan executed exactly as written.

## Issues Encountered
None

## User Setup Required
None - no external service configuration required.

## Next Phase Readiness
- Debug cycle memory is now fully wired: verify --debug writes diagnosis JSON (plan 01), discuss reads and presents it (plan 02)
- Ready for next phase work

---
*Phase: 08-debug-cycle-memory*
*Completed: 2026-03-22*
