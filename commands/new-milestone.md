---
name: brrr:new-milestone
description: Create a new trading strategy milestone
allowed-tools:
  - Read
  - Write
  - Bash
  - Glob
---

<objective>
Create a new trading strategy milestone by collecting the user's strategy idea, defining scope, setting success criteria, and outputting STRATEGY.md and STATE.md.
</objective>

<execution_context>
@~/.pmf/workflows/new-milestone.md
@~/.pmf/templates/STRATEGY.md
@~/.pmf/templates/STATE.md
</execution_context>

<process>
Follow the workflow defined in @~/.pmf/workflows/new-milestone.md to guide the user through milestone creation.
</process>
