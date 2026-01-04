"""Base class for PII detectors."""

from abc import ABC, abstractmethod

from pii_shield.core import PIIMatch


class Detector(ABC):
    """Abstract base class for PII detection."""

    @abstractmethod
    def detect(self, text: str) -> list[PIIMatch]:
        """Detect PII in text and return matches."""
        pass
