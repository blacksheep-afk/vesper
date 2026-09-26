# Vesper timing study — manual vs Bob-assisted investigation

## Purpose

Measure the elapsed time a developer spends investigating, reproducing and fixing the R3 boundary defect under two conditions:

1. **Manual** — developer reads the source code and requirements unaided, writes a test by hand, runs Maven, writes and applies the fix manually.
2. **Bob-assisted (Vesper)** — developer opens the project in Bob IDE, issues the Vesper starting request, confirms the requirement interpretation, reviews the proposed patch and accepts.

The goal is a comparable, honest measurement. No speedup figure will be claimed before it is measured.

---

## Scope

- **Module under test:** `demo/src/main/java/dev/vesper/Checkout.java`
- **Requirements document:** `demo/requirements.md`
- **Defect:** R3 expiry-boundary (seeded, disclosed) — single-line change on line 14
- **Test suite:** `demo/src/test/java/dev/vesper/CheckoutTest.java` + `ReproducerR3Test.java`

---

## Manual task protocol

### Setup (not timed)

- Fresh terminal, project cloned, Java + Maven on PATH confirmed.
- Developer has **not** read the source in this session.

### Timed steps

| Step | Action | Ends when |
|------|--------|-----------|
| M1 | Read `demo/requirements.md` | Developer says "understood" |
| M2 | Read `demo/src/main/java/dev/vesper/Checkout.java` | Developer locates the discount logic |
| M3 | Identify a suspected requirement violation | Developer writes down the specific line and condition |
| M4 | Write a JUnit test that targets the suspected bug | File saved |
| M5 | Run `mvn -f demo/pom.xml clean test` and observe failure | Exit code recorded |
| M6 | Decide on the fix and edit `Checkout.java` | File saved |
| M7 | Run `mvn -f demo/pom.xml clean test` and confirm all pass | Exit code 0 confirmed |

**Total manual time** = clock time from start of M1 to end of M7.

### What to record

- Wall-clock timestamps at the start and end of each step (phone or `date` command).
- Any wrong turns, re-reads, or compile errors — record these honestly; they are part of the measurement.
- The final test output showing 12 pass.

---

## Bob-assisted (Vesper) protocol

### Setup (not timed)

- Bob IDE open with the Vesper project loaded.
- Developer signed into the hackathon-provisioned account.
- `scripts/use-local-tools.ps1` sourced if on the Windows dev machine.

### Timed steps

| Step | Action | Ends when |
|------|--------|-----------|
| V1 | Issue the Vesper starting request in Bob | Bob has read the files and presented expected behaviours |
| V2 | Confirm the R3 interpretation | Developer types approval |
| V3 | Bob writes the reproducer and runs it | Failure result visible in chat |
| V4 | Review the proposed patch diff | Developer reads the diff |
| V5 | Accept and integrate the fix | `Checkout.java` updated and all tests pass |

**Total Bob-assisted time** = clock time from start of V1 to end of V5.

### What to record

- Same wall-clock approach.
- Bob task-summary screenshot captured immediately after the relevant task completes — save to `bob_sessions/` per the naming convention.
- Bobcoin consumption from the task summary (do not estimate; read the actual screenshot).

---

## Comparable-task design notes

- Both trials use the **same module, same requirements document, and the same seeded defect**.
- The manual trial uses a developer who has **not** recently reviewed this specific code (use a fresh session or a second team member if available).
- Both trials start from a clean Maven build (no stale `target/`).
- The defect is the same in both trials; no additional bugs are introduced.
- **No productivity claim will be published before both measurements are recorded.** The README currently reads: "Our business value is less investigation and rework. We will measure this with a comparable manual task; no productivity improvement has been measured yet."

---

## Results table (to be filled in after measurement)

| Metric | Manual | Bob-assisted |
|--------|--------|--------------|
| Total elapsed time | _record actual_ | _record actual_ |
| Time to identify suspect | — | — |
| Time to write/run reproducer | — | — |
| Time to write/apply fix | — | — |
| Tests passing at end | 12/12 | 12/12 |
| Wrong turns / retries | _record actual_ | — |
| Bobcoins consumed | N/A | _read from screenshot_ |

> **Integrity note:** Fill this table only from actual timed sessions. Do not estimate, interpolate, or use the workflow runner's stage durations as a proxy for human time.

---

## After measurement

Update `README.md` "Our business value" paragraph with the actual numbers. If the manual trial was not completed before the submission deadline, state that explicitly in the submission rather than omitting it.
