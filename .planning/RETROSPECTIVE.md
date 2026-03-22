# Project Retrospective

*A living document updated after each milestone. Lessons feed forward into future planning.*

## Milestone: v1.0 — MVP

**Shipped:** 2026-03-22
**Phases:** 5 | **Plans:** 14 | **Sessions:** ~4

### What Was Built
- Complete trading strategy pipeline: idea → discuss → research → plan → execute → verify → export
- 8 slash commands with 7 behavioral workflows (discuss 512L, execute 1067L, verify 999L)
- Python backtest infrastructure: metrics (32 TDD tests), data sources (ccxt/yfinance/CSV), report generator (504L)
- Interactive HTML report with 9 sections (plotly) + 7-file export package including PineScript v5
- npm package published as `@print-money-factory/cli@0.4.0`

### What Worked
- Thin command + behavioral workflow pattern — commands are 5-line markdown files that @-reference workflows, keeping commands stable while workflows evolve
- TDD for metrics module — 32 known-answer tests caught floating-point edge cases (Sharpe with zero std dev) early
- Human verification checkpoints at Phase 1 (install) and Phase 4 (execute loop) caught real issues that automated checks missed
- Research phase before planning Phase 5 identified the plotly CDN duplication pitfall and PineScript strategy/indicator split before any code was written

### What Was Inefficient
- Phase 1-3 ROADMAP checkboxes were never marked `[x]` — only Phase 4-5 used the completion tool properly
- The report_generator.py is 504 lines as a reference module — could have been split into smaller focused modules, but the single-file pattern matches the project's conventions (metrics.py, data_sources.py, backtest_engine.py)
- `__pycache__` and `.pytest_cache` leaked into the npm tarball on 0.4.0 publish — `.npmignore` fix was retroactive

### Patterns Established
- Reference modules (references/*.py) are fixed code that gets copied during install, not generated per strategy
- Workflows are the behavioral contract — they describe what Claude does step-by-step, not what code to write
- Install script uses recursive directory copy (copyDirRecursive) — new files in references/, workflows/, templates/ are automatically included
- PineScript reference file (pinescript-rules.md) as Claude's read-before-generating contract

### Key Lessons
1. Behavioral workflows (markdown describing AI behavior) are more maintainable than code-generating templates — the AI adapts the behavior to each strategy naturally
2. The plan-check-revise loop (planner → checker → revision) catches real issues — D-15 status value contradiction and weak automated verify were caught before execution
3. Human checkpoints are worth the workflow interruption for pipeline-critical features (install, execute loop, verify flow)

### Cost Observations
- Model mix: ~80% opus (planning, execution, research), ~20% sonnet (verification, checking)
- Sessions: ~4 across 2 days
- Notable: Phase 5 planning took 3 agent rounds (plan → check → revise → re-check) but produced higher quality plans

---

## Cross-Milestone Trends

### Process Evolution

| Milestone | Sessions | Phases | Key Change |
|-----------|----------|--------|------------|
| v1.0 | ~4 | 5 | Initial pipeline — established behavioral workflow pattern |

### Cumulative Quality

| Milestone | Tests | Coverage | Zero-Dep Additions |
|-----------|-------|----------|-------------------|
| v1.0 | 46 (32 metrics + 14 report/export) | Core metrics + report generation | 0 (all deps in requirements.txt) |

### Top Lessons (Verified Across Milestones)

1. Behavioral workflows > code templates for AI-driven tools
2. Human checkpoints catch what automated checks miss
