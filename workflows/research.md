# Workflow: research

Research known implementations, academic work, lookahead traps, and formalization alternatives for the user's strategy type. This workflow bridges discuss and plan -- it catches pitfalls before the plan is designed and surfaces formalization alternatives the user may not know about.

Follow these sections in order, top to bottom. Each section contains behavioral instructions -- read them, then execute them using your tools (Read, Write, Bash, Glob, WebFetch). Do NOT skip sections unless explicitly told to.

---

## Preamble: Sequence Validation

Before anything else, verify the discuss step is complete for the current phase.

1. Use the Read tool to check if `.pmf/STATE.md` exists
2. If the file does not exist, STOP immediately:

```
[STOP] Cannot run research -- no milestone exists.

No milestone exists. Create one first to define your strategy scope and targets.

Next step: `/brrr:new-milestone`
```

3. If the file exists, read it and find:
   - **Status** field -- must be "IN PROGRESS"
   - **Current Phase** number (N)
   - Whether the discuss step for Phase N is marked done: `- [x] Discuss`
4. Also check the file existence fallback: verify `.pmf/phases/phase_N_discuss.md` exists using Glob
5. If discuss is NOT done (neither STATE.md checkbox nor file exists), STOP immediately:

```
[STOP] Cannot run research -- discuss has not been completed yet.

The discuss phase fixes all strategy decisions -- entry/exit logic, indicators, stops.
Without it, there is nothing to research or plan around.

Current position:
  Phase {N}:
    {step_icon} discuss    {status}
    {step_icon} research   {status}
    {step_icon} plan       {status}
    {step_icon} execute    {status}
    {step_icon} verify     {status}

Next step: `/brrr:discuss`
```

6. If discuss IS done, proceed. Note: **Research is recommended but optional. You can skip to /brrr:plan if your strategy is well-understood.** Since the user already ran the command, proceed with research.

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
1. Use the Read tool to view the image file
2. Describe what you see: chart patterns, indicators, annotations, timeframe, asset, any visible text
3. Ask the user: "Is this understanding correct? Anything to add or correct?"
4. Wait for the user's response

### PDF files
1. Use the Read tool with the `pages` parameter to read the PDF (start with pages "1-5")
2. Summarize content relevant to trading strategy development
3. Ask the user: "Is this understanding correct? Anything to add or correct?"
4. Wait for the user's response

### Text files (.txt, .md, .csv, .json)
1. Use the Read tool to read the file content
2. Summarize what is relevant to trading strategy development
3. Ask the user: "Is this understanding correct? Anything to add or correct?"
4. Wait for the user's response

After each file is confirmed, record the filename, date, and one-line description.

---

## Step 1: Load Context

Gather all information needed for research.

1. Read `.pmf/STRATEGY.md` to extract:
   - Strategy type (trend-following, mean-reversion, breakout, custom)
   - Asset class and specific instrument
   - Core hypothesis
2. Read `.pmf/phases/phase_N_discuss.md` to extract:
   - Entry logic and exit logic
   - Stop-loss and take-profit rules
   - Position sizing approach
   - Commission assumptions
   - Parameters identified (which to optimize, which are fixed)
   - Any indicators or signals mentioned
3. Read `~/.pmf/references/common-pitfalls.md` to load the pitfalls catalog (6 pitfalls: Lookahead Bias, Survivorship Bias, Execution Price Bias, Over-Optimization, Commission Omission, IS/OOS Confusion)
4. Read `~/.pmf/references/backtest-engine.md` to load the engine pattern rules (anti-lookahead rules, position management, commission modeling)
5. Check if `--deep` flag was passed in the command arguments
6. Store: strategy_type, asset_class, hypothesis, entry_logic, exit_logic, indicators, parameters, is_deep_mode

---

## Step 2: Research Recommendation

Auto-detect whether research is needed based on the discuss output.

1. Evaluate the strategy against these criteria:

   **Research recommended** (any of these true):
   - Strategy uses non-standard indicators or custom signals
   - Strategy combines 3+ indicators or signals
   - Strategy type is "custom"
   - Strategy involves multi-timeframe analysis
   - User mentioned unfamiliar concepts or academic references in discuss
   - Entry or exit logic involves complex conditions (multiple AND/OR clauses)

   **Research optional** (all of these true):
   - Classic well-known strategy (SMA crossover, RSI overbought/oversold, Bollinger Bands bounce, MACD crossover)
   - Single-indicator strategy with standard parameters
   - Strategy type matches a textbook pattern exactly

2. Display the recommendation:

```
Research is {recommended | optional} for your strategy.
Reason: {specific reason based on criteria above}

Proceeding with research.
```

3. Always proceed -- the user already invoked the command, so the recommendation is informational only

---

## Step 3: Knowledge Base Research (Claude's Training Data)

Search Claude's training data first. This is the primary source for well-known strategies.

1. Based on the strategy type and indicators from Step 1, recall and present:

   **Known Implementations:**
   - Describe 1-2 common approaches to implementing this strategy type
   - Note any standard parameter values used in published implementations
   - Mention libraries or frameworks that implement similar strategies (for reference, not for use -- our engine is custom)

   **Academic / Published References:**
   - Identify relevant academic papers or well-known books related to the strategy concept
   - Note the key findings or recommendations from these sources
   - Cite specific authors, years, or publications where possible

   **Common Parameter Ranges:**
   - What parameter values are typically used for this strategy type?
   - What ranges do published sources recommend?
   - Are there parameter values that are known to be problematic?

   **Known Failure Modes:**
   - What market conditions cause this strategy type to fail?
   - Are there specific time periods or regimes where this approach historically struggled?
   - What are the most common mistakes when implementing this strategy?

   **Formalization Alternatives:**
   - Are there different mathematical ways to express the same trading idea?
   - Could the strategy be expressed as a different strategy type (e.g., a breakout reformulated as mean-reversion)?
   - Are there variations that are known to be more robust?

2. Present findings as they are discovered -- do not wait for all research to complete before showing results

---

## Step 4: Pitfall Cross-Reference

Cross-reference the user's specific strategy against the pitfalls catalog.

1. For each of the 6 pitfalls in `~/.pmf/references/common-pitfalls.md`, evaluate how it applies to THIS specific strategy:

   **Lookahead Bias:**
   - Does the entry/exit logic use any signals that could inadvertently use future data?
   - Are any indicators computed in a way that might use the full dataset?
   - Rate: HIGH RISK / MEDIUM RISK / LOW RISK
   - Explain specifically how this could manifest in the user's strategy

   **Survivorship Bias:**
   - Is the strategy single-instrument or multi-instrument?
   - If multi-instrument, how could the instrument universe introduce bias?
   - Rate: HIGH RISK / MEDIUM RISK / LOW RISK

   **Execution Price Bias:**
   - Does the strategy's timing assumptions match realistic execution?
   - Could the entry/exit logic depend on prices that are not actionable?
   - Rate: HIGH RISK / MEDIUM RISK / LOW RISK

   **Over-Optimization (Curve Fitting):**
   - How many free parameters does the strategy have?
   - Is the parameter space large relative to expected trade count?
   - Rate: HIGH RISK / MEDIUM RISK / LOW RISK

   **Commission and Slippage Omission:**
   - What is the expected trade frequency?
   - Is the average expected profit per trade large enough to absorb costs?
   - Rate: HIGH RISK / MEDIUM RISK / LOW RISK

   **In-Sample / Out-of-Sample Confusion:**
   - Does the planned optimization approach include a proper train/test split?
   - Rate: HIGH RISK / MEDIUM RISK / LOW RISK

2. For each pitfall rated HIGH RISK, provide a specific, actionable warning. For example:
   - "Your RSI-based entry could have lookahead bias if the RSI is computed on the full dataset rather than history[:i+1]"
   - "Your mean-reversion strategy is particularly vulnerable to commission omission because it trades frequently"
   - "With 5 free parameters and a medium-sized dataset, over-optimization risk is high -- consider fixing some parameters"

---

## Step 5: Web Search (if --deep or if gaps found)

Use WebFetch to supplement training data findings. This is the ONLY workflow with web search capability.

### Standard Mode (no --deep flag)

1. Review findings from Steps 3 and 4
2. If Claude's training data was sufficient (clear implementations found, pitfalls assessed, no knowledge gaps), skip web search entirely
3. If gaps exist (unfamiliar indicator, niche strategy type, recent technique), use WebFetch for 1-2 targeted searches:
   - Construct specific search queries related to the strategy type and asset class
   - Focus on filling the specific gap identified
4. If WebFetch fails or returns unhelpful results, gracefully continue with training data findings only -- note that web search was attempted but did not yield additional results

### Deep Mode (--deep flag)

1. Search 3-5 sources including:
   - Academic papers or preprints related to the strategy concept
   - Trading forums or community discussions with implementation details
   - Implementation guides or tutorials for the specific strategy type
   - Quantitative finance blogs with backtesting results

2. For each source found via WebFetch:
   - Extract relevant code patterns or implementation approaches
   - Compare the source's approach with the user's strategy from discuss
   - Rate the source's reliability (peer-reviewed, community-tested, blog post, etc.)
   - Note any parameter recommendations or warnings

3. Search queries should be specific. Examples:
   - "{strategy_type} {asset_class} backtest implementation"
   - "{indicator_name} optimal parameters academic research"
   - "{strategy_type} common pitfalls failure modes"
   - "{indicator_combination} trading strategy performance"

4. If WebFetch fails for some queries, continue with whatever results were obtained -- partial results are still valuable

---

## Step 6: Compile and Present Findings

Display all research findings in a structured format for the user to review.

1. Present the compiled findings:

```
--- Research Findings ---

Strategy Type: {type from STRATEGY.md}
Research Depth: {standard | deep}

## Known Implementations
{1-2 paragraph descriptions of common approaches to this strategy type}
{Standard parameter values and ranges from published sources}

## Academic/Published References
{Papers, books, or well-known sources related to this strategy concept}
{Key findings or recommendations from these sources}

## Pitfall Assessment
| Pitfall | Risk Level | How It Applies |
|---------|------------|----------------|
| Lookahead bias | {HIGH/MED/LOW} | {specific to this strategy} |
| Survivorship bias | {HIGH/MED/LOW} | {specific to this strategy} |
| Execution price bias | {HIGH/MED/LOW} | {specific to this strategy} |
| Over-optimization | {HIGH/MED/LOW} | {specific to this strategy} |
| Commission omission | {HIGH/MED/LOW} | {specific to this strategy} |
| IS/OOS confusion | {HIGH/MED/LOW} | {specific to this strategy} |

## Formalization Alternatives
{Other ways to express this trading idea that might be more robust}
{Different indicator choices, different entry/exit logic, different timeframes}

## Recommendations for Plan Phase
{Specific suggestions based on research:}
{- Parameter ranges to consider}
{- Optimization method recommendation (grid, random, walk-forward, Bayesian)}
{- Data period requirements (minimum history needed for indicators)}
{- Train/test split considerations}
{- Risk management suggestions based on pitfall assessment}
```

2. Ask the user: "Anything you want me to research further before we save this?"
3. If the user requests more research:
   - Repeat the relevant research steps (Step 3 for training data, Step 5 for web)
   - Update the compiled findings
   - Present the updated summary
   - Ask again if they want more research
4. If the user is satisfied (confirms or says to continue), proceed to Step 7

---

## Step 7: Write Output Artifact

Write the research findings to a structured phase artifact.

1. Determine the phase number N from STATE.md
2. Write `.pmf/phases/phase_N_research.md` with this structure:

```markdown
# Phase {N} -- Strategy Research

## Research Depth
{standard | deep}

## Recommendation
Research was {recommended | optional} for this strategy.
Reason: {why research was or was not needed, based on Step 2 criteria}

## Known Implementations
{Detailed findings from Step 3 -- common approaches, standard parameters, published implementations}

## Academic References
{Papers, books, established sources from Step 3 and Step 5}
{Author, year, key finding for each reference}

## Pitfall Assessment
| Pitfall | Risk Level | Specific Risk |
|---------|------------|---------------|
| Lookahead bias | {HIGH/MEDIUM/LOW} | {How it could manifest in this strategy} |
| Survivorship bias | {HIGH/MEDIUM/LOW} | {How it could manifest in this strategy} |
| Execution price bias | {HIGH/MEDIUM/LOW} | {How it could manifest in this strategy} |
| Over-optimization | {HIGH/MEDIUM/LOW} | {How it could manifest in this strategy} |
| Commission omission | {HIGH/MEDIUM/LOW} | {How it could manifest in this strategy} |
| IS/OOS confusion | {HIGH/MEDIUM/LOW} | {How it could manifest in this strategy} |

## Lookahead Trap Warnings
{Specific warnings extracted from the pitfall assessment, emphasized here because lookahead is the most dangerous pitfall}
{Each warning should be concrete: "When computing {indicator}, ensure you use history[:i+1] not the full dataset"}
{Reference the backtest engine pattern: signals see only past and current bar, execution at next bar open}

## Formalization Alternatives
{Alternative approaches found during research}
{Different ways to express the same trading idea}
{Variations that may be more robust or better-suited to backtesting}

## Recommendations for Plan Phase
{Concrete suggestions for the plan phase:}
{- Suggested parameter ranges based on research}
{- Recommended optimization method and why}
{- Minimum data requirements for the strategy's indicators}
{- Train/test split considerations}
{- Specific things to watch for during optimization}

## Sources
{List all sources consulted:}
{- Training data topics searched}
{- Web URLs fetched (if any, with brief description of what was found)}
{- Books or papers referenced}

---
*Phase {N} research completed: {date}*
```

---

## Step 8: Update STATE.md

Update the milestone state to reflect research completion.

1. Read `.pmf/STATE.md`
2. Mark the research step as done for the current phase: change `- [ ] Research (optional)` to `- [x] Research`
3. Update the **Last Updated** field to today's date
4. Append to the **History** section (newest entries first):

```
### {date} -- Phase {N} research completed
- **Depth:** {standard | deep}
- **Pitfalls identified:** {count} ({HIGH count} high risk)
- **Sources:** {count} ({training data topics} + {web sources if any})
```

5. Write the updated STATE.md

---

## Step 9: Confirmation

Display a summary of the research phase completion.

```
Phase {N} research complete!

Artifact: .pmf/phases/phase_{N}_research.md
Pitfalls: {count} identified ({HIGH count} high risk)
Sources: {count} consulted

Next step: `/brrr:plan`
```

---

*Workflow: research*
*Covers: RSCH-01, RSCH-02, RSCH-03, RSCH-04, RSCH-05*
