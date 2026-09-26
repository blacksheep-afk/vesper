# Petclinic Sprint 5 — Timing Record

Run identifier: `petclinic-sprint5-run-001`  
Assembled: Sprint 5 reporting task, 2026-09-26  

## Methodology note

Timing is derived from `started_at` epoch timestamps and `duration_seconds` fields
in `result.json` files, and from UTC start/end recorded in BASELINE.md.
File modification times are not used to infer durations.
No human active-time measurement was taken; all figures are command execution time.
Interval arithmetic uses the recorded epoch values directly.
Total investigation elapsed time is unknown — individual stage durations are known.

---

## Sprint 1 — Baseline (2026-09-25T22:17 UTC)

| Stage | Duration (s) | Source |
|---|---|---|
| `01-upstream-baseline` attempt | ~141 | BASELINE.md (UTC start/end) |

Note: The Sprint 1 baseline run was executed by participant "surprise2024-cpu" on
the developer's machine. The recorded elapsed time is ~141 seconds (2 min 21 s).
No retries were recorded for the baseline.

---

## Sprint 4 — Candidate verification (2026-09-26, epoch range ~1790388821–1790389130)

Epoch conversion: 1790388882 ≈ 2026-09-25T23:14 UTC (±timezone; exact date uncertain —
epoch seconds relative to 1970-01-01; conversion noted as approximate).

| Attempt | started_at (epoch) | Duration (s) | Exit | Note |
|---|---|---|---|---|
| 01-upstream-baseline | 1790382822 (run 044f6b11) | 218.94 | 0 | Fresh Sprint 4 baseline |
| 02-original-format-check | — | 11.437 | 1 | Setup failure — formatting gate |
| 03-original-reproduction | 1790388882.554 | 52.511 | 1 | First reproduction |
| 04-original-repeat | 1790388935.411 | 49.185 | 1 | Second reproduction |
| 05-candidate-reproducer | 1790389032.800 | None | 128 | Git ownership check — no Maven execution |
| 05-candidate-reproducer-retry | 1790389032.800 | 52.118 | 0 | Retry — passed |
| 06-candidate-regression | — | 97.139 | 0 | Full regression |

**Total recorded execution time for reproduction and candidate verification:**
11.437 + 52.511 + 49.185 + 0 + 52.118 + 97.139 = ~262 seconds (~4.4 minutes).

The upstream baseline (218.94 s) is a separate pre-investigation run.

---

## Evidence run 044f6b11 (second full workflow replay, 2026-09-26)

This is the checkout-demo R3 workflow, not the Petclinic investigation.
Recorded for completeness; not attributed to Petclinic timing.

| Stage | Duration (s) | Exit |
|---|---|---|
| 01-baseline | 51.937 | 0 |
| 02-original | 12.740 | 1 |
| 03-original-repeat | 12.358 | 1 |
| 04-candidate-reproducer | 12.993 | 0 |
| 05-candidate-regression | 16.297 | 0 |
| Total | 107.873 | — |

---

## What is not known

| Item | Reason |
|---|---|
| Total Sprint 1 investigation time | Only the single build attempt time (~141 s) is recorded |
| Time spent on Sprints 2 and 3 (scope definition, test authoring) | No timestamp records in available artifacts |
| Human active time | Not measured |
| Time between sprint sessions | Not recorded |
| Sprint 5 reporting time | This current task — started during this session |

The three-hour planning target in `docs/PETCLINIC-VALIDATION-SPRINTS.md` is a
planning target, not a measured result. Total elapsed calendar time across
Sprints 1–4 spans 2026-09-25T22:17 to 2026-09-26T04:26 UTC (~6 hours 9 minutes
calendar time including all sessions and gaps). Active execution time is
substantially less; the unrecorded portion cannot be reconstructed.

---

## Productivity claim status

No speedup, time-saved, or productivity improvement figure is claimed. No
comparable manual measurement has been taken. The methodology document
`docs/timing-study.md` describes the intended measurement approach; no
results from that study are available.
