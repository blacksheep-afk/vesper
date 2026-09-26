package dev.vesper;

import org.junit.jupiter.api.Test;
import java.time.LocalDate;
import static org.junit.jupiter.api.Assertions.assertEquals;

/**
 * Sprint 2 reproducer — R3 expiry-boundary defect.
 *
 * Requirement R3: "A discount is valid through its expiry date, inclusive.
 * A later checkout date receives no discount."
 *
 * Approved interpretation: checkout on the exact expiry date must receive the
 * discount.  today == expiry → discount applied.
 *
 * Seeded defect: Checkout.java line 14 uses !today.isBefore(expiry) instead of
 * today.isAfter(expiry), making the expiry day itself trigger the no-discount
 * branch.
 *
 * This test FAILS on the seeded (buggy) code and PASSES on the corrected code.
 * It is frozen for Sprint 2 reproduction and Sprint 3 candidate verification.
 *
 * SEEDED DEFECT — disclosed demo bug, not an organic finding.
 */
class ReproducerR3Test {

    private final LocalDate expiry = LocalDate.of(2026, 9, 25);

    /**
     * R3 reproducer: checkout on the expiry day must receive the discount.
     *
     * Input:  subtotal=1000 cents, percent=10, expiry=today=2026-09-25
     * Expected: 900 cents  (1000 - 10% = 900)
     * Buggy result: 1000 cents (no discount applied — off-by-one on boundary)
     */
    @Test
    void expiryDayMustReceiveDiscount_R3() {
        assertEquals(
            900L,
            Checkout.total(1000, 10, expiry, expiry),
            "R3: checkout on expiry day must receive the discount (expiry is inclusive)"
        );
    }
}
