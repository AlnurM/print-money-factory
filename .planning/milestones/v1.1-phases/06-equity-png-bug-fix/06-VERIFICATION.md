---
phase: 06-equity-png-bug-fix
verified: 2026-03-22T18:30:00Z
status: passed
score: 4/4 must-haves verified
---

# Phase 06: Equity PNG Bug Fix Verification Report

**Phase Goal:** Users see actual equity curve data in every execute iteration PNG
**Verified:** 2026-03-22T18:30:00Z
**Status:** passed
**Re-verification:** No — initial verification

## Goal Achievement

### Observable Truths

| #  | Truth                                                                                   | Status     | Evidence                                                                                   |
|----|-----------------------------------------------------------------------------------------|------------|--------------------------------------------------------------------------------------------|
| 1  | run_backtest() return dict contains 'trades' list and 'equity_curve' numpy array        | VERIFIED  | Lines 191-193 of backtest_engine.py: `metrics['trades'] = trades` and `metrics['equity_curve'] = np.array(equity)` |
| 2  | execute.md PNG generation uses returned equity_curve directly, not trade-based reconstruction | VERIFIED  | Line 537 of execute.md: `equity_arr = results_is.get('equity_curve', ...)` — old for-loop reconstruction is absent |
| 3  | Zero-trade iterations skip PNG generation with a warning message instead of rendering blank image | VERIFIED  | Lines 534-535 of execute.md: `if trade_count == 0: print("WARNING: No trades generated -- equity PNG skipped")` |
| 4  | PNG file contains a visible equity curve line when trades exist (not blank)             | VERIFIED  | Lines 539-548 of execute.md: `ax.plot(equity_arr, ...)` inside the `else` block; real equity_curve data plotted |

**Score:** 4/4 truths verified

### Required Artifacts

| Artifact                          | Expected                                                       | Status     | Details                                                                                              |
|-----------------------------------|----------------------------------------------------------------|------------|------------------------------------------------------------------------------------------------------|
| `references/backtest_engine.py`   | run_backtest() returns trades and equity_curve alongside metrics | VERIFIED  | Lines 186-193: `metrics = compute_all_metrics(...)`, then `metrics['trades'] = trades`, `metrics['equity_curve'] = np.array(equity)`, `return metrics` |
| `references/backtest_engine.py`   | run_backtest() returns equity_curve array                      | VERIFIED  | Line 192: `metrics['equity_curve'] = np.array(equity)` present                                      |
| `workflows/execute.md`            | PNG generation from returned equity_curve with zero-trade guard | VERIFIED  | Lines 531-548: zero-trade guard at line 534, equity_curve usage at line 537, matplotlib plot at 540 |

### Key Link Verification

| From                            | To                   | Via                                                    | Status    | Details                                                                      |
|---------------------------------|----------------------|--------------------------------------------------------|-----------|------------------------------------------------------------------------------|
| `references/backtest_engine.py` | `workflows/execute.md` | run_backtest() return dict consumed by PNG generation | VERIFIED | `equity_curve` key set in backtest_engine.py line 192; consumed by execute.md line 537 via `results_is.get('equity_curve', ...)` |

### Requirements Coverage

| Requirement | Source Plan | Description                                                                                | Status    | Evidence                                                                        |
|-------------|-------------|--------------------------------------------------------------------------------------------|-----------|---------------------------------------------------------------------------------|
| BFIX-01     | 06-01-PLAN  | Equity PNG shows actual equity curve data during `/brrr:execute` iterations (not blank)   | SATISFIED | run_backtest() returns bar-by-bar equity_curve; execute.md plots it directly; zero-trade guard prevents blank images |

No orphaned requirements found. REQUIREMENTS.md Traceability table maps only BFIX-01 to Phase 6, and it is marked Complete.

### Anti-Patterns Found

No blockers or warnings found.

Scans run on both modified files:
- No TODO/FIXME/placeholder comments
- No empty return stubs (return null / return {} / return [])
- Old broken trade-pnl for-loop reconstruction is fully removed from execute.md
- `ax.plot(equity_arr, ...)` is inside the `else` block (guarded by `trade_count > 0`), so blank images are structurally impossible

The only `np.array([initial_capital])` usage is as a `.get()` fallback default, not a primary code path that reaches the plotter. When `equity_curve` is absent entirely (edge case), the single-point array would render a flat line — this is a minor edge case but not a blocker because `run_backtest()` always sets `equity_curve`.

### Human Verification Required

1. **Visual equity curve appearance during live execute run**

   **Test:** Run `/brrr:execute` with a strategy that generates trades, check the saved PNG file.
   **Expected:** PNG contains a visible colored line rising or falling across bars, not a blank white image.
   **Why human:** Cannot render a matplotlib PNG from a code scan; requires actual Python execution with real OHLCV data.

2. **Zero-trade warning message appears in Claude's output**

   **Test:** Run `/brrr:execute` with a strategy that produces 0 trades (e.g., all signals return 'hold').
   **Expected:** Output includes `WARNING: No trades generated -- equity PNG skipped` and no PNG file is created for that iteration.
   **Why human:** Requires executing the Python code path with a known-zero-trade strategy.

### Gaps Summary

No gaps. All four observable truths are verified. Both required artifacts exist and are substantive. The key link between backtest_engine.py and execute.md is wired. BFIX-01 is satisfied. Commits d601db1 and 4a2ea90 are confirmed present in git history.

---

_Verified: 2026-03-22T18:30:00Z_
_Verifier: Claude (gsd-verifier)_
