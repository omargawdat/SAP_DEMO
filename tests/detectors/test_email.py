"""Tests for email detector."""

from pii_shield.core import PIIType
from pii_shield.detectors import EmailDetector


class TestEmailDetector:
    """Tests for EmailDetector."""

    def test_detects_simple_email(self):
        detector = EmailDetector()
        matches = detector.detect("Contact hans@sap.com for help")
        assert len(matches) == 1
        assert matches[0].type == PIIType.EMAIL
        assert matches[0].text == "hans@sap.com"
        assert matches[0].start == 8
        assert matches[0].end == 20

    def test_detects_plus_addressing(self):
        detector = EmailDetector()
        matches = detector.detect("Email: hans+work@sap.com")
        assert len(matches) == 1
        assert matches[0].text == "hans+work@sap.com"

    def test_detects_subdomain(self):
        detector = EmailDetector()
        matches = detector.detect("Email: hans@mail.sap.com")
        assert len(matches) == 1
        assert matches[0].text == "hans@mail.sap.com"

    def test_detects_multiple_emails(self):
        detector = EmailDetector()
        matches = detector.detect("Contact hans@sap.com or anna@sap.com")
        assert len(matches) == 2
        assert matches[0].text == "hans@sap.com"
        assert matches[1].text == "anna@sap.com"

    def test_no_match_in_plain_text(self):
        detector = EmailDetector()
        matches = detector.detect("Hello world, no emails here")
        assert len(matches) == 0

    def test_confidence_is_one(self):
        detector = EmailDetector()
        matches = detector.detect("test@example.com")
        assert matches[0].confidence == 1.0

    def test_detector_name(self):
        detector = EmailDetector()
        matches = detector.detect("test@example.com")
        assert matches[0].detector == "email"

    def test_various_tlds(self):
        detector = EmailDetector()
        matches = detector.detect("a@b.de c@d.org e@f.co.uk")
        assert len(matches) == 3
