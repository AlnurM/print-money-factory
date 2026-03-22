# Phase 7: Maintenance Tooling - Context

**Gathered:** 2026-03-22
**Status:** Ready for planning

<domain>
## Phase Boundary

Add `/brrr:doctor` diagnostic command and silent auto version check across all `/brrr:*` commands. Doctor checks installation health. Version check nudges users to update.

</domain>

<decisions>
## Implementation Decisions

### Doctor output format
- **D-01:** `/brrr:doctor` displays a pass/fail checklist with one line per check. Format: `[PASS] Python 3.14 detected` or `[FAIL] venv missing — run npx print-money-factory install`
- **D-02:** Checks to run (in order): Python version (>=3.10), venv exists at `~/.pmf/venv/`, core imports work (`import pandas, numpy, ccxt, yfinance, plotly, optuna, ta, matplotlib, scipy, jinja2`), command files present in `~/.claude/commands/brrr/`, workflow files present in `~/.pmf/workflows/`, reference files present in `~/.pmf/references/`
- **D-03:** Each failing check includes a one-line fix suggestion (e.g., "run `npx print-money-factory install`" or "run `~/.pmf/venv/bin/pip install -r requirements.txt`")
- **D-04:** Doctor ends with a summary line: "X/Y checks passed" with overall HEALTHY or NEEDS ATTENTION verdict

### Version check behavior
- **D-05:** Version check runs silently at the start of every `/brrr:*` workflow via a preamble section. It never blocks or delays command execution.
- **D-06:** Check frequency: once per 24 hours, gated by a timestamp file at `~/.pmf/.last_version_check`. If the file's mtime is within 24h, skip the check entirely.
- **D-07:** Check mechanism: read `~/.pmf/.version` for current version, run `npm view @print-money-factory/cli version` for latest. If different, display: `Update available: v{current} → v{latest}. Run /brrr:update`
- **D-08:** On network failure (npm view fails): silently skip — no error, no notice. Version check is best-effort.
- **D-09:** Notice position: printed at the very top of command output, before the workflow begins, as a single line.

### Claude's Discretion
- Exact command/workflow file structure for `/brrr:doctor`
- Whether to add the version check preamble to each workflow file or to a shared preamble file
- Whether to check reference file count vs just directory existence

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Command pattern
- `commands/status.md` — Example thin command structure with allowed-tools and @-reference
- `commands/update.md` — Existing version-related command

### Install script
- `bin/install.mjs` — Writes `~/.pmf/.version` with version, installed date, package name (line 126)

### Workflow pattern
- `workflows/status.md` — Example workflow structure for reference

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- `~/.pmf/.version` JSON file already exists with `version`, `installed`, `package` fields
- `bin/install.mjs` has `detectPython()` function that returns `{path, version}` — doctor could reuse this pattern
- All commands follow the thin-command-@-ref-workflow pattern

### Established Patterns
- Commands: frontmatter (name, description, allowed-tools) + objective + execution_context + process
- Workflows: behavioral markdown with step-by-step instructions for Claude
- Install script: uses `execSync` for Python detection, `existsSync` for file checks

### Integration Points
- Doctor: new `commands/doctor.md` + `workflows/doctor.md` pair
- Version check: preamble addition to existing workflows (or shared preamble)
- `~/.pmf/.last_version_check` timestamp file (new)

</code_context>

<specifics>
## Specific Ideas

No specific requirements — standard CLI diagnostic patterns apply.

</specifics>

<deferred>
## Deferred Ideas

None — discussion stayed within phase scope

</deferred>

---

*Phase: 07-maintenance-tooling*
*Context gathered: 2026-03-22*
