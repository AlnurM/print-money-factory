# Workflow: doctor

Run diagnostic checks on the Print Money Factory installation. This workflow is READ-ONLY -- it does not modify any files.

---

## Section 1: Check Python Version

1. Run via Bash: `python3 --version`
2. Parse the version number from the output (e.g., "Python 3.14.1" -> 3.14).
3. If the major version is 3 and the minor version is >= 10:
   - Report: `[PASS] Python {version} detected`
4. If Python is not found or the version is < 3.10:
   - Report: `[FAIL] Python >= 3.10 required -- install from python.org`
5. Track the result (pass or fail) for the summary.

---

## Section 2: Check venv

1. Run via Bash: `ls ~/.pmf/venv/bin/python 2>/dev/null && echo "EXISTS" || echo "MISSING"`
2. If the output contains "EXISTS":
   - Report: `[PASS] venv exists at ~/.pmf/venv/`
   - Set a flag `venv_ok = true` for use in Section 3.
3. If the output contains "MISSING":
   - Report: `[FAIL] venv missing -- run npx print-money-factory install`
   - Set a flag `venv_ok = false`.
4. Track the result for the summary.

---

## Section 3: Check Core Imports

**If `venv_ok` is false (venv check failed in Section 2):**
- Report all 10 imports as `[FAIL]` with the message: `[FAIL] import {library} -- venv missing, run npx print-money-factory install`
- Skip the actual import checks. Track 10 failures for the summary.
- Proceed to Section 4.

**If `venv_ok` is true:**

Run the following single Bash command to test all imports at once:

```bash
~/.pmf/venv/bin/python -c "
import sys
libraries = ['pandas', 'numpy', 'ccxt', 'yfinance', 'plotly', 'optuna', 'ta', 'matplotlib', 'scipy', 'jinja2']
for lib in libraries:
    try:
        __import__(lib)
        print(f'[PASS] import {lib}')
    except ImportError:
        print(f'[FAIL] import {lib} -- run ~/.pmf/venv/bin/pip install -r requirements.txt')
"
```

Display each line of output as-is. Track pass/fail counts for the summary.

---

## Section 4: Check Command Files

1. Use Glob to list all files matching `~/.claude/commands/brrr/*.md`.
2. Define the expected command files: `discuss.md`, `doctor.md`, `execute.md`, `new-milestone.md`, `plan.md`, `research.md`, `status.md`, `update.md`, `verify.md`
3. For each expected file, check if it exists in the Glob results.
4. If ALL 9 expected files are present:
   - Report: `[PASS] Command files (9 files in ~/.claude/commands/brrr/)`
   - Track 1 pass for the summary.
5. For any missing file:
   - Report: `[FAIL] Missing command: {name}.md -- run npx print-money-factory install`
   - Track 1 fail per missing file for the summary.
   - If some files ARE present, do NOT report a pass line -- only report the individual failures.

---

## Section 5: Check Workflow Files

1. Use Glob to list all files matching `~/.pmf/workflows/*.md`.
2. Define the expected workflow files: `discuss.md`, `doctor.md`, `execute.md`, `new-milestone.md`, `plan.md`, `research.md`, `status.md`, `verify.md`
3. For each expected file, check if it exists in the Glob results.
4. If ALL 8 expected files are present:
   - Report: `[PASS] Workflow files (8 files in ~/.pmf/workflows/)`
   - Track 1 pass for the summary.
5. For any missing file:
   - Report: `[FAIL] Missing workflow: {name}.md -- run npx print-money-factory install`
   - Track 1 fail per missing file for the summary.
   - If some files ARE present, do NOT report a pass line -- only report the individual failures.

---

## Section 6: Check Reference Files

1. Run via Bash: `ls ~/.pmf/references/ 2>/dev/null | head -1`
2. If the command produces output (directory exists and has files):
   - Report: `[PASS] Reference files present in ~/.pmf/references/`
3. If the command produces no output (directory missing or empty):
   - Report: `[FAIL] Reference files missing -- run npx print-money-factory install`
4. Track the result for the summary.

---

## Section 7: Summary

1. Count the total number of checks run and the total number of passes across all sections.
   - Section 1: 1 check (Python version)
   - Section 2: 1 check (venv)
   - Section 3: 10 checks (one per library)
   - Section 4: 1 check if all present, or N checks (one per missing file) if any missing
   - Section 5: 1 check if all present, or N checks (one per missing file) if any missing
   - Section 6: 1 check (reference files)
2. Display: `{X}/{Y} checks passed`
3. If all checks passed:
   - Display: `Verdict: HEALTHY`
4. If any checks failed:
   - Display: `Verdict: NEEDS ATTENTION`
   - Display: `Run the suggested fix commands above to resolve issues.`

---

## Important Constraints

- **READ-ONLY**: This workflow does NOT modify any files. It only reads and runs diagnostic commands.
- Use the exact `[PASS]` and `[FAIL]` prefix format for every check result.
- Each `[FAIL]` line MUST include a fix suggestion after the `--`.
- Handle the case where venv does not exist gracefully (skip import checks, report venv FAIL and 10 import FAILs).
- All output must be in English.
