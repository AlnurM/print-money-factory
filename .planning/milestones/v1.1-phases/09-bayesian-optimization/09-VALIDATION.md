---
phase: 9
slug: bayesian-optimization
status: draft
nyquist_compliant: false
wave_0_complete: false
created: 2026-03-22
---

# Phase 9 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | pytest (available in venv) |
| **Config file** | none — pytest works without config |
| **Quick run command** | `~/.pmf/venv/bin/python -m pytest tests/test_optuna_bridge.py -x --tb=short` |
| **Full suite command** | `~/.pmf/venv/bin/python -m pytest tests/ -v` |
| **Estimated runtime** | ~5 seconds |

---

## Sampling Rate

- **After every task commit:** Run `~/.pmf/venv/bin/python -m pytest tests/test_optuna_bridge.py -x --tb=short`
- **After every plan wave:** Run `~/.pmf/venv/bin/python -m pytest tests/ -v`
- **Before `/gsd:verify-work`:** Full suite must be green
- **Max feedback latency:** 10 seconds

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|-----------|-------------------|-------------|--------|
| 09-01-01 | 01 | 1 | OPT-01 | unit | `pytest tests/test_optuna_bridge.py::test_ask_tell_lifecycle -x` | ❌ W0 | ⬜ pending |
| 09-01-01 | 01 | 1 | OPT-01 | unit | `pytest tests/test_optuna_bridge.py::test_tpe_default_sampler -x` | ❌ W0 | ⬜ pending |
| 09-01-01 | 01 | 1 | OPT-02 | unit | `pytest tests/test_optuna_bridge.py::test_cmaes_auto_selection -x` | ❌ W0 | ⬜ pending |
| 09-01-01 | 01 | 1 | OPT-02 | unit | `pytest tests/test_optuna_bridge.py::test_tpe_fallback_categorical -x` | ❌ W0 | ⬜ pending |
| 09-01-01 | 01 | 1 | OPT-03 | unit | `pytest tests/test_optuna_bridge.py::test_sqlite_persistence -x` | ❌ W0 | ⬜ pending |
| 09-01-01 | 01 | 1 | OPT-03 | unit | `pytest tests/test_optuna_bridge.py::test_param_change_detection -x` | ❌ W0 | ⬜ pending |
| 09-02-01 | 02 | 1 | OPT-04 | manual | Run `/brrr:plan` with >500 combos | N/A | ⬜ pending |
| 09-03-01 | 03 | 2 | OPT-01 | integration | grep verify on execute.md | N/A | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

- [ ] `tests/test_optuna_bridge.py` — unit tests for ask-tell lifecycle, sampler selection, persistence, param change detection
- [ ] `tests/conftest.py` — shared fixtures (tmp dirs, sample param spaces) — may already exist from Phase 5

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| Plan workflow auto-selects bayesian at 500+ combos | OPT-04 | Requires live Claude Code session | Run `/brrr:plan` with a strategy that has >500 param combos, verify "bayesian" auto-selected |
| Execute loop shows [WARMUP]/[GUIDED] tags | OPT-01 | Requires live backtest run | Run `/brrr:execute` with bayesian method, verify iteration display |
| --resume loads SQLite study | OPT-03 | Requires interrupted run | Start `/brrr:execute`, interrupt, resume with `--resume` |

---

## Validation Sign-Off

- [ ] All tasks have `<automated>` verify or Wave 0 dependencies
- [ ] Sampling continuity: no 3 consecutive tasks without automated verify
- [ ] Wave 0 covers all MISSING references
- [ ] No watch-mode flags
- [ ] Feedback latency < 10s
- [ ] `nyquist_compliant: true` set in frontmatter

**Approval:** pending
