# Sprint 5 — Demo and submission

Date: 2026-09-25 / 2026-09-27 (deadline 17:00 SAST)
Status: **IN PROGRESS**
Toolchain (macOS rehearsal machine): Python 3.9.6 · Java 21.0.9 (Oracle) · Maven 3.9.15

---

## Sprint 5 tasks

| Task | Status |
|------|--------|
| 5.1 Rehearse the complete workflow | ✅ DONE |
| 5.2 Add `workflow` subcommand to runner | ✅ DONE |
| 5.3 Manual vs Bob-assisted timing study — design | ✅ DONE |
| 5.4 Bob walkthrough and screenshot capture guide | ✅ DONE |
| 5.5 Demo video script | ✅ DONE |
| 5.6 Submission assets (slides, statements) | ✅ DONE |
| 5.7 Final verification | ⬜ Pending |
| 5.8 Timing study — actual measurements | ⬜ Pending (requires live session) |
| 5.9 bob_sessions task 04+ screenshots | ⬜ Pending (requires live Bob session) |
| 5.10 Demo video recording | ⬜ Pending |
| 5.11 Hackathon form submission | ⬜ Pending — do not submit without user instruction |

---

## 5.1 — Workflow rehearsal result

Run ID: `workflow-20260925-233816`
Date: 2026-09-25 23:38 SAST (macOS rehearsal machine)
Command: `python3 -m vesper workflow --timeout 300`

| Stage | Status | Tests | Failures | Duration |
|-------|--------|-------|----------|----------|
| 1. baseline | passed | 12 | 0 | 1.526s |
| 2. seed | ok | — | — | — |
| 3. reproduce | **reproduced** | 1 | 1 | 1.248s |
| 4. regress_bug | exit 1 (expected) | 12 | 5 | 1.261s |
| 5. restore | ok | — | — | — |
| 6. verify | **verified** | 1 | 0 | 1.246s |
| 7. regress_fix | **all_passed** | 12 | 0 | 1.227s |
| 8. report | written | — | — | — |

**Overall: ✓ WORKFLOW PASSED  (6.5s total)**

Evidence: `.vesper/runs/workflow-20260925-233816/result.json` and `workflow_report.md`

### Key observations

- Stage 3 (reproduce): `expected: <900> but was: <1000>` — seeded R3 boundary bug confirmed on this machine.
- Stage 4 (regress_bug): exactly the same 5 failures as Sprint 2/3 (Windows machine). Consistent across platforms.
- Stage 6 (verify): reproducer passes on fixed code. Frozen test unchanged.
- Stage 7 (regress_fix): 12/12 pass, 0 skipped, clean build.

### Note on toolchain difference

Sprint 3 ran on OpenJDK 17.0.20.1 (Microsoft) + Maven 3.9.9 on Windows.
This rehearsal ran on Oracle Java 21.0.9 + Maven 3.9.15 on macOS (arm64).
Results are identical. The demo POM uses `<release>17</release>` for Java compatibility.

---

## 5.2 — `workflow` subcommand

New file: [`vesper/workflow.py`](vesper/workflow.py)
Updated: [`vesper/__main__.py`](vesper/__main__.py) — routes `baseline` and `workflow` subcommands.

The workflow runner:
- Runs `clean` before every Maven stage to avoid stale `.class` files masking the seeded defect.
- Saves a backup of the fixed source before seeding, and restores it in a `finally` block even on error.
- Writes a `result.json` and a `workflow_report.md` in a timestamped run directory.
- Exits 0 only if both stage 6 (verify) and stage 7 (regress_fix) passed.

---

## 5.3 — Manual vs Bob-assisted timing study

Methodology document: [`docs/timing-study.md`](docs/timing-study.md)

Actual measurements have not yet been taken. The methodology is designed for a timed session on the same module (R3 defect, `Checkout.java`). Results must be recorded from an actual session — not estimated. The README "business value" paragraph will be updated once both measurements exist.

---

## 5.4 — Bob walkthrough guide

Guide: [`docs/bob-walkthrough.md`](docs/bob-walkthrough.md)

Covers:
- Prerequisite setup
- Screenshot naming convention
- Step-by-step Bob prompts for tasks 01–04
- Checklist before recording the demo video

**bob_sessions status:**
- Tasks 01–03: PNG files present (filenames contain a doubled `.png.png` extension — must be corrected before submission).
- Task 04 (workflow rehearsal): not yet captured — requires a live Bob session.

Action required: rename existing files and capture task 04 screenshot in Bob.

---

## 5.5 — Demo video script

Script: [`docs/demo-video-script.md`](docs/demo-video-script.md)

| Segment | Content | Duration |
|---------|---------|----------|
| A | Hook + problem | 0:00–0:25 |
| B | Approach | 0:25–0:45 |
| C | **Live workflow** (working solution) | 0:45–2:20 |
| D | Results + value | 2:20–2:45 |
| E | Wrap-up | 2:45–3:00 |

Segment C = 1:35 of working-solution footage (≥ 90s required). Total = 3:00 (≤ 3:00 required).

Video not yet recorded.

---

## 5.6 — Submission assets

| Asset | Location | Status |
|-------|----------|--------|
| Problem & Solution Statement | `docs/submission-statements.md` §Statement 1 | ✅ Written (437 words, 2803 chars) |
| IBM Bob Usage Statement | `docs/submission-statements.md` §Statement 2 | ✅ Written (415 words, 2910 chars) |
| Slides outline | `docs/slides-outline.md` | ✅ Written (10 slides) |
| Cover image | Not yet created | ⬜ Pending |
| Demo video | Not yet recorded | ⬜ Pending |

Both statements satisfy: ≤500 words AND 500–4000 characters.

### Submission form metadata

| Field | Value |
|-------|-------|
| Title | `Vesper` (6 chars — satisfies 5–50) |
| Short description | `AI bug investigation with verifiable evidence — IBM Bob connects requirements to reproducer tests and tested fixes.` (113 chars — satisfies 50–255) |
| Category | Developer Tools |
| Technologies | IBM Bob IDE, Java, Maven, JUnit, Python |
| Repository | https://github.com/blacksheep-afk/vesper |
| Application URL | TBC — local demo, no hosted service yet |

---

## 5.7 — Final verification checklist (pending)

- [ ] `Checkout.java` line 14: `today.isAfter(expiry)` (fixed state)
- [ ] `python3 -m vesper workflow --timeout 300` exits 0
- [ ] `python3 -m unittest discover -s tests -v` — all 10 runner checks pass
- [ ] All `bob_sessions/` files renamed to single `.png` extension
- [ ] `bob_sessions/README.md` updated with actual Bobcoin figures from screenshots
- [ ] `bob_sessions/` contains at minimum tasks 01–04
- [ ] `docs/submission-statements.md` reviewed for accuracy
- [ ] Demo video recorded, ≤3:00, ≥1:30 working solution
- [ ] Cover image created and ready for upload
- [ ] Repository is public
- [ ] MIT license file added (see below)
- [ ] No client data, personal information, or unauthorized assets in repo
- [ ] Submission form NOT filled in until user instruction

---

## 5.8 — License (action required)

The README states: "A project license has not yet been added. The event requires an original, MIT-compliant submission."

A `LICENSE` file with MIT license text must be added before submission. This requires the user's confirmation of the copyright holder name.

---

## What remains unverified

- Actual manual vs Bob-assisted timing measurements (requires timed live session).
- Task 04 Bob session screenshot (requires live Bob task).
- Demo video recording.
- Cover image.
- License file.
- Application URL (local demo — lablab form field may be optional or a placeholder URL is acceptable; later form steps not yet inspected).

---

## Artefacts created in Sprint 5

| Artefact | Path |
|----------|------|
| Workflow runner | `vesper/workflow.py` |
| Updated entry point | `vesper/__main__.py` |
| Timing study methodology | `docs/timing-study.md` |
| Bob walkthrough guide | `docs/bob-walkthrough.md` |
| Demo video script | `docs/demo-video-script.md` |
| Submission statements | `docs/submission-statements.md` |
| Slides outline | `docs/slides-outline.md` |
| Workflow run evidence | `.vesper/runs/workflow-20260925-233816/` |
| Sprint 5 evidence | `docs/SPRINT-5.md` (this file) |
