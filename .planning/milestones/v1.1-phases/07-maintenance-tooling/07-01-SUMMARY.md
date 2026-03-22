---
phase: 07-maintenance-tooling
plan: 01
subsystem: maintenance
tags: [doctor, diagnostics, health-check, venv, python]

# Dependency graph
requires:
  - phase: 01-install-architecture
    provides: install script, venv setup, command/workflow file structure
provides:
  - "/brrr:doctor diagnostic command with 6-category health check"
  - "Behavioral workflow for installation diagnostics"
affects: [07-02-version-check]

# Tech tracking
tech-stack:
  added: []
  patterns: [diagnostic-workflow, pass-fail-checklist]

key-files:
  created:
    - commands/doctor.md
    - workflows/doctor.md
  modified: []

key-decisions:
  - "Used single Python script for all import checks rather than individual commands for efficiency"
  - "Command files counted as 1 check (all-or-nothing per missing file) for cleaner summary math"

patterns-established:
  - "Diagnostic workflow pattern: section-per-check, [PASS]/[FAIL] prefix, fix suggestion on failure, X/Y summary with verdict"

requirements-completed: [MANT-01]

# Metrics
duration: 1min
completed: 2026-03-22
---

# Phase 7 Plan 1: Doctor Diagnostic Command Summary

**`/brrr:doctor` slash command with 6-category health check: Python version, venv, 10 library imports via actual `python -c import`, command/workflow/reference file integrity, and HEALTHY/NEEDS ATTENTION verdict**

## Performance

- **Duration:** 1 min
- **Started:** 2026-03-22T18:23:52Z
- **Completed:** 2026-03-22T18:24:59Z
- **Tasks:** 2
- **Files modified:** 2

## Accomplishments
- Created thin `/brrr:doctor` command following established pattern from commands/status.md
- Created comprehensive diagnostic workflow with 6 check categories and [PASS]/[FAIL] output format
- Import checks use actual `python -c "import X"` inside venv, not directory existence

## Task Commits

Each task was committed atomically:

1. **Task 1: Create /brrr:doctor thin command** - `442fe14` (feat)
2. **Task 2: Create doctor diagnostic workflow** - `dc46e89` (feat)

## Files Created/Modified
- `commands/doctor.md` - Thin slash command for /brrr:doctor with frontmatter and workflow reference
- `workflows/doctor.md` - Full diagnostic workflow with 6 check sections, import verification, and summary verdict

## Decisions Made
- Used a single Python script that loops over all 10 libraries with try/except for import checks, rather than running 10 separate shell commands -- more efficient and cleaner output
- Command file checks report individual [FAIL] per missing file but a single [PASS] when all present, keeping the summary count practical

## Deviations from Plan

None - plan executed exactly as written.

## Issues Encountered
None

## User Setup Required
None - no external service configuration required.

## Next Phase Readiness
- Doctor command ready for installation into ~/.claude/commands/brrr/ and ~/.pmf/workflows/
- bin/install.mjs will need to include doctor.md in both command and workflow copy lists (handled by install script's glob pattern)
- Ready for 07-02 (version check preamble) which is independent

---
*Phase: 07-maintenance-tooling*
*Completed: 2026-03-22*
