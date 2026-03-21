# Workflow: plan

Design the parameter space, optimization method, evaluation criteria, data period, and train/test split for the backtest.

Follow these sections in order, top to bottom. Each section contains behavioral instructions -- read them, then execute them using your tools (Read, Write, Bash, Glob). Do NOT skip sections unless explicitly told to.

---

## Preamble: Sequence Validation

Before anything else, verify that discuss has been completed for the current phase.

1. Use the Read tool to check if `.pmf/STATE.md` exists
2. If it exists, read it and find:
   - **Current Phase** number (N)
   - Whether discuss is marked done for phase N: look for `- [x] Discuss` under Phase N
3. File existence fallback: check if `.pmf/phases/phase_N_discuss.md` exists
4. If discuss is NOT done (neither STATE.md checkbox nor file exists), STOP immediately:

```
[STOP] Cannot run plan -- discuss has not been completed yet.

The discuss phase fixes all strategy decisions -- entry/exit logic, indicators,
stops. Without it, there is nothing to plan around.

Current position:
  Phase {N}:
    {step_icon} discuss    {status}
    {step_icon} research   {status}
    {step_icon} plan       {status}
    {step_icon} execute    {status}
    {step_icon} verify     {status}

Next step: `/brrr:discuss`
```

5. If discuss IS done, proceed to the next section
6. Note: research is OPTIONAL. Do NOT require it. If phase_N_research.md exists, it will be loaded in Step 1. If not, proceed without it.

---

## Preamble: Context File Scan

Scan `.pmf/context/` for files the user may have dropped in for reference.

1. If `--no-context` was passed as an argument, skip this entire section
2. Use Glob to check if `.pmf/context/` directory exists and list all files in it: `.pmf/context/**/*`
3. If the directory does not exist or is empty, proceed to the next section
4. If `.pmf/STATE.md` exists, read the Processed Context table to identify which files have already been processed
5. Identify NEW files (present in directory but not in the Processed Context table)
6. If there are no new files, proceed to the next section
7. If there are new files, process them using the same pattern as new-milestone (images, PDFs, text files)
8. Record processed files for STATE.md update later

---

## Step 1: Load Inputs

Gather all the information needed to design the optimization plan.

1. Read `.pmf/STRATEGY.md` and extract:
   - Asset (e.g., BTC/USDT, AAPL, EUR/USD)
   - Exchange/Source (e.g., Binance, yfinance, Dukascopy)
   - Timeframe (e.g., 1H, 4H, 1D)
   - Date Range (start and end dates)
   - Success Criteria: Sharpe target, Max Drawdown target, Minimum trade count
   - Strategy type (trend-following, mean-reversion, breakout, custom)

2. Read `.pmf/phases/phase_N_discuss.md` and extract:
   - All strategy decisions: entry logic, exit logic, stop-loss, take-profit, position sizing, commission
   - Parameters to optimize: each with min, max, step, type (from the "To Optimize" table)
   - Fixed parameters: each with value and rationale (from the "Fixed" table)
   - Any constraints mentioned during discussion

3. Check if `.pmf/phases/phase_N_research.md` exists:
   - If it exists, read it and extract:
     - Recommendations for plan phase (parameter ranges, optimization suggestions, data requirements)
     - Pitfall assessment (risk ratings that should inform constraints)
     - Any lookahead traps specific to this strategy type
   - If it does NOT exist, note that research was skipped and proceed

4. Read `~/.pmf/references/backtest-engine.md` and note the engine constraints:
   - Anti-lookahead rules: signal sees only past and current bar
   - Execution at next bar's open price
   - Event-loop architecture (one bar at a time)
   - The plan must design parameters that work within these constraints

5. Display a summary of what was loaded:

```
--- Inputs Loaded ---
Strategy: {strategy type} on {asset} ({timeframe})
Parameters: {X} to optimize, {Y} fixed
Research: {available -- summary of key recommendations / not done}
Engine constraints: loaded (anti-lookahead, next-bar execution)
```

---

## Step 2: Define Parameter Space

Build the complete parameter space from the discuss output.

### Free Parameters (to optimize)

For each parameter the user wants to optimize (from phase_N_discuss.md):

1. **Confirm the range** (min, max) from discuss output
2. **Confirm or suggest step size:**
   - If discuss specified a step size, use it
   - If discuss did NOT specify a step size, suggest reasonable defaults:
     - **Integer params** (e.g., period lengths): step = 1 (or round to nearest meaningful increment)
     - **Float params** (e.g., thresholds, multipliers): step = (max - min) / 20 (approximately 20 steps)
     - **Period params** (e.g., SMA length, lookback): step = 1 for small ranges (<50 span), step = 5 for large ranges (>50 span)
   - Present the suggested step size and let the user adjust
3. **Calculate total combinations** for each parameter: floor((max - min) / step) + 1
4. **Confirm parameter type:** int, float, or categorical

Present the complete free parameter table:

```
### Parameters to Optimize
| Parameter | Min | Max | Step | Type | Combinations |
|-----------|-----|-----|------|------|--------------|
| {name}    | {min} | {max} | {step} | {type} | {combos} |
...

Total combinations (all parameters): {product of all individual combinations}
```

### Fixed Parameters

For each fixed parameter from discuss output, list with its value and rationale:

```
### Fixed Parameters
| Parameter | Value | Rationale |
|-----------|-------|-----------|
| {name}    | {value} | {why it's fixed} |
```

### Parameter Constraints

Detect and define constraints between parameters:

1. **Auto-detect obvious constraints** from the strategy logic:
   - If two period parameters exist (e.g., fast_period / slow_period), enforce fast < slow
   - If stop-loss and take-profit both exist, note if relationship matters (e.g., TP must be > SL for positive risk-reward ratio)
   - If lookback periods exist, note minimum data requirement (lookback must be < available bars)
   - If a threshold parameter exists alongside a period, check for logical relationships

2. **Incorporate research recommendations** (if available):
   - If research identified pitfalls related to parameter ranges, add constraints to prevent them
   - If research recommended specific range restrictions, apply them

3. **Present detected constraints** and ask the user if any others apply:

```
### Detected Constraints
- {constraint 1}: {description and rationale}
- {constraint 2}: {description and rationale}

Any additional constraints? (add them or say "none")
```

4. Record all constraints (auto-detected + user-added) in the plan

---

## Step 3: Parameter Budget Check

Calculate the parameter budget to detect and warn about overfitting risk.

Compute the following:
- **Total free parameters:** count of parameters to optimize
- **Total combinations:** product of (combinations per parameter)
- **Estimated data points:** approximate number of bars in the date range based on timeframe
  - 1D bars: trading days in range (roughly 252/year for stocks, 365/year for crypto/forex)
  - 4H bars: ~6 per day (stocks) or ~6 per day (crypto 24/7)
  - 1H bars: ~24 per day (crypto) or ~6.5 per day (stocks)
  - Use reasonable approximations -- exact counts come during execute
- **Minimum trades:** from STRATEGY.md success criteria (default 30 if not specified)
- **Ratio:** estimated_data_points / (total_combinations * free_params)

### Warning Thresholds

Apply these checks in order:

1. **Free parameter count:**
   - If free_params > 5: WARN "You have {N} free parameters. More than 5 significantly increases overfitting risk. Consider fixing some parameters based on domain knowledge."

2. **Combination-to-trade ratio:**
   - If total_combinations > 100 * min_trades: WARN "You're testing {N} combinations against a {min_trades}-trade minimum. With this many combinations, there is a high probability of finding parameters that look good by chance. Statistical significance is questionable."

3. **Absolute combination count:**
   - If total_combinations > 10000: WARN "Grid search with {N} combinations will be slow and prone to overfitting. Random search or walk-forward optimization is strongly recommended."

### Display and User Decision

Present the budget analysis:

```
--- Parameter Budget ---
Free parameters: {N}
Total combinations: {N}
Estimated data bars: ~{N}
Min trades required: {N}

{WARNING if applicable -- display all triggered warnings}
{RECOMMENDATION if applicable:
  - "Consider reducing parameter ranges or increasing step sizes"
  - "Consider fixing some parameters based on domain knowledge"
  - "Walk-forward optimization is recommended for this parameter space"
}

Continue with this parameter space? (yes / modify)
```

If the user says "modify," go back to Step 2 and let them adjust ranges, steps, or fix some parameters.

If warnings were triggered but user says "yes," accept and proceed -- the budget check warns and recommends but does NOT enforce. Record the user's decision to proceed despite warnings.

---

## Step 4: Select Optimization Method

Auto-select the optimization method based on parameter count and total combinations.

### Auto-Selection Rules

- **Total combinations < 1000:** Grid search (exhaustive) -- tests every single combination. Feasible and gives the most complete picture.
- **Total combinations 1000-10000:** Random search -- samples N iterations (default: 50) from the parameter space. Covers the space efficiently without testing everything.
- **3+ free parameters OR total combinations > 10000:** Walk-forward optimization -- rolling train/test windows. Recommended for robustness and best defense against overfitting.

### Display and Override

Present the auto-selection with reasoning:

```
--- Optimization Method ---
Method: {grid_search / random_search / walk_forward}
Reason: {why this was selected, referencing the rules above}

{If random_search: "Max iterations: 50 (adjustable)"}
{If walk_forward: "Train window and test window will be configured in Step 6"}

Override? (grid / random / walk-forward / keep)
```

If the user overrides:
- Accept their choice
- Record it with a note: "User override: selected {method} instead of auto-selected {method}"
- If the user selects grid search for a large parameter space (>10000), remind them: "Grid search with {N} combinations will take significant time. Are you sure? (yes / pick another method)"

If the user says "keep," proceed with the auto-selected method.

---

## Step 5: Define Evaluation Criteria

Set the criteria used to evaluate each parameter combination during optimization.

### Primary Metric

- **Sharpe Ratio** is always the primary optimization metric
- Target: use the Sharpe target from STRATEGY.md success criteria
- Display: "Primary metric: Sharpe Ratio > {target} (from your milestone success criteria)"

### Secondary Metrics

Present these defaults and let the user adjust:

| Metric | Default Target | Notes |
|--------|---------------|-------|
| Max Drawdown | < {target from STRATEGY.md}% | Hard filter -- iterations exceeding this are discarded |
| Profit Factor | > 1.5 | Ratio of gross profit to gross loss |
| Win Rate | informational | No hard target unless user sets one |
| Expectancy | > 0 | Average profit per trade (informational) |

### Minimum Trade Count

- Default: 30 (or the value from STRATEGY.md / discuss if different)
- Explanation: "Iterations with fewer than {N} trades are automatically discarded. Too few trades means the results are not statistically significant -- a strategy that makes 5 great trades could easily be luck."
- Let the user adjust if they have a reason (e.g., weekly timeframe strategies may have fewer opportunities)

### Display

```
--- Evaluation Criteria ---
Primary: Sharpe Ratio > {target}

Secondary filters:
  Max Drawdown: < {target}%    [hard filter]
  Profit Factor: > 1.5         [hard filter]
  Win Rate: informational      [no hard target]
  Expectancy: > 0              [informational]

Minimum trade count: {N} (iterations with fewer trades are discarded)

Adjust any criteria? (yes / looks good)
```

If the user wants to adjust, let them modify targets, add new metrics, or change whether a metric is a hard filter vs informational.

---

## Step 6: Define Data Period and Train/Test Split

Define the data configuration and how the data will be split for optimization vs validation.

### Data Configuration

Read from STRATEGY.md (set during new-milestone) and confirm:

```
--- Data Configuration ---
Asset: {from STRATEGY.md}
Source: {from STRATEGY.md}
Timeframe: {from STRATEGY.md}
Date Range: {from STRATEGY.md}
```

### Train/Test Split

The plan defines RULES (percentages and method). The execute phase calculates exact dates from actual data.

**Default split:** 70% train / 30% test (chronological)
- The first 70% of data (by date) is used for optimization
- The last 30% is held out for validation
- The optimizer NEVER sees test data during parameter search
- Test results are evaluated ONCE after optimization completes

**For walk-forward optimization:** define window configuration
- **Train window:** suggested default based on timeframe and date range
  - Daily: 6-12 months of bars
  - Intraday: 3-6 months of bars
- **Test window:** typically 1/3 of train window
  - Daily: 2-4 months
  - Intraday: 1-2 months
- **Step size:** how far the window advances each iteration (typically = test window size for non-overlapping)

Present the configuration:

```
Train/Test Split:
  Method: chronological
  Train: 70%
  Test: 30%

{If walk-forward method was selected in Step 4:}
Walk-Forward Windows:
  Train window: {N} bars (~{M} months)
  Test window: {N} bars (~{M} months)
  Step size: {N} bars
  Estimated windows: {N} walk-forward iterations

Note: Exact bar counts and dates will be calculated by the execute
phase from the actual downloaded data.

Adjust? (yes / looks good)
```

If the user adjusts:
- Let them change the train/test percentage (must sum to 100%)
- Let them change walk-forward window sizes
- Record their choices

---

## Step 7: Compile and Confirm Plan

Display the complete optimization plan in one consolidated view for final review.

```
========================================
         OPTIMIZATION PLAN
========================================

## Parameters
### To Optimize
| Parameter | Min | Max | Step | Type | Combinations |
|-----------|-----|-----|------|------|--------------|
{table rows}

### Fixed
| Parameter | Value | Rationale |
|-----------|-------|-----------|
{table rows}

### Constraints
{list of all constraints}

## Optimization
Method: {grid_search / random_search / walk_forward}
{If random: Max iterations: {N}}
{If walk-forward: Train {N} bars, Test {M} bars, Step {S} bars}

## Evaluation
Primary: Sharpe > {target}
Secondary: Max DD < {target}%, Profit Factor > 1.5
Min trades: {N}

## Data
Asset: {asset} on {source}
Timeframe: {timeframe}
Date Range: {start} to {end}
Split: {train}% train / {test}% test

## Parameter Budget
Free params: {N}
Combinations: {N}
Budget: {OK / WARNING: reason}

========================================
```

Use AskUserQuestion with header "Confirm", question "Does this plan look correct?", options: "Yes, save it" (proceed to write artifact), "Change something" (ask what to change). If user picks Other with a comment, treat as change request.

If the user requests changes:
- Identify which step the change belongs to (Step 2 for parameters, Step 3 for budget, Step 4 for method, Step 5 for criteria, Step 6 for data)
- Go back to that step, make the change, then return here for re-confirmation
- Loop until the user confirms

---

## Step 8: Write Output Artifact

After confirmation, write the formal plan artifact.

Write `.pmf/phases/phase_N_plan.md` with this structure:

```markdown
# Phase {N} -- Optimization Plan

## Parameter Space

### Free Parameters (to optimize)
| Parameter | Min | Max | Step | Type | Combinations |
|-----------|-----|-----|------|------|--------------|
| {name} | {min} | {max} | {step} | {type} | {combos} |

### Fixed Parameters
| Parameter | Value | Rationale |
|-----------|-------|-----------|
| {name} | {value} | {why} |

### Constraints
- {constraint description}

## Optimization Method
- **Method:** {grid_search | random_search | walk_forward}
- **Reason:** {auto-selected because X | user override: selected Y instead of Z}
- **Max iterations:** {N}

{If walk-forward:}
### Walk-Forward Configuration
- Train window: {N} bars
- Test window: {M} bars
- Step size: {S} bars

## Evaluation Criteria
- **Primary metric:** Sharpe Ratio > {target}
- **Max Drawdown:** < {target}%
- **Profit Factor:** > {target}
- **Minimum trade count:** {N}
- **Win Rate:** informational (no hard target) {or user-set target}

## Data Configuration
- **Asset:** {asset}
- **Source:** {exchange/source}
- **Timeframe:** {timeframe}
- **Date Range:** {start} to {end}
- **Train/Test Split:** {train}% / {test}% (chronological)

## Parameter Budget
- **Free parameters:** {N}
- **Total combinations:** {N}
- **Estimated data bars:** ~{N}
- **Budget status:** {OK | WARNING: reason}

## Research Inputs
{If research was done: summary of recommendations incorporated}
{If no research: "Research phase was skipped"}

---
*Phase {N} plan completed: {date}*
*Ready for: /brrr:execute*
```

---

## Step 9: Update STATE.md

Update the milestone state to reflect plan completion.

1. Read `.pmf/STATE.md`
2. Mark plan step as done: `- [x] Plan`
3. Update Current Step to `execute` (the next step in the sequence)
4. Update Last Updated to today's date
5. Append to History (newest entries first):

```
### {date} -- Phase {N} plan completed
- **Method:** {optimization method}
- **Free params:** {N}, Fixed: {M}
- **Combinations:** {N}
- **Budget:** {OK / WARNING}
```

6. Write updated STATE.md

---

## Step 10: Confirmation

Display the completion message.

```
Phase {N} plan complete!

Artifact: .pmf/phases/phase_{N}_plan.md
Method: {optimization method}
Parameters: {X} to optimize ({Y} combinations), {Z} fixed
Split: {train}% train / {test}% test

Next step: `/brrr:execute`
```

---

*Workflow: plan*
*Covers: PLAN-01, PLAN-02, PLAN-03, PLAN-04, PLAN-05, PLAN-06, PLAN-07, PLAN-08*
