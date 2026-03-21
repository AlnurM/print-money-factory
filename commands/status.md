---
name: brrr:status
description: Show milestone progress and next step
allowed-tools:
  - Read
  - Bash
  - Glob
---

<objective>
Display an ASCII tree showing milestone progress, all phases, and the recommended next step.
</objective>

<execution_context>
@~/.pmf/workflows/status.md
</execution_context>

<process>
Follow the workflow defined in @~/.pmf/workflows/status.md to display current status.
</process>
