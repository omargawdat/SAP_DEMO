"""Tests for ProcessingReport."""

import json

from pii_shield.core import PIIMatch, PIIType
from pii_shield.pipeline import ProcessingReport


class TestProcessingReport:
    """Tests for ProcessingReport."""

    def test_empty_report(self):
        report = ProcessingReport(
            original_text="Hello world",
            processed_text="Hello world",
        )
        assert report.pii_found is False
        assert report.pii_count == 0
        assert report.count_by_type() == {}

    def test_report_with_matches(self):
        matches = [
            PIIMatch(type=PIIType.EMAIL, text="a@b.com", start=0, end=7),
            PIIMatch(type=PIIType.EMAIL, text="c@d.com", start=12, end=19),
            PIIMatch(type=PIIType.PHONE, text="+49123", start=24, end=30),
        ]
        report = ProcessingReport(
            original_text="a@b.com and c@d.com and +49123",
            processed_text="[EMAIL] and [EMAIL] and [PHONE]",
            matches=matches,
        )
        assert report.pii_found is True
        assert report.pii_count == 3

    def test_count_by_type(self):
        matches = [
            PIIMatch(type=PIIType.EMAIL, text="a@b.com", start=0, end=7),
            PIIMatch(type=PIIType.EMAIL, text="c@d.com", start=12, end=19),
            PIIMatch(type=PIIType.PHONE, text="+49123", start=24, end=30),
        ]
        report = ProcessingReport(
            original_text="test",
            processed_text="test",
            matches=matches,
        )
        counts = report.count_by_type()
        assert counts[PIIType.EMAIL] == 2
        assert counts[PIIType.PHONE] == 1

    def test_to_dict(self):
        matches = [
            PIIMatch(type=PIIType.EMAIL, text="a@b.com", start=0, end=7),
        ]
        report = ProcessingReport(
            original_text="a@b.com",
            processed_text="[EMAIL]",
            matches=matches,
            processing_time_ms=1.5,
        )
        result = report.to_dict()
        assert result["original_text"] == "a@b.com"
        assert result["processed_text"] == "[EMAIL]"
        assert result["summary"]["pii_found"] is True
        assert result["summary"]["total_count"] == 1
        assert result["summary"]["by_type"]["EMAIL"] == 1
        assert result["processing_time_ms"] == 1.5

    def test_to_json(self):
        report = ProcessingReport(
            original_text="test@example.com",
            processed_text="[EMAIL]",
            matches=[
                PIIMatch(type=PIIType.EMAIL, text="test@example.com", start=0, end=16)
            ],
        )
        json_str = report.to_json()
        parsed = json.loads(json_str)
        assert parsed["original_text"] == "test@example.com"
        assert parsed["processed_text"] == "[EMAIL]"
