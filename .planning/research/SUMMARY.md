# Project Research Summary

**Project:** Print Money Factory v1.1 Enhancement
**Domain:** AI-assisted trading strategy development CLI — backtest-to-export pipeline
**Researched:** 2026-03-22
**Confidence:** HIGH

## Executive Summary

Print Money Factory v1.1 is a workflow-and-pattern milestone, not a stack milestone. Every feature in scope can be built with the libraries already installed: Optuna is in requirements.txt but unused, Jinja2 is installed for HTML reports and will serve the new MD export, and matplotlib Agg is already used for iteration PNGs. The stack decision is settled — zero new Python or npm dependencies are needed. This frees the entire development effort for workflow design, integration logic, and bug repair rather than dependency management.

The six v1.1 features split into two categories: one bug fix (blank equity PNG) and five additive enhancements (Bayesian optimization, debug cycle memory, doctor command, auto version check, enhanced export). Architecture research confirms a clear build order grounded in dependencies and risk: fix the bug first (smallest change surface, unblocks visual feedback for all other features), add independent tooling (doctor, version check), improve the debug loop (debug memory), then integrate Bayesian optimization using Optuna's Ask-and-Tell API so the per-iteration architecture stays intact. Enhanced export lands last as a purely additive verify step.

The critical risk across all features is integration pattern fidelity. Optuna must use Ask-and-Tell (not `study.optimize()`) to preserve per-iteration artifacts. Debug memory must be a fixed-size summary table (not an append log) to avoid context explosion. The doctor command must check actual package imports inside the venv, not just that the venv directory exists. Optuna's SQLite study persistence must be part of the initial integration, not an afterthought — in-memory studies lose the TPE model on `--resume`, wasting all warmup iterations. Each of these has a clearly documented "looks done but isn't" failure mode that must appear explicitly in each phase's acceptance criteria.

---

## Key Findings

### Recommended Stack

No new dependencies. See `.planning/research/STACK.md` for full analysis.

**Core technologies (all existing):**
- `optuna>=4.7,<5` (4.8.0 stable): Bayesian optimization via TPESampler — already installed, currently unused
- `matplotlib>=3.10,<4` (Agg backend): iteration equity PNGs — correct choice, headless, no Chrome dep
- `jinja2>=3.1,<4`: enhanced export MD template — same engine already used for HTML report
- `tabulate>=0.9,<1`: doctor command output formatting — already installed
- `npm view` CLI: version check — no HTTP client code needed, zero new packages

**Critical version note:** Optuna 4.8.0 is current stable and within the `>=4.7,<5` pin. TPESampler's `multivariate=True` mode (available in 4.7+) is required for trading parameters because fast_period and slow_period are correlated — independent sampling produces worse suggestions than joint sampling.

**What NOT to add:**
- `optuna-dashboard` — requires server, violates CLI-only constraint
- `SQLAlchemy` — Optuna's SQLite storage works without it
- `kaleido` — v1.0 requires Chrome; matplotlib Agg is the right choice for iteration PNGs
- `semver` npm package — version comparison for "0.4.0" vs "0.5.0" is trivial string logic

### Expected Features

See `.planning/research/FEATURES.md` for full feature table with complexity and dependency analysis.

**Must have (table stakes for v1.1):**
- Fix blank equity PNG — broken in v1.0, users see nothing during optimization; zero-dependency fix
- Optuna TPE integration with Ask-and-Tell in execute loop — the headline feature; replaces AI-only parameter selection with AI-guided Bayesian search
- `/brrr:doctor` diagnostic command — standard in mature CLI tooling (homebrew doctor, flutter doctor); low effort, high trust signal
- Failed approach registry (debug memory) — current debug cycles "forget" prior attempts; prevents circular optimization

**Should have (significantly improves the release):**
- Auto version check (once per 24h, silent on failure) — trivial to implement, prevents stale installs
- MD-instruction bot-building guide export — bridges the backtest-to-live gap that every competitor ignores
- Cross-phase metric trajectory — reveals whether debug cycles are converging or stalling
- Optuna study SQLite persistence for `--resume` support — must be part of initial Bayesian integration, not added later

**Defer to v2+:**
- Full multi-objective Optuna (Pareto front) — requires redesigning plan and verify workflows
- Optuna dashboard web UI — violates the no-server constraint
- Platform-specific bot-building guide sections (per-exchange code) — high effort, narrow audience per section
- Automatic strategy generation from Optuna — produces overfitted garbage without human hypothesis guiding it

### Architecture Approach

v1.1 integrates six features into the existing npm package without changing the core command/workflow/references/templates contract. The thin-command-refs-workflow pattern is preserved throughout. See `.planning/research/ARCHITECTURE.md` for full component-level integration maps with file and line references.

**Major components and what changes:**

1. `references/backtest_engine.py` — 3-line fix: `run_backtest()` must include `trades` and `equity_curve` keys in its return dict; these keys currently exist in `compute_all_metrics()` inputs but are not passed through to the return value
2. `references/optuna_bridge.py` (NEW, ~80 lines) — thin wrapper managing Optuna study lifecycle: create/load SQLite study, Ask-and-Tell interface (`study.ask()` / `study.tell()`), parameter suggestion from plan-defined param_space
3. `workflows/execute.md` — modified for Bayesian code path (Steps 4, 5a, 5f); Step 5e reads `phase_N_debug_memory.md`; equity PNG code uses `results['equity_curve']` directly instead of reconstructing from trades
4. `workflows/plan.md` — adds `bayesian` as 4th optimization method with auto-selection rule: 3+ free params AND >500 combos
5. `workflows/verify.md` — appends to `phase_N_debug_memory.md` on debug verdict; adds Step 5a.9 for `bot-building-guide.md` generation on `--approved`
6. `workflows/discuss.md` — reads `phase_N_debug_memory.md` first in debug mode before reading individual phase artifacts
7. `commands/doctor.md` + `workflows/doctor.md` (NEW) — new command/workflow pair, read-only health checks
8. `bin/install.mjs` — writes `.pmf/.version` file for version check
9. `workflows/status.md` — version check preamble (here and in doctor.md only; not all 8 workflows)

**New runtime artifacts:**
- `.pmf/phases/phase_N_execute/optuna_study.db` — SQLite Optuna study per phase
- `.pmf/phases/phase_N_debug_memory.md` — phase-scoped failed approach registry (NOT global)
- `.pmf/output/bot-building-guide.md` — generated on `--approved`
- `.pmf/.version` — installed version string for update check
- `.pmf/.last_version_check` — 24h sentinel file to rate-limit npm registry calls

**Critical architectural constraint:** Debug memory MUST be phase-scoped (`phase_N_debug_memory.md`), not global. A global file leaks strategy-level context across phase boundaries — Phase 3's RSI mean-reversion should not be influenced by Phase 1's SMA crossover failures.

### Critical Pitfalls

See `.planning/research/PITFALLS.md` for full catalog with recovery strategies and "looks done but isn't" checklist.

1. **Optuna replaces the iteration loop** — if `study.optimize(objective, n_trials=N)` is called directly, all per-iteration infrastructure (equity PNGs, verdict JSONs, AI analysis, `--resume`, stop conditions) is bypassed. Use Ask-and-Tell: `trial = study.ask()` before backtest, `study.tell(trial, value)` after. Highest-severity integration risk; recovery cost is HIGH (rewrite execute workflow Step 5).

2. **Debug memory context explosion** — appending full error traces creates 2,200+ lines of context by iteration 20. Cap the memory file at 50 lines using a structured summary table (`| Iter | Params Tried | Result | Why Failed |`), not a verbose append log.

3. **Equity PNG blank due to wrong data source** — `run_backtest()` does not include `trades` or `equity_curve` in its return dict currently; the execute workflow's `results_is.get('trades', [])` always returns `[]`. Fix requires 3 lines in `backtest_engine.py` plus updating the execute workflow template to use `equity_curve` directly.

4. **Optuna study lost on `--resume`** — in-memory studies lose the TPE probability model on interruption; resumed optimization restarts the warmup phase, wasting up to 10 previously completed iterations. Use `storage="sqlite:///.pmf/phases/phase_N_execute/optuna_study.db"` from the start.

5. **TPE warmup wastes all iterations** — TPE needs `n_startup_trials` (default 10) random trials before guided sampling begins. With the current default of 10 max iterations, every trial is random. Enforce minimum 20 iterations when Bayesian is selected; display "warmup" vs "guided" mode per iteration so users can see Bayesian is working.

---

## Implications for Roadmap

Based on combined research, the dependency graph and risk profile dictate a 5-phase build order.

### Phase 1: Equity PNG Bug Fix

**Rationale:** Smallest change surface (3 lines in backtest_engine.py, ~15 lines in execute.md template), zero new files, unblocks the visual feedback mechanism that Bayesian optimization and AI analysis depend on. Fix bugs before adding features.
**Delivers:** Working equity curve PNGs in every execute iteration with graceful skip when trades are absent.
**Addresses:** "Fix blank equity PNG" (must-have table stakes) from FEATURES.md.
**Avoids:** Pitfall 3 (blank PNG from wrong data source). Acceptance criteria: PNG file size >5KB when trades > 0; graceful skip with logged warning when trades = 0.
**Research flag:** None needed. Root cause confirmed via codebase analysis at line level. Pattern is documented.

### Phase 2: /brrr:doctor + Auto Version Check

**Rationale:** Both features are independent and additive (no modifications to existing files for doctor; minimal changes for version check). Adding diagnostic tooling before the more complex Optuna and debug-memory phases gives a safety net for catching integration issues during development. Doctor alone justifies the phase — it surfaces the most common silent failure mode (corrupt or outdated venv).
**Delivers:** `commands/doctor.md` + `workflows/doctor.md` with 9 health checks (Python version, venv activation, package imports, reference files, template files, workflow files, disk space, milestone status, dep versions vs requirements.txt). Silent version check in `status.md` and `doctor.md` preambles.
**Addresses:** Diagnostic/maintenance table stakes from FEATURES.md.
**Avoids:** Pitfall 7 (doctor too shallow — must test actual imports via `python -c "import optuna"`, not just venv directory existence). Pitfall 8 (version check latency — 24h cache via `.pmf/.last_version_check`, silent offline failure, never blocks execution).
**Research flag:** None needed. Standard CLI diagnostic pattern.

### Phase 3: Smarter Debug Cycles (Failed Approach Memory)

**Rationale:** Improves the core debug loop that already exists in v1.0. Should land before Bayesian optimization because Bayesian iterations may generate more debug cycles, and the memory mechanism needs to be in place to benefit from them. All changes are additive (append/read behavior added to existing workflows).
**Delivers:** Phase-scoped `phase_N_debug_memory.md` written by verify.md on debug verdict, read by discuss.md first in debug mode. Fixed-size summary table capped at 50 entries. AI analysis in execute.md Step 5e references memory before proposing parameter changes.
**Addresses:** "Failed approach registry" and "automatic phase budget warning" from FEATURES.md.
**Avoids:** Pitfall 4 (context explosion — summary table, not verbose log). Pitfall 10 (cross-phase memory leak — phase-scoped files, not a global `DEBUG_MEMORY.md`).
**Research flag:** None needed. Data structure is settled; changes are additive file operations.

### Phase 4: Bayesian Optimization (Optuna Integration)

**Rationale:** Depends on Phase 1 (equity PNG must work for AI visual analysis to have value), benefits from Phase 2 (doctor diagnoses optuna import issues), benefits from Phase 3 (debug memory reduces circular optimization if Bayesian iterations trigger debug cycles). Highest-complexity phase — modifies the core optimization loop and introduces a new Python module.
**Delivers:** `references/optuna_bridge.py`, bayesian method in plan.md auto-selection (3+ params OR >500 combos), Ask-and-Tell integration in execute.md Steps 4/5a/5f, SQLite study persistence for `--resume` compatibility, warmup/guided mode display per iteration.
**Addresses:** "Optuna TPE integration" (must-have) and "Optuna study persistence" (should-have) from FEATURES.md.
**Avoids:** Pitfall 1 (must use Ask-and-Tell, not `study.optimize()`). Pitfall 2 (enforce min 20 iterations for Bayesian, display warmup/guided mode). Pitfall 5 (SQLite persistence from day one). Pitfall 9 (composite objective function: `sharpe - penalty * max(0, |drawdown| - target)` instead of multi-objective Pareto, which would require redesigning plan and verify workflows).
**Research flag:** NEEDS deeper planning research. Verify the Ask-and-Tell sequence with SQLite-backed studies on `--resume`. Confirm that `study.ask()` on a loaded study correctly uses the persisted TPE model. Validate optuna_bridge.py constraint handling (fast_period < slow_period) against Optuna 4.8 docs — reporting `float('-inf')` for invalid combos may distort the TPE probability model; Optuna's native constraint API may be preferable. Reference: https://optuna.readthedocs.io/en/stable/tutorial/20_recipes/009_ask_and_tell.html

### Phase 5: Enhanced Export (Bot-Building Guide)

**Rationale:** Purely additive — new Step 5a.9 in verify.md's `--approved` path. Does not block or interact with any other v1.1 feature. Appropriate as the final phase: no dependencies on Phase 1-4 beyond verify.md existing.
**Delivers:** `bot-building-guide.md` in `.pmf/output/`, platform-detected based on asset class from STRATEGY.md (ccxt for crypto, broker API for stocks, MT5/OANDA for forex). Canonical `strategy_definition.json` as single source of truth to prevent format drift across export files.
**Addresses:** "MD-instruction bot-building guide" (should-have differentiator) from FEATURES.md.
**Avoids:** Pitfall 6 (export format drift — canonical `strategy_definition.json` drives all 7 export formats so entry/exit conditions are identical across PineScript, Python, and the new guide). Bot guide generated only on `--approved`, never during debug cycles.
**Research flag:** None needed. Template-based markdown generation is a Claude-native task. The canonical JSON structure may need one planning iteration to define the schema.

### Phase Ordering Rationale

- **Bug before features:** Phase 1 eliminates broken visual feedback before building features that depend on it (AI equity analysis in Bayesian mode depends on PNGs being non-blank).
- **Independent tooling before complex integrations:** Phase 2 adds a diagnostic safety net before modifying the core optimization loop in Phase 4. If Phase 4 introduces issues, doctor helps surface them.
- **Debug loop before Bayesian:** Phase 3 improves the fallback path (debug cycles) before Phase 4 potentially triggers more of them.
- **Export last:** Phase 5 is purely additive and lowest risk. It is the natural milestone cap.
- **No new dependencies across all 5 phases:** Eliminates an entire class of integration risk.

### Research Flags

Phases needing deeper research during planning:
- **Phase 4 (Bayesian Optimization):** Verify Ask-and-Tell sequence with SQLite-backed study on `--resume`. Confirm `study.ask()` on a loaded study uses the persisted TPE model. Validate constraint handling approach (invalid param combos). Review Optuna 4.8 Ask-and-Tell recipe before writing optuna_bridge.py.

Phases with standard patterns (skip research-phase):
- **Phase 1 (Equity PNG):** Root cause confirmed at line level. Fix pattern is documented in matplotlib guides.
- **Phase 2 (Doctor + Version Check):** Standard CLI tooling patterns. Well-documented across multiple ecosystems (homebrew, flutter, npm).
- **Phase 3 (Debug Memory):** Data structure design is settled. Changes are additive markdown file operations.
- **Phase 5 (Enhanced Export):** Template generation task with no novel integration points.

---

## Confidence Assessment

| Area | Confidence | Notes |
|------|------------|-------|
| Stack | HIGH | Zero new dependencies confirmed. All existing packages verified against current stable versions (Optuna 4.8.0, matplotlib 3.10.8, plotly 6.5.2). No version bumps needed. requirements.txt and package.json require only a version bump. |
| Features | HIGH | Priority order backed by multiple sources (Optuna docs, trading tool patterns, codebase analysis). Must-have vs should-have vs defer boundaries are clear. |
| Architecture | HIGH | Integration maps derived from direct codebase analysis: execute.md (1067 lines), backtest_engine.py (241 lines), metrics.py, verify.md, discuss.md. Root cause of equity PNG bug confirmed at line level (metrics.py return dict does not include raw trades or equity_curve). |
| Pitfalls | HIGH | Critical pitfalls verified via official Optuna docs (Ask-and-Tell recipe), matplotlib blank PNG documentation, and direct codebase analysis. Recovery strategies are concrete, not theoretical. |

**Overall confidence:** HIGH

### Gaps to Address

- **Composite objective function penalty weight:** PITFALLS.md recommends `sharpe - 2*drawdown_penalty` but flags the constant "2" as arbitrary. During Phase 4 planning, decide whether to make the penalty weight user-configurable via the plan artifact or hardcode it with an explicit "tune this" comment.

- **optuna_bridge.py constraint handling:** Trading parameters often have constraints (fast_period < slow_period). The current design returns `float('-inf')` for invalid combos. Verify this is compatible with TPE's internal model — many negative-infinity objectives may distort the probability model. Optuna's native constraint API (`study.tell(trial, values, constraint_values)`) may be preferable. Validate before implementation.

- **Doctor `--fix` flag scope:** Research agrees doctor should be diagnose-only in v1.1, with `--fix` deferred. If scope pressure forces a choice, drop `--fix` entirely — auto-repairing venvs risks breaking the user's setup worse than the original problem.

- **Version check placement:** Architecture research recommends adding the version check preamble only to `status.md` and `doctor.md` (not all 8 workflows) to reduce maintenance burden. This is the right call but should be made explicit in the Phase 2 plan to prevent the temptation to add it everywhere.

- **strategy_definition.json schema:** Phase 5 introduces a canonical JSON as single source of truth for all export formats. The schema needs to be defined before templating any of the 7 export formats in the bot-building guide. A one-iteration planning step to define required fields (entry conditions, exit conditions, parameters, indicator definitions, position sizing rules) will prevent rework.

---

## Sources

### Primary (HIGH confidence)
- [Optuna 4.8 TPESampler docs](https://optuna.readthedocs.io/en/stable/reference/samplers/generated/optuna.samplers.TPESampler.html) — TPE multivariate mode, n_startup_trials defaults, constructor options
- [Optuna Ask-and-Tell recipe](https://optuna.readthedocs.io/en/stable/tutorial/20_recipes/009_ask_and_tell.html) — ask/tell API for external loop integration, the pattern that makes Bayesian mode work without replacing the iteration loop
- [Matplotlib savefig blank image causes](https://pythonguides.com/matplotlib-savefig-blank-image/) — 5 documented causes of blank PNGs with fixes
- [npm view documentation](https://docs.npmjs.com/cli/v7/commands/npm-view/) — version lookup via CLI, rate limits
- Codebase: `workflows/execute.md` (1067 lines), `references/backtest_engine.py` (241 lines), `references/metrics.py` — direct line-level analysis confirming root cause of equity PNG bug

### Secondary (MEDIUM confidence)
- [Piotr Pomorski — Hyperparameter optimization with backtesting](https://piotrpomorski.substack.com/p/hyperparameter-optimisation-with) — Optuna + trading strategy integration pattern
- [3Commas Backtesting Guide 2025](https://3commas.io/blog/comprehensive-2025-guide-to-backtesting-ai-trading) — optimization workflow patterns
- [Optuna Efficient Optimization Algorithms](https://optuna.readthedocs.io/en/stable/tutorial/10_key_features/003_efficient_optimization_algorithms.html) — TPE sampler details, pruning, n_startup_trials behavior
- [Optuna Multi-objective Optimization](https://optuna.readthedocs.io/en/stable/tutorial/20_recipes/002_multi_objective.html) — rationale for deferring Pareto front

### Tertiary (LOW confidence)
- [Walk-forward optimization for trading strategies](https://eveince.substack.com/p/walk-forward-optimization-for-algorithmic) — WFO as user override (not default)
- [The Probability of Backtest Overfitting](https://www.davidhbailey.com/dhbpapers/backtest-prob.pdf) — academic reference on overfitting risk in composite objectives

---
*Research completed: 2026-03-22*
*Ready for roadmap: yes*
