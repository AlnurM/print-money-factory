# Phase 2: Milestone Lifecycle & State - Research

**Researched:** 2026-03-21
**Domain:** Claude Code workflow markdown, state management via markdown files, multimodal context handling
**Confidence:** HIGH

## Summary

Phase 2 replaces the stub workflow files (`workflows/new-milestone.md` and `workflows/status.md`) with full behavioral prompt documents that Claude reads and follows at runtime. It also introduces state management (reading/writing `.pmf/STATE.md`), sequence validation logic, context file scanning (`.pmf/context/`), and one-active-milestone enforcement. The "code" is markdown workflow instructions -- there is no traditional programming involved beyond what Claude executes at runtime (Read/Write/Bash/Glob tool calls).

The architecture is already established by Phase 1: commands are thin YAML-frontmatter markdown files in `commands/` that `@`-reference workflow files in `~/.pmf/workflows/`. The workflow files contain the actual behavioral instructions Claude follows. This phase fills two stubs with real content and ensures all `/brrr:*` commands share common preamble logic (context scanning, state validation).

**Primary recommendation:** Structure each workflow as a sequential instruction document with clear sections (preamble checks, main flow, output generation, state update). Use markdown with embedded examples for Claude to follow. All state lives in `.pmf/STATE.md` as a structured markdown document that Claude reads and writes using the Read/Write tools.

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions
- **D-01:** Guided conversation style -- Claude asks questions one by one, follows threads, challenges vague answers (not a structured form)
- **D-02:** Context file scan happens FIRST before any questions -- if files exist in .pmf/context/, parse them to inform the conversation
- **D-03:** Smart scope defaults based on idea complexity -- simple strategy = strategy+backtest+PineScript, complex = add tuning+risk management
- **D-04:** Success criteria defaults by strategy type: Trend (Sharpe>1.2, DD<30%), Mean-reversion (Sharpe>1.5, DD<20%), Breakout (Sharpe>1.0, DD<35%)
- **D-05:** Scope splitting is suggested only, not enforced -- user can override with "I know it's big, do it anyway"
- **D-06:** Creates .pmf/ directory in user's project on first run (per Phase 1 D-05)
- **D-07:** Outputs STRATEGY.md (from template) and STATE.md (from template) into .pmf/
- **D-08:** Determines phase list (discuss/research/plan/execute/verify) and records in STATE.md
- **D-09:** Sequence validation uses BOTH: STATE.md as primary (check current step), file existence as fallback (check if prerequisite artifacts exist like phase_N_plan.md)
- **D-10:** Out-of-sequence commands show clear error: what's missing, where you are, what to run next
- **D-11:** Phase artifacts named as `phase_N_step.md` -- e.g., phase_1_discuss.md, phase_1_plan.md
- **D-12:** One active milestone enforced -- new milestone only after current is approved via /brrr:verify --approved
- **D-13:** STATE.md history is structured entries (multi-line with timestamp, metrics, AI diagnosis summary)
- **D-14:** Phase artifacts are append-only -- history never overwritten, only new phases added
- **D-15:** Auto-detect on every /brrr:* command start -- check .pmf/context/ for new files. `--no-context` flag to skip scanning
- **D-16:** For images/screenshots: Claude reads via multimodal vision, writes detailed description, asks user to confirm/correct BEFORE incorporating
- **D-17:** Processed files tracked in STATE.md (record filename + processing date) -- files stay in place, not moved
- **D-18:** Supported types: PNG, JPG, PDF, any image format Claude can read. Text files read directly.
- **D-19:** Full ASCII tree showing every step (discuss/research/plan/execute/verify) with status icons per phase
- **D-20:** Always ends with actionable next step: "Next step: /brrr:plan"
- **D-21:** All output in English
- **D-22:** Shows milestone name, asset/timeframe, target metrics, and current phase progress

### Claude's Discretion
- Exact wording of scoping questions
- How to detect strategy type for default criteria
- STATE.md internal format details beyond the template
- Error message exact formatting
- How many context files can be processed at once

### Deferred Ideas (OUT OF SCOPE)
None -- discussion stayed within phase scope
</user_constraints>

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|-----------------|
| MILE-01 | `/brrr:new-milestone` creates milestone with strategy idea, scope, asset/data, success criteria | new-milestone workflow covers Steps 1-7 from spec |
| MILE-02 | Scope selection includes: strategy, backtest, tuning, risk management, PineScript export, MD instructions export | Scope checklist in the workflow with smart defaults |
| MILE-03 | System recommends scope splitting when selection is too large | Splitting suggestion logic with user override |
| MILE-04 | One active milestone at a time -- new only after current approved | Preamble check in new-milestone workflow |
| MILE-05 | `/brrr:status` shows ASCII tree of milestone progress, all phases, next step | Status workflow with tree rendering |
| STAT-01 | STATE.md tracks current milestone, status, all phases with step completion | STATE.md format specification |
| STAT-02 | STATE.md records best metrics per phase (Sharpe, DD, trades) | Best Results table in STATE.md |
| STAT-03 | Commands validate sequence -- cannot run execute without plan, verify without execute | Shared preamble pattern with sequence validation |
| STAT-04 | STRATEGY.md captures original hypothesis and scope from new-milestone | Template filling from scoping conversation |
| STAT-05 | Phase artifacts are append-only -- history never overwritten | Append-only pattern in STATE.md history |
| CTXT-01 | System checks `.pmf/context/` at start of each command for new files | Context scanning preamble section |
| CTXT-02 | System parses and describes context files, asks for confirmation before incorporating | Multimodal describe+confirm flow |
| CTXT-03 | Context files included in subsequent phase artifacts after confirmation | Tracking in STATE.md processed_context section |
</phase_requirements>

## Standard Stack

This phase has no traditional library dependencies. The "stack" is Claude Code's built-in tool set and markdown workflow files.

### Core
| Technology | Version | Purpose | Why Standard |
|------------|---------|---------|--------------|
| Claude Code slash commands | current | Command execution interface | The only runtime -- commands are markdown prompts |
| Markdown workflow files | N/A | Behavioral instructions for Claude | Established Phase 1 pattern (commands/ @-ref workflows/) |
| Read/Write/Bash/Glob tools | built-in | File I/O for state management | Only way Claude interacts with filesystem |

### Supporting
| Technology | Version | Purpose | When to Use |
|------------|---------|---------|-------------|
| YAML frontmatter | N/A | Command metadata (name, description, tools) | In command .md files only |
| Structured markdown | N/A | STATE.md and STRATEGY.md data format | All state persistence |

### Alternatives Considered
| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| Markdown STATE.md | JSON state file | Markdown is human-readable, editable, and Claude parses it natively. JSON would need explicit parsing logic in workflows |
| Inline workflow instructions | Separate Python state manager | Over-engineering -- Claude can read/write markdown directly. Adding code adds a dependency and complexity |
| Template variables ({{var}}) | No templating | Templates provide consistent structure; Claude fills them at runtime |

## Architecture Patterns

### Project Structure (what Phase 2 creates/modifies)
```
workflows/
  new-milestone.md     # REPLACE stub with full implementation (~200-300 lines)
  status.md            # REPLACE stub with full implementation (~100-150 lines)
  _preamble.md         # NEW: shared preamble logic (context scan + state validation)

# Created at runtime in user's project:
.pmf/
  STRATEGY.md          # Filled from template by new-milestone
  STATE.md             # Filled from template by new-milestone
  context/             # Directory created by new-milestone
  phases/              # Directory created by new-milestone
```

### Pattern 1: Shared Preamble (Context Scan + State Validation)

**What:** Every `/brrr:*` command starts with the same checks: scan for context files, validate state, verify sequence.

**When to use:** At the top of every workflow file.

**Implementation approach:** Create a `_preamble.md` file that other workflows `@`-reference, OR embed the preamble instructions directly in each workflow. Given that workflow files are behavioral prompts (not code), embedding is cleaner -- Claude reads the workflow top-to-bottom and follows it.

**Recommended: Embed preamble in each workflow** rather than a separate file. Reason: Claude reads @-referenced files as context, but inline instructions are followed more reliably in sequence. A shared preamble file would need to be @-referenced AND the workflow would need to say "follow _preamble.md first" -- adding indirection. Inline keeps it simple.

**Preamble sequence:**
```
1. Check if .pmf/ exists (if not, and this isn't new-milestone: error)
2. Read .pmf/STATE.md (if not new-milestone)
3. Check --no-context flag; if not set, scan .pmf/context/
4. For each new file in context/:
   a. Read it (images via multimodal, text directly, PDF via reader)
   b. Describe what you see
   c. Ask user to confirm understanding
   d. Record in STATE.md processed_context section
5. Validate command sequence (is this command allowed given current state?)
6. If out-of-sequence: show error with current position + next step
7. Proceed to main workflow
```

### Pattern 2: Guided Conversation Flow (new-milestone)

**What:** Claude asks questions one at a time, adapts based on answers, challenges vague responses.

**When to use:** The new-milestone scoping flow (Steps 1-7 from spec).

**Key design points:**
- The workflow file describes the CONVERSATION STRUCTURE, not a rigid form
- Each "step" is a section Claude reads and follows conversationally
- Claude has discretion on exact wording but must cover required topics
- The flow is: context scan -> idea -> scope -> splitting check -> data source -> criteria -> summary

**Example workflow structure:**
```markdown
## Step 2: Collect Strategy Idea

Ask the user to describe their trading idea. Listen for:
- Strategy type (trend, mean-reversion, breakout, arbitrage, custom)
- Key indicators or signals mentioned
- Asset class hints

If the idea mixes multiple concepts, help clarify:
- "You mentioned X, Y, and Z -- these are different approaches.
   Which is the core idea, and which are filters?"

Do NOT proceed until you have a clear, single-thesis hypothesis.
Record the strategy type for use in Step 6 (default criteria).
```

### Pattern 3: STATE.md as Structured Data

**What:** STATE.md is a markdown file that serves as both human-readable status AND machine-parseable state.

**When to use:** All state persistence.

**Format recommendation (extending the template):**

```markdown
# Print Money Factory -- State

## Status
- **Milestone:** v1
- **Name:** SMC + RSI Filter | BTC/USDT 4H
- **Status:** IN PROGRESS
- **Current Phase:** 1
- **Current Step:** plan
- **Created:** 2026-03-21
- **Last Updated:** 2026-03-21

## Scope
- [x] Strategy logic (entry/exit rules)
- [x] Backtesting & optimization
- [x] Parameter tuning
- [x] PineScript export
- [ ] Risk management
- [ ] MD instructions export

## Data Source
- **Asset:** BTC/USDT
- **Exchange/Source:** Binance via ccxt
- **Timeframe:** 4H
- **Date Range:** 2021-01-01 to 2024-12-31

## Success Criteria
- **Primary:** Sharpe Ratio > 1.5
- **Max Drawdown:** < 25%
- **Minimum Trades:** 30
- **Type:** Trend

## Phases
### Phase 1
- [x] discuss -- 2026-03-21
- [x] research -- 2026-03-21
- [x] plan -- 2026-03-21
- [x] execute -- Sharpe 1.58 | MaxDD -17.2% | Trades 52
- [x] verify -- verdict: debug

### Phase 2
- [x] discuss -- 2026-03-22
- [ ] research (skipped)
- [ ] plan
- [ ] execute
- [ ] verify

## Best Results
| Phase | Sharpe | Max DD | Trades | Verdict |
|-------|--------|--------|--------|---------|
| 1 | 1.58 | -17.2% | 52 | debug |

## Processed Context
| File | Processed | Description |
|------|-----------|-------------|
| chart_markup.png | 2026-03-21 | Order block zones at 42K and 38.5K, sweep entries on 4H |

## History
### 2026-03-21 -- Phase 1 verify
- **Metrics:** Sharpe 1.58, MaxDD -17.2%, WinRate 41%, Trades 52
- **Verdict:** debug
- **Diagnosis:** Strategy trend-dependent, failed in 2023-2024 sideways market. Recommend regime filter.

### 2026-03-21 -- Milestone created
- **Hypothesis:** SMC + RSI Filter on BTC/USDT 4H
- **Scope:** strategy, backtest, tuning, PineScript
```

**Key design choices:**
- Checkbox syntax `[x]`/`[ ]` for step completion -- universally understood
- Structured tables for best results and processed context
- History section is append-only (newest at top for quick reading)
- Each step completion includes a date
- Execute step includes inline metrics summary

### Pattern 4: Sequence Validation

**What:** Dual validation -- STATE.md primary + file existence fallback.

**Validation matrix:**

| Command | Requires STATE.md says | Requires files exist |
|---------|----------------------|---------------------|
| new-milestone | No active milestone (status != IN PROGRESS) | No .pmf/STATE.md with active milestone |
| discuss | Phase N has no discuss done yet | .pmf/STRATEGY.md exists |
| research | Phase N discuss is done | .pmf/phases/phase_N_discuss.md exists |
| plan | Phase N discuss done (research optional) | .pmf/phases/phase_N_discuss.md exists |
| execute | Phase N plan is done | .pmf/phases/phase_N_plan.md exists |
| verify | Phase N execute is done | .pmf/phases/phase_N_best_result.json exists |
| status | .pmf/ exists | .pmf/STATE.md exists |

**Error message pattern:**
```
[STOP] Cannot run {command} -- {prerequisite} has not been completed yet.

{Explanation of WHY the prerequisite matters}

Current position:
  {checkmark or empty for each step}

Next step: /brrr:{next_command}
```

### Pattern 5: ASCII Status Tree

**What:** Visual progress display matching the spec example.

**Format:**
```
Print Money Factory -- Status

  Milestone v1: SMC + RSI Filter | BTC/USDT 4H
  Target: Sharpe > 1.5 | Max DD < 25%
  -------------------------------------------
  Phase 1
    [DONE] discuss    strategy logic fixed
    [DONE] research   SMC implementations found
    [DONE] plan       walk-forward, 6 params
    [DONE] execute    Sharpe 1.58 | MaxDD -17.2% | 52 trades
    [DONE] verify     -> debug
  Phase 2
    [DONE] discuss    added ADX regime filter
    [WIP]  plan       in progress...
    [    ] execute
    [    ] verify

  Next step: /brrr:plan
```

Note: The spec uses emoji icons (checkmarks, spinners, empty boxes). Claude can output these. Using `[DONE]`/`[WIP]`/`[    ]` as text alternatives if emoji rendering is unreliable in terminal, but per the spec and D-19, use the actual icons: checkmark for done, spinner for in-progress, empty square for pending.

### Anti-Patterns to Avoid
- **Overloading workflow files with code:** Workflows are behavioral prompts, not programs. Don't try to encode complex logic -- describe what Claude should DO, not HOW to implement it in code.
- **Separate state validation code:** Don't create a Python or Node.js script to validate state. Claude reads STATE.md directly and applies the rules described in the workflow.
- **Moving/renaming context files:** D-17 says files stay in place. Only track processing status in STATE.md.
- **Hardcoding conversation scripts:** D-01 says guided conversation, not a form. The workflow should describe TOPICS to cover and RULES to follow, not exact question text.

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Markdown parsing | Custom parser script | Claude's native markdown reading (Read tool) | Claude understands markdown structure natively |
| Image/PDF analysis | External OCR/vision service | Claude's built-in multimodal capability (Read tool on image files) | Claude Code can read images directly |
| State validation logic | Python/Node validator script | Workflow instructions that Claude follows | Adding code adds complexity; Claude can reason about state from markdown |
| Template filling | Template engine (jinja2, etc.) | Claude reads template + fills variables via Write tool | Templates are simple {{variable}} patterns; Claude handles this trivially |
| Conversation flow engine | State machine or dialog framework | Natural language workflow instructions | Claude IS the conversation engine |

**Key insight:** This project's runtime IS Claude Code. Every "feature" is a set of instructions Claude follows. Don't add code layers between Claude and the user -- that's the entire design philosophy.

## Common Pitfalls

### Pitfall 1: Workflow Instructions Too Vague
**What goes wrong:** Claude doesn't follow the intended flow because instructions are ambiguous ("collect strategy information" vs "ask about entry signals, then exit signals, then stops").
**Why it happens:** Treating workflow markdown as documentation instead of behavioral instructions.
**How to avoid:** Write workflows as specific, sequential instructions. Each step should have: what to do, what to look for, what to output, when to proceed.
**Warning signs:** Claude skips steps, asks all questions at once, or produces inconsistent outputs.

### Pitfall 2: STATE.md Format Drift
**What goes wrong:** Different commands write STATE.md in slightly different formats, making it unparseable by subsequent commands.
**Why it happens:** No single canonical format definition; each workflow describes state updates independently.
**How to avoid:** Define the EXACT STATE.md format in the new-milestone workflow (which creates it) and reference that format in all other workflows. Include a complete example in each workflow's state-update section.
**Warning signs:** Status command fails to parse state; commands misread current phase.

### Pitfall 3: Context Scan Blocking Conversation
**What goes wrong:** Context file processing (describe + confirm) derails the main workflow, especially when multiple files exist.
**Why it happens:** The preamble processes ALL context files before any workflow-specific work begins.
**How to avoid:** Process context files sequentially but keep confirmations brief. Set a practical limit (e.g., 5 files per scan). For large batches, summarize and ask for batch confirmation.
**Warning signs:** User loses track of main objective; conversation is mostly about context files.

### Pitfall 4: Sequence Validation False Positives
**What goes wrong:** User is blocked from running a command they should be able to run (e.g., research is optional but validation blocks plan because research isn't "done").
**Why it happens:** Treating all steps as required in sequence validation.
**How to avoid:** Mark research as optional in STATE.md (use "skipped" status). Validation logic must know which steps are optional. The spec says research is optional -- plan should be allowed after discuss even without research.
**Warning signs:** Users get stuck and can't advance.

### Pitfall 5: new-milestone Doesn't Create Directory Structure
**What goes wrong:** Subsequent commands fail because .pmf/context/ or .pmf/phases/ directories don't exist.
**Why it happens:** The workflow focuses on conversation flow and forgets the filesystem setup.
**How to avoid:** Include explicit directory creation step in new-milestone workflow: create .pmf/, .pmf/context/, .pmf/phases/ using Bash mkdir -p.
**Warning signs:** First /brrr:discuss fails with "directory not found" errors.

## Code Examples

Since this phase produces markdown workflow files (not traditional code), "code examples" are workflow patterns.

### Example 1: new-milestone Workflow Structure

```markdown
# Workflow: new-milestone

## Preamble

### Check for active milestone
1. Check if `.pmf/STATE.md` exists in the current working directory
2. If it exists, read it and check the Status section
3. If status is "IN PROGRESS", STOP:

   [STOP] Cannot create a new milestone -- you already have an active one.

   Current milestone: {name}
   Status: {status}

   To start a new milestone:
   - Complete the current one: /brrr:verify --approved
   - Or abandon it manually by setting status to "ABANDONED" in .pmf/STATE.md

4. If no active milestone, proceed

### Scan context files
1. Check if `.pmf/context/` directory exists
2. If it exists, list all files using Glob
3. For each file not already in STATE.md processed_context:
   a. Read the file (images via Read tool -- Claude sees them visually)
   b. Describe what you see in detail
   c. Ask user: "Is this understanding correct?"
   d. If confirmed, note the description for use in conversation
   e. If corrected, update understanding
4. If --no-context flag present, skip this section

## Step 1: Setup

Create the directory structure if it doesn't exist:
- .pmf/
- .pmf/context/
- .pmf/phases/

## Step 2: Strategy Idea

Ask the user to describe their trading strategy idea.

Listen for and identify:
- Strategy type: trend-following, mean-reversion, breakout, or custom
- Asset class: crypto, stocks, forex
- Any specific indicators or signals mentioned
- Timeframe hints

If the idea is vague or mixes concepts, clarify before proceeding.

## Step 3: Scope Selection

Based on the strategy complexity, suggest a default scope:

**Simple strategies** (single indicator, classic pattern):
- [x] Strategy logic
- [x] Backtesting & optimization
- [x] PineScript export

**Complex strategies** (multiple signals, custom logic):
- [x] Strategy logic
- [x] Backtesting & optimization
- [x] Parameter tuning
- [x] Risk management
- [x] PineScript export

Present the suggestion and let the user modify.

## Step 4: Scope Splitting Check

If the user selected 5+ items, suggest splitting:
- Recommend what goes in v1 vs v2
- But respect user override ("I know it's big, do it anyway")

## Step 5: Data Source

Ask about the asset and determine data source:
- Crypto -> which exchange? -> ccxt
- Stocks -> daily or intraday? -> yfinance or polygon
- Forex -> daily or intraday? -> yfinance or dukascopy

Also ask about timeframe and date range.

## Step 6: Success Criteria

Based on strategy type detected in Step 2, offer defaults:
- Trend: Sharpe > 1.2, Max DD < 30%
- Mean-reversion: Sharpe > 1.5, Max DD < 20%
- Breakout: Sharpe > 1.0, Max DD < 35%

Let user adjust.

## Step 7: Summary and Confirmation

Display a summary of all decisions. Ask for confirmation.

## Step 8: Create Files

After confirmation:
1. Read templates/STRATEGY.md and templates/STATE.md
2. Fill in the template variables with collected information
3. Write .pmf/STRATEGY.md
4. Write .pmf/STATE.md with:
   - Status: IN PROGRESS
   - Current Phase: 1
   - Current Step: discuss (the next thing to do)
   - Phases section with Phase 1 checklist
5. Display: "Milestone created. Next step: /brrr:discuss"
```

### Example 2: status Workflow Structure

```markdown
# Workflow: status

## Preamble

### Check for .pmf/
1. Check if `.pmf/STATE.md` exists
2. If not: "No active milestone. Run /brrr:new-milestone to get started."
3. If exists, read it

### Context scan (if not --no-context)
[Same context scan as other workflows]

## Display Status

Read STATE.md and render the ASCII tree:

1. Extract: milestone name, asset/timeframe, target metrics
2. For each phase in the Phases section:
   - For each step: show icon based on status
     - Completed: checkmark icon
     - In progress: spinner icon
     - Not started: empty square icon
   - If step has metrics (execute), show inline
   - If step has verdict (verify), show inline
3. Determine next step from current position
4. Display the tree followed by "Next step: /brrr:{command}"

## No State Updates

This workflow is READ-ONLY. Do not modify STATE.md.
```

### Example 3: Context File Processing Pattern

```markdown
## Context File Processing

For each unprocessed file in .pmf/context/:

### Images (PNG, JPG, JPEG, GIF, WEBP)
1. Use the Read tool to view the image
2. Describe what you see in detail:
   - Chart patterns, indicators visible
   - Annotations or markup
   - Timeframe and asset if discernible
3. State your interpretation of how this relates to a trading strategy
4. Ask: "Is this understanding correct? Anything to add or correct?"
5. Wait for user response before proceeding

### PDF files
1. Use the Read tool with pages parameter to read the PDF
2. Summarize the content relevant to trading strategy
3. Ask for confirmation

### Text files (.txt, .md, .csv)
1. Read the file content directly
2. Summarize what's relevant
3. Ask for confirmation

### After confirmation
Record in STATE.md under Processed Context:
| {filename} | {date} | {one-line description} |
```

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| Rigid form-based input | Guided conversation (D-01) | This phase | More natural UX, Claude adapts to user's style |
| Single validation method | Dual: STATE.md + file existence (D-09) | This phase | More robust -- survives corrupted state or manual edits |
| Process then delete context files | Process, track, leave in place (D-17) | This phase | User can re-reference files; no data loss |

## Open Questions

1. **How should the workflow reference templates?**
   - What we know: Templates live at `~/.pmf/templates/STRATEGY.md` and `~/.pmf/templates/STATE.md` (installed by Phase 1). The command file already @-references `@~/.pmf/templates/STRATEGY.md` and `@~/.pmf/templates/STATE.md`.
   - What's unclear: Whether to @-reference templates from WITHIN the workflow file too, or rely on the command's @-reference already loading them into context.
   - Recommendation: Include @-references in the workflow file as well -- it's harmless if loaded twice and ensures templates are available regardless of how the workflow is invoked.

2. **Batch context file limit**
   - What we know: D-15 says auto-detect on every command. Many files could slow things down.
   - What's unclear: No explicit cap was set.
   - Recommendation: Process up to 5 new files per command invocation. If more than 5 new files, process first 5 and note "X more files detected -- run the command again to process more."

3. **How other workflows (discuss, research, etc.) will integrate the preamble**
   - What we know: Phase 3+ workflows need the same preamble (context scan, state validation).
   - What's unclear: Whether to update those workflow stubs now or leave them for their phases.
   - Recommendation: Leave Phase 3+ workflow stubs as-is. Document the preamble pattern clearly so future phases can adopt it. Optionally include a brief comment in each stub referencing the preamble pattern.

## Validation Architecture

### Test Framework
| Property | Value |
|----------|-------|
| Framework | Manual validation via Claude Code |
| Config file | None -- workflows are behavioral prompts |
| Quick run command | Run `/brrr:new-milestone` and verify output |
| Full suite command | Run full flow: new-milestone -> status -> out-of-sequence error |

### Phase Requirements -> Test Map
| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|-------------|
| MILE-01 | new-milestone creates STRATEGY.md + STATE.md | manual | Run `/brrr:new-milestone`, check .pmf/ | N/A |
| MILE-02 | Scope selection includes all options | manual | Verify workflow text includes all scope items | N/A |
| MILE-03 | Scope splitting suggested for large scopes | manual | Select all scope items, verify suggestion | N/A |
| MILE-04 | One active milestone enforced | manual | Try `/brrr:new-milestone` with active milestone | N/A |
| MILE-05 | Status shows ASCII tree | manual | Run `/brrr:status` after creating milestone | N/A |
| STAT-01 | STATE.md tracks milestone and phases | manual | Read .pmf/STATE.md after new-milestone | N/A |
| STAT-02 | Best metrics recorded | manual | Verified in later phases (execute populates this) | N/A |
| STAT-03 | Sequence validation works | manual | Try `/brrr:execute` without plan | N/A |
| STAT-04 | STRATEGY.md captures hypothesis | manual | Read .pmf/STRATEGY.md after new-milestone | N/A |
| STAT-05 | Append-only history | manual | Check STATE.md history section format | N/A |
| CTXT-01 | Context scan on every command | manual | Drop file in .pmf/context/, run status | N/A |
| CTXT-02 | Describe + confirm flow for images | manual | Drop image in .pmf/context/, run command | N/A |
| CTXT-03 | Context included after confirmation | manual | Confirm context, check it appears in artifacts | N/A |

### Sampling Rate
- **Per task commit:** Read workflow file, verify structure and completeness
- **Per wave merge:** Run `/brrr:new-milestone` end-to-end in a test project
- **Phase gate:** Full flow validation (new-milestone + status + sequence error + context scan)

### Wave 0 Gaps
None -- this phase produces markdown workflow files, not testable code. Validation is behavioral (run the commands and verify output).

## Sources

### Primary (HIGH confidence)
- `PROJECT.md` (task.md in repo) -- Original spec with full new-milestone flow Steps 1-7, STATE.md format, status tree format, context file handling
- `templates/STATE.md` -- State template structure (Phase 1 output)
- `templates/STRATEGY.md` -- Strategy template structure (Phase 1 output)
- `commands/new-milestone.md` -- Command file with @-references (Phase 1 output)
- `commands/status.md` -- Command file (Phase 1 output)
- `bin/install.mjs` -- How commands reference workflows pattern

### Secondary (MEDIUM confidence)
- `02-CONTEXT.md` -- All 22 locked decisions from discuss phase
- Phase 1 workflow stubs -- Established file naming and location patterns

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH -- no external dependencies; architecture fully established by Phase 1
- Architecture: HIGH -- all patterns flow directly from Phase 1 conventions and the original spec
- Pitfalls: HIGH -- pitfalls identified from concrete experience with the existing codebase and the spec requirements

**Research date:** 2026-03-21
**Valid until:** 2026-04-21 (stable domain -- markdown workflow patterns don't change)
