---
status: partial
phase: 05-verify-export
source: [05-VERIFICATION.md]
started: 2026-03-22T00:00:00.000Z
updated: 2026-03-22T00:00:00.000Z
---

## Current Test

[awaiting human testing]

## Tests

### 1. HTML report visual rendering
expected: Open generated HTML in a browser; verify all 9 sections render with correct colors, interactive charts, and two equity lines
result: [pending]

### 2. --approved end-to-end
expected: Run `/brrr:verify --approved` on a real milestone; confirm 7 files in `output/` and `STATE.md` shows `CLOSED`
result: [pending]

### 3. --debug end-to-end
expected: Run `/brrr:verify --debug`; confirm `debug_diagnosis.md` created and STATE.md increments phase number
result: [pending]

### 4. AI assessment specificity
expected: Confirm the AI assessment references actual metric values vs targets, not generic advice
result: [pending]

## Summary

total: 4
passed: 0
issues: 0
pending: 4
skipped: 0
blocked: 0

## Gaps
