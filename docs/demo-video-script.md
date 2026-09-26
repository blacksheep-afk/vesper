# Vesper demo video — script and timing plan

**Format:** MP4, narrated screen recording, at most 3:00, at least 1:30 showing the working solution.

---

## Segment overview

| Segment | Content | Target time | Cumulative |
|---------|---------|-------------|------------|
| A | Hook + problem statement | 0:00 – 0:25 | 0:25 |
| B | Vesper approach (concept, not running) | 0:25 – 0:45 | 0:45 |
| C | **Live workflow — Bob in action** (working solution) | 0:45 – 2:20 | 2:20 |
| D | Results and business value | 2:20 – 2:45 | 2:45 |
| E | Wrap-up and team credit | 2:45 – 3:00 | 3:00 |

Segment C is 1:35 of working-solution footage — above the 90-second minimum.

---

## Segment A — Hook (0:00–0:25)

**Screen:** Title card with project name and tagline, or slide 1.

**Narration:**
> "AI code review tools suggest bugs. But how do you know which ones are real?
> A developer can spend hours reading source code, writing tests, and second-guessing
> findings before they even know if a problem exists.
> Vesper changes that. It makes Bob back every finding with evidence."

---

## Segment B — Approach (0:25–0:45)

**Screen:** Slide showing the 5-stage workflow diagram (Read → Review → Reproduce → Fix → Verify).

**Narration:**
> "Vesper connects Bob IDE to a local test runner across five stages:
> read the requirements, identify a suspect, reproduce the failure with a real test,
> prepare a fix, and verify it — all from one request.
> The developer confirms the requirement and reviews the patch. Bob handles the rest."

---

## Segment C — Live workflow — Bob in action (0:45–2:20)

> This is the working-solution segment. Record this in Bob IDE with the Vesper project open.

### C1 — Starting the workflow (0:45–1:00)

**Screen:** Bob IDE, chat panel visible, project loaded.

**Action:** Type the Vesper starting request and press Enter:
```
Run the Vesper workflow on the checkout module using demo/requirements.md.
Show me the expected behaviours, reproduce any supported findings, and
prepare a tested fix for my review.
```

**Narration:**
> "From one request, Bob reads the requirements and the source code,
> then presents the expected behaviours for me to confirm."

---

### C2 — Confirming R3 (1:00–1:15)

**Screen:** Bob has presented the expected behaviours. Scroll to R3.

**Action:** Type your confirmation:
```
R3 confirmed: a checkout on the exact expiry day must receive the discount.
today == expiry means the discount is applied.
```

**Narration:**
> "I confirm requirement R3: the expiry date is inclusive.
> A checkout made on the expiry day must still receive the discount."

---

### C3 — Reproducer failure (1:15–1:35)

**Screen:** Bob has run the frozen reproducer. Scroll to the failure output.

**Narration:**
> "Bob writes a test for that exact boundary case and runs it.
> The test fails: expected 900 cents, got 1000.
> The discount was skipped on the expiry day — that is the R3 violation."

Point at: `expected: <900> but was: <1000>`

---

### C4 — Candidate diff (1:35–1:50)

**Screen:** Bob shows the single-line diff.

**Narration:**
> "Bob prepares a one-line fix: change the boundary condition from
> 'not before' to 'is after'. The diff is shown before anything is applied.
> I review it — this restores the inclusive semantics."

Point at the diff:
```
- if (!today.isBefore(expiry)) return subtotalCents;
+ if (today.isAfter(expiry))   return subtotalCents;
```

---

### C5 — Verification: reproducer passes, all 12 pass (1:50–2:20)

**Screen:** Bob runs the workflow runner, or runs the reproducer and then the full suite.
Show the terminal/output panel with the passing results.

**Action (optional alternative):** Switch to a terminal and run:
```
python -m vesper workflow --timeout 300
```

**Narration:**
> "With the fix applied, the frozen reproducer passes —
> the same unchanged test now gets 900 as expected.
> The full regression suite: 12 tests, 0 failures.
> The fix is verified."

Point at: `Tests run: 12, Failures: 0, Errors: 0, Skipped: 0` and `✓ WORKFLOW PASSED`

---

## Segment D — Results and business value (2:20–2:45)

**Screen:** Slide or Bob task summary / workflow report.

**Narration:**
> "What used to require manually reading source code, writing a test from scratch,
> and applying an untested fix — Vesper completes with one starting request.
> The result is an evidence trail: requirement, failing test, diff, passing test,
> full regression — all recorded, none fabricated.
> The developer stays in control. The evidence is real."

> _(If timing study is complete, add: "In our timed comparison, manual investigation
> took X minutes. The Bob-assisted workflow completed in Y minutes.")_

---

## Segment E — Wrap-up (2:45–3:00)

**Screen:** Slide with team name, repo URL, and "IBM Bob 2.0 Hackathon".

**Narration:**
> "Vesper — built by the Black Sheep team for the IBM Bob 2.0 Hackathon.
> Source at github.com/blacksheep-afk/vesper.
> Thank you."

---

## Recording checklist

Before hitting record:

- [ ] `Checkout.java` is in **fixed** state (line 14: `today.isAfter`)
- [ ] `python -m vesper workflow --timeout 300` exits 0 in a clean run
- [ ] Bob IDE is logged into the hackathon account
- [ ] Font size in IDE is readable at 1080p (≥ 14pt)
- [ ] No personal or confidential information visible on screen
- [ ] Terminal working directory is the project root
- [ ] On Windows dev machine: `use-local-tools.ps1` already sourced

## Post-recording checklist

- [ ] Video is MP4
- [ ] Total length ≤ 3:00
- [ ] Working-solution footage (Segment C) ≥ 1:30
- [ ] Narration is audible throughout
- [ ] Bob IDE and Vesper are clearly identified in the video
- [ ] Uploaded and URL ready for the submission form

## Notes

- If you cannot show the live Bob workflow (e.g. Bobcoins exhausted), show the recorded Sprint 3/4 evidence (the test outputs in `docs/SPRINT-3.md`) side-by-side with the source diff. Segment C still meets the "working solution" bar if it shows actual passing test output.
- Do not re-seed the bug just for the video using the workflow runner — the runner's automated seed/restore is not suitable for a live demo. Instead, for the demo either: (a) show Bob walking through the workflow live from scratch, or (b) narrate over the recorded workflow runner output with the terminal visible.
