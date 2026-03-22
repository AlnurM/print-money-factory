# Roadmap: Print Money Factory

## Milestones

- ✅ **v1.0 MVP** -- Phases 1-5 (shipped 2026-03-22)
- 🚧 **v1.1 Enhancement** -- Phases 6-10 (in progress)

## Phases

<details>
<summary>v1.0 MVP (Phases 1-5) -- SHIPPED 2026-03-22</summary>

- [x] Phase 1: Package Scaffolding & Install (4/4 plans) -- completed 2026-03-21
- [x] Phase 2: Milestone Lifecycle & State (2/2 plans) -- completed 2026-03-21
- [x] Phase 3: Strategy Specification (3/3 plans) -- completed 2026-03-21
- [x] Phase 4: AI Backtest Loop (2/2 plans) -- completed 2026-03-21
- [x] Phase 5: Verify & Export (3/3 plans) -- completed 2026-03-22

</details>

### v1.1 Enhancement (In Progress)

**Milestone Goal:** Polish the existing pipeline with smarter optimization, better debug cycles, maintenance tooling, and bug fixes.

- [ ] **Phase 6: Equity PNG Bug Fix** - Fix blank equity curve PNGs during execute iterations
- [ ] **Phase 7: Maintenance Tooling** - Diagnostic command and automatic version checking
- [ ] **Phase 8: Debug Cycle Memory** - Structured failed-approach tracking across debug iterations
- [ ] **Phase 9: Bayesian Optimization** - Optuna TPE/CMA-ES integration with Ask-and-Tell API
- [ ] **Phase 10: Enhanced Export** - Bot-building guide for going live after strategy approval

## Phase Details

### Phase 6: Equity PNG Bug Fix
**Goal**: Users see actual equity curve data in every execute iteration PNG
**Depends on**: Phase 5 (v1.0 complete)
**Requirements**: BFIX-01
**Success Criteria** (what must be TRUE):
  1. Running `/brrr:execute` produces a PNG with a visible equity curve line when the backtest generates trades
  2. When a backtest iteration produces zero trades, the PNG is skipped gracefully with a logged warning instead of a blank image
  3. PNG file size is consistently above 5KB when trades exist (not a blank canvas)
**Plans**: 1 plan

Plans:
- [x] 06-01-PLAN.md -- Return trades/equity_curve from run_backtest() and fix execute.md PNG generation

### Phase 7: Maintenance Tooling
**Goal**: Users can diagnose installation health and know when updates are available
**Depends on**: Phase 6
**Requirements**: MANT-01, MANT-02
**Success Criteria** (what must be TRUE):
  1. Running `/brrr:doctor` displays pass/fail results for Python version, venv health, dependency imports, and command file integrity
  2. Doctor checks actual package imports inside the venv (e.g., `python -c "import optuna"`), not just directory existence
  3. Running any `/brrr:*` command shows an update notice when a newer npm version is available (checked once per 24h session, silent on network failure)
  4. The version check never blocks or delays command execution
**Plans**: 2 plans

Plans:
- [ ] 07-01-PLAN.md -- Create /brrr:doctor diagnostic command and workflow
- [ ] 07-02-PLAN.md -- Add version check preamble to all workflows

### Phase 8: Debug Cycle Memory
**Goal**: Debug cycles carry forward knowledge of failed approaches so the AI never retries what already failed
**Depends on**: Phase 7
**Requirements**: DBUG-01, DBUG-02, DBUG-03
**Success Criteria** (what must be TRUE):
  1. After `/brrr:verify --debug`, a structured diagnosis artifact exists listing failed parameter regions and explicit "do NOT retry" entries
  2. Running `/brrr:discuss` in debug mode displays all prior failed approaches as context before gathering new decisions
  3. Debug memory is scoped per-phase (Phase 3 failures do not leak into Phase 4 context)
  4. Debug memory stays under 50 entries regardless of how many debug iterations occur
**Plans**: TBD

Plans:
- [ ] 08-01: TBD
- [ ] 08-02: TBD

### Phase 9: Bayesian Optimization
**Goal**: Users can run Optuna-powered Bayesian parameter optimization that outperforms random/grid search on large parameter spaces
**Depends on**: Phase 6 (equity PNGs working), Phase 8 (debug memory for failed Bayesian iterations)
**Requirements**: OPT-01, OPT-02, OPT-03, OPT-04
**Success Criteria** (what must be TRUE):
  1. Running `/brrr:execute` with Bayesian method uses Optuna TPE sampler via Ask-and-Tell API while preserving per-iteration artifacts (PNGs, verdicts, AI analysis)
  2. When all parameters are continuous, the system auto-selects CMA-ES sampler; otherwise TPE
  3. Interrupting and resuming with `--resume` loads the persisted SQLite study and continues from the existing probability model (no warmup restart)
  4. `/brrr:plan` offers Bayesian as an optimization method and auto-recommends it when parameter space exceeds 500 combinations
  5. Each iteration displays whether it is in "warmup" (random) or "guided" (Bayesian) mode
**Plans**: TBD

Plans:
- [ ] 09-01: TBD
- [ ] 09-02: TBD
- [ ] 09-03: TBD

### Phase 10: Enhanced Export
**Goal**: Approved strategies include a step-by-step guide for deploying to live trading
**Depends on**: Phase 9
**Requirements**: EXPT-08
**Success Criteria** (what must be TRUE):
  1. Running `/brrr:verify --approved` generates a `bot-building-guide.md` alongside the existing export files
  2. The guide contains platform-specific instructions detected from the strategy's asset class (crypto exchanges for crypto, broker APIs for stocks, MT5/OANDA for forex)
  3. The guide is only generated on `--approved`, never during `--debug` cycles
**Plans**: TBD

Plans:
- [ ] 10-01: TBD

## Progress

**Execution Order:**
Phases execute in numeric order: 6 -> 7 -> 8 -> 9 -> 10

| Phase | Milestone | Plans Complete | Status | Completed |
|-------|-----------|----------------|--------|-----------|
| 1. Package Scaffolding & Install | v1.0 | 4/4 | Complete | 2026-03-21 |
| 2. Milestone Lifecycle & State | v1.0 | 2/2 | Complete | 2026-03-21 |
| 3. Strategy Specification | v1.0 | 3/3 | Complete | 2026-03-21 |
| 4. AI Backtest Loop | v1.0 | 2/2 | Complete | 2026-03-21 |
| 5. Verify & Export | v1.0 | 3/3 | Complete | 2026-03-22 |
| 6. Equity PNG Bug Fix | v1.1 | 0/1 | Planning | - |
| 7. Maintenance Tooling | v1.1 | 0/2 | Planning | - |
| 8. Debug Cycle Memory | v1.1 | 0/? | Not started | - |
| 9. Bayesian Optimization | v1.1 | 0/? | Not started | - |
| 10. Enhanced Export | v1.1 | 0/? | Not started | - |

---
*Roadmap created: 2026-03-22*
*v1.0 details archived to `.planning/milestones/v1.0-ROADMAP.md`*
