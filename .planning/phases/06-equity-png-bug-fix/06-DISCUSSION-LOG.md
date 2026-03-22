# Phase 6: Equity PNG Bug Fix - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-03-22
**Phase:** 06-equity-png-bug-fix
**Areas discussed:** Fix approach, Zero-trade handling

---

## Fix Approach

| Option | Description | Selected |
|--------|-------------|----------|
| Fix approach | Modify run_backtest() return dict — 3-line fix to backtest_engine.py | ✓ |
| Zero-trade handling | What to do when no trades generated | ✓ |
| You decide on both | Claude picks simplest correct approach | ✓ |

**User's choice:** All three selected — user wants visibility but gave Claude full discretion
**Notes:** Root cause identified via code analysis: run_backtest() returns compute_all_metrics() which discards trades and equity_curve. Fix is adding them to the return dict.

---

## Claude's Discretion

- Fix approach: modify backtest_engine.py return dict (simplest fix)
- Zero-trade handling: skip PNG + log warning (don't render blank images)
- Whether to include dates array for x-axis (nice-to-have)

## Deferred Ideas

None
