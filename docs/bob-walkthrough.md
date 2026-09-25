# Bob live walkthrough — Sprint 5 screenshot capture guide

This guide walks you through the complete Vesper workflow inside Bob IDE so you can capture the required task-summary screenshots for `bob_sessions/`.

---

## Prerequisites

- Bob IDE installed and updated to 2.0.2 or later (see `docs/event-requirements.md`).
- Signed into the hackathon-provisioned account (ibm-hackathon-xxxx or ibm-coding-challenge-xxx — verify the actual name in your IDE settings, do not guess).
- Project folder open: File > Open Folder → select the `vesper` project root.
- On the Windows dev machine: open a Bob terminal and run `. ./scripts/use-local-tools.ps1` before asking Bob to run any Maven commands.
- Bobcoin balance confirmed in account settings.

---

## Screenshot naming convention

```
bob_sessions/black_sheep_<yourname>_task<NN>_<short_description>_summary.png
```

Examples already present (note: files currently have a doubled `.png.png` extension — rename them before submission):
- `black_sheep_sam_task01_baseline_summary.png`
- `black_sheep_sam_task02_reproduction_summary.png`
- `black_sheep_sam_task03_fix_summary.png`

For Sprint 5 add at minimum:
- `black_sheep_<name>_task04_workflow_rehearsal_summary.png`

---

## How to capture a task-summary screenshot in Bob

1. In Bob IDE, click **Tasks** in the left panel (or the task icon in the activity bar).
2. Find the task that just completed.
3. Click the task header row — this opens the task detail panel.
4. Scroll to the **Consumption Summary** section showing tokens/Bobcoins used.
5. Take a screenshot of the full summary (include task name, date/time, and consumption figures).
6. Save the PNG to `bob_sessions/` using the naming convention above.

> **Integrity reminder (from AGENTS.md):** Record actual task-summary screenshots. Never synthesize them. If Bob didn't run a task, there is no screenshot to capture.

---

## Complete walkthrough — step by step

### Task 1 (if not already captured): Baseline

**Bob prompt:**
```
Read AGENTS.md and docs/requirements.md. Then run the demo baseline:
  python -m vesper baseline
Show me the result.
```

Expected: Bob reads the files, runs the baseline, reports "passed: 12 tests, 0 failures".

📸 **Capture screenshot** → `black_sheep_<name>_task01_baseline_summary.png`

---

### Task 2 (if not already captured): Reproduce R3

**Bob prompt:**
```
Using the Vesper skill, review Checkout.java against demo/requirements.md.
Focus on requirement R3. Confirm the expected behaviour with me, then write and
run a reproducer test. Show me the actual test output.
```

Expected: Bob presents R3 interpretation, you confirm it, Bob writes `ReproducerR3Test.java`, runs it, shows the failure output (expected: 900, was: 1000).

📸 **Capture screenshot** → `black_sheep_<name>_task02_reproduction_summary.png`

---

### Task 3 (if not already captured): Fix and verify

**Bob prompt:**
```
The reproducer confirms the R3 bug. Prepare a candidate fix for Checkout.java.
Show me the exact diff before applying it. Then run the unchanged reproducer and
the full regression suite and show me the results.
```

Expected: Bob shows the single-line diff (`!today.isBefore` → `today.isAfter`), you approve, Bob runs both suites, reports 12/12 pass.

📸 **Capture screenshot** → `black_sheep_<name>_task03_fix_summary.png`

---

### Task 4 (Sprint 5): Full workflow rehearsal

**Bob prompt:**
```
Run the complete Vesper workflow end-to-end:
  python -m vesper workflow --timeout 300
Show me each stage result and the final summary report.
```

Expected: All 8 stages pass. Final line: `✓ WORKFLOW PASSED  (6–10s total)`

📸 **Capture screenshot** → `black_sheep_<name>_task04_workflow_rehearsal_summary.png`

---

### Task 5 (Sprint 5): Timing study — manual task

Ask Bob to time you through the manual protocol from `docs/timing-study.md`. Or time yourself independently and report the numbers honestly.

📸 **Capture screenshot** → `black_sheep_<name>_task05_timing_study_summary.png` (if Bob was used to facilitate)

---

## After all tasks are captured

1. Open `bob_sessions/` in Finder/Explorer.
2. Rename the existing `.png.png` files to `.png` (remove the doubled extension):
   - `bob_sessionsblack_sheep_sam_task01_baseline_summary.png.png` → `black_sheep_sam_task01_baseline_summary.png`
   - Same for tasks 02 and 03.
3. Verify all screenshots are readable (not blank, not cropped before the consumption figures).
4. Update `bob_sessions/README.md` with a table listing every captured screenshot, the task number, and the Bobcoin consumption (read from the screenshot — do not estimate).

---

## Checklist before recording the demo video

- [ ] At least tasks 01–04 have real screenshots in `bob_sessions/`
- [ ] All filenames follow the convention (no doubled extensions)
- [ ] `bob_sessions/README.md` lists every screenshot with actual Bobcoin figures
- [ ] `Checkout.java` is in its **fixed** state (line 14: `today.isAfter(expiry)`)
- [ ] `python -m vesper workflow --timeout 300` exits 0 when run from the project root
