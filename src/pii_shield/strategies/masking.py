"""Masking strategy for partial PII visibility."""

from pii_shield.core import PIIMatch
from pii_shield.strategies.base import Strategy


class MaskingStrategy(Strategy):
    """Partially mask PII while preserving some visibility.

    Shows first and last characters, masks the middle.
    Useful when partial recognition is needed without full exposure.
    """

    def __init__(self, mask_char: str = "*", visible_chars: int = 3):
        """Initialize masking strategy.

        Args:
            mask_char: Character to use for masking (default "*").
            visible_chars: Number of chars to show at start and end (default 3).
        """
        self.mask_char = mask_char
        self.visible_chars = visible_chars

    def apply(self, text: str, matches: list[PIIMatch]) -> str:
        """Replace PII with masked versions."""
        for match in sorted(matches, key=lambda m: m.start, reverse=True):
            masked = self._mask(match.text)
            text = text[: match.start] + masked + text[match.end :]
        return text

    def _mask(self, value: str) -> str:
        """Mask a value, showing first and last chars."""
        if len(value) <= self.visible_chars * 2:
            return self.mask_char * len(value)
        return (
            value[: self.visible_chars]
            + self.mask_char * 3
            + value[-self.visible_chars :]
        )
