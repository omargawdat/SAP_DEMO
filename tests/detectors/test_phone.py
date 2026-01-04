"""Tests for German phone number detector."""

from pii_shield.core import PIIType
from pii_shield.detectors.phone import PhoneDetector


class TestPhoneDetector:
    """Tests for PhoneDetector."""

    # === International Format Tests ===

    def test_detects_international_plus49(self):
        detector = PhoneDetector()
        matches = detector.detect("Call +49 171 1234567 for help")
        assert len(matches) == 1
        assert matches[0].type == PIIType.PHONE
        assert matches[0].text == "+49 171 1234567"
        assert matches[0].confidence == 1.0

    def test_detects_international_0049(self):
        detector = PhoneDetector()
        matches = detector.detect("Call 0049 171 1234567 for help")
        assert len(matches) == 1
        assert matches[0].text == "0049 171 1234567"
        assert matches[0].confidence == 1.0

    def test_detects_international_with_hyphen(self):
        detector = PhoneDetector()
        matches = detector.detect("Phone: +49-171-1234567")
        assert len(matches) == 1
        assert matches[0].text == "+49-171-1234567"

    # === National Mobile Format Tests ===

    def test_detects_mobile_with_spaces(self):
        detector = PhoneDetector()
        matches = detector.detect("Mobile: 0171 1234567")
        assert len(matches) == 1
        assert matches[0].text == "0171 1234567"
        assert matches[0].confidence >= 0.9

    def test_detects_mobile_without_spaces(self):
        detector = PhoneDetector()
        matches = detector.detect("Mobile: 01711234567")
        assert len(matches) == 1
        assert matches[0].text == "01711234567"

    def test_detects_mobile_with_hyphens(self):
        detector = PhoneDetector()
        matches = detector.detect("Call 0171-123-4567")
        assert len(matches) == 1
        assert matches[0].text == "0171-123-4567"

    def test_detects_various_mobile_prefixes(self):
        detector = PhoneDetector()
        text = "Contacts: 0151 1234567, 0160 2345678, 0175 3456789"
        matches = detector.detect(text)
        assert len(matches) == 3

    # === Landline Format Tests ===

    def test_detects_berlin_landline(self):
        detector = PhoneDetector()
        matches = detector.detect("Berlin office: 030 12345678")
        assert len(matches) == 1
        assert matches[0].text == "030 12345678"

    def test_detects_munich_landline(self):
        detector = PhoneDetector()
        matches = detector.detect("Munich: 089 12345678")
        assert len(matches) == 1
        assert matches[0].text == "089 12345678"

    def test_detects_landline_with_parentheses(self):
        detector = PhoneDetector()
        matches = detector.detect("Phone: (030) 12345678")
        assert len(matches) == 1
        assert matches[0].text == "(030) 12345678"

    def test_detects_international_landline(self):
        detector = PhoneDetector()
        matches = detector.detect("Berlin: +49 30 12345678")
        assert len(matches) == 1
        assert matches[0].text == "+49 30 12345678"

    # === Service Number Tests ===

    def test_detects_toll_free_0800(self):
        detector = PhoneDetector()
        matches = detector.detect("Hotline: 0800 1234567")
        assert len(matches) == 1
        assert matches[0].text == "0800 1234567"

    def test_detects_shared_cost_0180(self):
        detector = PhoneDetector()
        matches = detector.detect("Service: 0180 1234567")
        assert len(matches) == 1
        assert matches[0].text == "0180 1234567"

    # === Multiple Numbers Test ===

    def test_detects_multiple_numbers(self):
        detector = PhoneDetector()
        text = "Call +49 171 1234567 or 030 98765432"
        matches = detector.detect(text)
        assert len(matches) == 2
        assert matches[0].text == "+49 171 1234567"
        assert matches[1].text == "030 98765432"

    # === No Match Tests ===

    def test_no_match_in_plain_text(self):
        detector = PhoneDetector()
        matches = detector.detect("Hello world, no phone numbers here")
        assert len(matches) == 0

    def test_no_match_for_short_numbers(self):
        detector = PhoneDetector()
        # Too short to be a valid phone number
        matches = detector.detect("Code: 12345")
        assert len(matches) == 0

    # === Metadata Tests ===

    def test_detector_name(self):
        detector = PhoneDetector()
        matches = detector.detect("+49 171 1234567")
        assert matches[0].detector == "phone"

    def test_match_positions(self):
        detector = PhoneDetector()
        text = "Call 0171 1234567 now"
        matches = detector.detect(text)
        assert matches[0].start == 5
        assert matches[0].end == 17
        assert text[5:17] == "0171 1234567"
