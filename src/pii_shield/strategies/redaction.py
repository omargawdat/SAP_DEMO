"""Redaction strategy - replaces PII with type placeholders."""

from pii_shield.core import PIIMatch
from pii_shield.strategies.base import Strategy


class RedactionStrategy(Strategy):
    """Replace PII with placeholder tags like [EMAIL], [PHONE], etc."""

    def __init__(self, placeholder_format: str = "[{type}]"):
        """Initialize redaction strategy.

        Args:
            placeholder_format: Format string for placeholders.
                               Must contain {type} which will be replaced
                               with the PII type name.
        """
        self.placeholder_format = placeholder_format

    def apply(self, text: str, matches: list[PIIMatch]) -> str:
        """Replace all PII matches with placeholders.

        Args:
            text: Original text containing PII.
            matches: List of detected PII matches.

        Returns:
            Text with PII replaced by placeholders.
        """
        if not matches:
            return text

        # Sort matches by position (reverse order for safe replacement)
        sorted_matches = sorted(matches, key=lambda m: m.start, reverse=True)

        result = text
        for match in sorted_matches:
            placeholder = self.placeholder_format.format(type=match.type.value)
            result = result[:match.start] + placeholder + result[match.end:]

        return result
