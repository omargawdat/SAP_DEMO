"""Tests for IBAN detector."""

from pii_shield.core import PIIType
from pii_shield.detectors.iban import IBANDetector


class TestIBANDetector:
    """Tests for IBANDetector."""

    # === Valid German IBAN Tests ===

    def test_detects_valid_german_iban(self):
        detector = IBANDetector()
        # Valid German IBAN (checksum verified)
        matches = detector.detect("Account: DE89370400440532013000")
        assert len(matches) == 1
        assert matches[0].type == PIIType.IBAN
        assert matches[0].text == "DE89370400440532013000"
        assert matches[0].confidence == 1.0

    def test_detects_lowercase_iban(self):
        detector = IBANDetector()
        matches = detector.detect("IBAN: de89370400440532013000")
        assert len(matches) == 1
        assert matches[0].confidence == 1.0

    # === Other EU IBAN Tests ===

    def test_detects_austrian_iban(self):
        detector = IBANDetector()
        # Valid Austrian IBAN
        matches = detector.detect("AT611904300234573201")
        assert len(matches) == 1
        assert matches[0].confidence == 1.0

    def test_detects_french_iban(self):
        detector = IBANDetector()
        # Valid French IBAN
        matches = detector.detect("FR7630006000011234567890189")
        assert len(matches) == 1
        assert matches[0].confidence == 1.0

    # === Invalid Checksum Tests ===

    def test_invalid_checksum_lower_confidence(self):
        detector = IBANDetector()
        # Invalid checksum (changed last digit)
        matches = detector.detect("DE89370400440532013001")
        assert len(matches) == 1
        assert matches[0].confidence == 0.7

    # === Format Tests ===

    def test_iban_in_sentence(self):
        detector = IBANDetector()
        text = "Please transfer to DE89370400440532013000 by Friday."
        matches = detector.detect(text)
        assert len(matches) == 1
        assert matches[0].start == 19
        assert matches[0].end == 41

    def test_multiple_ibans(self):
        detector = IBANDetector()
        text = "From DE89370400440532013000 to AT611904300234573201"
        matches = detector.detect(text)
        assert len(matches) == 2

    # === No Match Tests ===

    def test_no_match_plain_text(self):
        detector = IBANDetector()
        matches = detector.detect("Hello world, no IBAN here")
        assert len(matches) == 0

    def test_no_match_wrong_length(self):
        detector = IBANDetector()
        # German IBAN must be 22 chars, this is 20
        matches = detector.detect("DE89370400440532013")
        assert len(matches) == 0

    def test_no_match_invalid_country(self):
        detector = IBANDetector()
        # XX is not a valid country code pattern
        matches = detector.detect("12345678901234567890")
        assert len(matches) == 0

    # === Metadata Tests ===

    def test_detector_name(self):
        detector = IBANDetector()
        matches = detector.detect("DE89370400440532013000")
        assert matches[0].detector == "iban"
