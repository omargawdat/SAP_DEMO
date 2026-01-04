"""Text normalizer for consistent PII detection."""

import unicodedata

from pii_shield.preprocessing.base import Preprocessor


class TextNormalizer(Preprocessor):
    """Normalize text for consistent PII detection."""

    def process(self, text: str) -> str:
        """Normalize unicode and whitespace."""
        # Unicode NFC normalization
        text = unicodedata.normalize("NFC", text)
        # Collapse multiple whitespace to single space
        text = " ".join(text.split())
        return text
