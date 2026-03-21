---
name: brrr:verify
description: Generate interactive report and approve or debug strategy
argument-hint: "[--approved] [--debug]"
allowed-tools:
  - Read
  - Write
  - Bash
  - Glob
---

<objective>
Generate an interactive HTML report for strategy evaluation. Accept --approved to close milestone and generate exports, or --debug to open a new phase cycle with AI diagnosis.
</objective>

<execution_context>
@~/.pmf/workflows/verify.md
</execution_context>

<context>
$ARGUMENTS
</context>

<process>
Follow the workflow defined in @~/.pmf/workflows/verify.md to generate the report and handle approval or debug flow.
</process>
