# Workflow: discuss

Collect all strategy decisions through guided conversation before any code is written.

Follow these sections in order, top to bottom. Each section contains behavioral instructions -- read them, then execute them using your tools (Read, Write, Bash, Glob). Do NOT skip sections unless explicitly told to.

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

## CRITICAL: Interaction Rules

**ONE question at a time.** This is a conversation, not a questionnaire.

- Ask ONE question, wait for the user's response, then ask the next
- NEVER present multiple topics or questions in a single message
- NEVER dump a checklist of decisions for the user to fill in
- Use short, focused messages -- 2-4 sentences max per turn
- After each user response, acknowledge briefly ("Got it"), then ask the next question
- Follow the thread -- if the user's answer opens an interesting direction, explore it before moving on
- The 7 decision topics (entry/exit, stops, sizing, etc.) should be covered naturally through conversation, not as a numbered list

**Example of WRONG approach:**
```
Let's collect your strategy decisions:
1. Entry logic: ...
2. Exit logic: ...
3. Stop loss: ...
4. Position sizing: ...
Please describe each.
```

**Example of RIGHT approach:**
```
Tell me about the entry signal -- what tells you to get into a trade?
```
(wait for response)
```
Makes sense -- a close above the order block. And how do you exit? Fixed target, or trailing?
```
(wait for response)

---

## Preamble: Sequence Validation

Before anything else, verify the discuss step is valid for the current phase.

1. Use the Read tool to check if `.pmf/STATE.md` exists
2. If the file does not exist, STOP immediately. Display this error and do nothing else:

```
[STOP] Cannot run discuss -- no milestone exists.

No milestone exists. Create one first to define your strategy scope and targets.

Next step: `/brrr:new-milestone`
```

3. If the file exists, read it and extract:
   - **Status** field (must be "IN PROGRESS")
   - **Current Phase** number (N)
   - The Phase N checklist to see if Discuss is already checked
4. If Status is not "IN PROGRESS", STOP:

```
[STOP] Cannot run discuss -- milestone is not active.

Current milestone status: {status}

To start a new milestone: /brrr:new-milestone
```

5. If Discuss is already checked for Phase N, STOP:

```
[STOP] Cannot run discuss -- Phase {N} discuss is already completed.

The discuss phase fixes all strategy decisions -- entry/exit logic, indicators, stops.
Running it again would overwrite those decisions.

Current position:
  Phase {N}:
    [DONE] discuss
    {step_icon} research   {status}
    {step_icon} plan       {status}
    {step_icon} execute    {status}
    {step_icon} verify     {status}

Next step: `/brrr:{next_command}`
```

6. As a file existence fallback, verify `.pmf/STRATEGY.md` exists. If it does not exist, STOP:

```
[STOP] Cannot run discuss -- STRATEGY.md not found.

The discuss phase fixes all strategy decisions -- entry/exit logic, indicators, stops. Without it, there is nothing to research or plan around.

STRATEGY.md is created by /brrr:new-milestone and is required for discuss.

Next step: `/brrr:new-milestone`
```

7. If all checks pass, proceed to the next section

---

## Preamble: Context File Scan

Scan `.pmf/context/` for files the user may have dropped in for reference.

1. If `--no-context` was passed as an argument, skip this entire section
2. Use Glob to check if `.pmf/context/` directory exists and list all files in it: `.pmf/context/**/*`
3. If the directory does not exist or is empty, proceed to the next section
4. If `.pmf/STATE.md` exists, read the Processed Context table to identify which files have already been processed
5. Identify NEW files (present in directory but not in the Processed Context table)
6. If there are no new files, proceed to the next section
7. If there are more than 5 new files, note: "X files detected in .pmf/context/ -- processing the first 5 now. Run the command again to process the rest."

For each new file (up to 5), process based on type:

### Images (PNG, JPG, JPEG, GIF, WEBP)
1. Use the Read tool to view the image file -- you will see it visually
2. Describe in detail what you see: chart patterns, indicators, annotations, timeframe, asset, any visible text or labels
3. State your interpretation of how this image relates to the trading strategy
4. Use AskUserQuestion with header "Context", question "Is this understanding correct?", options: "Yes, correct" (confirm and continue), "Not quite" (user explains correction via Other).
5. Wait for the user's response before moving to the next file

### PDF files
1. Use the Read tool with the `pages` parameter to read the PDF (start with pages "1-5")
2. Summarize the content that is relevant to trading strategy development
3. Use AskUserQuestion with header "Context", question "Is this understanding correct?", options: "Yes, correct" (confirm and continue), "Not quite" (user explains correction via Other).
4. Wait for the user's response

### Text files (.txt, .md, .csv, .json)
1. Use the Read tool to read the file content directly
2. Summarize what is relevant to trading strategy development
3. Use AskUserQuestion with header "Context", question "Is this understanding correct?", options: "Yes, correct" (confirm and continue), "Not quite" (user explains correction via Other).
4. Wait for the user's response

After each file is confirmed (or corrected), record:
- Filename
- Today's date
- One-line description based on the confirmed understanding

These records will be written to STATE.md Processed Context table in Step 5.

---

## Preamble: Mode Detection

Determine which discussion mode to use based on arguments and state.

1. Check if `--auto` flag was passed as an argument
2. Read `.pmf/STATE.md` and extract the Current Phase number N
3. Determine mode:
   - If `--auto` flag was passed: mode = **auto**
   - If N > 1 (meaning prior phases have been executed): mode = **debug-discuss**
   - Otherwise: mode = **first-discuss**
4. Store the mode for use throughout the workflow
5. Display the detected mode:

```
Mode: {first-discuss | debug-discuss | auto}
Phase: {N}
```

---

## Step 1: Load Strategy Context

Load the strategy definition and any prior phase context.

1. Read `.pmf/STRATEGY.md` and extract:
   - **Hypothesis** (the one-sentence strategy thesis)
   - **Strategy Type** (trend-following, mean-reversion, breakout, custom)
   - **Asset & Timeframe** (asset, exchange/source, timeframe, date range)
   - **Scope** (which items are checked)
   - **Success Criteria** (Sharpe target, max drawdown, min trades)
   - **Original Idea** (the user's original description, preserved verbatim)

2. Read `.pmf/STATE.md` and extract the Current Phase number N

3. Quote the original hypothesis to anchor the conversation:

```
Your strategy hypothesis: "{hypothesis from STRATEGY.md}"
Original idea: "{original idea from STRATEGY.md}"
```

4. If mode is **debug-discuss**, also read ALL prior phase artifacts:
   - Use Glob to find all `.pmf/phases/phase_*` files
   - Read each prior discuss artifact: `.pmf/phases/phase_M_discuss.md` for all M < N
   - Read each prior research artifact: `.pmf/phases/phase_M_research.md` (if exists) for all M < N
   - Read each prior plan artifact: `.pmf/phases/phase_M_plan.md` (if exists) for all M < N
   - Read the last phase's best result: `.pmf/phases/phase_{N-1}_best_result.json` (if exists)
   - Read the last phase's verify report or diagnosis if it exists in `.pmf/phases/`
   - Read ALL diagnosis JSON files (DBUG-02, DBUG-03): Use Glob to find `.pmf/phases/phase_*_diagnosis.json`. Read each one and collect:
     - All `failed_approaches` entries across all files
     - All `do_not_retry` entries (flattened from all failed_approaches across all files)
     - The `overall_diagnosis` from the most recent diagnosis file
     - The `suggested_changes` from the most recent diagnosis file
   - Count total `failed_approaches` entries across all diagnosis files
   - If total exceeds 50 (per DBUG-03), merge the oldest entries:
     - Take the oldest N entries that bring the total down to 45 (leaving room for growth)
     - Replace them with a single summary entry:
       ```json
       {
         "iteration_range": "merged (phases 1-M)",
         "params_tried": {},
         "best_result": { "sharpe": best_sharpe_from_merged, "trades": total_trades_from_merged },
         "diagnosis": "Early phases summary: [AI-generated 2-3 sentence summary of the merged entries]",
         "do_not_retry": [all unique do_not_retry entries from merged entries, deduplicated]
       }
       ```
     - Write the updated diagnosis files back (remove entries from oldest files, add merged entry to earliest remaining file)
   - Store the collected data for use in Step 2-debug:
     - `all_failed_approaches`: the full list (after any merging)
     - `all_do_not_retry`: deduplicated flat list of all do_not_retry strings
     - `latest_diagnosis`: overall_diagnosis from most recent file
     - `latest_suggestions`: suggested_changes from most recent file
   - Summarize what you found:
     ```
     Prior phases loaded:
       Phase {M}: discuss + research + plan + execute results
       ...
     Last phase metrics: Sharpe {X}, Max DD {Y}%, {Z} trades
     Verify diagnosis: {summary of what went wrong or what to improve}
     Debug memory: {count} failed approaches across {file_count} diagnosis files
     Do-not-retry constraints: {count} active
     ```

---

## Step 2: Strategy Discussion (first-discuss mode)

**Only execute this step if mode is `first-discuss`.** Otherwise skip to Step 2-alt or Step 2-debug.

This is a follow-the-thread conversation, not a questionnaire. Start open and follow the user's energy.

1. Start with an open question:
   "Tell me more about your strategy. What is the core idea -- what market behavior are you trying to exploit?"

2. As the user describes their strategy, follow what they emphasize. If they talk about entries first, dig deeper into entries. If they start with risk management, explore that. Do NOT jump to a different topic -- follow the thread.

3. As the conversation progresses, internally track which of the 7 required topics have been covered:

   | # | Topic | Status |
   |---|-------|--------|
   | 1 | **Entry logic** -- what triggers a buy/sell signal | |
   | 2 | **Exit logic** -- what triggers closing a position | |
   | 3 | **Stop-loss rules** -- fixed %, trailing, ATR-based, none | |
   | 4 | **Take-profit rules** -- fixed target, trailing, signal-based | |
   | 5 | **Position sizing** -- fixed size, % of equity, Kelly criterion | |
   | 6 | **Commission assumptions** -- per-trade flat or percentage | |
   | 7 | **Parameter ranges** -- which params are fixed, which to optimize, ranges and step sizes | |

4. Use natural transitions to move between topics. Examples:
   - "That makes sense for entries. What about exits -- how do you know when to close?"
   - "Good. And for risk management -- do you have a stop-loss approach in mind?"
   - "One thing we should nail down is commissions. For {asset_class}, the typical cost is {default}. Sound reasonable?"

5. For **commissions**, if the user does not specify, use these defaults by asset class:
   - Crypto: 0.1% per trade (round trip 0.2%)
   - Stocks: 0.01% per trade ($0.005/share minimum)
   - Forex: 0.005% per trade (or spread-based)

6. For **parameter ranges**, ask which values the user wants to test vs keep fixed:
   - "Which of these values should we optimize, and which should be fixed?"
   - For parameters to optimize: collect min, max, and step size
   - For fixed parameters: collect the value and reason it is fixed

7. After the natural conversation winds down, review the 7-topic tracker. For any uncovered topics, ask directly:
   - "We have not discussed {topic} yet. {Specific question about that topic}."

8. Do NOT proceed to Step 3 until ALL 7 topics have been covered. Every topic must have a decision recorded.

---

## Step 2-alt: Strategy Discussion (auto mode)

**Only execute this step if mode is `auto`.** Otherwise skip.

In auto mode, apply type-specific defaults and confirm with one question.

1. Detect the strategy type from STRATEGY.md (already loaded in Step 1)

2. Apply type-specific defaults based on strategy type:

   **Trend-following defaults:**
   - Stop-loss: trailing stop at 2x ATR(14)
   - Take-profit: no fixed target (trail until stopped out)
   - Position sizing: 2% risk per trade
   - Commissions: 0.1% (crypto), 0.01% (stocks), 0.005% (forex) -- based on asset class
   - Parameters to optimize: ATR period (10-20, step 2), ATR multiplier (1.5-3.0, step 0.5), lookback period (20-100, step 10)

   **Mean-reversion defaults:**
   - Stop-loss: fixed at 2% from entry
   - Take-profit: 1.5x stop distance (3% from entry)
   - Position sizing: 1% risk per trade
   - Commissions: per asset class (same as above)
   - Parameters to optimize: lookback period (10-50, step 5), entry threshold (1.5-3.0 std dev, step 0.25), exit threshold (0.0-1.0 std dev, step 0.25)

   **Breakout defaults:**
   - Stop-loss: just below breakout level (1x ATR below)
   - Take-profit: 2x risk distance
   - Position sizing: 2% risk per trade
   - Commissions: per asset class (same as above)
   - Parameters to optimize: breakout period (10-50, step 5), confirmation bars (1-3, step 1), volume threshold (1.0-2.0x avg, step 0.25)

   **Custom defaults:**
   - Stop-loss: fixed at 2%
   - Take-profit: 2:1 risk-reward (4% from entry)
   - Position sizing: 1% risk per trade
   - Commissions: per asset class (same as above)
   - Parameters to optimize: as specified in STRATEGY.md or as detected from the strategy description

3. Override any defaults with specifics already present in STRATEGY.md or prior discuss artifacts

4. Extract entry and exit logic from the STRATEGY.md hypothesis and original idea -- formalize them as rules

5. Present the full default set to the user:

```
--- Auto-generated Strategy Decisions ---

Based on your {strategy_type} strategy for {asset} on {timeframe}:

Entry: {formalized entry logic from hypothesis}
Exit: {formalized exit logic}
Stop-Loss: {type and value}
Take-Profit: {type and value}
Position Sizing: {method and value}
Commissions: {value} per trade ({asset_class} default)

Parameters to Optimize:
  {param_name}: {min} to {max}, step {step}
  ...

Fixed Parameters:
  {param_name}: {value}
  ...

These are the defaults for your {strategy_type} strategy. Any changes?
```

6. If the user says "looks good", "no changes", or similar -- proceed to Step 3 with these defaults
7. If the user requests changes, apply them and re-display the updated set
8. Only ONE round of changes -- after that, proceed to Step 3

---

## Step 2-debug: Strategy Discussion (debug-discuss mode)

**Only execute this step if mode is `debug-discuss`.** Otherwise skip.

In debug mode, start from AI diagnosis of what went wrong, not from scratch.

1. Using the prior phase artifacts loaded in Step 1, formulate a diagnosis:
   - What was the strategy configuration in the previous phase?
   - What were the actual metrics (Sharpe, drawdown, trade count)?
   - How did the metrics compare to the success criteria?
   - What specific aspect failed? (entries too frequent, stops too tight, wrong market regime, etc.)

2. **Present prior debug cycle memory** (DBUG-02):

   If `phase_*_diagnosis.json` files were loaded in Step 1, present a failure summary table BEFORE the diagnosis:

   ```
   ## Prior Debug Cycles

   | Phase | Iterations | Best Sharpe | Diagnosis | Do NOT Retry |
   |-------|------------|-------------|-----------|--------------|
   | {phase} | {iteration_range} | {best_sharpe} | {diagnosis (truncated to 60 chars)} | {do_not_retry entries, comma-separated} |
   | ...   | ...        | ...         | ...       | ...          |

   Active constraints ({count} total):
   {bulleted list of ALL unique do_not_retry entries across all phases}

   AI synthesis: {latest_overall_diagnosis from most recent diagnosis file}
   Suggested starting point: {latest_suggested_changes, bulleted}
   ```

   If no `phase_*_diagnosis.json` files were found, skip this presentation and proceed with the existing diagnosis flow.

3. Present the diagnosis to the user:

```
--- Phase {N} Debug Analysis ---

Previous phase ({N-1}) results:
  Sharpe: {value} (target: {target})
  Max Drawdown: {value}% (target: <{target}%)
  Trades: {count} (minimum: {min})

Diagnosis: {specific analysis of what went wrong}

Suggested changes:
  1. {specific, actionable change with rationale}
  2. {specific, actionable change with rationale}
  ...

What do you think? Should we proceed with these changes, modify them, or take a different approach?
```

   - **CRITICAL CONSTRAINT (DBUG-02):** When formulating the diagnosis and suggested changes, you MUST NOT propose any parameter ranges or approaches that overlap with entries in the `all_do_not_retry` list from Step 1. If your analysis suggests a parameter region that is in the do_not_retry list, explicitly state: "This region was already tried in Phase {N} and failed -- skipping." Choose an alternative direction instead.

4. Let the user react and discuss. This is a conversation -- the user may agree, disagree, or propose alternatives.
   - If the user proposes a change that overlaps with a do_not_retry entry, warn them: "That approach was tried in Phase {N} and failed because: {diagnosis}. Are you sure you want to retry it?" Let the user override if they insist, but make the prior failure visible.

5. As the conversation proceeds, collect the updated decisions for all 7 topics (same tracker as first-discuss mode). Many will carry over from the previous phase -- only changed topics need discussion.

6. **DRIFT DETECTION** -- Before proceeding to Step 3, compare ALL proposed changes against the original STRATEGY.md:

   a. Read `.pmf/STRATEGY.md` and extract the **Original Idea** and **Hypothesis**
   b. Compare proposed changes against the original:
      - Drift = new indicators/signals NOT in original STRATEGY.md OR fundamentally changed entry/exit logic
      - But ONLY if changes affect >50% of the strategy
      - Minor tweaks are NOT drift: filter adjustments, parameter range changes, stop-loss value changes, commission adjustments
   c. If NO drift detected, proceed to Step 3
   d. If drift IS detected, activate the HARD GATE:

```
[DRIFT DETECTED] Your proposed changes significantly alter the original strategy.

Original hypothesis: "{quoted from STRATEGY.md}"
Proposed changes: {list changes that constitute drift}

This looks like a different strategy. Choose:
1. Stay within current scope (revert drift changes)
2. Open a new milestone for this new approach (/brrr:new-milestone)

Cannot continue until you choose.
```

   e. Do NOT allow "continue anyway" -- the user MUST pick option 1 or option 2
   f. If option 1: revert the drift changes and proceed to Step 3 with the remaining non-drift changes
   g. If option 2: STOP the workflow entirely. Tell the user to run `/brrr:new-milestone` for the new approach

---

## Step 3: Compile and Confirm Decisions

Display all collected decisions in a structured format for final confirmation.

1. Compile all 7 decision topics into a summary:

```
--- Strategy Decisions for Phase {N} ---

Entry: {detailed entry logic with specific rules}
Exit: {detailed exit logic with specific rules}
Stop-Loss: {type and value -- e.g., "Trailing stop at 2x ATR(14)"}
Take-Profit: {type and value -- e.g., "Fixed target at 3% from entry"}
Position Sizing: {method and value -- e.g., "2% risk per trade"}
Commissions: {type and value -- e.g., "0.1% per trade (crypto)"}

Parameters to Optimize:
  {param_name}: {min} to {max}, step {step} ({int or float})
  ...

Fixed Parameters:
  {param_name}: {value} -- {reason it is fixed}
  ...
```

2. Use AskUserQuestion with header "Confirm", question "Does this look correct?", options: "Yes, save it" (proceed to write artifact), "Change something" (ask what to change). If user picks Other with a comment, treat as change request.

3. If the user requests changes:
   - Go back to the relevant topic
   - Update the decision
   - Re-display the full summary
   - Ask for confirmation again


---

## Step 4: Write Output Artifact

Create the phase discuss artifact with all decisions.

1. Get the current phase number N from STATE.md (already loaded)
2. Get today's date
3. Write `.pmf/phases/phase_{N}_discuss.md` with this structure:

```markdown
# Phase {N} -- Strategy Discussion

## Mode
{first-discuss | debug-discuss | auto}

## Strategy Summary
{One paragraph summarizing the strategy as decided in this discussion. Include the core hypothesis, key signals, and overall approach.}

## Entry Logic
{Detailed entry rules as decided. Be specific -- include indicator names, thresholds, conditions, and the logical combination (AND/OR) of signals.}

## Exit Logic
{Detailed exit rules as decided. Include what triggers a position close -- signal reversal, opposing signal, time-based, etc.}

## Stop-Loss
- **Type:** {fixed | trailing | ATR-based | none}
- **Value:** {specific value or formula}
- **Rationale:** {why this stop type and value were chosen}

## Take-Profit
- **Type:** {fixed | trailing | signal-based | none}
- **Value:** {specific value or formula}
- **Rationale:** {why this take-profit type and value were chosen}

## Position Sizing
- **Method:** {fixed size | % of equity | Kelly criterion | other}
- **Value:** {specific value}
- **Rationale:** {why this method and value were chosen}

## Commission Assumptions
- **Type:** {percentage | flat fee}
- **Value:** {value per trade}
- **Asset Class Default:** {whether this is a default or user-specified}

## Parameters
### To Optimize
| Parameter | Min | Max | Step | Type |
|-----------|-----|-----|------|------|
| {name} | {min} | {max} | {step} | {int/float} |

### Fixed
| Parameter | Value | Rationale |
|-----------|-------|-----------|
| {name} | {value} | {why fixed} |

## Context Files Incorporated
{List of context files processed during this discuss session, or "None"}

## Drift Assessment
{For debug mode: summary of what changed vs the original strategy, and whether changes were within scope or drift was detected and resolved. For first-discuss and auto modes: "N/A -- first phase"}

---
*Phase {N} discuss completed: {YYYY-MM-DD}*
```

4. The output artifact follows the phase_N_discuss.md naming convention where N is the current phase number
5. Verify the file was written by reading it back

---

## Step 5: Update STATE.md

Update the milestone state to reflect discuss completion.

1. Read `.pmf/STATE.md`
2. Make these updates:
   - Mark the Discuss step as done for the current phase: change `- [ ] Discuss` to `- [x] Discuss` under the Phase {N} section
   - Update **Current Step** from `discuss` to `research`
   - Update **Last Updated** to today's date
3. Append a new history entry at the TOP of the History section (newest first):

```
### {YYYY-MM-DD} -- Phase {N} discuss completed
- **Mode:** {first-discuss | debug-discuss | auto}
- **Decisions:** 7 decisions fixed (entry, exit, stop-loss, take-profit, sizing, commissions, parameters)
- **Parameters:** {X} to optimize, {Y} fixed
```

4. If context files were processed in the Preamble, add them to the Processed Context table:

```
| {filename} | {YYYY-MM-DD} | {one-line description} |
```

5. Write the updated STATE.md
6. Verify the update by reading STATE.md back and confirming the changes are present

---

## Step 6: Confirmation

Display a completion message to the user.

1. Count the number of parameters to optimize and fixed parameters from the decisions
2. Display:

```
Phase {N} discuss complete!

Artifact: .pmf/phases/phase_{N}_discuss.md
Decisions fixed: 7 (entry, exit, stop-loss, take-profit, sizing, commissions, parameters)
Parameters: {X} to optimize, {Y} fixed

Next step: `/brrr:research` (optional) or `/brrr:plan`
```

---

*Workflow: discuss*
*Covers: DISC-01, DISC-02, DISC-03, DISC-04, DISC-05, DISC-06*
