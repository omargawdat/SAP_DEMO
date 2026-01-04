"""Tests for TextProcessor."""

from pii_shield.core import PIIMatch, PIIType
from pii_shield.detectors import EmailDetector
from pii_shield.detectors.base import Detector
from pii_shield.pipeline import TextProcessor
from pii_shield.strategies import RedactionStrategy


class MockPhoneDetector(Detector):
    """Mock phone detector for testing."""

    def detect(self, text: str) -> list[PIIMatch]:
        # Simple mock: detect "+49" followed by digits
        matches = []
        import re

        for match in re.finditer(r"\+49\s?\d+", text):
            matches.append(
                PIIMatch(
                    type=PIIType.PHONE,
                    text=match.group(),
                    start=match.start(),
                    end=match.end(),
                    confidence=0.9,
                    detector="phone",
                )
            )
        return matches


class TestTextProcessor:
    """Tests for TextProcessor."""

    def test_process_with_single_detector(self):
        processor = TextProcessor(
            detectors=[EmailDetector()],
            strategy=RedactionStrategy(),
        )
        report = processor.process("Contact hans@sap.com")
        assert report.pii_found is True
        assert report.pii_count == 1
        assert report.processed_text == "Contact [EMAIL]"

    def test_process_with_multiple_detectors(self):
        processor = TextProcessor(
            detectors=[EmailDetector(), MockPhoneDetector()],
            strategy=RedactionStrategy(),
        )
        report = processor.process("Email hans@sap.com or call +49123")
        assert report.pii_count == 2
        assert "[EMAIL]" in report.processed_text
        assert "[PHONE]" in report.processed_text

    def test_process_without_strategy(self):
        processor = TextProcessor(
            detectors=[EmailDetector()],
            strategy=None,
        )
        report = processor.process("Contact hans@sap.com")
        assert report.pii_found is True
        assert report.processed_text == "Contact hans@sap.com"  # Unchanged

    def test_process_no_pii(self):
        processor = TextProcessor(
            detectors=[EmailDetector()],
            strategy=RedactionStrategy(),
        )
        report = processor.process("Hello world")
        assert report.pii_found is False
        assert report.processed_text == "Hello world"

    def test_matches_sorted_by_position(self):
        processor = TextProcessor(
            detectors=[EmailDetector()],
        )
        report = processor.process("a@b.com and c@d.com")
        assert len(report.matches) == 2
        assert report.matches[0].start < report.matches[1].start

    def test_processing_time_recorded(self):
        processor = TextProcessor(detectors=[EmailDetector()])
        report = processor.process("test@example.com")
        assert report.processing_time_ms > 0

    def test_deduplicates_same_position_matches(self):
        """When two detectors find same match, keep highest confidence."""

        class DuplicateDetector(Detector):
            def detect(self, text: str) -> list[PIIMatch]:
                # Return same match as EmailDetector but lower confidence
                return [
                    PIIMatch(
                        type=PIIType.EMAIL,
                        text="a@b.com",
                        start=0,
                        end=7,
                        confidence=0.5,
                        detector="duplicate",
                    )
                ]

        processor = TextProcessor(
            detectors=[EmailDetector(), DuplicateDetector()],
        )
        report = processor.process("a@b.com")
        assert report.pii_count == 1
        assert report.matches[0].confidence == 1.0  # EmailDetector's confidence

    def test_empty_detectors_list(self):
        processor = TextProcessor(detectors=[])
        report = processor.process("test@example.com")
        assert report.pii_found is False
        assert report.processed_text == "test@example.com"
