---
phase: 03-strategy-specification
verified: 2026-03-21T00:00:00Z
status: passed
score: 5/5 success criteria verified
re_verification: false
---

# Phase 3: Strategy Specification Verification Report

**Phase Goal:** User can go from a vague trading idea to a complete, formal backtest specification through guided conversation, optional research, and structured planning
**Verified:** 2026-03-21
**Status:** PASSED
**Re-verification:** No — initial verification

---

## Goal Achievement

### Observable Truths (from ROADMAP.md Success Criteria)

| # | Truth | Status | Evidence |
|---|-------|--------|----------|
| 1 | User runs `/brrr:discuss` and the system collects all strategy decisions through guided conversation, outputting `phase_N_discuss.md` | VERIFIED | `workflows/discuss.md` — 512 lines; covers all 7 decision topics (entry, exit, stop-loss, TP, sizing, commissions, parameters); Step 4 writes `phase_N_discuss.md`; footer: `DISC-01, DISC-02, DISC-03, DISC-04, DISC-05, DISC-06` |
| 2 | User runs `/brrr:discuss --auto` and gets reasonable defaults with minimal questions | VERIFIED | Mode detection preamble (line 115) checks `--auto` flag; Step 2-alt (line 219) applies type-specific defaults for trend-following, mean-reversion, breakout, custom with ONE confirmation question |
| 3 | User runs `/brrr:research` and gets known implementations, academic references, and lookahead trap warnings, saved to `phase_N_research.md` | VERIFIED | `workflows/research.md` — 411 lines; Step 3 covers training-data research; Step 4 cross-references all 6 pitfalls with HIGH/MEDIUM/LOW ratings; Step 5 adds web search via WebFetch; Step 7 writes `phase_N_research.md` |
| 4 | User runs `/brrr:plan` and gets a complete parameter space, optimization method, evaluation criteria, data period, and train/test split, saved to `phase_N_plan.md` | VERIFIED | `workflows/plan.md` — 532 lines; Step 2 defines parameter space; Step 3 checks parameter budget; Step 4 auto-selects grid/random/walk-forward; Step 5 defines evaluation criteria with Sharpe primary; Step 6 sets data period + train/test split; Step 8 writes `phase_N_plan.md` |
| 5 | When a user drifts significantly from their original strategy in debug discuss, the system detects it and offers to open a new milestone | VERIFIED | `workflows/discuss.md` lines 328-353: HARD GATE quotes original hypothesis, lists drift changes, forces binary choice — option 1 (stay in scope) or option 2 (`/brrr:new-milestone`); explicit "Cannot continue until you choose" with no bypass path |

**Score:** 5/5 truths verified

---

### Required Artifacts

| Artifact | Expected | Actual Lines | Min Required | Status | Details |
|----------|----------|-------------|-------------|--------|---------|
| `workflows/discuss.md` | Complete behavioral workflow for /brrr:discuss | 512 | 250 | VERIFIED | 3 preambles + 6 steps; all 3 modes (first-discuss, auto, debug-discuss); drift detection hard gate; outputs phase_N_discuss.md |
| `workflows/research.md` | Complete behavioral workflow for /brrr:research | 411 | 150 | VERIFIED | 2 preambles + 9 steps; pitfall cross-reference; --deep mode; auto-recommendation; outputs phase_N_research.md |
| `workflows/plan.md` | Complete behavioral workflow for /brrr:plan | 532 | 200 | VERIFIED | 2 preambles + 10 steps; parameter space + budget + method selection + evaluation + train/test; outputs phase_N_plan.md |

All three artifacts are substantive (well over minimum line counts, contain no stub patterns, no TODO/FIXME/PLACEHOLDER comments found).

---

### Key Link Verification

| From | To | Via | Status | Evidence |
|------|-----|-----|--------|---------|
| `workflows/discuss.md` | `.pmf/STRATEGY.md` | Read tool at workflow start | WIRED | Lines 139-154: reads STRATEGY.md, extracts hypothesis, strategy type, asset, scope, success criteria, original idea; quotes hypothesis to user |
| `workflows/discuss.md` | `.pmf/STATE.md` | Read for sequence validation, Write for step update | WIRED | Preamble reads STATE.md (10 refs total); Step 5 writes updated STATE.md with discuss completion |
| `workflows/discuss.md` | `.pmf/phases/phase_N_discuss.md` | Write tool at workflow end | WIRED | Step 4 (line 394) writes structured artifact; Step 6 confirms artifact path |
| `workflows/research.md` | `.pmf/phases/phase_N_discuss.md` | Read tool to understand strategy decisions | WIRED | Line 28 checks file existence fallback; line 96 reads discuss artifact in Step 1 |
| `workflows/research.md` | `.pmf/STATE.md` | Read for validation, Write for step update | WIRED | Preamble reads STATE.md; Step 8 writes completion |
| `workflows/research.md` | `references/common-pitfalls.md` | Read tool for cross-referencing | WIRED | Step 4 explicitly cross-references all 6 pitfalls from common-pitfalls.md with strategy-specific risk ratings |
| `workflows/plan.md` | `.pmf/phases/phase_N_discuss.md` | Read tool to get parameter ranges | WIRED | Line 69: Step 1 reads discuss artifact; line 106 builds parameter space from it |
| `workflows/plan.md` | `.pmf/phases/phase_N_research.md` | Read tool (if exists) | WIRED | Line 75: Step 1 checks if research artifact exists and loads it conditionally; research optional is correctly handled |
| `workflows/plan.md` | `.pmf/STATE.md` | Read for validation, Write for step update | WIRED | Preamble reads STATE.md; Step 9 writes completion |
| `workflows/plan.md` | `references/backtest-engine.md` | Read to ensure engine constraints respected | WIRED | Line 82: Step 1 reads backtest-engine.md for anti-lookahead rules and execution model |
| `commands/discuss.md` | `workflows/discuss.md` | @-reference | WIRED | Line 17 of commands/discuss.md: `@~/.pmf/workflows/discuss.md` |
| `commands/research.md` | `workflows/research.md` | @-reference | WIRED | Line 18 of commands/research.md: `@~/.pmf/workflows/research.md` |
| `commands/plan.md` | `workflows/plan.md` | @-reference | WIRED | Line 16 of commands/plan.md: `@~/.pmf/workflows/plan.md` |

---

### Requirements Coverage

| Requirement | Source Plan | Description | Status | Evidence |
|-------------|------------|-------------|--------|---------|
| DISC-01 | 03-01-PLAN.md | `/brrr:discuss` collects entry/exit, stops, TP, sizing, commissions, parameter ranges | SATISFIED | discuss.md covers all 7 topics in first-discuss mode; DISC-01 in footer |
| DISC-02 | 03-01-PLAN.md | First discuss builds strategy spec via guided conversation | SATISFIED | Step 2 (line 174): follow-the-thread conversation starting open, tracks 7 topics, fills gaps |
| DISC-03 | 03-01-PLAN.md | Debug discuss starts from AI diagnosis, reads full milestone context | SATISFIED | Step 2-debug (line 292): loads all prior phase artifacts, formulates diagnosis, presents suggested changes |
| DISC-04 | 03-01-PLAN.md | Drift detection — detects changes exceeding original strategy scope | SATISFIED | Lines 328-353: hard gate with >50% threshold, quotes original hypothesis, binary choice only |
| DISC-05 | 03-01-PLAN.md | `--auto` flag lets Claude choose reasonable defaults | SATISFIED | Mode detection preamble + Step 2-alt: type-specific defaults, one confirmation question |
| DISC-06 | 03-01-PLAN.md | Outputs `phase_N_discuss.md` with all decisions fixed | SATISFIED | Step 4 writes structured artifact with all 7 decision sections |
| RSCH-01 | 03-02-PLAN.md | `/brrr:research` finds known implementations, academic work, formalization alternatives | SATISFIED | Step 3 covers training-data research (implementations, academic, common params, failure modes, alternatives); Step 6 compiles findings |
| RSCH-02 | 03-02-PLAN.md | Warns about known lookahead traps specific to strategy type | SATISFIED | Step 4: cross-references all 6 pitfalls from common-pitfalls.md with strategy-specific risk ratings and "Lookahead Trap Warnings" section in artifact |
| RSCH-03 | 03-02-PLAN.md | Recommends when research is needed vs optional | SATISFIED | Step 2 (line 110): auto-recommends based on complexity criteria (non-standard = recommended, classic = optional) |
| RSCH-04 | 03-02-PLAN.md | `--deep` flag for extended search across multiple sources | SATISFIED | Step 5: --deep mode searches 3-5 sources with per-source reliability rating via WebFetch |
| RSCH-05 | 03-02-PLAN.md | Outputs `phase_N_research.md` | SATISFIED | Step 7 writes structured artifact with implementations, references, pitfall table, lookahead warnings, sources |
| PLAN-01 | 03-03-PLAN.md | `/brrr:plan` defines parameter space — fixed and free params with ranges and step sizes | SATISFIED | Step 2 builds complete parameter space from discuss output with range, step, type, combinations for each param |
| PLAN-02 | 03-03-PLAN.md | Defines constraints between parameters | SATISFIED | Step 2 detects obvious constraints (fast < slow, TP > stop, lookback minimums) and asks for additional ones |
| PLAN-03 | 03-03-PLAN.md | Selects optimization method: grid, random, walk-forward | SATISFIED | Step 4: auto-selects based on combination count (<1000 grid, 1000-10000 random, 3+ params = walk-forward); user override allowed |
| PLAN-04 | 03-03-PLAN.md | Sets evaluation criteria: Sharpe primary, secondary metrics | SATISFIED | Step 5: Sharpe as primary metric, Max Drawdown, Win Rate, Profit Factor, Expectancy as secondary |
| PLAN-05 | 03-03-PLAN.md | Enforces minimum trade count threshold (default 30) | SATISFIED | Step 5: default 30 minimum trades with explanation; iterations below threshold discarded |
| PLAN-06 | 03-03-PLAN.md | Defines data period, timeframe, and train/test split | SATISFIED | Step 6: reads asset/timeframe/date range from STRATEGY.md; 70%/30% chronological default; walk-forward window config |
| PLAN-07 | 03-03-PLAN.md | Enforces parameter budget to prevent overfitting | SATISFIED | Step 3: 3 warning thresholds (>5 free params, combos > 100x min trades, combos > 10000); warns but allows override per D-13 |
| PLAN-08 | 03-03-PLAN.md | Outputs `phase_N_plan.md` | SATISFIED | Step 8 writes complete artifact with parameter space, optimization method, evaluation criteria, data config, parameter budget |

All 18 requirements covered across 3 plans. No orphaned requirements found — REQUIREMENTS.md maps exactly DISC-01..06, RSCH-01..05, PLAN-01..08 to Phase 3, all accounted for.

---

### Anti-Patterns Found

| File | Pattern | Severity | Impact |
|------|---------|----------|--------|
| (none) | — | — | — |

No TODO, FIXME, PLACEHOLDER, stub, or empty-implementation patterns found in any of the three workflow files.

---

### Human Verification Required

#### 1. Discuss Conversation Flow Quality

**Test:** Run `/brrr:discuss` with a vague strategy idea (e.g., "I want to trade moving average crossovers")
**Expected:** Claude asks a follow-the-thread opening question, naturally covers all 7 topics through conversation (not a checklist interrogation), and produces a well-organized `phase_1_discuss.md`
**Why human:** Conversation quality, naturalness of follow-the-thread approach, and whether the 7-topic coverage feels organic vs mechanical cannot be verified from the workflow file alone

#### 2. Drift Detection Sensitivity

**Test:** Run `/brrr:discuss` in debug mode and propose changes that cross the >50% threshold vs changes that are clearly minor tweaks
**Expected:** Minor tweaks (adjusting stop % from 2% to 2.5%) proceed without triggering the gate; major changes (completely different indicator set) trigger the `[DRIFT DETECTED]` hard gate
**Why human:** The >50% threshold is a behavioral judgment call that Claude must make from context — cannot verify the calibration programmatically

#### 3. Research Recommendation Accuracy

**Test:** Run `/brrr:research` on (a) a classic SMA crossover strategy and (b) a custom multi-signal strategy
**Expected:** SMA crossover gets "Research is optional — this is a well-understood classic strategy"; multi-signal gets "Research is recommended — your strategy combines multiple non-standard signals"
**Why human:** The recommendation logic evaluates strategy complexity from discuss output — quality of classification requires runtime behavior check

#### 4. Parameter Budget Warning Readability

**Test:** Run `/brrr:plan` with 6 free parameters spanning a large range
**Expected:** Clear warning explaining overfitting risk with specific numbers (free params count, combinations count, data bars estimate), followed by a clear "Continue or modify?" prompt
**Why human:** The warning content is generated at runtime from actual parameter values — readability and actionability of the warning needs live testing

---

### Gaps Summary

No gaps. All 5 success criteria from ROADMAP.md are fully implemented and verified. All 18 requirements (DISC-01..06, RSCH-01..05, PLAN-01..08) are satisfied by substantive, wired workflow artifacts.

The three workflow files collectively form a complete pipeline:
- `discuss.md` (512 lines) — guided conversation collecting all strategy decisions, with --auto and debug-discuss modes and drift protection
- `research.md` (411 lines) — training-data-first research with pitfall cross-reference, --deep web search, and auto-recommendation
- `plan.md` (532 lines) — parameter space design, optimization method selection, parameter budget, evaluation criteria, and train/test split

All three are referenced by their respective command files (`commands/discuss.md`, `commands/research.md`, `commands/plan.md`) via @-references that will load them when the slash commands are invoked. All three read prior artifacts (STRATEGY.md, STATE.md, discuss/research output) and write to STATE.md on completion.

---

_Verified: 2026-03-21_
_Verifier: Claude (gsd-verifier)_
