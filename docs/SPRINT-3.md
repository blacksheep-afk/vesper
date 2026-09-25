# Sprint 3 — Fix and verify the R3 defect

Date: 2026-09-25
Status: **COMPLETE — fix integrated, all 12 tests passing**
Toolchain: OpenJDK 17.0.20.1 (Microsoft) · Maven 3.9.9
Candidate run ID: `sprint3-candidate-20260925-212132`
Integration run ID: `sprint3-integrated-20260925-213158`

---

## Baseline / seeded-state confirmation

| Artefact | State |
|---|---|
| Sprint 1 baseline (11 tests, 0 failures) | intact at `.vesper/runs/20260925-204635-57bee762/result.json` |
| Seeded `Checkout.java` (line 14, `!today.isBefore`) | unchanged — confirmed line 14 before and after this sprint |
| Seeded backup | `demo/src/main/java/dev/vesper/Checkout.java.seeded-bak` |
| `ReproducerR3Test.java` | frozen, unchanged |
| `CheckoutTest.java` | unchanged |

The seeded source was temporarily swapped for test execution, then restored. No Sprint 2 evidence was overwritten.

---

## Requirement and disclosed seeded defect

**R3:** "A discount is valid through its expiry date, inclusive. A later checkout date receives no discount."

**Approved interpretation (Sprint 2):** `today == expiry` → discount is applied. Only `today.isAfter(expiry)` triggers no-discount.

**Seeded defect** (disclosed demo bug, not an organic finding):

| Field | Value |
|---|---|
| Location | `demo/src/main/java/dev/vesper/Checkout.java` line 14 |
| Seeded (buggy) | `if (!today.isBefore(expiry)) return subtotalCents;` |
| Correct original | `if (today.isAfter(expiry)) return subtotalCents;` |
| Effect | `!today.isBefore(expiry)` is true when `today == expiry`, so the discount is skipped on the expiry day |

---

## Original failure (reproduced Sprint 2, confirmed here)

Running the frozen reproducer against the **seeded** code (Sprint 2 evidence):

```
Tests run: 1, Failures: 1, Errors: 0, Skipped: 0
FAILURE: expiryDayMustReceiveDiscount_R3
  expected: <900> but was: <1000>
Exit code: 1
```

Full regression on seeded code (Sprint 2): **12 run · 5 failures** — all sharing the same root cause.

---

## Candidate diff

**Candidate file:** `demo/src/main/java/dev/vesper/CheckoutCandidate.java`  
**Candidate content applied to Checkout.java for test runs (seeded source restored after).**

Exact single-line change (line 14 of `Checkout.java`):

```diff
-        if (!today.isBefore(expiry)) return subtotalCents;  // SEEDED BUG (Sprint 2): expiry day incorrectly excluded — violates R3 "inclusive"
+        if (today.isAfter(expiry)) return subtotalCents;   // CANDIDATE FIX (Sprint 3): restored original correct boundary
```

No other lines changed. The fix restores the original semantics: `today.isAfter(expiry)` is `false` when `today == expiry`, so the discount branch executes on the expiry day.

**Full candidate source:** [`CheckoutCandidate.java`](demo/src/main/java/dev/vesper/CheckoutCandidate.java)

---

## Frozen reproducer result — candidate

Run: 2026-09-25 21:21:05 SAST

```
[INFO] Running dev.vesper.ReproducerR3Test
Tests run: 1, Failures: 0, Errors: 0, Skipped: 0, Time elapsed: 0.122 s
[INFO] BUILD SUCCESS
Exit code: 0
```

**Reproducer is UNCHANGED and now PASSES.** The test is frozen — no modifications were made.

---

## Full regression result — candidate

Run ID: `sprint3-candidate-20260925-212132`  
Time: 2026-09-25 21:21:32–21:21:40 SAST  
Reports: `.vesper/runs/sprint3-candidate-20260925-212132/reports/`

```
[INFO] Running dev.vesper.CheckoutTest
Tests run: 11, Failures: 0, Errors: 0, Skipped: 0, Time elapsed: 0.172 s
[INFO] Running dev.vesper.ReproducerR3Test
Tests run:  1, Failures: 0, Errors: 0, Skipped: 0, Time elapsed: 0.000 s

Results:
Tests run: 12, Failures: 0, Errors: 0, Skipped: 0
[INFO] BUILD SUCCESS
Exit code: 0
```

### Per-test breakdown

| Test | Result | Note |
|---|---|---|
| `CheckoutTest#validDiscount` | PASS | today < expiry |
| `CheckoutTest#expiryDayIsInclusive` | **PASS** | today == expiry — was FAIL on seeded code |
| `CheckoutTest#expiredDiscountIsRejected` | PASS | today > expiry |
| `CheckoutTest#fractionalDiscountRoundsDown` | **PASS** | today == expiry — was FAIL on seeded code |
| `CheckoutTest#zeroSubtotal` | PASS | |
| `CheckoutTest#zeroPercent` | PASS | |
| `CheckoutTest#fullDiscount` | **PASS** | today == expiry — was FAIL on seeded code |
| `CheckoutTest#largeSubtotalDoesNotOverflow` | **PASS** | today == expiry — was FAIL on seeded code |
| `CheckoutTest#negativeSubtotalRejected` | PASS | |
| `CheckoutTest#invalidPercentRejected` | PASS | |
| `CheckoutTest#missingDatesRejected` | PASS | |
| `ReproducerR3Test#expiryDayMustReceiveDiscount_R3` | **PASS** | frozen reproducer — was FAIL on seeded code |

**Summary: 12 run · 0 failures · 0 errors · 0 skipped**

---

## Overlapping test note

`CheckoutTest#expiryDayIsInclusive` and `ReproducerR3Test#expiryDayMustReceiveDiscount_R3` both exercise `today == expiry`. Per the instruction, these are counted as **one bug** — a single root cause with two test expressions.

---

## Classification

| Dimension | Value |
|---|---|
| Investigation | **reproduced (Sprint 2)** |
| Candidate fix | **prepared and verified** — single line, requirement-linked |
| Reproducer result | **PASS** (unchanged test, candidate code) |
| Candidate full regression | **12/12 pass** |
| Developer approval | **granted 2026-09-25** |
| Integration status | **INTEGRATED** — fix applied to `Checkout.java` |
| Integration full regression | **12/12 pass** (clean build, exit 0) |

---

## What remains unverified

- No other requirements were checked in this sprint.
- The runner does not yet record integration runs automatically; that is Sprint 4 work.

---

## Artefacts

| Artefact | Path |
|---|---|
| Fixed application source | `demo/src/main/java/dev/vesper/Checkout.java` (line 14, `today.isAfter`) |
| Seeded source (demonstration evidence) | `demo/evidence/seeded/Checkout.java.seeded` |
| Frozen reproducer test (unchanged) | `demo/src/test/java/dev/vesper/ReproducerR3Test.java` |
| Candidate run result JSON | `.vesper/runs/sprint3-candidate-20260925-212132/result.json` |
| Candidate Surefire XML reports | `.vesper/runs/sprint3-candidate-20260925-212132/reports/` |
| Integration run result JSON | `.vesper/runs/sprint3-integrated-20260925-213158/result.json` |
| Integration Surefire XML reports | `.vesper/runs/sprint3-integrated-20260925-213158/reports/` |
| Sprint 1 baseline JSON | `.vesper/runs/20260925-204635-57bee762/result.json` |
