---
phase: 5
slug: verify-export
status: draft
nyquist_compliant: false
wave_0_complete: false
created: 2026-03-21
---

# Phase 5 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | pytest 7.x (existing in venv) |
| **Config file** | none — existing test infrastructure from Phase 1 |
| **Quick run command** | `~/.pmf/venv/bin/python -m pytest tests/ -x -q` |
| **Full suite command** | `~/.pmf/venv/bin/python -m pytest tests/ -v` |
| **Estimated runtime** | ~10 seconds |

---

## Sampling Rate

- **After every task commit:** Run `~/.pmf/venv/bin/python -m pytest tests/ -x -q`
- **After every plan wave:** Run `~/.pmf/venv/bin/python -m pytest tests/ -v`
- **Before `/gsd:verify-work`:** Full suite must be green
- **Max feedback latency:** 15 seconds

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|-----------|-------------------|-------------|--------|
| 05-01-01 | 01 | 1 | VRFY-01 | integration | `python report_gen.py && test -f report.html` | ❌ W0 | ⬜ pending |
| 05-01-02 | 01 | 1 | VRFY-02 | integration | `grep "regime" report.html` | ❌ W0 | ⬜ pending |
| 05-01-03 | 01 | 1 | VRFY-03 | integration | `grep "benchmark" report.html` | ❌ W0 | ⬜ pending |
| 05-02-01 | 02 | 2 | EXPT-01 | integration | `test -d output/ && ls output/` | ❌ W0 | ⬜ pending |
| 05-02-02 | 02 | 2 | EXPT-02 | manual | PineScript paste in TradingView | N/A | ⬜ pending |
| 05-03-01 | 03 | 2 | VRFY-07 | integration | `grep "debug" verify.md` | ❌ W0 | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

- [ ] Report generation script template — stubs for VRFY-01 through VRFY-06
- [ ] Export package structure — stubs for EXPT-01 through EXPT-07

*Existing test infrastructure from Phase 1 (test_metrics.py) covers metric computation.*

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| HTML report opens in browser with interactive charts | VRFY-01 | Requires browser rendering | Open generated HTML in browser, verify plotly charts are interactive |
| PineScript compiles in TradingView | EXPT-02 | Requires TradingView Pine Editor | Paste generated .pine into Pine Editor, verify no compilation errors |
| Equity curve is visually correct | VRFY-04 | Visual verification | Compare equity curve shape to known backtest results |

---

## Validation Sign-Off

- [ ] All tasks have `<automated>` verify or Wave 0 dependencies
- [ ] Sampling continuity: no 3 consecutive tasks without automated verify
- [ ] Wave 0 covers all MISSING references
- [ ] No watch-mode flags
- [ ] Feedback latency < 15s
- [ ] `nyquist_compliant: true` set in frontmatter

**Approval:** pending
