# Workflow: status

Display milestone progress as an ASCII tree with next step recommendation.
This workflow is READ-ONLY -- it does not modify any files.

---

## Preamble: Version Check

**This check is silent and best-effort. It MUST NOT block or delay the workflow.**

1. Check if the version check was done recently:
   Run via Bash: `find ~/.pmf/.last_version_check -mtime -1 2>/dev/null`
   - If the command outputs the filename, the check was done within the last 24 hours -- SKIP the rest of this preamble and proceed to the next section.
   - If the command outputs nothing (file missing or older than 24h), continue.

2. Read `~/.pmf/.version` to get the current installed version:
   - Use the Read tool to read `~/.pmf/.version` and parse the JSON to extract the `version` field.
   - If the file does not exist, SKIP the rest of this preamble silently.

3. Check npm for the latest version:
   Run via Bash: `npm view @print-money-factory/cli version 2>/dev/null`
   - If the command fails (network error, package not found), SKIP silently -- no error, no notice.

4. Compare versions:
   - If the npm version differs from the installed version, display exactly:
     `Update available: v{current} -> v{latest}. Run /brrr:update`
   - If versions match, display nothing.

5. Update the timestamp file:
   Run via Bash: `touch ~/.pmf/.last_version_check`
   This gates the check to once per 24 hours.

---

## Section 1: Check for Active Milestone

1. Check if `.pmf/STATE.md` exists in the current working directory using the Read tool.
2. If the file does NOT exist or `.pmf/` directory does not exist:
   - Display:
     ```
     No active milestone. Run /brrr:new-milestone to get started.
     ```
   - STOP. Do not continue.
3. If found, read the entire `.pmf/STATE.md` file and proceed to Section 2.

---

## Section 2: Context Scan (optional)

1. If the user passed `--no-context`, skip this section entirely.
2. Otherwise, check if `.pmf/context/` directory exists using Glob.
3. If it exists, list all files in `.pmf/context/`.
4. Read the **Processed Context** table from STATE.md to get already-processed filenames.
5. For each file NOT already in the Processed Context table (up to 5 new files):
   - Read the file:
     - **Images** (PNG, JPG, JPEG, GIF, WEBP): Use the Read tool -- Claude sees them visually via multimodal.
     - **PDF files**: Use the Read tool with `pages` parameter (e.g., pages "1-5" for large PDFs).
     - **Text files** (.txt, .md, .csv): Read content directly.
   - Describe what you see and how it relates to the trading strategy.
   - Use AskUserQuestion with header "Context", question "Is this understanding correct?", options: "Yes, correct" (confirm and continue), "Not quite" (user explains correction via Other).
   - **Important:** Since the status command has no Write permission, you cannot update STATE.md.
     Inform the user: "New context file detected: {filename}. Context will be processed on your next /brrr: command that modifies state."
6. If more than 5 new files exist, note: "{N} more context files detected -- they will be shown on subsequent commands."

---

## Section 3: Parse STATE.md

Extract the following data from the `.pmf/STATE.md` file you read in Section 1:

### From ## Status section:
- **milestone_name**: The value after "Milestone:" (e.g., "v1")
- **milestone_status**: The value after "Status:" (e.g., "IN PROGRESS", "APPROVED", "ABANDONED")
- **current_phase**: The number after "Current Phase:" (e.g., 2)
- **current_step**: The value after "Current Step:" (e.g., "plan")

### From ## Data Source section:
- **asset**: The value after "Asset:" (e.g., "BTC/USDT")
- **timeframe**: The value after "Timeframe:" (e.g., "4H")

### From ## Success Criteria section:
- **sharpe_target**: The number in "Sharpe Ratio > {N}" (e.g., 1.5)
- **maxdd_target**: The number in "Max Drawdown: < {N}%" (e.g., 25)
- **strategy_type**: The value after "Type:" (e.g., "Trend")

### From ## Phases section:
For each Phase heading (### Phase N):
- For each step line (discuss, research, plan, execute, verify):
  - **completed**: `[x]` means completed, `[ ]` means not completed
  - **skipped**: line contains "skipped" or "optional" and is unchecked in a completed phase
  - **description**: any text after the `--` on the checkbox line (dates, metrics, notes)
- The step matching `current_step` in the `current_phase` is the Work-In-Progress step.

### From ## Best Results section:
- Parse the markdown table rows. Each row has: Phase, Sharpe, Max DD, Trades, Verdict.
- Store all rows for rendering later.

---

## Section 4: Render ASCII Tree

Using the parsed data from Section 3, render the status display in this exact format:

```
Print Money Factory -- Status

  Milestone: {milestone_name} | {asset} {timeframe}
  Target: Sharpe > {sharpe_target} | Max DD < {maxdd_target}%
  -------------------------------------------
  Phase 1
    [DONE] discuss    {description or date}
    [SKIP] research   skipped
    [DONE] plan       {description}
    [DONE] execute    Sharpe {value} | MaxDD {value}% | {N} trades
    [DONE] verify     -> {verdict}
  Phase 2
    [DONE] discuss    {description}
    [WIP]  plan       in progress...
    [    ] execute
    [    ] verify

  Next step: `/brrr:{command}`
```

### Icon rules

Determine the icon for each step using these rules in order:

1. **Completed** -- the checkbox is `[x]` in STATE.md:
   - Display: `[DONE]`

2. **Work-In-Progress** -- the step matches `current_step` AND the phase matches `current_phase`, AND the checkbox is `[ ]`:
   - Display: `[WIP] `  (note the extra trailing space for column alignment)

3. **Skipped** -- the line contains "skipped" or the step is "research" marked as unchecked in a phase where later steps are already completed:
   - Display: `[SKIP]`

4. **Not started** -- checkbox is `[ ]` and none of the above apply:
   - Display: `[    ]`  (4 spaces inside brackets)

### Step description rules

- **discuss**: Show the text after `--` on the checkbox line (usually a date or brief note).
- **research**: If skipped, show "skipped". If completed, show the description after `--`.
- **plan**: Show the text after `--` on the checkbox line.
- **execute**: If completed (`[x]`), show inline metrics: `Sharpe {value} | MaxDD {value}% | {N} trades`. Extract these from the checkbox line text (format: "Sharpe X | MaxDD X% | Trades N") or from the Best Results table for that phase.
- **verify**: If completed (`[x]`), show the verdict: `-> {verdict}` (e.g., "-> debug", "-> mint").
- **Any step in progress** (`[WIP]`): Show "in progress..."
- **Any step not started** (`[    ]`): Show nothing (leave blank after the step name).

### Column alignment

Align step names to the same column and descriptions to the same starting column for readability. Step names are: discuss, research, plan, execute, verify. Pad shorter names with spaces so descriptions start at the same column.

---

## Section 5: Determine Next Step

After rendering the tree, determine the actionable next step:

1. Read `current_phase` and `current_step` from the parsed STATE.md data.
2. The current step IS the next action the user needs to take.
3. Display at the bottom of the tree:
   ```
   Next step: `/brrr:{current_step}`
   ```
4. **Special cases:**
   - If `milestone_status` is "APPROVED" or "CLOSED":
     ```
     Milestone complete! Strategy approved and exported.
     ```
   - If `milestone_status` is "ABANDONED":
     ```
     Milestone abandoned. Run /brrr:new-milestone to start fresh.
     ```

---

## Section 6: Best Results Summary

After the tree and next step line, check if the Best Results table has any data rows.

If there are rows, render the table:

```
  Best Results:
  | Phase | Sharpe | Max DD  | Trades | Verdict |
  |-------|--------|---------|--------|---------|
  | 1     | 1.58   | -17.2%  | 52     | debug   |
  | 2     | 2.01   | -12.8%  | 67     | mint    |
```

If the Best Results table is empty (no data rows), skip this section entirely -- do not show the heading or an empty table.

---

## Section 7: Scope Progress (if available)

If the ## Scope section exists in STATE.md and has checkbox items, display a brief scope summary after Best Results:

```
  Scope:
    [x] Strategy logic
    [x] Backtesting & optimization
    [ ] Parameter tuning
    [x] PineScript export
```

Use the same `[x]`/`[ ]` notation from STATE.md directly. If no Scope section exists, skip this.

---

## Important Constraints

- **READ-ONLY**: This workflow does NOT modify any files. The status command's allowed-tools list does not include Write. Do not include any file writes, STATE.md updates, or modifications of any kind.
- **English only**: All output text must be in English (per D-21).
- **Actionable**: The display must always end with a clear next step so the user knows exactly what command to run next.
- **Graceful degradation**: If any section of STATE.md is missing or malformed, skip that section in the display rather than erroring. Show what you can parse.
