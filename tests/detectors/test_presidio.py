"""Tests for Presidio NER-based detector."""

import pytest

from pii_shield.core import PIIType
from pii_shield.detectors.presidio import PRESIDIO_AVAILABLE, PresidioDetector

# Skip all tests if Presidio/spaCy not available (Python 3.14+ compatibility)
pytestmark = pytest.mark.skipif(
    not PRESIDIO_AVAILABLE,
    reason="Presidio/spaCy not available on this Python version",
)


@pytest.fixture(scope="module")
def detector():
    """Create detector once for all tests (model loading is slow)."""
    det = PresidioDetector(language="de")
    if det.analyzer is None:
        pytest.skip("spaCy German model not installed")
    return det


class TestPresidioDetector:
    """Tests for PresidioDetector."""

    # === Name Detection Tests ===

    def test_detects_german_name(self, detector):
        matches = detector.detect("Kontakt: Hans Müller ist unser Ansprechpartner.")
        name_matches = [m for m in matches if m.type == PIIType.NAME]
        assert len(name_matches) >= 1
        assert any("Hans" in m.text or "Müller" in m.text for m in name_matches)

    def test_detects_full_name(self, detector):
        matches = detector.detect("Dr. Angela Schmidt leitet das Projekt.")
        name_matches = [m for m in matches if m.type == PIIType.NAME]
        assert len(name_matches) >= 1

    # === Location/Address Detection Tests ===

    def test_detects_german_city(self, detector):
        matches = detector.detect("Das Büro befindet sich in Berlin.")
        location_matches = [m for m in matches if m.type == PIIType.ADDRESS]
        assert len(location_matches) >= 1
        assert any("Berlin" in m.text for m in location_matches)

    def test_detects_address(self, detector):
        matches = detector.detect("Adresse: Hauptstraße 123, München")
        location_matches = [m for m in matches if m.type == PIIType.ADDRESS]
        assert len(location_matches) >= 1

    # === Confidence Score Tests ===

    def test_confidence_score_in_range(self, detector):
        matches = detector.detect("Hans Müller wohnt in Berlin.")
        for match in matches:
            assert 0.0 <= match.confidence <= 1.0

    # === Metadata Tests ===

    def test_detector_name(self, detector):
        matches = detector.detect("Hans Müller")
        if matches:
            assert matches[0].detector == "presidio"

    def test_match_positions(self, detector):
        text = "Name: Hans Müller ist hier."
        matches = detector.detect(text)
        for match in matches:
            assert match.text == text[match.start : match.end]

    # === No Match Tests ===

    def test_no_match_plain_text(self, detector):
        matches = detector.detect("Das ist ein einfacher Text ohne Namen.")
        name_matches = [m for m in matches if m.type == PIIType.NAME]
        assert len(name_matches) == 0

    # === Integration with other detectors ===

    def test_only_detects_configured_entities(self, detector):
        """Presidio should only detect NAME, ADDRESS, DATE - not email/phone."""
        text = "hans@example.com"
        matches = detector.detect(text)
        # Email should not be detected (handled by EmailDetector)
        email_matches = [m for m in matches if m.type == PIIType.EMAIL]
        assert len(email_matches) == 0
