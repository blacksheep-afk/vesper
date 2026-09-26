package dev.vesper;

import java.time.LocalDate;
import java.util.Objects;

public final class Checkout {
    private Checkout() {}

    public static long total(long subtotalCents, int percent, LocalDate expiry, LocalDate today) {
        if (subtotalCents < 0) throw new IllegalArgumentException("Subtotal must be nonnegative");
        if (percent < 0 || percent > 100) throw new IllegalArgumentException("Discount must be 0..100");
        Objects.requireNonNull(expiry, "expiry");
        Objects.requireNonNull(today, "today");
        if (!today.isBefore(expiry)) return subtotalCents;  // SEEDED BUG (Sprint 2): expiry day incorrectly excluded — violates R3 "inclusive"
        // Split before multiplying to avoid overflow for large subtotals.
        long discount = (subtotalCents / 100) * percent + ((subtotalCents % 100) * percent) / 100;
        return subtotalCents - discount;
    }
}
