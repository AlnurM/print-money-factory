# Phase 2: Milestone Lifecycle & State - Context

**Gathered:** 2026-03-21
**Status:** Ready for planning

<domain>
## Phase Boundary

Implement `/brrr:new-milestone` (guided scoping flow), `/brrr:status` (ASCII progress tree), state management (STATE.md read/write, sequence validation), context file support (.pmf/context/ scanning and parsing), and one-active-milestone enforcement. This phase fills the workflow stubs created in Phase 1 with real behavior.

</domain>

<decisions>
## Implementation Decisions

### Scoping flow (/brrr:new-milestone)
- **D-01:** Guided conversation style — Claude asks questions one by one, follows threads, challenges vague answers (not a structured form)
- **D-02:** Context file scan happens FIRST before any questions — if files exist in .pmf/context/, parse them to inform the conversation
- **D-03:** Smart scope defaults based on idea complexity — simple strategy = strategy+backtest+PineScript, complex = add tuning+risk management
- **D-04:** Success criteria defaults by strategy type: Trend (Sharpe>1.2, DD<30%), Mean-reversion (Sharpe>1.5, DD<20%), Breakout (Sharpe>1.0, DD<35%)
- **D-05:** Scope splitting is suggested only, not enforced — user can override with "I know it's big, do it anyway"
- **D-06:** Creates .pmf/ directory in user's project on first run (per Phase 1 D-05)
- **D-07:** Outputs STRATEGY.md (from template) and STATE.md (from template) into .pmf/
- **D-08:** Determines phase list (discuss/research/plan/execute/verify) and records in STATE.md

### State tracking
- **D-09:** Sequence validation uses BOTH: STATE.md as primary (check current step), file existence as fallback (check if prerequisite artifacts exist like phase_N_plan.md)
- **D-10:** Out-of-sequence commands show clear error: what's missing, where you are, what to run next (per spec: "⛔ Нельзя запустить execute без plan...")
- **D-11:** Phase artifacts named as `phase_N_step.md` — e.g., phase_1_discuss.md, phase_1_plan.md, phase_2_discuss.md (matches original spec)
- **D-12:** One active milestone enforced — new milestone only after current is approved via /brrr:verify --approved
- **D-13:** STATE.md history is structured entries (multi-line with timestamp, metrics, AI diagnosis summary) — richer context for debug cycles
- **D-14:** Phase artifacts are append-only — history never overwritten, only new phases added

### Context files (.pmf/context/)
- **D-15:** Auto-detect on every /brrr:* command start — check .pmf/context/ for new files. `--no-context` flag to skip scanning
- **D-16:** For images/screenshots: Claude reads via multimodal vision, writes detailed description of what it sees, asks user to confirm/correct BEFORE incorporating
- **D-17:** Processed files tracked in STATE.md (record filename + processing date) — files stay in place, not moved
- **D-18:** Supported types: PNG, JPG, PDF, any image format Claude can read. Text files read directly.

### Status display (/brrr:status)
- **D-19:** Full ASCII tree showing every step (discuss/research/plan/execute/verify) with status icons per phase — matches the spec example
- **D-20:** Always ends with actionable next step: "Следующий шаг: /brrr:plan" — user always knows what to do
- **D-21:** All output in English
- **D-22:** Shows milestone name, asset/timeframe, target metrics, and current phase progress

### Claude's Discretion
- Exact wording of scoping questions
- How to detect strategy type for default criteria
- STATE.md internal format details beyond the template
- Error message exact formatting
- How many context files can be processed at once

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Project spec
- `PROJECT.md` — Original project spec with full new-milestone flow (Steps 1-7), discuss phase, status display format, and context file handling

### Templates (Phase 1 outputs)
- `templates/STATE.md` — State template with placeholder variables to fill
- `templates/STRATEGY.md` — Strategy template with hypothesis, asset, scope, criteria fields

### Existing workflow stubs (Phase 1 outputs)
- `workflows/new-milestone.md` — Stub to replace with real implementation
- `workflows/status.md` — Stub to replace with real implementation

### Commands (Phase 1 outputs)
- `commands/new-milestone.md` — Thin command that @-references workflow
- `commands/status.md` — Thin command that @-references workflow

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- `templates/STATE.md`: State template with status, phases, best results, history sections — fill variables at runtime
- `templates/STRATEGY.md`: Strategy template with hypothesis, asset, scope, criteria — fill from scoping conversation
- `bin/install.mjs`: Pattern for how commands @-reference workflows (D-03 from Phase 1)

### Established Patterns
- Commands are thin markdown with YAML frontmatter, @-reference workflows from `~/.pmf/workflows/`
- All Python execution via `~/.pmf/venv/bin/python` full path
- Workflows are markdown files that Claude reads and follows as behavioral prompts

### Integration Points
- `~/.pmf/workflows/new-milestone.md` — stub to be replaced with full implementation
- `~/.pmf/workflows/status.md` — stub to be replaced with full implementation
- `.pmf/` in user's project — created by new-milestone, read by all subsequent commands
- `.pmf/context/` — scanned by all commands for new files
- `.pmf/STRATEGY.md` and `.pmf/STATE.md` — created by new-milestone, read/updated by all commands
- `.pmf/phases/` — artifact directory for phase outputs

</code_context>

<specifics>
## Specific Ideas

- The scoping flow should feel like the PROJECT.md spec Steps 1-7: разбор контекста → идея → скоуп → проверка на разбивку → данные → критерии → итог
- Error messages for out-of-sequence commands should explain WHY the sequence matters (not just "error"), like the spec's "plan определяет параметры и метод оптимизации — без него execute не знает что именно гонять"
- Status tree should look like the spec's ASCII example with ✅/🔄/⬜ icons

</specifics>

<deferred>
## Deferred Ideas

None — discussion stayed within phase scope

</deferred>

---

*Phase: 02-milestone-lifecycle-state*
*Context gathered: 2026-03-21*
