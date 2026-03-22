# Pitfalls Research

**Domain:** v1.1 Enhancement features for AI-driven trading strategy backtesting pipeline
**Researched:** 2026-03-22
**Confidence:** HIGH (Optuna pitfalls verified via docs; matplotlib blank PNG is well-documented; debug cycle memory and export pitfalls derived from codebase analysis)

**Scope:** This document covers pitfalls specific to ADDING v1.1 features to the existing v1.0 system. For foundational backtesting pitfalls (lookahead bias, overfitting, IS/OOS confusion, etc.), see `references/common-pitfalls.md`.

## Critical Pitfalls

### Pitfall 1: Optuna Objective Function Runs Full Backtest Inside Trial, Destroying the Existing Iteration Architecture

**What goes wrong:**
The natural way to use Optuna is to define an `objective(trial)` function that runs a complete backtest, returning a metric for Optuna to optimize. But the existing execute workflow has a carefully designed per-iteration architecture: write a Python script, run it, read artifacts, display terminal output, write verdict JSON, and let Claude perform AI analysis between iterations. If Optuna's `study.optimize()` runs 50 trials internally in a single Python process, ALL of that per-iteration infrastructure is bypassed. No equity PNGs, no AI analysis, no verdict JSONs, no resume capability, no stop conditions (MINT/PLATEAU/REKT). The user sees nothing for minutes, then gets a single "best params" result.

**Why it happens:**
Optuna's standard usage pattern (`study.optimize(objective, n_trials=N)`) is a blocking call that runs all trials sequentially or in parallel within one process. Developers copy this pattern from Optuna tutorials without considering that the existing system's value comes from the per-iteration feedback loop.

**How to avoid:**
Use Optuna's Ask-and-Tell interface instead of `study.optimize()`. This lets the existing iteration loop remain the outer controller:
1. Create the study and sampler once at iteration start
2. Each iteration: `trial = study.ask()` to get suggested parameters
3. Run the backtest using the existing per-iteration script pattern
4. `study.tell(trial, metric_value)` to report results back
5. All existing infrastructure (equity PNGs, AI analysis, verdict JSON, stop conditions) stays intact

This is documented in Optuna's official recipes: https://optuna.readthedocs.io/en/stable/tutorial/20_recipes/009_ask_and_tell.html

**Warning signs:**
- Execute workflow has a single long-running Python script instead of per-iteration scripts
- No `iter_NN_verdict.json` files being created during Optuna optimization
- User sees no output between start and finish
- `--resume` flag stops working

**Phase to address:**
Bayesian optimization phase. The Ask-and-Tell integration pattern must be designed before any Optuna code is written. Modifying the execute workflow's Step 5 loop to use Ask-and-Tell should be the first task.

---

### Pitfall 2: Optuna TPE Sampler Needs Warmup Trials, Causing Poor Early Iterations

**What goes wrong:**
TPE (Tree-structured Parzen Estimator), Optuna's default sampler, requires a minimum number of completed trials before it can build a useful probability model. The default `n_startup_trials` is 10 -- meaning the first 10 trials are effectively random. If `max_iterations` is set to 10 (the current default), every single iteration is random and the Bayesian optimization adds zero value over random search.

**Why it happens:**
TPE models the distribution of "good" vs "bad" parameter values, but needs enough data points to separate them. With fewer completed trials than `n_startup_trials`, it falls back to random sampling. The existing system defaults to 10 max iterations, which exactly equals the TPE default startup count.

**How to avoid:**
- When Bayesian optimization is selected, enforce a minimum of 20 iterations (or set `n_startup_trials` to 5 to reduce warmup at the cost of slightly less informed initial model)
- The plan workflow should warn if `max_iterations < 2 * n_startup_trials`
- Consider seeding Optuna with the existing grid/random search results from prior phases using `study.add_trial()` so TPE has prior data to learn from
- Display which sampling mode is active per iteration: "Iteration 7/30 (TPE warmup -- random sampling)" vs "Iteration 12/30 (TPE guided)"

**Warning signs:**
- All iterations show random-looking parameter changes with no convergence pattern
- User sets `--iterations 10` with Bayesian mode and gets the same quality as random search
- No improvement trajectory visible despite "Bayesian optimization" being selected

**Phase to address:**
Bayesian optimization phase. The plan workflow must enforce minimum iteration counts when Bayesian is selected, and the execute workflow must display sampling mode.

---

### Pitfall 3: Blank Equity PNG -- plt.close() Before savefig(), or Plotting on Wrong Figure

**What goes wrong:**
The current equity PNG generation produces blank images. This is a known v1.0 bug being fixed in v1.1. The most common causes of blank matplotlib PNGs are: (1) calling `plt.show()` before `savefig()`, which clears the figure buffer, (2) calling `plt.close()` before `savefig()`, (3) creating a new `plt.figure()` after plotting but before saving, which switches the active figure to a blank one, (4) plotting on `plt` (pyplot state machine) but saving from a different `fig` object.

**Why it happens:**
The current execute workflow (Step 5a, line ~526-554) creates a figure with `fig, ax = plt.subplots()`, plots on `ax`, then saves with `fig.savefig()`. This pattern is correct in isolation. The blank image is likely caused by one of: the equity array being `[initial_capital]` (single point, no visible line), the `trades` list being empty so only a dot is plotted, or the x-axis being "Trade #" but the data having zero trades. When `calculate_signal()` returns only 'hold' for the entire dataset (e.g., insufficient warmup bars), trades is empty, equity_arr has one element, and matplotlib draws nothing visible.

**How to avoid:**
- Guard against empty/single-point equity: if `len(equity_arr) <= 1`, skip PNG generation and log "No trades -- equity curve skipped"
- Use the bar-level equity curve from `run_backtest()` (returned by `compute_all_metrics` as `equity_curve` key) instead of reconstructing from trades. The trade-based reconstruction loses the mark-to-market detail between trades
- After plotting, verify the figure has visible content: `if ax.lines and len(ax.lines[0].get_ydata()) > 1`
- Use the explicit figure/axes pattern (`fig, ax = plt.subplots()` then `fig.savefig()`) consistently -- never mix with pyplot state machine (`plt.plot()` then `fig.savefig()`)

**Warning signs:**
- PNG file exists but has 0KB or very small file size
- PNG opens but shows only axis labels with no line
- Equity curve PNG shows a flat line at initial_capital despite positive net P&L in metrics

**Phase to address:**
Bug fix phase (should be done first as it is the simplest and unblocks visual feedback for all other features).

---

### Pitfall 4: Debug Cycle Memory Creates Unbounded Context, Hitting Claude's Token Limit

**What goes wrong:**
The "smarter debug cycles" feature carries forward failed approaches across iterations. If implemented naively (concatenating all previous verdict JSONs, error logs, and analysis text into the prompt), the context grows linearly with iterations. After 15-20 iterations, the accumulated context can exceed Claude's effective working memory, causing degraded analysis quality or prompt truncation. The execute workflow already reads ALL prior verdict JSONs (Step 5e point 4), but adding full error traces and "why this failed" narratives from debug cycles multiplies the context per iteration.

**Why it happens:**
The instinct is to give Claude "all the information" so it can avoid repeating mistakes. But each verdict JSON is ~40 lines, each error trace can be 50+ lines, and each "failed approach" narrative adds 10-20 lines. At 20 iterations with debug memory: 20 * (40 + 50 + 20) = 2,200 lines of accumulated context, on top of the strategy definition, plan, research, and backtest engine reference.

**How to avoid:**
- Use a SUMMARY approach, not an APPEND approach: maintain a single `debug_memory.md` file that is a condensed summary (max 50 lines) of all failed approaches and why they failed
- After each failed iteration, ADD one 2-3 line entry to the summary: parameter combination, result, why it failed
- REMOVE raw error traces and verbose analysis after summarizing
- Cap the debug memory file at 50 entries (drop oldest when exceeded)
- Structure entries as a table for scannability:
  ```
  | Iter | Params Tried | Result | Why Failed |
  |------|-------------|--------|------------|
  | 3 | fast=5, slow=20 | Sharpe -0.3 | Too tight stops in ranging market |
  ```

**Warning signs:**
- Execute workflow slowing down noticeably after iteration 10+
- Claude's per-iteration analysis becoming generic or repetitive (sign of context pressure)
- Identical parameter combinations being tried again despite "memory" feature
- Token count warnings or truncation errors

**Phase to address:**
Debug cycle memory phase. The data structure for storing failed approaches must be designed as a fixed-size summary, not an append-only log.

---

### Pitfall 5: Optuna Study Persistence Breaks --resume Flag

**What goes wrong:**
The existing `--resume` flag works by scanning for `iter_NN_verdict.json` files and reconstructing state. If Optuna is introduced with an in-memory study, resuming loses all of Optuna's learned probability model. The TPE sampler's internal state (the Parzen estimator models) is gone, so resumed optimization restarts the warmup phase. This means a user who ran 15 Bayesian iterations, stopped, and resumed effectively wasted their first 10 warmup trials.

**Why it happens:**
Optuna studies are in-memory by default. The `--resume` flag was designed for the v1.0 system which only needs to restore parameter values and best metrics, not a statistical model. Optuna supports SQLite-backed studies (`storage="sqlite:///study.db"`) but this adds a new file to manage and a new dependency to handle.

**How to avoid:**
- Use `optuna.create_study(storage="sqlite:///.pmf/phases/phase_N_execute/optuna_study.db")` to persist the study
- On `--resume`: load the existing study with `optuna.load_study(study_name=..., storage=...)`
- The Ask-and-Tell interface works with persisted studies -- completed trials are preserved
- Fall back gracefully: if the study DB is missing on resume, log a warning and create a new study, seeding it with results from verdict JSONs via `study.add_trial()`
- Add the study DB path to the artifacts that `--resume` checks for

**Warning signs:**
- Resumed Bayesian optimization shows random-looking parameter choices despite 15+ prior iterations
- Log shows "n_startup_trials" behavior after resume
- User reports that resuming "resets" the optimization

**Phase to address:**
Bayesian optimization phase. Study persistence must be part of the initial Optuna integration, not an afterthought. The `--resume` path in Step 4 of the execute workflow needs updating simultaneously.

---

### Pitfall 6: Enhanced Export MD-Instruction Format Duplicates Logic Across Formats

**What goes wrong:**
The v1.0 export already produces PineScript, trading-rules.md, performance-report.md, backtest_final.py, live-checklist.md, and the HTML report. Adding an "MD-instruction format for bot-building guides" creates a seventh export artifact. If each format independently describes the strategy logic (entry conditions, exit conditions, parameters), any change to one format requires updating all seven. Over time, formats drift: the PineScript says "enter when RSI < 30 AND price above SMA50" but the bot-building guide says "enter when RSI < 30 OR price above SMA50."

**Why it happens:**
Each export format is typically a separate template with strategy details hard-coded into it by Claude during the export step. There is no single source of truth that all formats derive from.

**How to avoid:**
- Create a canonical `strategy_definition.json` as the single source of truth, generated once during the verify/export phase
- All export formats (PineScript, Python, MD-instruction, trading-rules) should READ from this JSON, not re-derive strategy logic from the discuss/plan artifacts
- The JSON should contain: entry conditions (structured), exit conditions, parameter values, indicator definitions, position sizing rules
- Template each export format to consume this JSON

**Warning signs:**
- Strategy logic described differently across export files
- Bug fix to one export format not reflected in others
- User reports confusion when bot-building guide contradicts PineScript

**Phase to address:**
Enhanced export phase. The canonical strategy definition must be created before the new MD-instruction format is templated.

---

## Moderate Pitfalls

### Pitfall 7: /brrr:doctor Checks Python Version But Not Package Versions Inside Venv

**What goes wrong:**
A diagnostic command that only checks "Python >= 3.10 exists" and "venv directory exists" misses the most common failure mode: package version conflicts or missing packages inside the venv. Users may have a corrupt venv (partial pip install failure), outdated packages (installed months ago), or conflicting versions (optuna 4.7 requires scipy >= 1.13 but user has 1.12).

**How to avoid:**
- Check each critical package with version: `venv/bin/python -c "import optuna; print(optuna.__version__)"`
- Compare against requirements.txt pinned versions
- Test actual functionality, not just import: e.g., `from metrics import compute_all_metrics` verifies the reference module loads
- Provide a `--fix` flag that runs `pip install -r requirements.txt --upgrade` inside the venv

**Warning signs:**
- Doctor reports "all good" but execute fails with ImportError
- User has an old venv from a previous version

**Phase to address:**
Maintenance commands phase.

---

### Pitfall 8: Auto Version Check on Every /brrr:* Command Adds Latency

**What goes wrong:**
Checking npm for the latest version on every command invocation adds 500ms-2s of network latency to every slash command. On slow connections or offline environments, it can cause timeout errors or make the tool feel sluggish. If the check blocks the main flow, a network timeout delays every single command.

**How to avoid:**
- Check at most once per session (use a timestamp file: `.pmf/.last_version_check`)
- Make the check async/non-blocking: fire the request, continue with the command, show result at the end if available
- Cache the result for 24 hours
- Fail silently if offline (no error, just skip the check)
- Never block command execution on the version check result

**Warning signs:**
- Commands feel slow on first run of the day
- User reports timeout errors in offline environments
- Every command shows "checking for updates..." message

**Phase to address:**
Maintenance commands phase.

---

### Pitfall 9: Optuna Direction Mismatch -- Maximizing Sharpe But Minimizing Drawdown

**What goes wrong:**
Trading strategy optimization naturally has multiple objectives: maximize Sharpe ratio, minimize max drawdown, maximize profit factor. Optuna's single-objective `create_study(direction="maximize")` can only optimize one metric. If you maximize Sharpe, you get strategies with high returns but potentially catastrophic drawdowns. If you use multi-objective (`directions=["maximize", "minimize"]`), the result is a Pareto front, not a single "best" solution, and the existing workflow (which expects a single best iteration) breaks.

**How to avoid:**
- Use single-objective optimization with a composite score: `score = sharpe_ratio - penalty * max(0, abs(max_drawdown) - dd_target)`
- The penalty term ensures drawdown constraints are respected without needing multi-objective
- Keep the existing "best iteration by Sharpe" logic but add a hard filter: reject any trial where drawdown exceeds the target
- In Optuna terms: use `study.optimize()` with the composite score as the return value, and let the existing stop conditions (MINT checks all targets) handle multi-criteria validation
- Do NOT use multi-objective Optuna unless the workflow is redesigned to handle Pareto fronts

**Warning signs:**
- Best Sharpe iteration has a drawdown of -60% (Sharpe maximized but drawdown ignored)
- Multi-objective study returns 15 "best" trials and the workflow picks one arbitrarily
- User hits MINT on Sharpe but fails on drawdown target

**Phase to address:**
Bayesian optimization phase. The objective function design must be settled before writing Optuna integration code.

---

### Pitfall 10: Debug Memory Remembers Strategy-Level Failures Across Phase Boundaries

**What goes wrong:**
If debug memory persists across phases (Phase 1 -> Phase 2 -> Phase 3), it carries forward failures that are irrelevant to the current phase. Phase 1 might have explored SMA crossover and found it didn't work, but Phase 2 is testing RSI mean-reversion -- the SMA failures are noise. Worse, Claude might avoid parameter ranges that "failed before" even though the strategy logic is completely different.

**How to avoid:**
- Reset debug memory at phase boundaries (when a new phase starts via discuss/plan)
- Keep phase-specific memory in `phase_N_debug_memory.md`, not a global file
- When starting a new phase, optionally carry forward ONE sentence: "Previous phase found that [asset] trends strongly on [timeframe]" -- strategic insight, not parameter-level detail

**Warning signs:**
- Phase 3 avoids parameter ranges that only failed in Phase 1's different strategy
- Debug memory file grows across milestones
- AI analysis references strategies that are not part of the current phase

**Phase to address:**
Debug cycle memory phase. Phase-scoped storage must be part of the design.

---

## Technical Debt Patterns

Shortcuts that seem reasonable but create long-term problems.

| Shortcut | Immediate Benefit | Long-term Cost | When Acceptable |
|----------|-------------------|----------------|-----------------|
| Optuna study in-memory only | Simpler code, no SQLite dependency | Resume loses TPE model, warmup wasted | Never -- always persist to SQLite |
| Composite objective as `sharpe - 2*drawdown` | Quick to implement | Magic constant "2" is arbitrary, doesn't generalize | Only for v1.1 MVP if documented as "tune this constant" |
| Appending full error traces to debug memory | Maximum context for AI | Token budget explosion after 15 iterations | Never -- always summarize |
| Version check via `npm view` shell command | Works immediately | Breaks on systems without npm in PATH, slow | Only if cached with 24h TTL and silent failure |
| Bot-building guide as freeform markdown | Fast to template | Drifts from PineScript/Python exports | Only if canonical strategy_definition.json exists |
| Doctor command only checks `python --version` | Covers the most common issue | Misses 80% of actual venv problems | Never -- must check package imports |

## Integration Gotchas

Common mistakes when connecting new v1.1 features to the existing v1.0 system.

| Integration | Common Mistake | Correct Approach |
|-------------|----------------|------------------|
| Optuna + execute workflow | Replacing the iteration loop with `study.optimize()` | Use Ask-and-Tell to keep existing loop as outer controller |
| Optuna + plan workflow | Not updating plan to include sampler choice and n_startup_trials | Add "Optimization Sampler" and "Warmup Trials" fields to plan artifact |
| Optuna + verdict JSON | Not recording trial number and sampler state | Add `optuna_trial_id` and `sampling_mode` (warmup/guided) to verdict JSON |
| Debug memory + STATE.md | Not tracking debug memory file path in STATE.md | Add debug_memory path to phase tracking in STATE.md |
| Doctor + install | Doctor checks system Python, not venv Python | Always use `~/.pmf/venv/bin/python` for all checks |
| Version check + offline | Blocking on network request | Async check with <2s timeout, silent failure, cached result |
| MD-instruction export + verify | Generating bot guide before verify approval | Bot guide is part of export package, only generated on `--approved` |

## Performance Traps

Patterns that work at small scale but fail as usage grows.

| Trap | Symptoms | Prevention | When It Breaks |
|------|----------|------------|----------------|
| Loading all verdict JSONs into prompt every iteration | Slow after iteration 10, context pressure after 15 | Summarize into fixed-size table, read only last 3 full verdicts | >10 iterations |
| Optuna study.db growing with full trial metadata | Slow resume, large file size | Prune startup trials after model is trained, or accept the growth (typically <1MB for 100 trials) | >500 trials (unlikely) |
| Re-downloading market data on each iteration | Slow iterations, API rate limits | Cache check already exists (v1.0), ensure Optuna path uses same cache | Immediate if cache is bypassed |
| Equity PNG generation per iteration at high iteration counts | Disk fills with PNGs, slower iterations | Already have `--fast` flag. With Optuna (30+ iterations), default to fast mode and generate PNG only for best trial | >30 iterations |

## UX Pitfalls

Common user experience mistakes when adding these features.

| Pitfall | User Impact | Better Approach |
|---------|-------------|-----------------|
| Optuna shows no output for 5 minutes during warmup | User thinks it's frozen, kills the process | Display "Warmup iteration 3/10 (random sampling)" per iteration |
| Doctor command outputs raw pip version strings | User can't tell if versions are good or bad | Show checkmark/X per dependency with expected vs actual version |
| Debug memory makes AI analysis verbose | User has to read 3 paragraphs of "we tried X before" before getting to current analysis | Put memory-informed insight in ONE sentence at the start, then current analysis |
| Bot-building guide uses technical jargon | User who needs a "guide" is probably less technical | Write for the audience: step-by-step with code blocks they can copy-paste |
| Auto version check nags on every command | User gets "update available" fatigue | Show update notice once per day maximum, never block workflow |

## "Looks Done But Isn't" Checklist

Things that appear complete but are missing critical pieces.

- [ ] **Optuna integration:** Often missing Ask-and-Tell pattern -- verify that `study.optimize()` is NOT called directly in the execute loop. Check that per-iteration artifacts (verdict JSON, equity PNG) are still generated.
- [ ] **Optuna integration:** Often missing study persistence -- verify that `storage="sqlite:///"` is used, and that `--resume` loads the existing study.
- [ ] **Optuna integration:** Often missing warmup display -- verify that iterations show whether TPE is in warmup or guided mode.
- [ ] **Debug memory:** Often missing phase-scoping -- verify that memory resets at phase boundaries and uses `phase_N_debug_memory.md`.
- [ ] **Debug memory:** Often missing size cap -- verify that memory is summarized (not appended) and capped at ~50 entries.
- [ ] **Equity PNG fix:** Often missing the empty-trades guard -- verify that PNG generation is skipped when trades list is empty or equity has <= 1 data point.
- [ ] **Equity PNG fix:** Often missing bar-level equity -- verify that the equity curve uses `results['equity_curve']` from the engine, not trade-level reconstruction.
- [ ] **Doctor command:** Often missing package-level checks -- verify it tests actual imports, not just file existence.
- [ ] **Doctor command:** Often missing `--fix` flag -- verify there is a remediation path, not just diagnosis.
- [ ] **Enhanced export:** Often missing canonical source -- verify that a `strategy_definition.json` drives all export formats, not re-derivation from discuss artifacts.
- [ ] **Version check:** Often missing cache -- verify that npm registry is checked at most once per 24 hours, with silent offline failure.

## Recovery Strategies

When pitfalls occur despite prevention, how to recover.

| Pitfall | Recovery Cost | Recovery Steps |
|---------|---------------|----------------|
| Optuna replaces iteration loop | HIGH | Rewrite execute workflow Step 5 to use Ask-and-Tell. All Optuna integration code must be restructured. |
| TPE warmup wastes all iterations | LOW | Re-run with `--iterations 30` or reduce `n_startup_trials` to 5. Existing results not lost. |
| Blank equity PNG persists | LOW | Check if trades list is empty; if so, add guard. If not empty, verify `fig.savefig()` is called before any `plt.close()` or `plt.show()`. |
| Debug memory explodes context | MEDIUM | Replace append-only log with summary table. Requires rewriting the memory storage format and updating execute workflow Step 5e. |
| Resume loses Optuna model | MEDIUM | Add SQLite storage. Seed new study with existing verdict JSON results via `study.add_trial()`. Previous iterations' guidance is partially recovered. |
| Export formats drift | MEDIUM | Create canonical `strategy_definition.json` and re-template all export formats to read from it. Existing exports must be re-generated. |
| Doctor gives false "all good" | LOW | Add package import checks. No data loss, just add more checks. |

## Pitfall-to-Phase Mapping

How roadmap phases should address these pitfalls.

| Pitfall | Prevention Phase | Verification |
|---------|------------------|--------------|
| Optuna replaces iteration loop (P1) | Bayesian optimization | Execute workflow still produces per-iteration verdict JSONs; `--resume` still works |
| TPE warmup wastes iterations (P2) | Bayesian optimization | Plan enforces min iterations; terminal shows "warmup/guided" per iteration |
| Blank equity PNG (P3) | Bug fix (do first) | PNG has visible line when trades > 0; graceful skip when trades = 0 |
| Debug memory context explosion (P4) | Debug cycle memory | Memory file stays under 50 lines after 20 iterations |
| Optuna resume breaks (P5) | Bayesian optimization | Resume after 15 Bayesian iterations shows guided (not random) sampling on iteration 16 |
| Export format drift (P6) | Enhanced export | All 7 export files describe identical entry/exit conditions |
| Doctor too shallow (P7) | Maintenance commands | Doctor catches missing optuna package in venv |
| Version check latency (P8) | Maintenance commands | Command executes in <1s; no error when offline |
| Direction mismatch (P9) | Bayesian optimization | Best trial respects both Sharpe AND drawdown targets |
| Debug memory cross-phase leak (P10) | Debug cycle memory | Phase 2 memory file contains no Phase 1 entries |

## Sources

- [Optuna Ask-and-Tell Interface](https://optuna.readthedocs.io/en/stable/tutorial/20_recipes/009_ask_and_tell.html) -- official recipe for external loop integration
- [Optuna Multi-objective Optimization](https://optuna.readthedocs.io/en/stable/tutorial/20_recipes/002_multi_objective.html) -- Pareto front handling
- [Optuna Efficient Optimization Algorithms](https://optuna.readthedocs.io/en/stable/tutorial/10_key_features/003_efficient_optimization_algorithms.html) -- TPE sampler details, n_startup_trials
- [Matplotlib savefig blank image fix](https://pythonguides.com/matplotlib-savefig-blank-image/) -- common causes of blank PNGs
- [Matplotlib savefig empty when fig size matches data](https://github.com/matplotlib/matplotlib/issues/17542) -- figure size edge case
- [Walk-forward optimization for trading strategies](https://eveince.substack.com/p/walk-forward-optimization-for-algorithmic) -- WFO patterns
- [Avoiding overfitting when testing trading rules](http://adventuresofgreg.com/blog/2025/12/18/avoid-overfitting-testing-trading-rules/) -- overfitting prevention in trading
- [The Probability of Backtest Overfitting](https://www.davidhbailey.com/dhbpapers/backtest-prob.pdf) -- academic reference on overfitting risk
- Codebase analysis: `workflows/execute.md` (1067 lines), `references/backtest_engine.py` (241 lines), `references/common-pitfalls.md`

---
*Pitfalls research for: v1.1 enhancement features (Bayesian optimization, enhanced export, diagnostic commands, debug cycle memory, equity PNG fix)*
*Researched: 2026-03-22*
