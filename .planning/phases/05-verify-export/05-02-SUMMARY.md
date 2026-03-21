---
phase: 05-verify-export
plan: 02
subsystem: workflow
tags: [pinescript, verify, export, approval, debug, state-management]

requires:
  - phase: 05-verify-export
    provides: report_generator.py module, extended HTML template with 9 sections
  - phase: 04-ai-backtest-loop
    provides: execute.md workflow pattern, iteration artifacts format, best_result.json
provides:
  - Complete verify.md behavioral workflow (999 lines) for report generation, AI assessment, approval/debug flow
  - PineScript v5 syntax rules reference for Claude to read before generating Pine code
  - Export package specification covering all 7 output files
  - --approved path with STATE.md CLOSED status and full export generation
  - --debug path with diagnosis document and new phase cycle
affects: [verify-command, pinescript-generation, milestone-closure]

tech-stack:
  added: []
  patterns: [PineScript v5 dual-output pattern (strategy + indicator), force-approve with unmet targets warning]

key-files:
  created:
    - references/pinescript-rules.md
  modified:
    - workflows/verify.md

key-decisions:
  - "PineScript rules reference covers strategy vs indicator distinction with explicit never-call warnings"
  - "Verify workflow follows same preamble pattern as execute.md and discuss.md for consistency"
  - "Both alert() and alertcondition() included in indicator version for maximum TradingView compatibility"

patterns-established:
  - "PineScript dual-output: generate both strategy() and indicator() versions from same logic"
  - "Force-approve pattern: warn about unmet targets but allow user override per D-08"
  - "Debug diagnosis document with specific hypothesis driving next phase cycle"

requirements-completed: [VRFY-10, VRFY-11, VRFY-12, EXPT-01, EXPT-02, EXPT-03, EXPT-04, EXPT-05, EXPT-06, EXPT-07]

duration: 4min
completed: 2026-03-21
---

# Phase 5 Plan 2: Verify Workflow & PineScript Reference Summary

**Complete verify.md behavioral workflow (999 lines) with PineScript v5 syntax rules reference, covering report generation, AI assessment, 7-file export package on --approved, and diagnosis-driven debug cycles on --debug**

## Performance

- **Duration:** 4 min
- **Started:** 2026-03-21T18:37:12Z
- **Completed:** 2026-03-21T18:41:00Z
- **Tasks:** 2
- **Files modified:** 2

## Accomplishments
- Created PineScript v5 syntax rules reference (405 lines) covering strategy vs indicator distinction, all common ta namespace functions, signal patterns, and v6 migration notes
- Replaced 10-line verify.md stub with 999-line behavioral workflow covering the complete verify pipeline: sequence validation, report generation, AI analysis, approval/debug flow, export package, and STATE.md updates
- Workflow specifies all 7 export files (2 PineScript, trading-rules, performance-report, backtest_final, live-checklist, report HTML) in output/ directory

## Task Commits

Each task was committed atomically:

1. **Task 1: Create PineScript v5 syntax rules reference** - `1e73377` (feat)
2. **Task 2: Write complete verify.md behavioral workflow** - `28ec1b3` (feat)

## Files Created/Modified
- `references/pinescript-rules.md` - PineScript v5 syntax reference with strategy/indicator distinction, input functions, ta namespace, strategy execution, indicator signals, common patterns, v6 migration notes, generation checklist
- `workflows/verify.md` - Complete behavioral workflow: preamble (sequence validation, context scan, argument parsing), load inputs, generate report via report_generator.py, AI analysis with quant assessment tone, approval path with 7-file export package, debug path with diagnosis document and new phase cycle, STATE.md updates (CLOSED on approved, increment on debug)

## Decisions Made
- PineScript rules reference includes explicit warning about never calling strategy.* in indicator scripts (the #1 PineScript generation error)
- Verify workflow follows established preamble pattern from execute.md and discuss.md for consistency across all workflows
- Both alert() and alertcondition() included in indicator output for maximum TradingView compatibility
- Force-approve warning pattern per D-08: warn about unmet targets but allow user to proceed

## Deviations from Plan

None - plan executed exactly as written.

## Issues Encountered

None.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness
- Verify workflow ready for end-to-end testing with a real strategy milestone
- PineScript reference ready for Claude to read before generating Pine code
- Plan 05-03 can proceed with any remaining Phase 5 work (command files, final polish)
- All VRFY-10..12 and EXPT-01..07 requirements addressed by this plan

## Self-Check: PASSED
