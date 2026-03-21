---
phase: 4
slug: ai-backtest-loop
status: draft
nyquist_compliant: false
wave_0_complete: false
created: 2026-03-21
---

# Phase 4 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | grep/content checks (behavioral workflow) + Python smoke tests |
| **Config file** | none |
| **Quick run command** | `grep -c "## Step" workflows/execute.md && wc -l workflows/execute.md` |
| **Full suite command** | `bash -c 'grep -q "MINT\|PLATEAU\|REKT\|NO DATA" workflows/execute.md && grep -q "iter_.*_params.json" workflows/execute.md && echo OK'` |
| **Estimated runtime** | ~2 seconds |

---

## Sampling Rate

- **After every task commit:** Quick grep checks on modified workflow
- **After every plan wave:** Full content verification
- **Before `/gsd:verify-work`:** Manual test with real data source
- **Max feedback latency:** 5 seconds

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|-----------|-------------------|-------------|--------|
| 04-01-01 | 01 | 1 | EXEC-01..14, DATA-01..05 | content | `wc -l workflows/execute.md \| awk '{print ($1 >= 400)}'` | ❌ W0 | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

- [ ] Execute workflow must replace stub with complete behavioral instructions

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| AI iteration loop runs end-to-end | EXEC-01 | Requires live data + Python execution | Run /brrr:execute with a simple MA crossover strategy |
| Stop conditions trigger correctly | EXEC-08 | Requires multiple iterations | Run until PLATEAU or MINT |
| Equity PNG generated | EXEC-10 | Requires matplotlib + actual data | Check .pmf/phases/phase_N_execute/ for PNG files |
| Data validation catches gaps | DATA-04 | Requires intentionally bad data | Test with CSV containing NaN values |
| Walk-forward analysis | EXEC-07 | Requires sufficient data + params | Run with walk-forward optimization method |

---

## Validation Sign-Off

- [ ] All tasks have `<automated>` verify or Wave 0 dependencies
- [ ] Sampling continuity: no 3 consecutive tasks without automated verify
- [ ] Wave 0 covers all MISSING references
- [ ] No watch-mode flags
- [ ] Feedback latency < 5s
- [ ] `nyquist_compliant: true` set in frontmatter

**Approval:** pending
