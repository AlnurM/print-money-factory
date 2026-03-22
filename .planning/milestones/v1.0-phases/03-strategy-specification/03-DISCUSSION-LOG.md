# Phase 3: Strategy Specification - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.

**Date:** 2026-03-21
**Phase:** 03-strategy-specification
**Areas discussed:** Discuss workflow, Research workflow, Plan workflow, Drift protection

---

## Discuss Workflow

| Question | Selected | Alternatives |
|----------|----------|-------------|
| Conversation structure | Follow the thread | Topic-by-topic |
| --auto defaults | Both (type + STRATEGY.md context) | From strategy type only, From STRATEGY.md only |
| Debug discuss context | Everything (all prior phases) | Last phase only |

## Research Workflow

| Question | Selected | Alternatives |
|----------|----------|-------------|
| Search sources | Training + web | Web search only |
| --deep flag | Both (more sources + deeper analysis) | More sources only, Deeper analysis only |
| When to recommend | Auto-detect from discuss output | Strategy complexity, User confidence |

## Plan Workflow

| Question | Selected | Alternatives |
|----------|----------|-------------|
| Optimization method | Auto by param count, user override | Always ask user |
| Parameter budget | Warn + explain, allow override | Warn only, Hard limit |
| Train/test split | Plan sets rules, execute calculates | Plan defines exact split |

## Drift Protection

| Question | Selected | Alternatives |
|----------|----------|-------------|
| Drift definition | New indicators OR changed logic, >50% threshold | New indicators only, Changed logic only |
| Response | Hard gate (stop, force choice) | Soft suggestion |

## Claude's Discretion
- Question wording and conversation flow
- Research findings presentation
- Parameter range suggestions
- Plan output format
- Web search queries

## Deferred Ideas
None
