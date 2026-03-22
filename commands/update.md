---
name: brrr:update
description: Update Print Money Factory to the latest version
allowed-tools:
  - Read
  - Bash
---

<objective>
Update Print Money Factory to the latest version by re-running the install command.
</objective>

<process>
1. Read `~/.pmf/.version` to record the current installed version.
2. Run `npx @print-money-factory/cli@latest install` to update all commands, workflows, templates, and references.
3. Read the new `~/.pmf/.version` and report what changed (version number, date).
</process>
