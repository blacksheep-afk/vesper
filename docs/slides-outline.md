# Vesper — presentation slides outline

## Slide 1: Title

**Vesper**
*AI-assisted bug investigation with verifiable evidence*

IBM Bob 2.0 Hackathon · Black Sheep Team · September 2026

---

## Slide 2: The problem

**AI review creates investigation work**

- A developer receives a list of findings — but which ones are real?
- Every finding needs: read the code, understand the requirement, write a test, run it
- A proposed fix raises another question: does it pass existing tests?
- Result: AI assistance creates manual work *before* it saves work

> "Without evidence, every AI finding is a hypothesis, not a bug."

---

## Slide 3: The Vesper approach

**Make Bob back its claims with evidence**

Five sequential stages — one starting request:

| Stage | What Bob does |
|-------|---------------|
| Read | Understands requirements and selected source |
| Confirm | Presents expected behaviours for developer approval |
| Reproduce | Writes and runs a targeted test — must fail first |
| Fix | Prepares a candidate patch, shows the exact diff |
| Verify | Runs the unchanged test + full regression suite |

Developer reviews evidence → decides to accept or reject.

---

## Slide 4: The workflow in action

**Demo: R3 — discount expiry boundary**

```
Requirement R3: "A discount is valid through its expiry date,
                  inclusive. A later checkout date receives no discount."
```

Seeded defect (disclosed demo bug):
```java
// BUGGY:   if (!today.isBefore(expiry)) return subtotalCents;
// FIXED:   if (today.isAfter(expiry))   return subtotalCents;
```

Single-line change. Off-by-one on the inclusive boundary.
Bob identifies it, reproduces it, fixes it, verifies it.

---

## Slide 5: Evidence trail

**Every finding is backed by actual test output**

| Evidence | Record |
|----------|--------|
| Baseline (before) | 12 tests, 0 failures — clean start |
| Reproducer (seeded) | 1 test, 1 failure — `expected: 900 / was: 1000` |
| Full regression (seeded) | 12 tests, 5 failures — same root cause |
| Candidate diff | 1 line, requirement-linked |
| Reproducer (fixed) | 1 test, 0 failures — verified |
| Full regression (fixed) | 12 tests, 0 failures — no regressions |

All results saved in `.vesper/runs/` with Surefire XML, logs, and result JSON.

---

## Slide 6: Business value

**Less investigation. More decisions.**

- Reduces manual review of unsupported findings
- Connects review, debugging and testing in one workflow
- Keeps the developer in control — approval and integration are separate states
- Evidence trail is independently verifiable — no trust required

> "Vesper doesn't ask developers to trust AI. It makes AI back its claims with evidence."

---

## Slide 7: IBM Bob — central to every stage

**Bob is the core, not a peripheral**

- Reads requirements and source at task start
- Authors the reproducer test and candidate fix
- Invokes the local runner and interprets results
- Enforces the confirmation gate before investigation
- Governed by `AGENTS.md` — no fabricated results, no self-approval

Reusable Bob skill: `.bob/skills/vesper/SKILL.md`
Task evidence: `bob_sessions/` (real screenshots, actual Bobcoin consumption)

---

## Slide 8: Technical stack

| Component | Technology |
|-----------|------------|
| Workflow orchestration | IBM Bob IDE + Vesper Bob skill |
| Demo application | Java 17 + Maven · JUnit 5 |
| Runner + reporting | Python 3 (stdlib only) |
| Evidence storage | JSON + Surefire XML + Markdown |
| Source control | Git |

No hosted backend, database, or external model API required.

---

## Slide 9: Project status at submission

**Sprint 3 (Fix and verify) — COMPLETE**
- 12 tests pass on fixed code
- Fix integrated, evidence recorded
- Frozen reproducer unchanged throughout

**Sprint 5 (Demo and submission) — IN PROGRESS**
- Workflow runner operational (`python -m vesper workflow --timeout 300`)
- All submission documents prepared
- Bob session screenshots: tasks 01–03 captured; task 04 to be captured live

---

## Slide 10: Team and repository

**Black Sheep team — IBM Bob 2.0 Hackathon**

Repository: https://github.com/blacksheep-afk/vesper

Key files:
- `AGENTS.md` — agent operating rules
- `docs/requirements.md` — MVP acceptance criteria
- `.bob/skills/vesper/SKILL.md` — Bob workflow skill
- `demo/` — Java checkout service + test suite
- `vesper/` — Python runner
- `bob_sessions/` — real task-summary screenshots
- `docs/SPRINT-1.md` through `docs/SPRINT-5.md` — sprint evidence

*Thank you.*
