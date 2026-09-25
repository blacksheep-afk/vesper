# Bob session evidence

After each relevant Bob task: Tasks > select task > select task header > capture the consumption summary.
Save actual PNG screenshots here using the naming convention below.
Every participant must include their relevant task summaries.

## Naming convention

```
black_sheep_<yourname>_task<NN>_<short_description>_summary.png
```

## Screenshots captured

| File | Task | Description | Bobcoins | Status |
|------|------|-------------|----------|--------|
| `black_sheep_sam_task01_baseline_summary.png` | 01 | Baseline run — 12 tests pass | _read from screenshot_ | ✅ Renamed |
| `black_sheep_sam_task02_reproduction_summary.png` | 02 | R3 reproduction — reproducer FAIL | _read from screenshot_ | ✅ Renamed |
| `black_sheep_sam_task03_fix_summary.png` | 03 | Fix and verify — 12/12 pass | _read from screenshot_ | ✅ Renamed |
| `black_sheep_<name>_task04_workflow_rehearsal_summary.png` | 04 | Full workflow runner end-to-end | _pending_ | ⬜ Not yet captured |

## Action required before submission

1. **Capture task 04** — run `python -m vesper workflow --timeout 300` inside a Bob task, then capture the consumption summary screenshot.

2. **Fill in the Bobcoins column** — read the actual figures from each screenshot. Do not estimate.

3. **Verify** — each screenshot must show the task name, date/time, and consumption figures. Blank or cropped screenshots are not acceptable.

## Integrity note

Record actual task-summary screenshots after relevant tasks complete.
Never synthesize, fabricate, or estimate Bobcoin consumption.
(AGENTS.md: "Record actual task-summary screenshots under bob_sessions; never synthesize them.")
