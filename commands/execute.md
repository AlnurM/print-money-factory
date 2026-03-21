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
Run the AI-driven backtest loop: load data, run backtest, compute metrics, AI analyzes, adjust params, repeat until targets hit or strategy diagnosed.
</objective>

<execution_context>
@~/.pmf/workflows/execute.md
@~/.pmf/references/backtest-engine.md
@~/.pmf/references/metrics.py
@~/.pmf/references/data_sources.py
</execution_context>

<context>
$ARGUMENTS
</context>

<process>
Follow the workflow defined in @~/.pmf/workflows/execute.md to run the optimization loop.
</process>
