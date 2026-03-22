# Phase 2: Milestone Lifecycle & State - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-03-21
**Phase:** 02-milestone-lifecycle-state
**Areas discussed:** Scoping flow, State tracking, Context files, Status display

---

## Scoping Flow

### How interactive should the new-milestone scoping be?

| Option | Description | Selected |
|--------|-------------|----------|
| Guided conversation | Claude asks questions one by one, follows threads, challenges vague answers | ✓ |
| Structured form | Present all fields at once, user fills in, Claude validates | |

### Should Claude recommend a default scope?

| Option | Description | Selected |
|--------|-------------|----------|
| Smart defaults | Claude recommends based on idea complexity | ✓ |
| Always full menu | Show all options every time, no pre-selection | |

### Success criteria defaults

| Option | Description | Selected |
|--------|-------------|----------|
| By strategy type | Trend: Sharpe>1.2, DD<30%. Mean-rev: Sharpe>1.5, DD<20%. Breakout: Sharpe>1.0, DD<35% | ✓ |
| Universal defaults | Always start with Sharpe>1.5, DD<25%, 30 min trades | |

### Scope splitting enforcement

| Option | Description | Selected |
|--------|-------------|----------|
| Suggest only | Recommend splitting but let user override | ✓ |
| Enforce limit | Hard cap: max 4-5 scope items per milestone | |

---

## State Tracking

### Sequence validation method

| Option | Description | Selected |
|--------|-------------|----------|
| Read STATE.md | Each command reads STATE.md, checks current step | |
| File existence | Check if prerequisite artifacts exist | |
| Both | STATE.md as primary, file existence as fallback | ✓ |

### Phase artifact naming

| Option | Description | Selected |
|--------|-------------|----------|
| phase_N_step.md | phase_1_discuss.md, phase_1_plan.md — matches spec | ✓ |
| Flat with prefix | 01_discuss.md, 01_plan.md — shorter | |

### History log verbosity

| Option | Description | Selected |
|--------|-------------|----------|
| One line per event | Concise, scannable | |
| Structured entries | Multi-line with timestamp, metrics, AI diagnosis | ✓ |

---

## Context Files

### Image parsing approach

| Option | Description | Selected |
|--------|-------------|----------|
| Claude vision | Claude reads image directly | |
| Describe + confirm | Claude describes what it sees, user confirms before incorporating | ✓ |

### Detection trigger

| Option | Description | Selected |
|--------|-------------|----------|
| Auto on every cmd | Every /brrr:* command checks .pmf/context/ | |
| Manual trigger | User runs /brrr:context to process | |
| Auto + flag skip | Auto-detect by default, --no-context to skip | ✓ |

### Tracking processed files

| Option | Description | Selected |
|--------|-------------|----------|
| Move to processed/ | Move confirmed files to .pmf/context/processed/ | |
| Track in STATE.md | Record filenames in STATE.md, files stay in place | ✓ |

---

## Status Display

### Detail level

| Option | Description | Selected |
|--------|-------------|----------|
| Full tree | Every step with status icons per phase | ✓ |
| Phase summary | Phases only, expand on request | |

### Next step display

| Option | Description | Selected |
|--------|-------------|----------|
| Always | Always show actionable next step | ✓ |
| Only if stuck | Show only when not obvious | |

### Language

| Option | Description | Selected |
|--------|-------------|----------|
| English | All output in English | ✓ |
| Russian | All output in Russian | |
| Auto-detect | Follow user's language | |

---

## Claude's Discretion

- Exact wording of scoping questions
- Strategy type detection for default criteria
- STATE.md internal format details
- Error message formatting
- Context file processing limits

## Deferred Ideas

None — discussion stayed within phase scope
