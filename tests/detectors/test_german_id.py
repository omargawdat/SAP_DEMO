"""Tests for German ID (Personalausweis) detector."""

from pii_shield.core import PIIType
from pii_shield.detectors.german_id import GermanIDDetector


class TestGermanIDDetector:
    """Tests for GermanIDDetector."""

    # === Valid ID Tests ===

    def test_detects_valid_german_id_without_check(self):
        detector = GermanIDDetector()
        matches = detector.detect("ID: L01X00T47")
        assert len(matches) == 1
        assert matches[0].type == PIIType.GERMAN_ID
        assert matches[0].text == "L01X00T47"
        assert matches[0].confidence == 0.8

    def test_detects_valid_german_id_with_check_digit(self):
        detector = GermanIDDetector()
        # L01X00T47 with valid check digit
        matches = detector.detect("ID: L01X00T471")
        assert len(matches) == 1
        assert matches[0].text == "L01X00T471"

    def test_detects_lowercase_id(self):
        detector = GermanIDDetector()
        matches = detector.detect("Ausweis: l01x00t47")
        assert len(matches) == 1

    # === Different First Letters ===

    def test_detects_id_starting_with_m(self):
        detector = GermanIDDetector()
        matches = detector.detect("M12345678")
        assert len(matches) == 1

    def test_detects_id_starting_with_t(self):
        detector = GermanIDDetector()
        matches = detector.detect("T98765432")
        assert len(matches) == 1

    def test_detects_id_starting_with_x(self):
        detector = GermanIDDetector()
        matches = detector.detect("X00000000")
        assert len(matches) == 1

    # === Invalid Check Digit ===

    def test_invalid_check_digit_lower_confidence(self):
        detector = GermanIDDetector()
        # Wrong check digit (should be different)
        matches = detector.detect("L01X00T479")
        assert len(matches) == 1
        assert matches[0].confidence == 0.6

    # === Context Tests ===

    def test_id_in_sentence(self):
        detector = GermanIDDetector()
        text = "My ID number is L01X00T47 and it expires soon."
        matches = detector.detect(text)
        assert len(matches) == 1
        assert matches[0].start == 16
        assert matches[0].end == 25

    def test_multiple_ids(self):
        detector = GermanIDDetector()
        text = "IDs: L01X00T47, M98765432"
        matches = detector.detect(text)
        assert len(matches) == 2

    # === No Match Tests ===

    def test_no_match_plain_text(self):
        detector = GermanIDDetector()
        matches = detector.detect("Hello world, no ID here")
        assert len(matches) == 0

    def test_no_match_invalid_first_letter(self):
        detector = GermanIDDetector()
        # A is not a valid first letter for German ID
        matches = detector.detect("A12345678")
        assert len(matches) == 0

    def test_no_match_too_short(self):
        detector = GermanIDDetector()
        matches = detector.detect("L1234567")
        assert len(matches) == 0

    # === Metadata Tests ===

    def test_detector_name(self):
        detector = GermanIDDetector()
        matches = detector.detect("L01X00T47")
        assert matches[0].detector == "german_id"
