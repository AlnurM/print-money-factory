---
phase: 01-package-scaffolding-install
plan: 01
subsystem: infra
tags: [npm, nodejs, python, venv, slash-commands, install-script]

# Dependency graph
requires: []
provides:
  - npm package structure with bin entry point for npx execution
  - 8 thin slash command files in commands/ with frontmatter and workflow refs
  - Install script with Python 3.10+ detection, venv creation, idempotent update
  - requirements.txt with 14 Python backtest dependencies
affects: [01-02, 01-03, 01-04, phase-2, phase-3, phase-4, phase-5]

# Tech tracking
tech-stack:
  added: [node-esm, python-venv, pip]
  patterns: [thin-command-pattern, gsd-mirror-architecture, idempotent-install]

key-files:
  created:
    - package.json
    - bin/install.mjs
    - requirements.txt
    - .npmignore
    - commands/new-milestone.md
    - commands/discuss.md
    - commands/research.md
    - commands/plan.md
    - commands/execute.md
    - commands/verify.md
    - commands/status.md
    - commands/update.md
  modified: []

key-decisions:
  - "ESM-only install script (type: module) with zero external dependencies"
  - "Thin command files reference ~/.pmf/workflows/ except update.md which has inline process"
  - "detectPython checks python3/python/py-3 candidates, requires 3.10+"
  - "Idempotent install: existing venv gets pip upgrade, new install creates venv from scratch"

patterns-established:
  - "Thin command pattern: frontmatter (name, description, allowed-tools) + objective + execution_context with @-refs + process delegation"
  - "GSD-mirror directory structure: commands/, workflows/, templates/, references/, bin/"
  - "Node stdlib only for install script (no external npm dependencies)"

requirements-completed: [INST-01, INST-02, INST-03, INST-04, INST-05, ARCH-01, ARCH-02]

# Metrics
duration: 2min
completed: 2026-03-21
---

# Phase 1 Plan 1: Package Scaffolding & Install Script Summary

**npm package with 8 thin slash commands, ESM install script handling Python 3.10+ venv creation, and 14 backtest dependencies**

## Performance

- **Duration:** 2 min
- **Started:** 2026-03-21T12:15:29Z
- **Completed:** 2026-03-21T12:17:38Z
- **Tasks:** 2
- **Files modified:** 12

## Accomplishments
- Created complete npm package structure publishable via npx with bin entry, ESM type, engine requirements
- Built 8 thin slash command files following GSD pattern with frontmatter and workflow @-references
- Implemented install script with Python detection, venv lifecycle management, and idempotent reinstall support
- Defined 14 Python dependencies with version ranges in requirements.txt

## Task Commits

Each task was committed atomically:

1. **Task 1: Create npm package structure with all 8 command files** - `8e6a8f6` (feat)
2. **Task 2: Create install script with Python detection, venv management, and idempotent copy** - `9807b23` (feat)

## Files Created/Modified
- `package.json` - npm package metadata with bin entry, files array, ESM type, engine requirement
- `bin/install.mjs` - Install script: Python detection, venv creation/update, file copy, verification (188 lines)
- `requirements.txt` - 14 Python dependencies with version ranges
- `.npmignore` - Excludes .planning/, .git/, .claude/, tests, node_modules
- `commands/new-milestone.md` - Milestone creation command
- `commands/discuss.md` - Strategy discussion command with --auto flag
- `commands/research.md` - Strategy research command with --deep flag and WebFetch
- `commands/plan.md` - Parameter space and optimization plan command
- `commands/execute.md` - AI-driven backtest loop command with --iterations/--fast/--resume
- `commands/verify.md` - Report generation and approval/debug command
- `commands/status.md` - Read-only status display command (no Write tool)
- `commands/update.md` - Self-update via npx with inline process (no workflow ref)

## Decisions Made
- ESM-only install script with zero external dependencies (Node stdlib only)
- update.md uses inline process per decision D-04 instead of workflow reference
- status.md omits Write from allowed-tools (read-only command)
- Graceful handling of missing directories (workflows/templates/references not yet created -- prints skip message)
- pytest included in requirements.txt for user-runnable metric verification tests

## Deviations from Plan

None - plan executed exactly as written.

## Issues Encountered
None

## User Setup Required
None - no external service configuration required.

## Next Phase Readiness
- Package structure ready for plan 01-02 (metrics module) and 01-03 (reference patterns, templates, workflow stubs)
- directories workflows/, templates/, references/ exist but are empty -- will be populated by subsequent plans
- Install script handles empty directories gracefully (prints skip message)

## Self-Check: PASSED

All 12 created files verified present. Both task commits (8e6a8f6, 9807b23) verified in git log.

---
*Phase: 01-package-scaffolding-install*
*Completed: 2026-03-21*
