---
name: brrr:doctor
description: Diagnose installation health and report issues
allowed-tools:
  - Read
  - Bash
  - Glob
---

<objective>
Run diagnostic checks on the Print Money Factory installation and display pass/fail results.
</objective>

<execution_context>
@~/.pmf/workflows/doctor.md
</execution_context>

<process>
Follow the workflow defined in @~/.pmf/workflows/doctor.md to run all diagnostic checks.
</process>
