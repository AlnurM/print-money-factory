---
phase: 1
slug: package-scaffolding-install
status: draft
nyquist_compliant: false
wave_0_complete: false
created: 2026-03-21
---

# Phase 1 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | pytest 8.x (included in venv requirements.txt) |
| **Config file** | none — Wave 0 installs |
| **Quick run command** | `~/.pmf/venv/bin/python -m pytest tests/ -x -q` |
| **Full suite command** | `~/.pmf/venv/bin/python -m pytest tests/ -v` |
| **Estimated runtime** | ~5 seconds |

---

## Sampling Rate

- **After every task commit:** Run `~/.pmf/venv/bin/python -m pytest tests/ -x -q`
- **After every plan wave:** Run `~/.pmf/venv/bin/python -m pytest tests/ -v`
- **Before `/gsd:verify-work`:** Full suite must be green
- **Max feedback latency:** 10 seconds

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|-----------|-------------------|-------------|--------|
| 01-01-01 | 01 | 1 | INST-01 | integration | `node scripts/install.js --dry-run` | ❌ W0 | ⬜ pending |
| 01-01-02 | 01 | 1 | INST-03 | unit | `node -e "require('./scripts/install').checkPython()"` | ❌ W0 | ⬜ pending |
| 01-01-03 | 01 | 1 | INST-04 | integration | `node scripts/install.js && node scripts/install.js` | ❌ W0 | ⬜ pending |
| 01-02-01 | 02 | 1 | ARCH-03 | unit | `~/.pmf/venv/bin/python -m pytest tests/test_metrics.py -v` | ❌ W0 | ⬜ pending |
| 01-03-01 | 03 | 1 | ARCH-04 | unit | `~/.pmf/venv/bin/python -m pytest tests/test_backtest_engine.py -v` | ❌ W0 | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

- [ ] `tests/test_metrics.py` — known-answer tests for all 9 core metrics (Sharpe, Sortino, Calmar, Max DD, Win Rate, PF, expectancy, trade count, net P&L)
- [ ] `tests/test_backtest_engine.py` — event-loop pattern validation, next-bar execution enforcement
- [ ] `tests/conftest.py` — shared fixtures (sample trade log, sample returns series)
- [ ] pytest in requirements.txt — installed into venv

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| Commands appear in Claude Code | INST-01 | Requires Claude Code session | Run `/brrr:status` after install — should be recognized |
| Python 3.10+ missing error | INST-03 | Requires system without Python 3.10+ | Test on machine with Python 3.9 or no Python |
| Update via npx reinstall | INST-05 | Requires npm registry publish | Modify a file, reinstall, verify update applied |

---

## Validation Sign-Off

- [ ] All tasks have `<automated>` verify or Wave 0 dependencies
- [ ] Sampling continuity: no 3 consecutive tasks without automated verify
- [ ] Wave 0 covers all MISSING references
- [ ] No watch-mode flags
- [ ] Feedback latency < 10s
- [ ] `nyquist_compliant: true` set in frontmatter

**Approval:** pending
