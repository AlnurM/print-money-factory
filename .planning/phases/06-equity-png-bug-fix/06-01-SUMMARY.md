---
phase: 06-equity-png-bug-fix
plan: 01
subsystem: backtest
tags: [matplotlib, equity-curve, png, backtest-engine]

requires:
  - phase: none
    provides: n/a
provides:
  - "run_backtest() returns trades list and equity_curve array alongside scalar metrics"
  - "execute.md PNG generation uses returned equity_curve directly"
  - "Zero-trade iterations skip PNG with warning instead of blank image"
affects: [execute, verify, backtest-engine]

tech-stack:
  added: []
  patterns:
    - "Enrich return dict at caller (run_backtest) rather than modifying utility (compute_all_metrics)"

key-files:
  created: []
  modified:
    - references/backtest_engine.py
    - workflows/execute.md

key-decisions:
  - "Enrich run_backtest() return dict rather than modifying compute_all_metrics() -- keeps metrics module focused on scalar computation"
  - "Changed x-axis label from 'Trade #' to 'Bar' since equity_curve is now bar-by-bar mark-to-market"

patterns-established:
  - "run_backtest() return dict is the canonical data contract between engine and consumers"

requirements-completed: [BFIX-01]

duration: 1min
completed: 2026-03-22
---

# Phase 06 Plan 01: Equity PNG Bug Fix Summary

**Fixed blank equity PNGs by returning equity_curve from run_backtest() and using it directly in execute.md PNG generation with zero-trade guard**

## Performance

- **Duration:** 1 min
- **Started:** 2026-03-22T18:05:25Z
- **Completed:** 2026-03-22T18:06:25Z
- **Tasks:** 2
- **Files modified:** 2

## Accomplishments
- run_backtest() now returns trades list and equity_curve numpy array alongside all 9 scalar metrics
- execute.md PNG generation uses the returned bar-by-bar mark-to-market equity_curve directly instead of broken trade-pnl reconstruction
- Zero-trade iterations print a warning and skip PNG generation instead of rendering a blank image

## Task Commits

Each task was committed atomically:

1. **Task 1: Return trades and equity_curve from run_backtest()** - `d601db1` (fix)
2. **Task 2: Update execute.md PNG generation to use returned equity_curve with zero-trade guard** - `4a2ea90` (fix)

## Files Created/Modified
- `references/backtest_engine.py` - Added trades and equity_curve to run_backtest() return dict
- `workflows/execute.md` - Replaced broken reconstruction with direct equity_curve usage, added zero-trade guard

## Decisions Made
- Enriched run_backtest() return dict rather than modifying compute_all_metrics() -- keeps the metrics module focused on scalar computation while the engine owns raw data
- Changed x-axis label from "Trade #" to "Bar" since the equity curve is now bar-by-bar mark-to-market, not per-trade

## Deviations from Plan

None - plan executed exactly as written.

## Issues Encountered
None

## User Setup Required
None - no external service configuration required.

## Next Phase Readiness
- Equity PNG bug is fixed -- /brrr:execute iterations will now produce visible equity curves
- No blockers for subsequent phases

---
*Phase: 06-equity-png-bug-fix*
*Completed: 2026-03-22*
