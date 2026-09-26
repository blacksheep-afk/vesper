# Vesper evidence report

**Disclosed seeded demonstration — not an organic finding.**

Requirement R3: discounts remain valid on the expiry date.
Input: 1000 cents, 10% discount, checkout and expiry 2026-09-25. Expected: 900 cents.

Workflow: **verified_candidate**
Investigation: **reproduced**
Candidate: **regression_passed**
Human decision: **pending review**
Integration: **not performed by this workflow**
Elapsed: 81.489 seconds (this invocation only).

The expected result is specified by demo/requirements.md. This replay does not record a new human approval.

| Stage | Execution status | Tests / failures / errors / skipped | Seconds | Evidence |
| --- | --- | --- | --- | --- |
| 01-baseline | passed | 12 / 0 / 0 / 0 | 19.375 | [record](01-baseline/result.json), [log](01-baseline/execution.log) |
| 02-original | execution_failed | 1 / 1 / 0 / 0 | 12.185 | [record](02-original/result.json), [log](02-original/execution.log) |
| 03-original-repeat | execution_failed | 1 / 1 / 0 / 0 | 15.008 | [record](03-original-repeat/result.json), [log](03-original-repeat/execution.log) |
| 04-candidate-reproducer | passed | 1 / 0 / 0 / 0 | 13.869 | [record](04-candidate-reproducer/result.json), [log](04-candidate-reproducer/execution.log) |
| 05-candidate-regression | passed | 12 / 0 / 0 / 0 | 13.123 | [record](05-candidate-regression/result.json), [log](05-candidate-regression/execution.log) |

## Findings and unresolved work

One disclosed R3 defect reproduced twice: expected 900 cents, observed 1000. The unchanged reproducer and the full baseline test set passed on the candidate. Review the patch and evidence; no approval or integration is inferred.

A passing reproducer means not reproduced. Setup failures do not demonstrate an application bug.

## Candidate patch

```diff
--- original/src/main/java/dev/vesper/Checkout.java
+++ candidate/src/main/java/dev/vesper/Checkout.java
@@ -11,8 +11,8 @@
         if (percent < 0 || percent > 100) throw new IllegalArgumentException("Discount must be 0..100");
         Objects.requireNonNull(expiry, "expiry");
         Objects.requireNonNull(today, "today");
-        if (!today.isBefore(expiry)) return subtotalCents;  // SEEDED BUG (Sprint 2): expiry day incorrectly excluded — violates R3 "inclusive"
-        // Split before multiplying to avoid overflow for large subtotals.
+        if (today.isAfter(expiry)) return subtotalCents;  // R3: expiry is inclusive; discount expires only after the expiry date
+        // Split before multiplying to avoid overflow for large subtotals
         long discount = (subtotalCents / 100) * percent + ((subtotalCents % 100) * percent) / 100;
         return subtotalCents - discount;
     }
```

## Provenance and limits

[Run metadata, versions and input hashes](workflow.json).
[Original snapshot](original/) · [Candidate snapshot](candidate/) · [Baseline snapshot](baseline/)

The candidate is the existing corrected demo source; this command does not generate an AI repair.
This workflow supports the supplied Maven demo and its R3 test only. It does not prove general correctness.
No productivity improvement, Bob usage or Bobcoin consumption has been measured here.
Bob session screenshots must be captured from actual Bob sessions.
