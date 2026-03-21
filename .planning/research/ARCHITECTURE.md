# Architecture Research

**Domain:** Claude Code slash-command npm package for iterative trading strategy development
**Researched:** 2026-03-21
**Confidence:** HIGH

## System Overview

```
                          NPM PACKAGE (print-money-factory)
┌──────────────────────────────────────────────────────────────────────┐
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────────────┐    │
│  │ commands/ │  │workflows/│  │templates/│  │   references/    │    │
│  │ (thin MD) │→ │(full MD) │  │(MD + py  │  │(backtest engine, │    │
│  │          │  │          │  │ + html)  │  │ data, metrics)   │    │
│  └──────────┘  └──────────┘  └──────────┘  └──────────────────┘    │
│  ┌──────────────────┐  ┌────────────────────────────────────────┐   │
│  │ bin/              │  │ scripts/install.js                     │   │
│  │  gsd-tools-like   │  │  Copies to ~/.claude/commands/brrr/   │   │
│  │  (Node.js CLI)    │  │  Creates Python venv                  │   │
│  └──────────────────┘  └────────────────────────────────────────┘   │
└──────────────────────────────────────────────────────────────────────┘
         │ install
         ▼
┌──────────────────────────────────────────────────────────────────────┐
│               INSTALLED (user machine)                               │
│                                                                      │
│  ~/.claude/commands/brrr/      ~/.pmf-venv/                          │
│  ├── new-milestone.md          Python 3.10+                          │
│  ├── discuss.md                ├── pandas, numpy                     │
│  ├── research.md               ├── ccxt, yfinance                    │
│  ├── plan.md                   ├── plotly, kaleido                   │
│  ├── execute.md                ├── optuna                            │
│  ├── verify.md                 └── matplotlib                        │
│  ├── status.md                                                       │
│  └── update.md                                                       │
│                                                                      │
│  ~/.pmf/                        (package metadata)                   │
│  ├── .version                   version, repo, install date          │
│  ├── workflows/                 full workflow MDs                     │
│  ├── templates/                 strategy, state, report templates     │
│  └── references/                backtest engine, data, metrics        │
└──────────────────────────────────────────────────────────────────────┘
         │ user runs /brrr:execute
         ▼
┌──────────────────────────────────────────────────────────────────────┐
│               USER PROJECT (CWD)                                     │
│                                                                      │
│  .pmf/                          output/ (on --approved)              │
│  ├── STRATEGY.md                ├── pinescript_v5.pine               │
│  ├── STATE.md                   ├── trading-rules.md                 │
│  ├── context/                   ├── performance-report.md            │
│  │   └── (user images, PDFs)    ├── backtest_final.py                │
│  └── phases/                    ├── live-checklist.md                │
│      ├── phase_1_discuss.md     └── report_v1.html                   │
│      ├── phase_1_plan.md                                             │
│      ├── phase_1_execute/                                            │
│      │   ├── backtest.py                                             │
│      │   ├── iter_01_params.json                                     │
│      │   ├── iter_01_metrics.json                                    │
│      │   ├── iter_01_equity.png                                      │
│      │   └── iter_01_verdict.json                                    │
│      └── phase_1_best_result.json                                    │
└──────────────────────────────────────────────────────────────────────┘
```

### Component Responsibilities

| Component | Responsibility | Typical Implementation |
|-----------|----------------|------------------------|
| **commands/** | Thin entry points for Claude Code slash commands | Markdown with YAML frontmatter, `@` references to workflows |
| **workflows/** | Full behavioral instructions for each command | Large markdown files with detailed prompts, decision trees, output formats |
| **templates/** | Scaffolding for generated files | Markdown templates for STRATEGY.md, STATE.md; HTML template for reports; Python template for backtest |
| **references/** | Reusable knowledge Claude reads during execution | Backtest engine patterns, data source configs, metrics formulas, pitfall catalog |
| **bin/** | Node.js CLI tooling | Version checking, data source helper scripts, venv management |
| **scripts/install.js** | Installation orchestrator | Copies commands to `~/.claude/commands/brrr/`, creates venv, installs Python deps |
| **.pmf/ (user project)** | Per-project state and artifacts | STRATEGY.md, STATE.md, phases/, context/ |
| **output/ (user project)** | Final deliverables on milestone close | PineScript, reports, clean backtest code |

## Recommended Package Structure

```
print-money-factory/
├── package.json               # npm metadata, bin entry, version
├── scripts/
│   └── install.js             # Main installer: copies commands, creates venv
├── commands/                  # Thin slash-command entry points
│   ├── new-milestone.md       # → /brrr:new-milestone
│   ├── discuss.md             # → /brrr:discuss
│   ├── research.md            # → /brrr:research
│   ├── plan.md                # → /brrr:plan
│   ├── execute.md             # → /brrr:execute
│   ├── verify.md              # → /brrr:verify
│   ├── status.md              # → /brrr:status
│   └── update.md              # → /brrr:update
├── workflows/                 # Full behavioral prompts
│   ├── new-milestone.md       # Scoping flow with context parsing
│   ├── discuss.md             # Strategy decision gathering + debug diagnosis
│   ├── research.md            # Implementation/academic research
│   ├── plan.md                # Parameter space + optimization design
│   ├── execute.md             # Backtest loop orchestration
│   └── verify.md              # Report generation + approved/debug flow
├── templates/
│   ├── STRATEGY.md            # Milestone hypothesis scaffold
│   ├── STATE.md               # Milestone state tracker scaffold
│   ├── phase-discuss.md       # Discussion output format
│   ├── phase-plan.md          # Plan output format
│   ├── report-template.html   # Plotly HTML report scaffold
│   └── pinescript-template.pine # PineScript v5 skeleton
├── references/
│   ├── backtest-engine.md     # Patterns for Claude to write backtest code
│   ├── data-sources.md        # How to connect each data source (ccxt, yfinance, etc.)
│   ├── metrics-formulas.md    # Sharpe, Sortino, Calmar, MaxDD, etc.
│   ├── common-pitfalls.md     # Lookahead bias, survivorship bias, etc.
│   └── strategy-catalog.md    # Strategy archetypes and their gotchas
├── bin/
│   ├── pmf-tools.cjs          # Node.js CLI: version check, venv helpers
│   └── lib/
│       ├── install.cjs        # Install logic (copy, venv create)
│       ├── version.cjs        # Version check against GitHub releases
│       └── venv.cjs           # Python venv detection and management
└── python/
    └── requirements.txt       # pandas, numpy, ccxt, yfinance, plotly, optuna, etc.
```

### Structure Rationale

- **commands/ vs workflows/:** Commands are thin (5-15 lines) frontmatter + `@` references. Workflows contain the full behavioral prompt (hundreds of lines). This mirrors GSD exactly and keeps commands lightweight for Claude Code to parse.
- **references/ vs templates/:** References are read-only knowledge (how backtest engines work, what metrics mean). Templates are scaffolding that gets copied and filled in per project.
- **bin/ separate from scripts/:** `scripts/install.js` is the npx entry point. `bin/` holds runtime tools that commands invoke via Bash during normal operation.
- **python/ directory:** Contains only `requirements.txt`. Actual Python code is generated by Claude at runtime based on references/backtest-engine.md patterns. No fixed Python library ships with the package.

## Architectural Patterns

### Pattern 1: Thin Command / Fat Workflow Delegation

**What:** Each `/brrr:*` command is a thin markdown file with YAML frontmatter that delegates to a workflow file via `@` reference. The command defines *what* (name, description, allowed tools, arguments). The workflow defines *how* (full behavioral prompt, decision trees, output formats).

**When to use:** Every command. No exceptions.

**Trade-offs:** Adds indirection but keeps commands parseable by Claude Code's command system and enables workflow updates without touching the command interface.

**Example:**
```markdown
# commands/execute.md
---
name: brrr:execute
description: Run AI-driven backtest optimization loop
argument-hint: "[--iterations N] [--fast] [--resume]"
allowed-tools:
  - Read
  - Write
  - Bash
  - Glob
---
<objective>
Run the backtest optimization loop for the current phase.
</objective>

<execution_context>
@~/.pmf/workflows/execute.md
@~/.pmf/references/backtest-engine.md
@~/.pmf/references/metrics-formulas.md
@~/.pmf/references/data-sources.md
</execution_context>

<context>
Flags: $ARGUMENTS
</context>

<process>
Execute the backtest workflow from @~/.pmf/workflows/execute.md
</process>
```

### Pattern 2: State-Driven Command Routing

**What:** Every command reads STATE.md first to determine current position, then validates whether the command is valid in that state. Invalid commands get a helpful redirect instead of a generic error.

**When to use:** Every command except `new-milestone` (which creates STATE.md) and `status` (which is always valid).

**Trade-offs:** Requires STATE.md to be reliably maintained. If STATE.md gets corrupted, all commands break. Mitigation: `status` command can rebuild STATE.md from phase artifacts.

### Pattern 3: Claude-Generated Python (Not a Fixed Library)

**What:** The backtest engine is NOT a fixed Python library shipped with the package. Instead, `references/backtest-engine.md` contains patterns and building blocks. Claude writes the complete Python backtest script fresh for each strategy based on the plan phase decisions.

**When to use:** Every execute phase. Each strategy gets custom Python code tailored to its specific entry/exit logic, indicators, and optimization method.

**Trade-offs:**
- Pro: Maximum flexibility. No framework constraints. SMC strategies look completely different from MA crossover strategies.
- Pro: Claude can adapt the code structure to the optimization method (grid search vs walk-forward vs bayesian have fundamentally different loops).
- Con: More tokens per execution. Claude must write 200-400 lines of Python each time.
- Con: Risk of inconsistent quality. Mitigation: `references/backtest-engine.md` provides tested patterns for data loading, metric calculation, equity curve generation.

### Pattern 4: Accumulated Phase History

**What:** Phase artifacts are append-only. Debug cycles create new phase directories (phase_2, phase_3...) rather than overwriting phase_1. STATE.md tracks the full history. Each debug discuss starts by reading all previous phases to form a diagnosis.

**When to use:** The milestone lifecycle. Critical for the debug loop to work correctly.

**Trade-offs:** Disk usage grows with debug cycles but stays manageable (text files + PNGs). The real cost is context window usage when Claude reads all phases, but this is necessary for informed debug diagnosis.

## Data Flow

### Installation Flow

```
npx print-money-factory install
    │
    ▼
scripts/install.js
    │
    ├──→ Copy commands/ → ~/.claude/commands/brrr/
    ├──→ Copy workflows/ → ~/.pmf/workflows/
    ├──→ Copy templates/ → ~/.pmf/templates/
    ├──→ Copy references/ → ~/.pmf/references/
    ├──→ Copy bin/ → ~/.pmf/bin/
    ├──→ Write ~/.pmf/.version (version, date, repo URL)
    │
    └──→ Create Python venv
         ├──→ python3 -m venv ~/.pmf-venv
         └──→ ~/.pmf-venv/bin/pip install -r python/requirements.txt
```

### Milestone Lifecycle Flow

```
/brrr:new-milestone
    │
    ├──→ Parse .pmf/context/ (images, PDFs)
    ├──→ Collect strategy idea, scope, data source, targets
    ├──→ Write .pmf/STRATEGY.md
    └──→ Write .pmf/STATE.md
         │
         ▼
/brrr:discuss
    │
    ├──→ Read STATE.md → validate position
    ├──→ Read STRATEGY.md + previous phases (if debug)
    ├──→ Gather strategy decisions through conversation
    └──→ Write .pmf/phases/phase_N_discuss.md
         │
         ▼
/brrr:research (optional)
    │
    ├──→ Read STATE.md → validate position
    ├──→ WebSearch for implementations, pitfalls
    └──→ Write .pmf/phases/phase_N_research.md
         │
         ▼
/brrr:plan
    │
    ├──→ Read STATE.md + discuss + research
    ├──→ Design parameter space, optimization method, evaluation criteria
    └──→ Write .pmf/phases/phase_N_plan.md
         │
         ▼
/brrr:execute
    │
    ├──→ Read STATE.md + plan.md + references/
    ├──→ Write custom backtest.py based on plan decisions
    ├──→ LOOP: run backtest → compute metrics → AI analyze → adjust
    │    ├──→ Each iteration: write params.json, metrics.json, equity.png, verdict.json
    │    └──→ Stop on: MINT | PLATEAU | REKT | NO DATA
    └──→ Write .pmf/phases/phase_N_best_result.json
         │
         ▼
/brrr:verify
    │
    ├──→ Read all phase artifacts + best_result.json
    ├──→ Generate report HTML (plotly, standalone)
    │
    ├──→ --approved
    │    ├──→ Generate output/ package (PineScript, reports, clean Python)
    │    └──→ Update STATE.md → CLOSED
    │
    └──→ --debug
         ├──→ AI reads full milestone history
         ├──→ Formulates diagnosis
         ├──→ Update STATE.md → new phase cycle
         └──→ Redirect to /brrr:discuss (Phase N+1)
```

### Execute Phase Data Flow (Detail)

```
Plan decisions (phase_N_plan.md)
    │
    ▼
Claude writes backtest.py
    │
    ├──→ Data loading (ccxt/yfinance/polygon/CSV)
    │    └──→ ~/.pmf-venv/bin/python backtest.py
    │
    ▼
┌─────────────── Iteration Loop ───────────────┐
│                                               │
│  Parameters → Backtest Run → Raw Results      │
│       │                          │            │
│       │                     Metric Calc       │
│       │                     (Sharpe, DD,      │
│       │                      WinRate, PF)     │
│       │                          │            │
│       │                     AI Analysis       │
│       │                     (Claude reads     │
│       │                      metrics.json)    │
│       │                          │            │
│       │           ┌──────────────┼────────┐   │
│       │           ▼              ▼        ▼   │
│       │         MINT          PLATEAU   REKT  │
│       │        (stop)        (ask user) (stop)│
│       │                                       │
│       ◄────── Adjust params ◄── Continue      │
│                                               │
└───────────────────────────────────────────────┘
    │
    ▼
best_result.json + all iteration artifacts
```

### Key Data Flows

1. **Context propagation:** STRATEGY.md is written once in new-milestone and read by every subsequent command. It is never modified (append-only via phases). This is the hypothesis anchor.
2. **State as router:** STATE.md is read first by every command to determine what's valid. Updated after every phase completion. Commands that are out-of-order get redirected.
3. **Phase accumulation:** Each phase writes its own artifact (phase_N_discuss.md, phase_N_plan.md, etc.). Debug cycles create new phase numbers. The full history is available for diagnosis.
4. **Python execution bridge:** Claude writes Python code to a file, then runs it via `~/.pmf-venv/bin/python`. Results come back as JSON files and PNGs that Claude reads.

## Integration Points

### External Services

| Service | Integration Pattern | Notes |
|---------|---------------------|-------|
| **ccxt** (crypto) | Python library in venv, called from backtest.py | Exchange-specific. User specifies which exchange. Rate limits apply. |
| **yfinance** (stocks/forex daily) | Python library in venv | Free, no API key. 1H limited to 730 days. Daily goes back decades. |
| **polygon.io** (stocks intraday) | Python library or REST API | Requires API key. Free tier exists. Needed for <1D stock data. |
| **Dukascopy** (forex intraday) | Python scraper/parser | Free tick data. Needs custom download logic. |
| **GitHub API** | Node.js in bin/pmf-tools.cjs | Version check for /brrr:update. GET releases/latest. |
| **plotly** | Python library in venv | Generates standalone HTML reports. No server needed. |
| **kaleido** | Python library in venv | Plotly's static image export. Generates per-iteration equity PNGs. |
| **optuna** | Python library in venv | Bayesian optimization. Only used when plan selects bayesian method. |

### Internal Boundaries

| Boundary | Communication | Notes |
|----------|---------------|-------|
| Command MD → Workflow MD | `@` file reference (Claude Code native) | Command loads workflow into context window |
| Workflow → References | `@` file reference | Workflow loads relevant reference docs |
| Claude → Python | `Bash` tool: write .py file, then run via venv python | JSON files and PNGs as return channel |
| Python → Claude | File I/O: metrics.json, equity.png on disk | Claude reads files after Python exits |
| Command → STATE.md | Read/Write tool | Every command reads state, most update it |
| Install → ~/.claude/ | File copy via Node.js fs | Commands go to ~/.claude/commands/brrr/ |
| Install → ~/.pmf/ | File copy via Node.js fs | Workflows, templates, references, bin |
| Install → ~/.pmf-venv/ | python3 -m venv + pip install | Isolated Python environment |

## Critical Architecture Decisions

### Where to install workflows/references: ~/.pmf/ (not in npm package location)

The npm package location (`node_modules/` or wherever npx caches) is unreliable and varies across systems. Copy everything to a known location:
- Commands: `~/.claude/commands/brrr/` (Claude Code convention)
- Everything else: `~/.pmf/` (our own convention)
- Python venv: `~/.pmf-venv/` (separate to keep clean)

This means the package is "installed" not "linked" -- the npm package itself is only needed during install and update.

### Python execution: venv path hardcoded in workflows

Workflows reference `~/.pmf-venv/bin/python` directly. No PATH manipulation, no activation scripts. This is the simplest reliable approach:

```bash
~/.pmf-venv/bin/python .pmf/phases/phase_1_execute/backtest.py
```

### Report generation: Python writes HTML, not Node.js

Plotly is a Python library. The backtest data is already in Python. Writing the HTML report from Python avoids a data serialization bridge. The report template lives in `~/.pmf/templates/report-template.html` but Claude modifies it inline in the Python script using plotly's `to_html()`.

### Per-iteration artifacts: JSON + PNG, not a database

Each iteration writes discrete files (params.json, metrics.json, equity.png, verdict.json). This is simpler than SQLite, survives crashes (partial results preserved), and Claude can read any individual iteration without loading everything.

## Anti-Patterns

### Anti-Pattern 1: Shipping a Fixed Backtest Library

**What people do:** Build a generic backtesting framework (like vectorbt or backtesting.py) and try to fit all strategies into it.
**Why it's wrong:** Trading strategies vary wildly. SMC with order blocks needs completely different logic than a simple MA crossover. A generic framework either constrains strategies or becomes impossibly complex.
**Do this instead:** Ship patterns and building blocks in references/backtest-engine.md. Let Claude compose them into custom code per strategy.

### Anti-Pattern 2: Storing State in Multiple Places

**What people do:** Spread milestone state across different files without a single source of truth.
**Why it's wrong:** Commands need to know current position instantly. If state is scattered, commands make wrong decisions (running execute before plan, etc.).
**Do this instead:** STATE.md is the single router. Phase artifacts are append-only records. STATE.md points to the current position and references artifacts.

### Anti-Pattern 3: Running Python Without Venv Isolation

**What people do:** Use system Python or assume packages are globally installed.
**Why it's wrong:** Version conflicts with user's own Python projects. Missing packages. Different pandas versions causing subtle bugs.
**Do this instead:** Always use `~/.pmf-venv/bin/python`. Install script creates the venv. Never touch system Python.

### Anti-Pattern 4: Putting Logic in Commands Instead of Workflows

**What people do:** Write the full behavioral prompt directly in the command markdown file.
**Why it's wrong:** Commands are loaded by Claude Code's command parser. Large commands slow down the command menu. Also makes updates harder -- changing behavior requires updating the command file that the user has already installed.
**Do this instead:** Commands are thin (10-20 lines). All logic lives in workflows/ which are referenced via `@`.

## Build Order (Dependencies)

The system has clear dependency chains. Components must be built in this order:

### Layer 1: Foundation (no dependencies)

1. **Package scaffolding** -- package.json, directory structure, basic npm setup
2. **Templates** -- STRATEGY.md, STATE.md templates (they're just markdown scaffolding)
3. **References** -- backtest-engine.md, metrics-formulas.md, data-sources.md, common-pitfalls.md (pure knowledge documents)
4. **Python requirements.txt** -- list of pip packages

### Layer 2: Installation (depends on Layer 1)

5. **scripts/install.js** -- must know what to copy (commands/, workflows/, templates/, references/) and where. Must create venv from requirements.txt.
6. **bin/pmf-tools.cjs** -- version management, venv helpers

### Layer 3: State Management (depends on Layer 1)

7. **STATE.md design** -- the schema for milestone state tracking. Everything else reads/writes this.
8. **STRATEGY.md design** -- the schema for hypothesis documentation.

### Layer 4: Commands + Workflows (depends on Layers 1-3)

Build in lifecycle order because each workflow reads the output of the previous:

9. **new-milestone** (command + workflow) -- creates STRATEGY.md and STATE.md. No prior state needed.
10. **status** (command + workflow) -- reads STATE.md, displays tree. Can be built alongside new-milestone.
11. **discuss** (command + workflow) -- reads STRATEGY.md + STATE.md, outputs phase_N_discuss.md
12. **research** (command + workflow) -- reads discuss output, uses WebSearch, outputs phase_N_research.md
13. **plan** (command + workflow) -- reads discuss + research, outputs phase_N_plan.md
14. **execute** (command + workflow) -- the complex one. Reads plan, writes Python, runs backtest loop, outputs iteration artifacts. Depends on references/ being solid.
15. **verify** (command + workflow) -- reads execute output, generates HTML report, handles --approved and --debug flows
16. **update** (command + workflow) -- checks GitHub, updates installed files. Independent of milestone lifecycle.

### Why This Order Matters for Phases

- **Phase 1** should deliver: package scaffolding + install + new-milestone + status. This gives the user something installable that creates a milestone.
- **Phase 2** should deliver: discuss + plan. The "thinking" commands that don't require Python.
- **Phase 3** should deliver: execute. The backtest loop is the hardest component. It needs references/ to be polished and the Python bridge working reliably.
- **Phase 4** should deliver: verify + export generation. Depends on execute producing real artifacts to verify.
- **Phase 5** should deliver: research + update + polish. These are enhancement commands that add value but aren't on the critical path.

## Scaling Considerations

| Scale | Architecture Adjustments |
|-------|--------------------------|
| Single user, single strategy | Current architecture. No changes needed. |
| Single user, many milestones | STATE.md tracks one at a time. Closed milestones archived. No change needed. |
| Many users (npm downloads) | No server component. Each install is independent. Only concern is GitHub API rate limiting for version checks. |
| Large datasets (years of 1m data) | Python handles this. May need chunked data loading for very large CSVs. Reference doc should include memory management patterns. |
| Complex strategies (many parameters) | Bayesian (optuna) handles this better than grid search. Plan phase should recommend method based on parameter count. |

### Scaling Priorities

1. **First bottleneck:** Context window limits. A strategy with 5 debug cycles accumulates many phase artifacts. Solution: workflows should summarize previous phases rather than reading them in full when context would exceed limits.
2. **Second bottleneck:** Python execution time. Walk-forward with many windows on large datasets can take minutes. Solution: execute workflow should show progress indicators and support `--resume` for interrupted runs.

## Sources

- GSD (get-shit-done) architecture at `~/.claude/get-shit-done/` -- direct inspection of command/workflow/template/reference pattern (HIGH confidence)
- Claude Code slash command system -- direct inspection of `~/.claude/commands/gsd/` for frontmatter format and `@` reference pattern (HIGH confidence)
- PROJECT.md and task.md from project repository -- primary requirements source (HIGH confidence)
- npm package distribution patterns -- well-established, no novel patterns needed (HIGH confidence)
- Python venv management -- standard library, well-documented (HIGH confidence)

---
*Architecture research for: Print Money Factory -- Claude Code trading strategy CLI*
*Researched: 2026-03-21*
