# Checkout requirements

Synthetic demo. Sprint 1: no intentionally seeded bugs. Sprint 2: one disclosed defect seeded for demonstration — see SEEDED DEFECT below.

- R1: Subtotal is a nonnegative integer number of cents; negative values are rejected.
- R2: Discount percentage is an integer from 0 through 100 inclusive; other values are rejected.
- R3: A discount is valid through its expiry date, inclusive. A later checkout date receives no discount.
- R4: Discount cents are rounded down; payable cents equal subtotal minus discount cents.
- R5: Expiry and checkout dates are required. Null dates are rejected.

---

## SEEDED DEFECT (Sprint 2 — disclosed demo bug)

**Finding:** R3 expiry boundary treated as exclusive instead of inclusive.

**Location:** `Checkout.java` line 14 — the guard `if (today.isAfter(expiry))` was changed to
`if (!today.isBefore(expiry))`, making the expiry day itself cause the discount to be skipped.

**Requirement violated:** R3 — "A discount is valid through its expiry date, inclusive."

**Expected (correct):** `Checkout.total(1000, 10, expiry, expiry)` → 900 (discount applied on expiry day).

**Observed (buggy):** `Checkout.total(1000, 10, expiry, expiry)` → 1000 (no discount on expiry day).

This defect was intentionally introduced for the Sprint 2 reproduction exercise. It is not an organic finding.
