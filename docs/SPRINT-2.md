# Sprint 2 — Reproduce a requirement-linked bug

Date: 2026-09-25  
Status: **COMPLETE — defect reproduced (repeatable)**  
Toolchain: OpenJDK 17.0.20.1 (Microsoft) · Maven 3.9.9 · Python 3.12.14  
Local tools path: `.tools/jdk-17.0.20.1+1` · `.tools/apache-maven-3.9.9`

---

## Baseline confirmation

Sprint 1 baseline run `20260925-204635-57bee762`:

| Field | Value |
|---|---|
| Status | passed |
| Tests | 11 |
| Failures | 0 |
| Errors | 0 |
| Skipped | 0 |
| Duration | 9.233 s |

All 11 `dev.vesper.CheckoutTest#*` identities confirmed present. Baseline is clean before the seeded defect is introduced.

---

## Requirement interpretation — R3 (approved by developer)

**R3 text:** "A discount is valid through its expiry date, inclusive. A later checkout date receives no discount."

**Approved interpretation:** A checkout made on the exact expiry date **must** receive the discount. `today == expiry` → discount is applied.  
**Boundary:** `today.isAfter(expiry)` → no discount. `today == expiry` or earlier → discount applies.

Developer approval received: 2026-09-25 (this session).

---

## Seeded defect (disclosed demo bug)

**SEEDED DEFECT — not an organic finding. Introduced deliberately for the Sprint 2 reproduction exercise.**

| Field | Value |
|---|---|
| Requirement | R3 |
| Location | `demo/src/main/java/dev/vesper/Checkout.java` line 14 |
| Original (correct) | `if (today.isAfter(expiry)) return subtotalCents;` |
| Seeded (buggy) | `if (!today.isBefore(expiry)) return subtotalCents;` |
| Effect | Expiry day itself triggers the no-discount branch — boundary is off by one |

The change makes `!today.isBefore(expiry)` true when `today == expiry`, so the discount is skipped on the expiry day, violating R3's "inclusive" requirement.

---

## Reproducer

**File:** `demo/src/test/java/dev/vesper/ReproducerR3Test.java`  
**Test:** `dev.vesper.ReproducerR3Test#expiryDayMustReceiveDiscount_R3`

```
Input:  subtotal = 1000 cents, percent = 10, expiry = 2026-09-25, today = 2026-09-25
Expected (R3, correct): 900  (10% discount applied on expiry day)
Observed (seeded bug):  1000 (no discount — expiry day incorrectly excluded)
```

The assertion uses `assertEquals(900L, Checkout.total(1000, 10, expiry, expiry), "R3: ...")`.  
The test is frozen at this state for Sprint 3 candidate verification.

---

## Reproduction results

### Attempt 1 — 2026-09-25 ~20:59 SAST

```
Tests run: 1, Failures: 1, Errors: 0, Skipped: 0
FAILURE: expiryDayMustReceiveDiscount_R3
  expected: <900> but was: <1000>
Exit code: 1
```

### Attempt 2 — 2026-09-25 ~21:00 SAST (consistency check)

```
Tests run: 1, Failures: 1, Errors: 0, Skipped: 0
FAILURE: expiryDayMustReceiveDiscount_R3
  expected: <900> but was: <1000>
Exit code: 1
```

**Outcome: reproduced — repeatable, non-flaky.**  
Both attempts produce the identical assertion failure on the same input with the same observed vs expected values.

---

## Full regression suite on seeded code — 2026-09-25 ~21:01 SAST

12 tests total (11 original + 1 new reproducer).

| Test | Result | Note |
|---|---|---|
| `CheckoutTest#validDiscount` | PASS | today < expiry, unaffected |
| `CheckoutTest#expiryDayIsInclusive` | **FAIL** | today == expiry — same root cause as reproducer |
| `CheckoutTest#expiredDiscountIsRejected` | PASS | today > expiry, unaffected |
| `CheckoutTest#fractionalDiscountRoundsDown` | **FAIL** | today == expiry in fixture — same root cause |
| `CheckoutTest#zeroSubtotal` | PASS | result is 0 regardless |
| `CheckoutTest#zeroPercent` | PASS | result equals subtotal regardless |
| `CheckoutTest#fullDiscount` | **FAIL** | today == expiry, 100% discount skipped |
| `CheckoutTest#largeSubtotalDoesNotOverflow` | **FAIL** | today == expiry, discount skipped |
| `CheckoutTest#negativeSubtotalRejected` | PASS | throws before date check |
| `CheckoutTest#invalidPercentRejected` | PASS | throws before date check |
| `CheckoutTest#missingDatesRejected` | PASS | throws on null check |
| `ReproducerR3Test#expiryDayMustReceiveDiscount_R3` | **FAIL** | the targeted reproducer |

**Summary: 12 run · 5 failures · 0 errors · 0 skipped**

All 5 failures share a single root cause: the seeded `!today.isBefore(expiry)` bug on line 14.  
Four of the original CheckoutTest cases use `today == expiry` inputs and are therefore also affected.  
This is expected and confirms the scope of the seeded defect. It is not evidence of additional bugs.

---

## Classification

| Dimension | Value |
|---|---|
| Investigation | **reproduced** |
| Evidence | valid, repeatable assertion failure; application logic is the cause |
| Flakiness | none — both attempts produced identical failure |
| Repair | not_attempted (Sprint 3) |
| Approval | pending Sprint 3 |
| Integration | not_integrated |

---

## What remains unverified

- The candidate fix and its verification are Sprint 3 work.
- The runner does not yet record Sprint 2 results automatically; that integration is Sprint 4.
- No claims about other requirements or other potential defects.

---

## Artefacts

| Artefact | Path |
|---|---|
| Seeded application source | `demo/src/main/java/dev/vesper/Checkout.java` (line 14, tagged comment) |
| Reproducer test | `demo/src/test/java/dev/vesper/ReproducerR3Test.java` |
| Disclosed defect record | `demo/requirements.md` §SEEDED DEFECT |
| Sprint 1 baseline JSON | `.vesper/runs/20260925-204635-57bee762/result.json` |
