---
phase: 01-package-scaffolding-install
plan: 03
subsystem: references
tags: [backtest-engine, anti-lookahead, data-sources, pinescript, templates, workflows]

# Dependency graph
requires:
  - phase: none
    provides: greenfield
provides:
  - "Backtest engine skeleton with anti-lookahead enforcement"
  - "Data source adapters (ccxt, yfinance, CSV) with validation"
  - "Pattern guide for backtest code generation"
  - "Common pitfalls catalog (6 pitfalls)"
  - "PineScript v5 template + 3 complete examples"
  - "STRATEGY.md and STATE.md milestone templates"
  - "Plotly HTML report template"
  - "7 workflow stub files for install script"
affects: [02-milestone-state-management, 03-strategy-specification, 04-backtest-execution-loop, 05-verify-export-polish]

# Tech tracking
tech-stack:
  added: [pandas, numpy, ccxt, yfinance, plotly, jinja2]
  patterns: [event-loop-backtest, anti-lookahead, validate-ohlcv, thin-command-fat-workflow]

key-files:
  created:
    - references/backtest_engine.py
    - references/backtest-engine.md
    - references/data_sources.py
    - references/common-pitfalls.md
    - references/pinescript-examples/trend-following.pine
    - references/pinescript-examples/mean-reversion.pine
    - references/pinescript-examples/breakout.pine
    - templates/pinescript-template.pine
    - templates/STRATEGY.md
    - templates/STATE.md
    - templates/report-template.html
    - workflows/new-milestone.md
    - workflows/discuss.md
    - workflows/research.md
    - workflows/plan.md
    - workflows/execute.md
    - workflows/verify.md
    - workflows/status.md
  modified: []

key-decisions:
  - "Backtest engine uses mark-to-market equity tracking for unrealized positions"
  - "Commission applied at both entry and exit, tracked per-trade"
  - "Plotly CDN pinned to v2.35.2 in report template"

patterns-established:
  - "Anti-lookahead: history[:i+1] for signals, df.iloc[i]['open'] for execution"
  - "validate_ohlcv() pattern for all data sources before backtest"
  - "Workflow stubs as placeholder for install script file copying"

requirements-completed: [ARCH-04, ARCH-05]

# Metrics
duration: 5min
completed: 2026-03-21
---

# Phase 01 Plan 03: References, Templates, and Workflows Summary

**Backtest engine skeleton with anti-lookahead enforcement, 3 data source adapters, PineScript v5 templates/examples, and 7 workflow stubs**

## Performance

- **Duration:** 5 min
- **Started:** 2026-03-21T12:15:38Z
- **Completed:** 2026-03-21T12:20:29Z
- **Tasks:** 2
- **Files created:** 18

## Accomplishments
- Backtest engine skeleton enforcing anti-lookahead rules (event-loop, next-bar execution, history slicing)
- Data source adapters with shared validate_ohlcv() helper for ccxt, yfinance, and CSV loading
- Pattern guide documenting anti-lookahead rules, position management, and commission modeling
- Common pitfalls catalog covering 6 major backtesting risks with detection and prevention
- 3 complete PineScript v5 examples (trend-following, mean-reversion, breakout) ready for TradingView
- Project templates (STRATEGY.md, STATE.md, report HTML) and 7 workflow stubs

## Task Commits

Each task was committed atomically:

1. **Task 1: Create backtest engine skeleton, pattern guide, data sources, and pitfalls catalog** - `56525f8` (feat)
2. **Task 2: Create PineScript templates/examples, project templates, and workflow stubs** - `34e1989` (feat)

## Files Created/Modified
- `references/backtest_engine.py` - Event-loop backtest skeleton with anti-lookahead enforcement
- `references/backtest-engine.md` - Pattern guide with anti-lookahead rules and examples
- `references/data_sources.py` - Data source adapters: load_ccxt, load_yfinance, load_csv with validation
- `references/common-pitfalls.md` - Catalog of 6 major backtesting pitfalls
- `references/pinescript-examples/trend-following.pine` - EMA crossover strategy
- `references/pinescript-examples/mean-reversion.pine` - Bollinger Band bounce strategy
- `references/pinescript-examples/breakout.pine` - Donchian channel breakout strategy
- `templates/pinescript-template.pine` - PineScript v5 skeleton template
- `templates/STRATEGY.md` - Milestone hypothesis scaffold
- `templates/STATE.md` - Milestone state tracker scaffold
- `templates/report-template.html` - Plotly HTML report template with equity/drawdown/trade sections
- `workflows/new-milestone.md` - Stub for Phase 2
- `workflows/discuss.md` - Stub for Phase 3
- `workflows/research.md` - Stub for Phase 3
- `workflows/plan.md` - Stub for Phase 3
- `workflows/execute.md` - Stub for Phase 4
- `workflows/verify.md` - Stub for Phase 5
- `workflows/status.md` - Stub for Phase 2

## Decisions Made
- Backtest engine tracks unrealized P&L via mark-to-market at each bar's close for accurate equity curve
- Commission deducted on both entry and exit sides, stored per-trade for transparency
- Plotly CDN pinned to v2.35.2 in report template for reproducibility

## Deviations from Plan

None - plan executed exactly as written.

## Issues Encountered

None.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness
- All reference files ready for install script to copy to ~/.pmf/references/
- All templates ready for install script to copy to ~/.pmf/templates/
- All workflow stubs ready for install script to copy to ~/.pmf/workflows/
- Backtest engine depends on metrics.py module (created in plan 01-02) being present at ~/.pmf/references/

## Self-Check: PASSED

All 18 files verified present. Both task commits (56525f8, 34e1989) verified in git log.

---
*Phase: 01-package-scaffolding-install*
*Completed: 2026-03-21*
