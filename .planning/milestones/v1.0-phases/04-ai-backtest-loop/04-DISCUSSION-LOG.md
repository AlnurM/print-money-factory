# Phase 4: AI Backtest Loop - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.

**Date:** 2026-03-21
**Phase:** 04-ai-backtest-loop
**Areas discussed:** AI iteration loop, Stop conditions, Terminal display, Data handling

---

## AI Iteration Loop

| Question | Selected | Alternatives |
|----------|----------|-------------|
| How Claude decides what to change | Holistic analysis (all artifacts + equity PNG) | Metrics-driven rules |
| Parameters changed per iteration | Adaptive (1-2 start, 3-4 if plateau) | One at a time, Batch changes |
| Explain reasoning | Always explain | Brief + on request |

## Stop Conditions

| Question | Selected | Alternatives |
|----------|----------|-------------|
| PLATEAU configurable | From plan phase | Fixed defaults |
| REKT diagnosis | Strategy vs asset distinction | General diagnosis |
| MINT behavior | Stop + suggest more | Stop immediately, Auto-improve |

## Terminal Display

| Question | Selected | Alternatives |
|----------|----------|-------------|
| Display format | Spec format (header + iteration blocks + brrr) | Compact table |
| Equity PNG | Save + mention path | Save only |

## Data Handling

| Question | Selected | Alternatives |
|----------|----------|-------------|
| Crypto source | From STRATEGY.md | Ask at execute |
| Data cache | .pmf/cache/ (project-local) | ~/.pmf/cache/ (global) |
| Bad data | Auto-fix + warn (refuse if >10% affected) | Strict refuse |

## Claude's Discretion
- Python code structure per strategy
- Equity curve visual interpretation
- Incremental vs radical parameter changes
- Python error handling
- Verdict JSON format

## Deferred Ideas
None
