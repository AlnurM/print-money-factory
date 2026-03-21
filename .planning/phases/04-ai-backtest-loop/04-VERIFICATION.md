---
phase: 04-ai-backtest-loop
verified: 2026-03-21T16:00:00Z
status: human_needed
score: 9/10 automated must-haves verified
re_verification: false
human_verification:
  - test: "Run /brrr:execute --iterations 3 with a completed milestone that has discuss and plan artifacts"
    expected: "Claude writes a Python backtest script, executes it, reads back metrics JSON and equity PNG, prints the D-10 terminal block with 'brrr...', adjusts parameters, and repeats for 3 iterations. Per-iteration artifacts (iter_01_params.json, iter_01_metrics.json, iter_01_oos_metrics.json, iter_01_equity.png, iter_01_verdict.json) appear in .pmf/phases/phase_N_execute/. Loop stops and writes phase_N_best_result.json."
    why_human: "The execute.md workflow is behavioral markdown -- its correctness is verified only by running it through Claude Code. File presence and grep checks confirm instructions are written correctly, but cannot confirm Claude follows them, Python scripts execute correctly in the venv, or artifacts are actually written to disk."
  - test: "Trigger each stop condition by manipulating the test strategy: run a strategy that hits targets (MINT), stall parameters artificially (PLATEAU), and run with no-edge random parameters (REKT)"
    expected: "Each stop condition displays the correct labeled stop block. REKT output distinguishes 'strategy has no edge' from 'wrong asset/timeframe'. STATE.md is updated with execute marked done after each run."
    why_human: "Stop condition trigger logic is behavioral -- requires running Claude through the full loop to verify the conditions fire and produce the correct diagnostic messages."
  - test: "Run /brrr:execute --resume after a partially completed run where iterations 1-2 exist but 3 does not"
    expected: "Claude scans for iter_NN_verdict.json files, identifies iteration 2 as the last completed, and starts iteration 3 -- not iteration 1."
    why_human: "Resume behavior depends on Claude correctly scanning files and resuming from the right state. Only observable at runtime."
  - test: "Place a PDF or screenshot in .pmf/context/ and then run /brrr:execute"
    expected: "Preamble context scan detects the file, describes its contents, and asks for confirmation before incorporating it into strategy decisions."
    why_human: "Context file scan is part of the preamble behavioral instructions. Requires running the workflow to verify."
---

# Phase 4: AI Backtest Loop Verification Report

**Phase Goal:** User runs one command and the system loads market data, writes a custom backtest engine, runs iterative optimization with AI analysis, and stops when targets are hit or the strategy is diagnosed as unviable
**Verified:** 2026-03-21T16:00:00Z
**Status:** human_needed
**Re-verification:** No -- initial verification

---

## Goal Achievement

### Observable Truths (from ROADMAP.md Success Criteria)

| # | Truth | Status | Evidence |
|---|-------|--------|----------|
| SC-1 | User runs `/brrr:execute` and sees Claude write a Python backtest script from scratch, run it, read back metrics and equity PNG, diagnose results, adjust parameters, and repeat without manual intervention | ? HUMAN | Workflow instructs all of this in Step 5a-5f (1067 lines). Cannot verify behavioral execution without running it. |
| SC-2 | Each iteration produces saved artifacts (params JSON, metrics JSON, equity PNG, verdict JSON) persisting in the phase directory | ? HUMAN | Steps 5a, 5c, 5f in execute.md specify writing iter_NN_params.json, iter_NN_metrics.json, iter_NN_oos_metrics.json, iter_NN_equity.png, iter_NN_verdict.json. Artifact paths confirmed in workflow. Actual disk creation requires runtime. |
| SC-3 | Loop stops automatically on MINT, PLATEAU, REKT, or NO DATA, and user sees which condition triggered | ? HUMAN | All four stop conditions implemented in Step 5d with labeled output blocks. Confirmed by grep. Actual triggering requires runtime. |
| SC-4 | IS and OOS metrics reported separately, system warns when they diverge (overfitting signal) | ? HUMAN | IS/OOS split in Step 3, dual metrics in Step 5e terminal block, overfitting thresholds at IS Sharpe > 2x OOS Sharpe and suspicious Sharpe > 3.0 / PF > 5.0 / WR > 80% confirmed present. Runtime behavior requires human. |
| SC-5 | Data loads from ccxt and yfinance with CSV fallback, validated for gaps/NaN before backtest | ✓ VERIFIED | execute.md Step 2 instructs load_ccxt (with limit=50000), load_yfinance, load_csv. data_sources.py has multi_level_index=False fix and format='mixed' fix confirmed at lines 232 and 329. |

**Automated score: 1/5 success criteria fully automated-verifiable. 4/5 require human runtime testing (expected for behavioral markdown).**

### Must-Have Truths (from PLAN frontmatter)

| # | Must-Have Truth | Status | Evidence |
|---|-----------------|--------|----------|
| 1 | data_sources.py load_yfinance passes multi_level_index=False to yf.download | ✓ VERIFIED | Confirmed at references/data_sources.py line 232 |
| 2 | execute.md contains complete behavioral workflow replacing 10-line stub | ✓ VERIFIED | 1067 lines confirmed. Stub was 10 lines, replacement is 1067 lines |
| 3 | Workflow has preamble sequence validation matching discuss.md/plan.md pattern | ✓ VERIFIED | "## Preamble: Sequence Validation" at line 9 with STATE.md check, plan-done validation, STOP messages |
| 4 | Workflow has data loading step using data_sources.py adapters with caching | ✓ VERIFIED | Step 2 references load_ccxt, load_yfinance, load_csv with .pmf/cache/ parquet caching (10 grep matches for load_ccxt/load_yfinance/load_csv) |
| 5 | Workflow has IS/OOS split calculation from plan percentages | ✓ VERIFIED | Step 3 calculates split_idx from train_pct, records IS/OOS date ranges (21 matches for IS/OOS terminology) |
| 6 | Workflow has iteration loop with write-Python/execute/read-artifacts/analyze cycle | ✓ VERIFIED | Steps 5a (write), 5b (execute), 5c (read artifacts), 5d-5e (analyze) clearly delineated in workflow |
| 7 | Workflow has all 4 stop conditions: MINT, PLATEAU, REKT, NO DATA | ✓ VERIFIED | grep: MINT=6, PLATEAU=7, REKT=6, NO DATA/NO_DATA=10. Each has labeled output block with diagnostic messaging |
| 8 | Workflow has terminal display format matching D-10 spec | ✓ VERIFIED | "Terminal display (per D-10)" at line 748, exact format block with "brrr..." at position confirmed (3 matches for "brrr...") |
| 9 | Workflow has overfitting detection comparing IS vs OOS metrics | ✓ VERIFIED | IS Sharpe > 2x OOS Sharpe warning at line 737-739. Suspicious thresholds at lines 744-746. "overfitting" appears 10 times. |
| 10 | Workflow saves per-iteration artifacts and phase_N_best_result.json | ✓ VERIFIED | iter_NN_params.json (2 matches), iter_NN_metrics.json (4 matches), iter_NN_equity.png (3 matches), iter_NN_verdict.json (4 matches), phase_N_best_result.json (4 matches) |

**Automated must-have score: 10/10 truths verified.**

---

## Required Artifacts

| Artifact | Expected | Status | Details |
|----------|----------|--------|---------|
| `references/data_sources.py` | Fixed yfinance adapter with multi_level_index=False | ✓ VERIFIED | 334 lines, multi_level_index=False at line 232, format='mixed' at line 329, infer_datetime_format removed (0 grep matches) |
| `workflows/execute.md` | Complete AI backtest loop behavioral workflow, min 600 lines | ✓ VERIFIED | 1067 lines (178% of minimum). All required sections present. No placeholder anti-patterns detected. |

---

## Key Link Verification

| From | To | Via | Status | Details |
|------|----|-----|--------|---------|
| workflows/execute.md | references/backtest_engine.py | Instructs Claude to adapt calculate_signal() via monkey-patching | ✓ WIRED | "calculate_signal" appears 9 times. Monkey-patching instruction at line 445: `backtest_engine.calculate_signal = calculate_signal`. Critical rule at line 578: "Always use monkey-patching for calculate_signal, never modify reference files" |
| workflows/execute.md | references/data_sources.py | Instructs Claude to call load_ccxt/load_yfinance/load_csv | ✓ WIRED | load_ccxt/load_yfinance/load_csv appear 10 times combined. Step 2 fully details which adapter to call based on asset type. limit=50000 for ccxt confirmed at lines 179-180. |
| workflows/execute.md | references/metrics.py | Instructs Claude to use compute_all_metrics | ✓ WIRED | "compute_all_metrics" appears 7 times. Appendix entry at line 1031 documents exact function signature and return dict. |
| workflows/execute.md | workflows/plan.md | Execute reads phase_N_plan.md output from plan workflow | ✓ WIRED | "phase_N_plan" appears 3 times. Step 1 instructs reading phase_N_plan.md for parameter space, optimization method, train/test split, evaluation criteria. |
| commands/execute.md | workflows/execute.md | Command @-references workflow | ✓ WIRED | commands/execute.md line 17: `@~/.pmf/workflows/execute.md`. Also references backtest-engine.md, metrics.py, data_sources.py at lines 18-20. |

---

## Requirements Coverage

All 19 requirement IDs from PLAN 04-01 frontmatter verified against REQUIREMENTS.md and against execute.md Appendix (lines 1042-1062).

| Requirement | Description (from REQUIREMENTS.md) | Status | Evidence |
|-------------|-------------------------------------|--------|----------|
| EXEC-01 | AI-driven backtest loop: load data -> run backtest -> compute metrics -> AI analyzes -> adjust params -> repeat | ✓ SATISFIED | Step 5 (1a-5f) is the complete loop implementation |
| EXEC-02 | Claude writes Python backtest engine from scratch based on plan decisions | ✓ SATISFIED | Step 5a specifies writing run_iter_NN.py with full calculate_signal implementation |
| EXEC-03 | Data sourcing via ccxt (crypto), yfinance (stocks daily, forex daily), CSV fallback | ✓ SATISFIED | Step 2 with load_ccxt, load_yfinance, load_csv adapters |
| EXEC-04 | Core metrics: Sharpe, Sortino, Calmar, Max DD, Win Rate, Profit Factor, expectancy, trade count, net P&L | ✓ SATISFIED | Step 5a calls compute_all_metrics(), Step 5e displays all metrics in terminal block |
| EXEC-05 | Commission and slippage modeling included from first iteration | ✓ SATISFIED | Step 5a includes commission_rate in params dict (line 453). Step 1 reads commission rate from discuss/plan artifacts (lines 141, 352). |
| EXEC-06 | In-sample / out-of-sample split enforced -- metrics reported separately | ✓ SATISFIED | Step 3 calculates exact split, Step 5a runs run_backtest() twice (IS and OOS), terminal block shows "Metrics (IS / OOS)" format |
| EXEC-07 | Walk-forward analysis as optimization method -- rolling train/test windows | ✓ SATISFIED | Step 3 documents walk-forward window calculation, Step 5a has rolling window loop path (8 matches for walk_forward/walk-forward) |
| EXEC-08 | Stop conditions: MINT, PLATEAU, REKT, NO DATA | ✓ SATISFIED | Step 5d documents all four with exact trigger logic and threshold values |
| EXEC-09 | AI reads metrics and equity curve each iteration, diagnoses, decides next parameter adjustment | ✓ SATISFIED | Step 5c reads all artifacts including equity PNG via multimodal, Step 5e specifies holistic analysis in trading-domain language |
| EXEC-10 | Per-iteration artifacts: params JSON, metrics JSON, equity PNG (matplotlib), verdict JSON | ✓ SATISFIED | Step 5a writes params, IS metrics, OOS metrics, equity PNG; Step 5f writes verdict JSON |
| EXEC-11 | Real-time terminal display: iteration progress, current params, metrics, AI commentary | ✓ SATISFIED | D-10 terminal format block at lines 748-780 with exact layout specification |
| EXEC-12 | --iterations N, --fast, --resume flags | ✓ SATISFIED | Preamble "Parse Arguments" section (7 matches for --iterations, 6 for --fast, 7 for --resume) |
| EXEC-13 | Overfitting detection -- warns when IS/OOS diverge or metrics look too good | ✓ SATISFIED | Step 5e, lines 737-746: IS > 2x OOS warning, Sharpe > 3.0, PF > 5.0, WR > 80% thresholds |
| EXEC-14 | Outputs phase_N_best_result.json | ✓ SATISFIED | Step 6 (Finalize) specifies best_result.json structure including stop_reason, total_iterations, iteration summary |
| DATA-01 | ccxt integration for crypto -- auto-detect exchange | ✓ SATISFIED | Step 2: load_ccxt with limit=50000 for pagination, asset type drives adapter selection |
| DATA-02 | yfinance integration for stocks (daily) and forex (daily) | ✓ SATISFIED | data_sources.py fix confirmed. Step 2 calls load_yfinance(). Appendix line 1021 notes multi_level_index=False fix. |
| DATA-03 | CSV fallback for any asset | ✓ SATISFIED | Step 2 includes load_csv() fallback path |
| DATA-04 | Data validation before every backtest -- gaps, NaN, timezone | ✓ SATISFIED | Step 2 calls validate_ohlcv() with enhanced gap detection: auto-fix <5 bars forward-fill, REFUSE if >10% data affected |
| DATA-05 | Local data caching to avoid re-downloading | ✓ SATISFIED | Step 2: cache check at .pmf/cache/{asset}_{source}_{timeframe}.parquet before download, write to cache after download |

**Requirements coverage: 19/19 SATISFIED**

**Orphaned requirements check:** REQUIREMENTS.md Traceability table maps DATA-01 through DATA-05 to Phase 4 with status "Complete". All 5 DATA requirements are also claimed in plan 04-01 frontmatter. No orphaned requirements found.

**PLAN 04-02 requirements** (EXEC-01, EXEC-08, EXEC-09, EXEC-10, EXEC-11, DATA-01, DATA-02) are a subset of PLAN 04-01 requirements. All are satisfied per the coverage table above. Plan 04-02 adds only human verification of what 04-01 implemented -- no additional code deliverables.

---

## Anti-Patterns Found

No blockers or warnings detected.

| File | Line | Pattern | Severity | Impact |
|------|------|---------|----------|--------|
| references/data_sources.py | -- | No TODO/FIXME/placeholder found | -- | Clean |
| workflows/execute.md | -- | No TODO/FIXME/placeholder/empty stub found | -- | Clean |

Anti-pattern scan results:
- `grep TODO/FIXME/XXX/HACK/PLACEHOLDER`: 0 matches in both files
- `grep "return null|return {}|return []"`: 0 matches (not applicable to .md, not found in .py)
- No console.log-only implementations (Python file, not JavaScript)
- No empty handler patterns

---

## Human Verification Required

The execute workflow is behavioral markdown -- it instructs Claude how to behave, not code that executes directly. All automated checks pass: the file is substantive (1067 lines, well above the 600-line minimum), all required behavioral sections are present, all key links are wired, all 19 requirements are covered. What cannot be verified programmatically is whether the workflow actually produces correct behavior when run through Claude Code.

### 1. Full Iteration Cycle

**Test:** With an active milestone that has completed discuss and plan phases, run `/brrr:execute --iterations 3`

**Expected:** Claude writes `.pmf/phases/phase_N_execute/run_iter_01.py`, executes it with `~/.pmf/venv/bin/python`, reads back iter_01_metrics.json, iter_01_oos_metrics.json, iter_01_equity.png, displays the D-10 terminal block with "brrr..." header, writes iter_01_verdict.json, then repeats for iterations 2 and 3. After 3 iterations, writes phase_N_best_result.json and displays "LOOP COMPLETE" with stop condition.

**Why human:** Behavioral markdown. Claude must correctly interpret and follow 1067 lines of step-by-step instructions. Python script must execute in the venv, produce JSON artifacts, and not crash.

### 2. Stop Condition Display

**Test:** Observe a natural stop condition trigger (PLATEAU after flat iterations, or MINT if targets are hit)

**Expected:** The correct labeled stop block appears -- e.g., "LOOP COMPLETE -- PLATEAU" with the specific message text from Step 6 ("Optimization has plateaued after N iterations..."). REKT output must include the diagnostic distinguishing "strategy has no edge" from "wrong asset/timeframe for this strategy type."

**Why human:** Stop condition logic is inside the AI iteration loop. Trigger conditions depend on metrics values computed at runtime.

### 3. Resume Flag

**Test:** After partially completing a run (iterations 1-2 complete, 3 not started), run `/brrr:execute --resume`

**Expected:** Claude scans for iter_NN_verdict.json files, identifies iteration 2 as the last completed (since verdict.json is the last artifact written), and starts from iteration 3 without re-running 1 and 2.

**Why human:** File scanning and counter logic is behavioral. Only observable at runtime.

### 4. Data Caching

**Test:** Run `/brrr:execute` twice on the same asset/timeframe combination

**Expected:** Second run uses the cached parquet file from `.pmf/cache/` rather than re-downloading from the exchange or Yahoo Finance. Step 2 should display "Data loaded from cache" rather than "Downloading from {source}."

**Why human:** Cache check/write behavior requires runtime observation.

---

## Summary

Phase 4 automated verification: all 10 must-have truths verified against actual codebase content. Both artifacts are substantive and wired. All 5 key links confirmed present. All 19 requirement IDs (EXEC-01..14, DATA-01..05) are covered in the execute.md appendix with specific step references, and both fixes in data_sources.py are confirmed at exact line numbers.

The overall status is `human_needed` rather than `passed` because the primary deliverable -- the execute.md behavioral workflow -- cannot be fully verified without running it through Claude Code. The four human verification tests above cover the complete runtime behavior: the core iteration cycle, stop condition triggering, resume behavior, and data caching. These tests are straightforward to run with any active milestone.

**Commit integrity:** Both commits from SUMMARY.md (e674df0 for data_sources.py fix, a889fed for execute.md) confirmed present in git log with matching commit messages.

---

_Verified: 2026-03-21T16:00:00Z_
_Verifier: Claude (gsd-verifier)_
