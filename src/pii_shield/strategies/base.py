"""Base class for de-identification strategies."""

from abc import ABC, abstractmethod

from pii_shield.core import PIIMatch


class Strategy(ABC):
    """Abstract base class for PII de-identification strategies."""

    @abstractmethod
    def apply(self, text: str, matches: list[PIIMatch]) -> str:
        """Apply de-identification strategy to text.

        Args:
            text: Original text containing PII.
            matches: List of detected PII matches.

        Returns:
            Text with PII de-identified according to the strategy.
        """
        pass
