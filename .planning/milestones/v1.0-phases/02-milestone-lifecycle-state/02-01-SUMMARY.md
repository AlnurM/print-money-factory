---
phase: 02-milestone-lifecycle-state
plan: 01
subsystem: workflow
tags: [milestone, state-management, guided-conversation, context-scanning, templates]

# Dependency graph
requires:
  - phase: 01-install-scaffold
    provides: command stubs, template files, directory structure
provides:
  - Complete new-milestone workflow (350+ lines) with guided conversation flow
  - Extended STATE.md template with 9 sections (scope, data source, success criteria, processed context, history)
  - Extended STRATEGY.md template with strategy type field and all 6 scope items
  - Sequence validation reference matrix for all /brrr commands
affects: [02-02-status-workflow, 03-discuss-research, 04-execute-loop, 05-verify-export]

# Tech tracking
tech-stack:
  added: []
  patterns: [behavioral-workflow-prompts, template-variable-filling, dual-state-validation]

key-files:
  created: []
  modified:
    - workflows/new-milestone.md
    - templates/STATE.md
    - templates/STRATEGY.md

key-decisions:
  - "Embedded preamble in workflow rather than separate _preamble.md file for simpler sequential execution"
  - "8 workflow steps (setup + 7 conversation steps) covering full scoping flow"
  - "Context file processing limited to 5 per invocation to prevent conversation derailment"
  - "Scope splitting is suggestion-only at 5+ items, never enforced"

patterns-established:
  - "Workflow structure: preamble checks -> sequential steps -> file creation"
  - "Context scan pattern: detect new files -> describe -> confirm -> record in STATE.md"
  - "Sequence validation: STATE.md primary + file existence fallback"
  - "Error message pattern: [STOP] + explanation + current position + next step"

requirements-completed: [MILE-01, MILE-02, MILE-03, MILE-04, STAT-01, STAT-03, STAT-04, STAT-05, CTXT-01, CTXT-02, CTXT-03]

# Metrics
duration: 3min
completed: 2026-03-21
---

# Phase 02 Plan 01: New-Milestone Workflow Summary

**Full guided conversation workflow for milestone creation with context scanning, smart scope defaults, strategy-type success criteria, and sequence validation reference**

## Performance

- **Duration:** 3 min
- **Started:** 2026-03-21T13:47:01Z
- **Completed:** 2026-03-21T13:50:02Z
- **Tasks:** 2
- **Files modified:** 3

## Accomplishments
- Extended STATE.md template from 4 sections to 9 sections (added Scope, Data Source, Success Criteria, Processed Context, History format)
- Extended STRATEGY.md template with Strategy Type field and all 6 scope items (added Risk management, MD instructions export)
- Replaced 10-line workflow stub with 351-line complete behavioral workflow covering the entire milestone creation flow

## Task Commits

Each task was committed atomically:

1. **Task 1: Extend STATE.md and STRATEGY.md templates** - `350bc0c` (feat)
2. **Task 2: Replace new-milestone workflow stub with full guided conversation** - `c8bee0b` (feat)

## Files Created/Modified
- `templates/STATE.md` - Extended state template with 9 sections: Status, Scope, Data Source, Success Criteria, Phases, Best Results, Processed Context, History
- `templates/STRATEGY.md` - Extended strategy template with Strategy Type field and all 6 scope items
- `workflows/new-milestone.md` - Complete 351-line behavioral workflow for guided milestone creation

## Decisions Made
- Embedded preamble logic directly in the workflow rather than creating a separate _preamble.md file -- inline keeps sequential execution simpler and avoids indirection
- Used 8 steps (Setup + 7 conversation steps) rather than 7 from the spec -- separated directory creation into its own step for clarity
- Context file processing capped at 5 per invocation to prevent conversation derailment (per research recommendation)

## Deviations from Plan

None - plan executed exactly as written.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness
- Templates are ready for the status workflow (02-02) which reads STATE.md
- Sequence validation matrix is documented and can be referenced by all future workflows
- Context scanning pattern is established for adoption by discuss, research, plan, execute workflows

## Self-Check: PASSED

All files verified present: workflows/new-milestone.md, templates/STATE.md, templates/STRATEGY.md, 02-01-SUMMARY.md
All commits verified: 350bc0c, c8bee0b

---
*Phase: 02-milestone-lifecycle-state*
*Completed: 2026-03-21*
