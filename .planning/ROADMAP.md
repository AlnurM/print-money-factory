# Roadmap: Print Money Factory

## Overview

This roadmap delivers a complete AI-driven trading strategy development pipeline as an npm package for Claude Code. The journey follows the natural dependency chain: the package must install before commands can run, milestone and state management must exist before the strategy workflow can proceed, strategy specification (discuss/research/plan) must produce a formal plan before the backtest loop can execute, execution must produce results before verification can analyze them, and verification must approve before exports are generated. Five phases, each delivering a coherent capability that unblocks the next.

## Phases

**Phase Numbering:**
- Integer phases (1, 2, 3): Planned milestone work
- Decimal phases (2.1, 2.2): Urgent insertions (marked with INSERTED)

Decimal phases appear between their surrounding integers in numeric order.

- [ ] **Phase 1: Package Scaffolding & Install** - npm package structure, install script, Python venv, and reference patterns
- [ ] **Phase 2: Milestone Lifecycle & State** - Milestone creation, state tracking, status display, context file support
- [ ] **Phase 3: Strategy Specification** - Discuss, research, and plan commands that produce a formal backtest spec
- [x] **Phase 4: AI Backtest Loop** - Execute command with data sourcing, Claude-written backtest engine, and iterative optimization (completed 2026-03-21)
- [ ] **Phase 5: Verify & Export** - Interactive HTML report generation, approval flow, debug cycles, and export package

## Phase Details

### Phase 1: Package Scaffolding & Install
**Goal**: User can install the package and have a working foundation -- commands directory, Python venv, reference patterns, and templates all in place
**Depends on**: Nothing (first phase)
**Requirements**: INST-01, INST-02, INST-03, INST-04, INST-05, ARCH-01, ARCH-02, ARCH-03, ARCH-04, ARCH-05
**Success Criteria** (what must be TRUE):
  1. User runs `npx print-money-factory install` and sees slash commands appear in `~/.claude/commands/brrr/`
  2. Running install a second time completes without errors and does not corrupt the existing setup
  3. A Python venv exists at the expected path with pandas, numpy, ccxt, yfinance, plotly, ta, matplotlib, and optuna importable
  4. Running install on a machine without Python 3.10+ fails with a clear, actionable error message
  5. The package contains commands/, workflows/, templates/, references/ directories with a fixed metrics module that has unit tests passing
**Plans:** 3/4 plans executed

Plans:
- [x] 01-01-PLAN.md -- npm package scaffolding + install script (commands, package.json, bin/install.mjs, requirements.txt)
- [x] 01-02-PLAN.md -- Fixed metrics module with known-answer TDD tests (metrics.py, test_metrics.py)
- [x] 01-03-PLAN.md -- Reference patterns + templates + workflow stubs (backtest engine, data sources, PineScript, templates)
- [x] 01-04-PLAN.md -- Integration test: full install + human verification

### Phase 2: Milestone Lifecycle & State
**Goal**: User can create a milestone, track its progress, and provide context files that the system understands
**Depends on**: Phase 1
**Requirements**: MILE-01, MILE-02, MILE-03, MILE-04, MILE-05, STAT-01, STAT-02, STAT-03, STAT-04, STAT-05, CTXT-01, CTXT-02, CTXT-03
**Success Criteria** (what must be TRUE):
  1. User runs `/brrr:new-milestone`, walks through strategy idea and scope selection, and gets STRATEGY.md and STATE.md created in `.pmf/`
  2. User runs `/brrr:status` and sees an ASCII tree showing milestone name, phases, and next step
  3. Running a command out of sequence (e.g., `/brrr:execute` before plan) is refused with a clear message about what to run first
  4. Dropping an image or PDF into `.pmf/context/` causes the next command to describe what it sees and ask for confirmation before incorporating
  5. User cannot start a new milestone while one is active -- system tells them to approve or abandon the current one first
**Plans:** 2 plans

Plans:
- [x] 02-01-PLAN.md -- new-milestone workflow + template updates (guided scoping, context scan, state management)
- [x] 02-02-PLAN.md -- status workflow (ASCII tree display, best metrics, next step)

### Phase 3: Strategy Specification
**Goal**: User can go from a vague trading idea to a complete, formal backtest specification through guided conversation, optional research, and structured planning
**Depends on**: Phase 2
**Requirements**: DISC-01, DISC-02, DISC-03, DISC-04, DISC-05, DISC-06, RSCH-01, RSCH-02, RSCH-03, RSCH-04, RSCH-05, PLAN-01, PLAN-02, PLAN-03, PLAN-04, PLAN-05, PLAN-06, PLAN-07, PLAN-08
**Success Criteria** (what must be TRUE):
  1. User runs `/brrr:discuss` and the system collects all strategy decisions (entry/exit, stops, sizing, commissions, parameter ranges) through a guided conversation, outputting a `phase_N_discuss.md`
  2. User runs `/brrr:discuss --auto` and gets reasonable defaults chosen with minimal questions
  3. User runs `/brrr:research` and gets back known implementations, academic references, and warnings about lookahead traps specific to their strategy type, saved to `phase_N_research.md`
  4. User runs `/brrr:plan` and gets a complete parameter space definition, optimization method selection, evaluation criteria, data period, and train/test split, saved to `phase_N_plan.md`
  5. When a user drifts significantly from their original strategy during a debug discuss cycle, the system detects it and offers to open a new milestone instead
**Plans:** 3 plans

Plans:
- [x] 03-01-PLAN.md -- Discuss workflow (guided conversation, --auto mode, debug-discuss, drift detection)
- [x] 03-02-PLAN.md -- Research workflow (implementations, pitfalls, --deep mode, auto-recommendation)
- [x] 03-03-PLAN.md -- Plan workflow (parameter space, optimization method, evaluation criteria, train/test split)

### Phase 4: AI Backtest Loop
**Goal**: User runs one command and the system loads market data, writes a custom backtest engine, runs iterative optimization with AI analysis, and stops when targets are hit or the strategy is diagnosed as unviable
**Depends on**: Phase 3
**Requirements**: EXEC-01, EXEC-02, EXEC-03, EXEC-04, EXEC-05, EXEC-06, EXEC-07, EXEC-08, EXEC-09, EXEC-10, EXEC-11, EXEC-12, EXEC-13, EXEC-14, DATA-01, DATA-02, DATA-03, DATA-04, DATA-05
**Success Criteria** (what must be TRUE):
  1. User runs `/brrr:execute` and sees Claude write a Python backtest script from scratch, run it, read back metrics and an equity PNG, diagnose results, adjust parameters, and repeat -- all without manual intervention
  2. Each iteration produces saved artifacts (params JSON, metrics JSON, equity PNG, verdict JSON) that persist in the phase directory
  3. The loop stops automatically on one of four conditions: MINT (targets hit), PLATEAU (no improvement), REKT (no edge found), or NO DATA -- and the user sees which condition triggered
  4. In-sample and out-of-sample metrics are reported separately, and the system warns when they diverge significantly (overfitting signal)
  5. Data loads successfully from at least ccxt (crypto) and yfinance (stocks), with CSV fallback working for any asset, and data is validated for gaps/NaN before every backtest run
**Plans:** 2/2 plans complete

Plans:
- [x] 04-01-PLAN.md -- Fix data_sources.py yfinance bug + complete execute.md behavioral workflow
- [x] 04-02-PLAN.md -- End-to-end human verification of /brrr:execute

### Phase 5: Verify & Export
**Goal**: User gets a polished interactive report to evaluate the strategy, can approve it to generate a complete export package, or send it back for another debug cycle with AI diagnosis
**Depends on**: Phase 4
**Requirements**: VRFY-01, VRFY-02, VRFY-03, VRFY-04, VRFY-05, VRFY-06, VRFY-07, VRFY-08, VRFY-09, VRFY-10, VRFY-11, VRFY-12, EXPT-01, EXPT-02, EXPT-03, EXPT-04, EXPT-05, EXPT-06, EXPT-07
**Success Criteria** (what must be TRUE):
  1. User runs `/brrr:verify` and gets a standalone HTML file they can open in any browser, containing interactive equity curve, drawdown chart, trade list, iteration table, and metrics summary -- no server required
  2. The report includes regime breakdown (bull/bear/sideways performance) and benchmark comparison (alpha/beta vs buy-and-hold)
  3. User runs `/brrr:verify --approved` and gets an `output/` directory containing valid PineScript v5, trading-rules.md, performance-report.md, backtest_final.py, live-checklist.md, and the HTML report
  4. User runs `/brrr:verify --debug` and the system diagnoses what went wrong, opens a new phase cycle, and the next `/brrr:discuss` starts from the AI diagnosis rather than from scratch
  5. The PineScript export is a valid TradingView strategy that can be pasted directly into the Pine Editor
**Plans:** 1/3 plans executed

Plans:
- [x] 05-01-PLAN.md -- HTML report template extension + Python report generator (all 9 sections, regime/benchmark analytics)
- [ ] 05-02-PLAN.md -- Verify workflow + PineScript syntax reference (AI analysis, approval/debug flow, export package)
- [ ] 05-03-PLAN.md -- Install script update + end-to-end human verification

## Progress

**Execution Order:**
Phases execute in numeric order: 1 -> 2 -> 3 -> 4 -> 5

| Phase | Plans Complete | Status | Completed |
|-------|----------------|--------|-----------|
| 1. Package Scaffolding & Install | 4/4 | Complete |  |
| 2. Milestone Lifecycle & State | 2/2 | Complete | - |
| 3. Strategy Specification | 3/3 | Complete | - |
| 4. AI Backtest Loop | 2/2 | Complete   | 2026-03-21 |
| 5. Verify & Export | 1/3 | In Progress|  |
