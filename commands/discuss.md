---
name: brrr:discuss
description: Collect strategy decisions through guided conversation
argument-hint: "[--auto]"
allowed-tools:
  - Read
  - Write
  - Bash
  - Glob
---

<objective>
Fix all strategy decisions before code: entry/exit logic, stops, position sizing, commissions, parameter ranges. In debug mode, starts from previous verify diagnosis.
</objective>

<execution_context>
@~/.pmf/workflows/discuss.md
@~/.pmf/references/common-pitfalls.md
</execution_context>

<context>
$ARGUMENTS
</context>

<process>
Follow the workflow defined in @~/.pmf/workflows/discuss.md to guide the strategy discussion.
</process>
