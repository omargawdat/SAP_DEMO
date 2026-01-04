"""Tests for redaction strategy."""

from pii_shield.core import PIIMatch, PIIType
from pii_shield.strategies import RedactionStrategy


class TestRedactionStrategy:
    """Tests for RedactionStrategy."""

    def test_redacts_single_email(self):
        strategy = RedactionStrategy()
        text = "Contact hans@sap.com for help"
        matches = [
            PIIMatch(
                type=PIIType.EMAIL,
                text="hans@sap.com",
                start=8,
                end=20,
            )
        ]
        result = strategy.apply(text, matches)
        assert result == "Contact [EMAIL] for help"

    def test_redacts_multiple_matches(self):
        strategy = RedactionStrategy()
        text = "Email hans@sap.com or call +49 123 456789"
        matches = [
            PIIMatch(type=PIIType.EMAIL, text="hans@sap.com", start=6, end=18),
            PIIMatch(type=PIIType.PHONE, text="+49 123 456789", start=27, end=41),
        ]
        result = strategy.apply(text, matches)
        assert result == "Email [EMAIL] or call [PHONE]"

    def test_empty_matches_returns_original(self):
        strategy = RedactionStrategy()
        text = "No PII here"
        result = strategy.apply(text, [])
        assert result == text

    def test_custom_placeholder_format(self):
        strategy = RedactionStrategy(placeholder_format="<{type}>")
        text = "Contact hans@sap.com"
        matches = [
            PIIMatch(type=PIIType.EMAIL, text="hans@sap.com", start=8, end=20)
        ]
        result = strategy.apply(text, matches)
        assert result == "Contact <EMAIL>"

    def test_redacts_at_start_of_text(self):
        strategy = RedactionStrategy()
        text = "hans@sap.com is my email"
        matches = [
            PIIMatch(type=PIIType.EMAIL, text="hans@sap.com", start=0, end=12)
        ]
        result = strategy.apply(text, matches)
        assert result == "[EMAIL] is my email"

    def test_redacts_at_end_of_text(self):
        strategy = RedactionStrategy()
        text = "My email is hans@sap.com"
        matches = [
            PIIMatch(type=PIIType.EMAIL, text="hans@sap.com", start=12, end=24)
        ]
        result = strategy.apply(text, matches)
        assert result == "My email is [EMAIL]"

    def test_redacts_different_pii_types(self):
        strategy = RedactionStrategy()
        text = "ID: L01X00T471"
        matches = [
            PIIMatch(type=PIIType.GERMAN_ID, text="L01X00T471", start=4, end=14)
        ]
        result = strategy.apply(text, matches)
        assert result == "ID: [GERMAN_ID]"

    def test_handles_unsorted_matches(self):
        strategy = RedactionStrategy()
        text = "a@b.com and c@d.com"
        # Provide matches in reverse order
        matches = [
            PIIMatch(type=PIIType.EMAIL, text="c@d.com", start=12, end=19),
            PIIMatch(type=PIIType.EMAIL, text="a@b.com", start=0, end=7),
        ]
        result = strategy.apply(text, matches)
        assert result == "[EMAIL] and [EMAIL]"
