# Phase 9: Bayesian Optimization - Context

**Gathered:** 2026-03-22
**Status:** Ready for planning

<domain>
## Phase Boundary

Integrate Optuna Bayesian optimization into the execute loop using Ask-and-Tell API. Add Bayesian as a plan workflow option. Persist studies to SQLite for --resume. Preserve all existing per-iteration artifacts and AI analysis.

</domain>

<decisions>
## Implementation Decisions

### Iteration loop integration
- **D-01:** Use Optuna's Ask-and-Tell API (`study.ask()` → run backtest → `study.tell(trial, value)`). This preserves the existing per-iteration loop: Claude still writes the Python script, runs it, reads metrics, generates equity PNG, writes verdict JSON. Optuna just replaces the "AI picks next params" step.
- **D-02:** AI analysis still runs between iterations. After each backtest, Claude reads metrics and equity PNG, writes its analysis (same as current). The difference: instead of Claude inventing the next params, Optuna suggests them via `study.ask()`. Claude can still comment on what Optuna chose.
- **D-03:** Display warmup vs guided mode: first N iterations (default 10 for TPE) show `[WARMUP]` tag, subsequent show `[GUIDED]`. This tells the user when random exploration ends and Bayesian guidance begins.
- **D-04:** The objective function value for `study.tell()` is a composite score: `sharpe_ratio` as primary, with penalty for exceeding max_drawdown target. Formula: `score = sharpe - max(0, abs(max_dd) - dd_target) * 2`. This keeps it single-objective.

### Plan workflow changes
- **D-05:** Add `bayesian` as a fourth optimization method in plan.md Step 4 alongside grid/random/walk-forward.
- **D-06:** Auto-recommendation rule: if total_combinations > 500, auto-select `bayesian`. If <= 500, keep current logic (grid for <100, random for 100-500).
- **D-07:** Plan artifact (`phase_N_plan.md`) needs a new field when bayesian is selected: `optimization_method: bayesian` with optional `sampler: auto` (auto-selects TPE vs CMA-ES based on param types).
- **D-08:** Plan workflow override prompt updated: `Override? (grid / random / walk-forward / bayesian / keep)`.

### Sampler auto-selection
- **D-09:** If ALL free parameters are continuous (float with no step constraint), auto-select CMA-ES sampler. Otherwise, use TPE with `multivariate=True`. Display which sampler was selected and why.
- **D-10:** The sampler selection happens at execute time, not plan time — because the plan just says `bayesian` and the execute workflow reads the actual param types to decide.

### Resume with SQLite
- **D-11:** Optuna study persists to SQLite at `.pmf/phases/phase_N_execute/optuna_study.db`. Created on first Bayesian iteration, loaded on `--resume`.
- **D-12:** On `--resume`, load the existing study with `optuna.load_study(storage=sqlite_url)`. New trials continue from where the study left off — the TPE probability model is preserved.
- **D-13:** If user changes parameter ranges between runs (detected by comparing plan params to study params), warn and offer: continue with existing study (may suggest out-of-range values) or start fresh study.
- **D-14:** For non-Bayesian methods (grid/random/walk-forward), `--resume` continues to work as before (scan for last `iter_NN_verdict.json`). SQLite is only used when `optimization_method: bayesian`.

### Claude's Discretion
- Exact composite score formula weights
- Whether to create an `optuna_bridge.py` helper module or inline the Optuna code in the execute template
- TPE `n_startup_trials` parameter (default 10 is reasonable)
- Whether to display Optuna's internal trial number alongside the PMF iteration number

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Plan workflow
- `workflows/plan.md` — Step 4 (Select Optimization Method) at line 253. Currently offers grid/random/walk-forward. Needs bayesian added.

### Execute workflow
- `workflows/execute.md` — Parameter selection strategy at line 810. Currently has grid/random/walk-forward branches. Needs bayesian branch with Ask-and-Tell.
- `workflows/execute.md` — Resume logic at line 134. Currently scans for verdict JSON. Needs SQLite study loading for bayesian.

### Research findings
- `.planning/research/FEATURES.md` — Optuna TPE analysis, warmup trials, Ask-and-Tell API
- `.planning/research/ARCHITECTURE.md` — optuna_bridge.py proposal, SQLite persistence
- `.planning/research/PITFALLS.md` — TPE warmup trial count, study.optimize() anti-pattern, SQLite resume requirement
- `.planning/research/STACK.md` — Confirms optuna already in requirements.txt, zero new deps

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- `optuna` already in venv (>=4.7, current 4.8.0) — no install changes needed
- Execute workflow iteration loop already structured as: write script → run → read metrics → analyze → decide next params → repeat
- Plan workflow already has auto-selection logic and override prompt

### Established Patterns
- Optimization method stored as string in `phase_N_plan.md` (`grid_search`, `random_search`, `walk_forward`)
- Execute workflow branches on method for parameter selection (line 810-813)
- Per-iteration artifacts: `iter_NN_params.json`, `iter_NN_metrics.json`, `iter_NN_equity.png`, `iter_NN_verdict.json`
- Resume scans for `iter_NN_verdict.json` as completion marker

### Integration Points
- `workflows/plan.md` Step 4: add bayesian to auto-selection rules and override prompt
- `workflows/execute.md` line 810: add bayesian parameter selection branch using Ask-and-Tell
- `workflows/execute.md` line 134: add SQLite study loading for bayesian --resume
- `.pmf/phases/phase_N_execute/optuna_study.db`: new artifact location

</code_context>

<specifics>
## Specific Ideas

No specific requirements — research covered Optuna integration thoroughly.

</specifics>

<deferred>
## Deferred Ideas

- Multi-objective Optuna optimization (Pareto front for Sharpe vs Drawdown) — deferred to v1.2 per Out of Scope
- Optuna visualization dashboard (parallel coordinate plots, importance) — future enhancement

</deferred>

---

*Phase: 09-bayesian-optimization*
*Context gathered: 2026-03-22*
