"""Tests for masking strategy."""

from pii_shield.core import PIIMatch, PIIType
from pii_shield.strategies.masking import MaskingStrategy


class TestMaskingStrategy:
    """Tests for MaskingStrategy."""

    def test_masks_email(self):
        strategy = MaskingStrategy()
        matches = [PIIMatch(PIIType.EMAIL, "hans@example.com", 0, 16, 1.0, "email")]
        result = strategy.apply("hans@example.com", matches)
        assert result == "han***com"

    def test_masks_phone(self):
        strategy = MaskingStrategy()
        matches = [PIIMatch(PIIType.PHONE, "+49 171 1234567", 0, 15, 1.0, "phone")]
        result = strategy.apply("+49 171 1234567", matches)
        assert result == "+49***567"

    def test_masks_iban(self):
        strategy = MaskingStrategy()
        iban = "DE89370400440532013000"
        matches = [PIIMatch(PIIType.IBAN, iban, 0, len(iban), 1.0, "iban")]
        result = strategy.apply(iban, matches)
        assert result == "DE8***000"

    def test_short_value_fully_masked(self):
        strategy = MaskingStrategy(visible_chars=3)
        # Value of 6 chars or less should be fully masked
        matches = [PIIMatch(PIIType.NAME, "Hans", 0, 4, 1.0, "presidio")]
        result = strategy.apply("Hans", matches)
        assert result == "****"

    def test_custom_mask_char(self):
        strategy = MaskingStrategy(mask_char="#")
        matches = [PIIMatch(PIIType.EMAIL, "hans@example.com", 0, 16, 1.0, "email")]
        result = strategy.apply("hans@example.com", matches)
        assert result == "han###com"

    def test_custom_visible_chars(self):
        strategy = MaskingStrategy(visible_chars=4)
        matches = [PIIMatch(PIIType.EMAIL, "hans@example.com", 0, 16, 1.0, "email")]
        result = strategy.apply("hans@example.com", matches)
        assert result == "hans***.com"

    def test_masks_multiple_matches(self):
        strategy = MaskingStrategy()
        text = "Email: hans@sap.com Phone: +49 171 123"
        matches = [
            PIIMatch(PIIType.EMAIL, "hans@sap.com", 7, 19, 1.0, "email"),
            PIIMatch(PIIType.PHONE, "+49 171 123", 27, 38, 1.0, "phone"),
        ]
        result = strategy.apply(text, matches)
        assert "han***com" in result
        assert "+49***123" in result

    def test_preserves_surrounding_text(self):
        strategy = MaskingStrategy()
        text = "Contact hans@example.com today"
        matches = [PIIMatch(PIIType.EMAIL, "hans@example.com", 8, 24, 1.0, "email")]
        result = strategy.apply(text, matches)
        assert result.startswith("Contact ")
        assert result.endswith(" today")

    def test_empty_matches(self):
        strategy = MaskingStrategy()
        result = strategy.apply("no pii here", [])
        assert result == "no pii here"
