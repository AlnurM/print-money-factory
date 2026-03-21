---
phase: 2
slug: milestone-lifecycle-state
status: draft
nyquist_compliant: false
wave_0_complete: false
created: 2026-03-21
---

# Phase 2 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | grep/file existence checks (markdown workflow files) |
| **Config file** | none |
| **Quick run command** | `grep -c "## Step" workflows/new-milestone.md && grep -c "status:" templates/STATE.md` |
| **Full suite command** | `bash -c 'for f in workflows/new-milestone.md workflows/status.md; do test -f "$f" && echo "OK: $f" || echo "MISSING: $f"; done'` |
| **Estimated runtime** | ~1 second |

---

## Sampling Rate

- **After every task commit:** Run quick check on modified workflow files
- **After every plan wave:** Verify all workflow files exist and have expected sections
- **Before `/gsd:verify-work`:** Full manual test of /brrr:new-milestone and /brrr:status flows
- **Max feedback latency:** 2 seconds

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|-----------|-------------------|-------------|--------|
| 02-01-01 | 01 | 1 | MILE-01..03 | content | `grep -q "## Step" workflows/new-milestone.md` | ❌ W0 | ⬜ pending |
| 02-02-01 | 02 | 1 | STAT-01..05 | content | `grep -q "current_step" workflows/new-milestone.md` | ❌ W0 | ⬜ pending |
| 02-03-01 | 03 | 1 | CTXT-01..03 | content | `grep -q "context" workflows/new-milestone.md` | ❌ W0 | ⬜ pending |
| 02-04-01 | 04 | 2 | MILE-05 | manual | Run `/brrr:status` in Claude Code | ❌ W0 | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

- [ ] Workflow files must replace stubs with real behavioral content
- [ ] Templates must have all placeholder variables documented

*Existing infrastructure covers verification needs — no test framework required for markdown workflows.*

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| Guided scoping conversation | MILE-01 | Requires Claude Code interactive session | Run `/brrr:new-milestone`, verify guided Q&A flow |
| Out-of-sequence refusal | STAT-03 | Requires Claude Code command execution | Run `/brrr:execute` without plan, verify error |
| Context file parsing | CTXT-02 | Requires multimodal Claude + user confirmation | Drop image in .pmf/context/, run any command |
| ASCII status tree | MILE-05 | Requires Claude Code rendering | Run `/brrr:status`, verify tree format |
| One-milestone enforcement | MILE-04 | Requires active milestone state | Run `/brrr:new-milestone` twice |

---

## Validation Sign-Off

- [ ] All tasks have `<automated>` verify or Wave 0 dependencies
- [ ] Sampling continuity: no 3 consecutive tasks without automated verify
- [ ] Wave 0 covers all MISSING references
- [ ] No watch-mode flags
- [ ] Feedback latency < 2s
- [ ] `nyquist_compliant: true` set in frontmatter

**Approval:** pending
