# Workflow: new-milestone

Create a new trading strategy milestone through guided conversation.

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

**ONE question at a time.** This is a conversation, not a form.

- Ask ONE question, wait for the user's response, then ask the next
- NEVER present multiple steps or questions in a single message
- NEVER dump a list of questions for the user to answer all at once
- Use short, focused messages -- 2-4 sentences max per turn
- After each user response, acknowledge it briefly, then move to the next question
- The user should feel like they're chatting, not filling out a form

**Example of WRONG approach:**
```
Here are the questions:
1. What's your strategy?
2. What asset?
3. What timeframe?
4. What targets?
```

**Example of RIGHT approach:**
```
What trading strategy are you thinking about? Describe the core idea.
```
(wait for response)
```
Got it -- SMC with RSI filter. What asset are you trading? Crypto, stocks, or forex?
```
(wait for response)
```
BTC/USDT -- which exchange? Binance is the default for best data fidelity.
```

---

## Preamble: Active Milestone Check

Before anything else, verify no milestone is currently active.

1. Use the Read tool to check if `.pmf/STATE.md` exists in the current working directory
2. If the file exists, read it and find the **Status** field
3. If Status is "IN PROGRESS", STOP immediately. Display this error and do nothing else:

```
[STOP] Cannot create a new milestone -- you already have an active one.

Current milestone: {name from STATE.md}
Status: IN PROGRESS

To start a new milestone, first:
- Complete the current one: /brrr:verify --approved
- Or abandon it: manually set Status to "ABANDONED" in .pmf/STATE.md
```

4. If Status is "APPROVED", "ABANDONED", or the file does not exist, proceed to the next section

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
3. State your interpretation of how this image relates to a trading strategy
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

These records will be written to STATE.md Processed Context table in Step 7.

---

## Step 1: Setup -- Create Directory Structure

Create the project directory structure if it does not already exist.

1. Run: `mkdir -p .pmf/context .pmf/phases`
2. This ensures `.pmf/`, `.pmf/context/`, and `.pmf/phases/` all exist

---

## Step 2: Collect Strategy Idea

Ask the user to describe their trading strategy idea. This is a conversation, not a form -- adapt to the user's style.

1. Ask the user to describe their trading idea in their own words
2. As they describe it, listen for and identify:
   - **Strategy type:** trend-following, mean-reversion, breakout, or custom
   - **Asset class:** crypto, stocks, forex
   - **Specific indicators or signals** mentioned (RSI, MACD, moving averages, order blocks, etc.)
   - **Timeframe hints** (mentions of "daily", "4-hour", "scalping", etc.)
3. If context files were processed in the Preamble, reference what was learned from them. For example: "Based on the chart you shared, it looks like you're interested in order block entries with RSI confirmation on the 4H timeframe -- is that the core idea?"
4. If the idea is vague, ask follow-up questions to clarify:
   - "What triggers an entry? What tells you to get in?"
   - "How do you know when to get out?"
   - "Is this based on any specific indicator or pattern?"
5. If the idea mixes multiple concepts, help the user separate them:
   - "You mentioned X, Y, and Z -- these are different approaches. Which is the core idea, and which are supporting filters?"
6. Do NOT proceed to Step 3 until you have a clear, single-thesis hypothesis
7. Record the detected **strategy type** for use in Step 5 (success criteria defaults)

---

## Step 3: Scope Selection

Based on what you learned about the strategy in Step 2, suggest a default scope.

1. Assess the strategy complexity:

   **Simple strategies** (single indicator, classic pattern, straightforward logic):
   Suggest 3 items pre-checked:
   - [x] Strategy logic (entry/exit rules)
   - [x] Backtesting & optimization
   - [ ] Parameter tuning
   - [ ] Risk management
   - [x] PineScript export
   - [ ] MD instructions export

   **Complex strategies** (multiple signals, custom logic, multi-timeframe, regime filters):
   Suggest 5 items pre-checked:
   - [x] Strategy logic (entry/exit rules)
   - [x] Backtesting & optimization
   - [x] Parameter tuning
   - [x] Risk management
   - [x] PineScript export
   - [ ] MD instructions export

2. Present the full list of 6 scope items with your suggestion pre-checked
3. Explain briefly what each item means if the user seems unfamiliar
4. Let the user modify the selection -- they can add or remove any items
5. Record the final scope selection for use in Step 7

---

## Step 4: Scope Splitting Check

If the user selected 5 or more scope items, suggest splitting into phases.

1. If fewer than 5 items selected, skip this step entirely
2. If 5 or more items selected, suggest a phased approach:
   - **v1 (core):** Strategy logic + Backtesting & optimization + PineScript export
   - **v2 (enhancement):** Parameter tuning + Risk management + MD instructions export
3. Explain the rationale: "A focused first pass gets you a working strategy faster. You can always add tuning and risk management in a debug cycle."
4. But respect the user's override -- if they say something like "I know it's big, do it anyway" or "keep everything", proceed with the full scope
5. Splitting is a **suggestion only**, never enforced

---

## Step 5: Data Source

Based on the asset class identified in Step 2, collect data source details.

1. **Crypto:**
   - Ask which trading pair (e.g., BTC/USDT, ETH/USDT)
   - Ask which exchange (default: Binance)
   - Data source: ccxt

2. **Stocks:**
   - Ask which ticker (e.g., AAPL, SPY)
   - Ask if daily or intraday data is needed
   - Daily -> yfinance (free, no API key)
   - Intraday -> polygon.io (requires API key -- note this to the user)
   - Data source: yfinance or polygon

3. **Forex:**
   - Ask which pair (e.g., EUR/USD, GBP/JPY)
   - Ask if daily or intraday data is needed
   - Daily -> yfinance (free)
   - Intraday -> Dukascopy (free, no API key, tick-level data)
   - Data source: yfinance or dukascopy

4. Ask about **timeframe**: 1m, 5m, 15m, 1H, 4H, 1D, 1W
5. Ask about **date range** and suggest reasonable defaults:
   - Daily data: 3-4 years (e.g., 2022-01-01 to present)
   - Intraday data: 1-2 years (e.g., 2024-01-01 to present)
6. Record: asset, exchange/source, timeframe, date range

---

## Step 6: Success Criteria

Based on the strategy type detected in Step 2, offer default success criteria.

1. Present defaults based on strategy type:

   | Strategy Type | Sharpe Target | Max Drawdown | Min Trades |
   |---------------|---------------|--------------|------------|
   | Trend-following | Sharpe > 1.2 | < 30% | 30 |
   | Mean-reversion | Sharpe > 1.5 | < 20% | 30 |
   | Breakout | Sharpe > 1.0 | < 35% | 30 |
   | Custom | Sharpe > 1.0 | < 30% | 30 |

2. Tell the user: "Based on your {strategy_type} strategy, here are the suggested targets: Sharpe > {X}, Max Drawdown < {Y}%, Minimum {Z} trades."
3. Let the user adjust any values
4. Record: sharpe target, max drawdown target, minimum trade count, strategy type

---

## Step 7: Summary and Confirmation

Display a complete summary of everything collected and ask for confirmation.

1. Format and display:

```
--- Milestone Summary ---

Strategy: {hypothesis -- one sentence}
Type: {strategy_type}

Asset: {asset}
Exchange/Source: {exchange_source}
Timeframe: {timeframe}
Date Range: {date_start} to {date_end}

Scope:
  [x] Strategy logic (entry/exit rules)
  [x] Backtesting & optimization
  [ ] Parameter tuning
  ...

Success Criteria:
  Sharpe Ratio > {target}
  Max Drawdown < {target}%
  Minimum trades: {N}

Context files processed: {count or "none"}
```

2. Use AskUserQuestion with header "Confirm", question "Does this look correct?", options: "Yes, create milestone" (proceed to file creation), "Change something" (ask what to change). If user selects "Change something" or picks Other with a comment, go back to the relevant step.
3. If the user requests changes, go back to the relevant step (Step 2 for idea changes, Step 3 for scope, Step 5 for data, Step 6 for criteria)
4. Once confirmed, proceed to file creation

---

## Step 8: Create Files

After confirmation, create STRATEGY.md and STATE.md from the templates.

1. Read the STRATEGY.md template from `~/.pmf/templates/STRATEGY.md`
2. Fill all template variables with collected information:
   - `{{STRATEGY_NAME}}` -- short name derived from hypothesis
   - `{{One-sentence strategy thesis}}` -- the hypothesis from Step 2
   - `{{strategy_type}}` -- detected type (trend-following, mean-reversion, breakout, custom)
   - `{{asset}}`, `{{data source}}`, `{{timeframe}}`, `{{start}}`, `{{end}}` -- from Step 5
   - Scope checkboxes -- mark selected items with `[x]`, unselected with `[ ]`
   - Success criteria values from Step 6
   - `{{User's original description}}` -- the user's words from Step 2, preserved verbatim
   - `{{date}}` -- today's date
   - `{{milestone_name}}` -- same as STRATEGY_NAME
3. Write the filled template to `.pmf/STRATEGY.md`

4. Read the STATE.md template from `~/.pmf/templates/STATE.md`
5. Fill all template variables:
   - `{{name}}` -- milestone name from hypothesis
   - Status: `IN PROGRESS`
   - Current Phase: `1`
   - Current Step: `discuss`
   - Created: today's date
   - Last Updated: today's date
   - Scope: checked items matching Step 3 selection
   - Data Source: values from Step 5
   - Success Criteria: values from Step 6, including strategy type
   - Phases section: Phase 1 with all steps unchecked:
     ```
     ### Phase 1
     - [ ] Discuss
     - [ ] Research (optional)
     - [ ] Plan
     - [ ] Execute
     - [ ] Verify
     ```
   - Best Results: empty table (header only, no rows)
   - Processed Context: entries from Preamble context scan (if any), or empty table (header only)
   - History (append-only log, newest entries first): single entry:
     ```
     ### {date} -- Milestone created
     - **Hypothesis:** {hypothesis}
     - **Scope:** {comma-separated list of selected scope items}
     ```
     Note: The history section is append-only -- entries are never removed or overwritten, only new ones added at the top.
6. Write the filled template to `.pmf/STATE.md`

7. Display confirmation message:
```
Milestone created! Your strategy milestone is set up and ready.

Files created:
  .pmf/STRATEGY.md -- strategy definition and scope
  .pmf/STATE.md    -- milestone state tracker

Next step: /brrr:discuss
```

---

## Sequence Validation (Reference for all commands)

This table documents the validation rules that ALL /brrr:* workflows should check before executing. It is included here as the canonical reference since new-milestone establishes the state that other commands depend on.

### Validation Matrix

| Command | STATE.md requires | File existence fallback |
|---------|-------------------|------------------------|
| new-milestone | No active milestone (Status != IN PROGRESS) | No .pmf/STATE.md with active milestone |
| discuss | Phase N has no discuss done | .pmf/STRATEGY.md exists |
| research | Phase N discuss done (research optional) | .pmf/phases/phase_N_discuss.md exists |
| plan | Phase N discuss done | .pmf/phases/phase_N_discuss.md exists |
| execute | Phase N plan done | .pmf/phases/phase_N_plan.md exists |
| verify | Phase N execute done | .pmf/phases/phase_N_best_result.json exists |
| status | .pmf/ exists | .pmf/STATE.md exists |

### Error Message Pattern

When a command is run out of sequence, display this error format:

```
[STOP] Cannot run {command} -- {prerequisite} has not been completed yet.

{Why this prerequisite matters -- one sentence explaining the dependency}

Current position:
  Phase {N}:
    {step_icon} discuss    {status}
    {step_icon} research   {status}
    {step_icon} plan       {status}
    {step_icon} execute    {status}
    {step_icon} verify     {status}

Next step: /brrr:{next_command}
```

### Prerequisite Explanations

Use these explanations in the error messages:

- **discuss before research/plan:** "The discuss phase fixes all strategy decisions -- entry/exit logic, indicators, stops. Without it, there is nothing to research or plan around."
- **plan before execute:** "The plan defines the parameter space, optimization method, and evaluation criteria -- without it, execute does not know what to optimize."
- **execute before verify:** "Verify generates a report from backtest results -- there are no results to report on yet."
- **new-milestone required:** "No milestone exists. Create one first to define your strategy scope and targets."

### Optional Steps

- **Research** is always optional. If research is not done, plan can still proceed after discuss.
- When validating sequence, skip over optional steps that are not done -- they do not block the next required step.

---

*Workflow: new-milestone*
*Covers: MILE-01, MILE-02, MILE-03, MILE-04, STAT-01, STAT-03, STAT-04, STAT-05, CTXT-01, CTXT-02, CTXT-03*
