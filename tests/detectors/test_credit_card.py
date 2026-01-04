"""Tests for credit card detector."""

from pii_shield.core import PIIType
from pii_shield.detectors.credit_card import CreditCardDetector


class TestCreditCardDetector:
    """Tests for CreditCardDetector."""

    # === Valid Card Tests ===

    def test_detects_visa(self):
        detector = CreditCardDetector()
        # Valid Visa test number
        matches = detector.detect("Card: 4111111111111111")
        assert len(matches) == 1
        assert matches[0].type == PIIType.CREDIT_CARD
        assert matches[0].text == "4111111111111111"
        assert matches[0].confidence == 1.0

    def test_detects_mastercard(self):
        detector = CreditCardDetector()
        # Valid Mastercard test number
        matches = detector.detect("Card: 5555555555554444")
        assert len(matches) == 1
        assert matches[0].confidence == 1.0

    def test_detects_amex(self):
        detector = CreditCardDetector()
        # Valid Amex test number (15 digits)
        matches = detector.detect("Amex: 378282246310005")
        assert len(matches) == 1

    def test_detects_discover(self):
        detector = CreditCardDetector()
        # Valid Discover test number
        matches = detector.detect("Discover: 6011111111111117")
        assert len(matches) == 1

    # === Formatted Card Tests ===

    def test_detects_card_with_spaces(self):
        detector = CreditCardDetector()
        matches = detector.detect("4111 1111 1111 1111")
        assert len(matches) == 1
        assert matches[0].text == "4111 1111 1111 1111"

    def test_detects_card_with_hyphens(self):
        detector = CreditCardDetector()
        matches = detector.detect("4111-1111-1111-1111")
        assert len(matches) == 1
        assert matches[0].text == "4111-1111-1111-1111"

    # === Context Tests ===

    def test_card_in_sentence(self):
        detector = CreditCardDetector()
        text = "Pay with 4111111111111111 please."
        matches = detector.detect(text)
        assert len(matches) == 1
        assert matches[0].start == 9
        assert matches[0].end == 25

    def test_multiple_cards(self):
        detector = CreditCardDetector()
        text = "Cards: 4111111111111111, 5555555555554444"
        matches = detector.detect(text)
        assert len(matches) == 2

    # === Invalid Luhn Tests ===

    def test_no_match_invalid_luhn(self):
        detector = CreditCardDetector()
        # Invalid Luhn (changed last digit)
        matches = detector.detect("4111111111111112")
        assert len(matches) == 0

    # === No Match Tests ===

    def test_no_match_plain_text(self):
        detector = CreditCardDetector()
        matches = detector.detect("Hello world, no card here")
        assert len(matches) == 0

    def test_no_match_too_short(self):
        detector = CreditCardDetector()
        matches = detector.detect("123456789012")
        assert len(matches) == 0

    def test_no_match_phone_number(self):
        detector = CreditCardDetector()
        # Phone numbers shouldn't match (different pattern)
        matches = detector.detect("Call 0171 1234567")
        assert len(matches) == 0

    # === Metadata Tests ===

    def test_detector_name(self):
        detector = CreditCardDetector()
        matches = detector.detect("4111111111111111")
        assert matches[0].detector == "credit_card"
