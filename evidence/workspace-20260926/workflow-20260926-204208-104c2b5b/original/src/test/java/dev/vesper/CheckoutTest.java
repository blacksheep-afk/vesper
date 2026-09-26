package dev.vesper;

import org.junit.jupiter.api.Test;
import java.time.LocalDate;
import static org.junit.jupiter.api.Assertions.*;

class CheckoutTest {
    private final LocalDate expiry = LocalDate.of(2026, 9, 25);
    @Test void validDiscount() { assertEquals(900, Checkout.total(1000, 10, expiry, expiry.minusDays(1))); }
    @Test void expiryDayIsInclusive() { assertEquals(900, Checkout.total(1000, 10, expiry, expiry)); }
    @Test void expiredDiscountIsRejected() { assertEquals(1000, Checkout.total(1000, 10, expiry, expiry.plusDays(1))); }
    @Test void fractionalDiscountRoundsDown() { assertEquals(91, Checkout.total(101, 10, expiry, expiry)); }
    @Test void zeroSubtotal() { assertEquals(0, Checkout.total(0, 50, expiry, expiry)); }
    @Test void zeroPercent() { assertEquals(123, Checkout.total(123, 0, expiry, expiry)); }
    @Test void fullDiscount() { assertEquals(0, Checkout.total(Long.MAX_VALUE, 100, expiry, expiry)); }
    @Test void largeSubtotalDoesNotOverflow() { assertEquals(8301034833169298227L, Checkout.total(Long.MAX_VALUE, 10, expiry, expiry)); }
    @Test void negativeSubtotalRejected() { assertThrows(IllegalArgumentException.class, () -> Checkout.total(-1, 10, expiry, expiry)); }
    @Test void invalidPercentRejected() {
        assertThrows(IllegalArgumentException.class, () -> Checkout.total(100, -1, expiry, expiry));
        assertThrows(IllegalArgumentException.class, () -> Checkout.total(100, 101, expiry, expiry));
    }
    @Test void missingDatesRejected() {
        assertThrows(NullPointerException.class, () -> Checkout.total(100, 10, null, expiry));
        assertThrows(NullPointerException.class, () -> Checkout.total(100, 10, expiry, null));
    }
}
