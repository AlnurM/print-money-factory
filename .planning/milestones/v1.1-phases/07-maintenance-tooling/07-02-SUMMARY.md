---
phase: 07-maintenance-tooling
plan: 02
subsystem: workflows
tags: [version-check, npm, update-notice, workflows]

# Dependency graph
requires:
  - phase: 07-maintenance-tooling
    provides: existing workflow files with preamble pattern
provides:
  - version check preamble in all 7 /brrr:* workflows
  - silent 24h-gated update notice mechanism
affects: [workflows, user-experience]

# Tech tracking
tech-stack:
  added: []
  patterns: [version-check-preamble, 24h-gate-via-mtime, silent-fail-network-check]

key-files:
  created: []
  modified:
    - workflows/discuss.md
    - workflows/execute.md
    - workflows/new-milestone.md
    - workflows/plan.md
    - workflows/research.md
    - workflows/status.md
    - workflows/verify.md

key-decisions:
  - "Version check preamble inserted as first section after header in all workflows"
  - "Uses find -mtime -1 for 24h gate instead of date arithmetic"
  - "npm view @print-money-factory/cli version for latest version check"

patterns-established:
  - "Version check preamble: standard block inserted before all other preambles/sections in workflows"
  - "24h gate pattern: touch timestamp file, check mtime with find -mtime -1"

requirements-completed: [MANT-02]

# Metrics
duration: 2min
completed: 2026-03-22
---

# Phase 07 Plan 02: Version Check Preamble Summary

**Silent 24h-gated version check preamble added to all 7 /brrr:* workflows using find-mtime gate and npm view**

## Performance

- **Duration:** 2 min
- **Started:** 2026-03-22T18:24:00Z
- **Completed:** 2026-03-22T18:25:32Z
- **Tasks:** 1
- **Files modified:** 7

## Accomplishments
- Added version check preamble as the first section in all 7 workflow files (discuss, execute, new-milestone, plan, research, status, verify)
- Version check runs at most once per 24 hours gated by ~/.pmf/.last_version_check mtime
- Network failures silently swallowed with 2>/dev/null on all Bash commands
- Update notice displayed only when versions differ: "Update available: v{current} -> v{latest}. Run /brrr:update"

## Task Commits

Each task was committed atomically:

1. **Task 1: Add version check preamble to all 7 workflows** - `8a9b3b2` (feat)

## Files Created/Modified
- `workflows/discuss.md` - Version check preamble inserted before CRITICAL: Interaction Rules
- `workflows/execute.md` - Version check preamble inserted before Sequence Validation preamble
- `workflows/new-milestone.md` - Version check preamble inserted before CRITICAL: Interaction Rules
- `workflows/plan.md` - Version check preamble inserted before Sequence Validation preamble
- `workflows/research.md` - Version check preamble inserted before Sequence Validation preamble
- `workflows/status.md` - Version check preamble inserted before Section 1
- `workflows/verify.md` - Version check preamble inserted before Sequence Validation preamble

## Decisions Made
- Version check preamble is identical across all 7 workflows for consistency and maintainability
- Uses find -mtime -1 for the 24-hour gate (simpler than date arithmetic, works cross-platform)
- npm view @print-money-factory/cli version used per D-07 decision from CONTEXT.md

## Deviations from Plan

None - plan executed exactly as written.

## Issues Encountered
None

## User Setup Required
None - no external service configuration required.

## Known Stubs
None - all functionality is fully specified in the preamble instructions.

## Next Phase Readiness
- All workflows now have version check capability
- The ~/.pmf/.version file is written by bin/install.mjs (already exists)
- The ~/.pmf/.last_version_check file is created on first version check run

## Self-Check: PASSED

- All 7 workflow files exist and contain Version Check preamble
- SUMMARY.md exists at expected path
- Commit 8a9b3b2 verified in git log

---
*Phase: 07-maintenance-tooling*
*Completed: 2026-03-22*
