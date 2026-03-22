---
phase: 01-package-scaffolding-install
verified: 2026-03-21T13:00:00Z
status: passed
score: 16/16 must-haves verified
re_verification: false
---

# Phase 1: Package Scaffolding & Install Verification Report

**Phase Goal:** User can install the package and have a working foundation -- commands directory, Python venv, reference patterns, and templates all in place
**Verified:** 2026-03-21
**Status:** passed
**Re-verification:** No -- initial verification

---

## Goal Achievement

### Observable Truths

| # | Truth | Status | Evidence |
|---|-------|--------|----------|
| 1 | npx print-money-factory install copies 8 command .md files to ~/.claude/commands/brrr/ | VERIFIED | `ls ~/.claude/commands/brrr/*.md` returns 8 files (discuss.md, execute.md, new-milestone.md, plan.md, research.md, status.md, update.md, verify.md) |
| 2 | Install creates ~/.pmf/venv/ with pandas, numpy, ccxt, yfinance, plotly, ta, matplotlib, optuna importable | VERIFIED | `~/.pmf/venv/bin/python -c "import pandas, numpy, ccxt, yfinance, plotly, ta, matplotlib, optuna"` exits 0 with ALL OK |
| 3 | Install on system without Python 3.10+ fails with clear error naming the minimum version | VERIFIED | bin/install.mjs detectPython() prints "Error: Python 3.10+ is required but was not found" with install instructions, then calls process.exit(1) |
| 4 | Running install twice completes without errors and does not corrupt existing setup | VERIFIED | existsSync(VENV_DIR) && existsSync(PYTHON_BIN) path triggers "Updating existing venv..." via pip upgrade. 01-04-SUMMARY.md confirms idempotent reinstall passed with 8 files intact post-reinstall |
| 5 | Package contains commands/, workflows/, templates/, references/ directory structure | VERIFIED | All 4 directories exist in repo root and package.json files array includes all 4. Installed: 8 commands, 7 workflows, 4 templates, 18+ references |
| 6 | Each command .md has frontmatter with name/description/allowed-tools and @~/.pmf/workflows/ reference | VERIFIED | 7 of 8 commands have @~/.pmf/workflows/ (update.md intentionally excluded per decision D-04 -- uses inline process). All 8 have name: brrr: prefix frontmatter |
| 7 | All 9 core metrics compute correctly against known-answer test cases | VERIFIED | `cd ~/.pmf/references && ~/.pmf/venv/bin/python -m pytest test_metrics.py -v` shows 32 passed in 0.05s |
| 8 | Metrics module accepts both trade log input and daily returns series input | VERIFIED | compute_all_metrics signature accepts trades, daily_returns, equity_curve. TestComputeAllMetrics::test_with_trade_log and test_with_daily_returns both pass |
| 9 | compute_all_metrics returns a dict with all 9 metric keys | VERIFIED | metrics.py line 286: compute_all_metrics returns dict with sharpe_ratio, sortino_ratio, calmar_ratio, max_drawdown, win_rate, profit_factor, expectancy, trade_count, net_pnl |
| 10 | Edge cases handled: empty trades, zero std, single bar, all winners, all losers | VERIFIED | TestWinRate, TestProfitFactor, TestSharpeRatio etc all include empty/edge tests -- all 32 pass |
| 11 | Backtest engine skeleton enforces anti-lookahead: signals use history[:i+1], execution at next bar open | VERIFIED | backtest_engine.py line 78: `history = df.iloc[:i+1]`, line 90: `execution_price = df.iloc[i]['open']`, RULE 1/2/3 comments present |
| 12 | Backtest engine imports compute_all_metrics from metrics module | VERIFIED | backtest_engine.py line 17: `from metrics import compute_all_metrics` |
| 13 | Data source adapters provide load_ccxt(), load_yfinance(), load_csv() functions | VERIFIED | data_sources.py lines 85, 190, 262: all three functions defined, with validate_ohlcv() helper at line 17 |
| 14 | PineScript template has valid v5 structure with strategy() call | VERIFIED | templates/pinescript-template.pine starts with //@version=5 and contains strategy() call. All 3 examples also contain //@version=5 and strategy.entry calls |
| 15 | Template files exist for STRATEGY.md, STATE.md, pinescript-template.pine, report-template.html | VERIFIED | All 4 files present in templates/. STRATEGY.md has Hypothesis section, STATE.md has Status/Phases/Best Results/History, report-template.html has DOCTYPE html and plotly script reference |
| 16 | Workflow stub files exist for all 7 commands | VERIFIED | 7 workflow stubs in workflows/ (new-milestone, discuss, research, plan, execute, verify, status) -- all contain "placeholder" text. Installed to ~/.pmf/workflows/ (7 files) |

**Score:** 16/16 truths verified

---

### Required Artifacts

| Artifact | Expected | Status | Details |
|----------|----------|--------|---------|
| `package.json` | npm package metadata with bin entry point | VERIFIED | Contains `"print-money-factory": "./bin/install.mjs"`, `"type": "module"`, `"engines": {"node": ">=18"}`, all 6 directories in files array |
| `bin/install.mjs` | Install script: copies files, creates venv, verifies deps | VERIFIED | 188 lines, shebang present, stdlib-only (0 require() calls), detectPython + copyDirRecursive + idempotent venv logic |
| `requirements.txt` | Python dependencies for venv | VERIFIED | 14 lines including pandas, numpy, matplotlib, plotly, optuna, ccxt, yfinance, scipy, ta, jinja2, tabulate, requests, pyyaml, pytest |
| `commands/execute.md` | Thin slash command entry point with workflow ref | VERIFIED | Contains `name: brrr:execute` and `@~/.pmf/workflows/execute.md` reference |
| `references/metrics.py` | Fixed financial metrics module with 9 metrics + compute_all_metrics | VERIFIED | 286 lines, 10 functions: 9 individual metrics + compute_all_metrics |
| `references/test_metrics.py` | Known-answer unit tests for all 9 metrics + edge cases | VERIFIED | 282 lines, 32 test functions across 10 test classes |
| `references/conftest.py` | Shared pytest fixtures | VERIFIED | 66 lines, sample_trades (10 trades), sample_returns (252 days), sample_equity fixtures |
| `references/backtest_engine.py` | Event-loop backtest skeleton with anti-lookahead enforcement | VERIFIED | 240 lines, calculate_signal stub, run_backtest event loop, RULE 1/2/3 comments, next-bar execution |
| `references/backtest-engine.md` | Pattern guide with anti-lookahead rules | VERIFIED | 227 lines (exceeds 50-line minimum), Anti-Lookahead section with examples of violations |
| `references/data_sources.py` | Ready-to-use data loading functions | VERIFIED | 333 lines (exceeds 80-line minimum), load_ccxt, load_yfinance, load_csv, validate_ohlcv |
| `templates/STRATEGY.md` | Milestone hypothesis scaffold | VERIFIED | Contains Hypothesis, Asset & Timeframe, Scope, Success Criteria, Original Idea sections |
| `templates/pinescript-template.pine` | PineScript v5 skeleton | VERIFIED | Starts with //@version=5, contains strategy() call with template variables |
| `references/pinescript-examples/*.pine` | 3 complete PineScript v5 examples | VERIFIED | trend-following (1 strategy.entry), mean-reversion (2), breakout (2) -- all valid v5 |
| `templates/report-template.html` | Plotly HTML report scaffold | VERIFIED | DOCTYPE html present, plotly CDN reference (pinned to v2.35.2), placeholder divs |
| `.npmignore` | Excludes .planning/, .git/, .claude/ | VERIFIED | All three exclusion patterns present |

---

### Key Link Verification

| From | To | Via | Status | Details |
|------|-----|-----|--------|---------|
| `package.json` | `bin/install.mjs` | bin field maps package name to install script | VERIFIED | `"print-money-factory": "./bin/install.mjs"` at line 6 |
| `bin/install.mjs` | `requirements.txt` | pip install -r requirements.txt inside venv | VERIFIED | requirements.txt referenced at lines 140, 159 in both upgrade and fresh install paths |
| `commands/*.md` (7) | `~/.pmf/workflows/` | @-reference in execution_context | VERIFIED | 7 of 8 command files contain @~/.pmf/workflows/ (update.md intentionally omitted per D-04) |
| `references/test_metrics.py` | `references/metrics.py` | import of all metric functions | VERIFIED | `from metrics import (` at line 8 imports all metric functions |
| `references/test_metrics.py` | `references/conftest.py` | pytest fixture usage | VERIFIED | sample_trades, sample_returns, sample_equity fixtures defined in conftest.py at lines 8, 53, 64 |
| `references/backtest_engine.py` | `references/metrics.py` | import compute_all_metrics | VERIFIED | `from metrics import compute_all_metrics` at line 17 |
| `references/data_sources.py` | ccxt/yfinance | library imports for data loading | VERIFIED | `import ccxt` at line 114 (inside load_ccxt), `import yfinance as yf` at line 215 (inside load_yfinance) -- lazy import pattern |

---

### Requirements Coverage

| Requirement | Source Plan | Description | Status | Evidence |
|-------------|-------------|-------------|--------|----------|
| INST-01 | 01-01 | User can install via `npx print-money-factory install` -- copies commands to `~/.claude/commands/brrr/` | SATISFIED | 8 command files installed to ~/.claude/commands/brrr/, install.mjs copies via copyDirRecursive |
| INST-02 | 01-01 | Install creates isolated Python venv with all backtest dependencies | SATISFIED | ~/.pmf/venv/ created with pandas, numpy, ccxt, yfinance, plotly, ta, matplotlib, optuna all importable |
| INST-03 | 01-01 | Install detects Python 3.10+ and fails gracefully with clear error if missing | SATISFIED | detectPython() checks python3/python/py-3, exits with actionable error message naming minimum version |
| INST-04 | 01-01 | Install is idempotent -- running twice doesn't break anything | SATISFIED | existsSync check triggers pip upgrade path on second run; verified in 01-04 integration test |
| INST-05 | 01-01 | `/brrr:update` checks GitHub for new version, shows changelog, updates commands and workflows | SATISFIED (scoped) | Decision D-04 explicitly chose "idempotent install IS the update mechanism" over GitHub check. update.md reads current version, runs npx install, reports version change. Changelog via version comparison. This is a deliberate scope reduction per CONTEXT.md D-04, accepted in DISCUSSION-LOG. |
| ARCH-01 | 01-01 | npm package structure mirrors GSD: commands/, workflows/, templates/, references/ | SATISFIED | All 4 directories present in package, included in package.json files array, copied to ~/.pmf/ on install |
| ARCH-02 | 01-01 | Commands are thin markdown files that @-reference workflow files | SATISFIED | 7 of 8 commands @-reference ~/.pmf/workflows/; update.md uses inline process per design decision D-04 |
| ARCH-03 | 01-02 | Fixed metrics module (not regenerated by Claude) with unit tests for financial calculations | SATISFIED | metrics.py (286 lines) with 9 metrics + compute_all_metrics; 32 known-answer tests all pass in 0.05s |
| ARCH-04 | 01-03 | Reference backtest engine patterns for Claude to adapt per strategy | SATISFIED | backtest_engine.py (240 lines) with calculate_signal stub, anti-lookahead event loop; backtest-engine.md (227 lines) with pattern guide |
| ARCH-05 | 01-03 | Template files: STRATEGY.md, STATE.md, pinescript-template.pine, report-template.html | SATISFIED | All 4 template files exist with correct sections. 3 PineScript examples also present |

**Orphaned requirements check:** No requirements mapped to Phase 1 in REQUIREMENTS.md were unaccounted for. All 10 IDs (INST-01 through INST-05, ARCH-01 through ARCH-05) are covered by plans 01-01, 01-02, 01-03.

---

### Anti-Patterns Found

| File | Line | Pattern | Severity | Impact |
|------|------|---------|----------|--------|
| None found | - | - | - | - |

No TODO/FIXME/PLACEHOLDER markers in any implementation file. No empty return stubs. No console.log-only handlers. Workflow stubs in `workflows/` intentionally contain placeholder text as documented design (Phase 1 explicitly scopes workflows as stubs for future phases).

---

### Human Verification Required

#### 1. Claude Code Command Discovery

**Test:** Open a new Claude Code session (or reload), type `/brrr:` and verify autocomplete shows all 8 commands.
**Expected:** Autocomplete list shows: new-milestone, discuss, research, plan, execute, verify, status, update
**Why human:** Claude Code's command discovery reads ~/.claude/commands/ at session start -- cannot verify file system presence translates to UI recognition programmatically.

**Note:** 01-04-SUMMARY.md documents this was verified by the human during Plan 04 Task 2 (human-verify gate was approved), confirming all 8 /brrr:* commands appeared in Claude Code autocomplete.

---

### Notes on INST-05 Scope

The REQUIREMENTS.md definition for INST-05 states "checks GitHub for new version, shows changelog." The actual implementation in update.md reports version change (before/after version numbers) but does not make a GitHub API call or fetch a CHANGELOG file. This was an explicit design decision documented in CONTEXT.md D-04 ("idempotent install IS the update mechanism") and confirmed in DISCUSSION-LOG.md ("npx reinstall" was the chosen option). The requirement is marked SATISFIED (scoped) because the core user need -- "update commands and workflows to latest version" -- is fully met. The "changelog" aspect is partially met via version number comparison. If full changelog display is desired, that would be a future enhancement.

---

## Summary

Phase 1 goal is achieved. The user can run `npx print-money-factory install` and receive:

1. 8 working slash commands at `~/.claude/commands/brrr/` that Claude Code recognizes
2. A managed Python venv at `~/.pmf/venv/` with all 8 required backtest packages installed
3. Reference patterns (backtest engine, data sources, pitfalls catalog) at `~/.pmf/references/`
4. Tested metrics module (32 tests, all passing) as the trust anchor for financial calculations
5. PineScript templates and 3 complete examples at `~/.pmf/references/pinescript-examples/`
6. Project templates (STRATEGY.md, STATE.md, report HTML) at `~/.pmf/templates/`
7. Workflow stubs at `~/.pmf/workflows/` ready for Phase 2-5 implementations
8. Idempotent reinstall that upgrades without breaking existing state

All 10 requirement IDs (INST-01 through INST-05, ARCH-01 through ARCH-05) are satisfied. No blocker anti-patterns found. 32/32 metrics tests pass. Install verified end-to-end including human confirmation of Claude Code command discovery.

---

_Verified: 2026-03-21_
_Verifier: Claude (gsd-verifier)_
