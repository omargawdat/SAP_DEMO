"""Core data models for PII detection results."""

from dataclasses import dataclass, field
from typing import Self

from pii_shield.core.types import PIIType


@dataclass(frozen=True, slots=True)
class PIIMatch:
    """Represents a single detected PII instance in text.

    Attributes:
        type: The category of PII detected.
        text: The actual matched text content.
        start: Starting character position in the original text.
        end: Ending character position in the original text.
        confidence: Detection confidence score from 0.0 to 1.0.
        detector: Name of the detector that found this match.
    """

    type: PIIType
    text: str
    start: int
    end: int
    confidence: float = 1.0
    detector: str = "unknown"

    def __post_init__(self) -> None:
        """Validate match data."""
        if self.start < 0:
            raise ValueError("start position must be non-negative")
        if self.end < self.start:
            raise ValueError("end position must be >= start position")
        if not 0.0 <= self.confidence <= 1.0:
            raise ValueError("confidence must be between 0.0 and 1.0")

    @property
    def length(self) -> int:
        """Length of the matched text."""
        return self.end - self.start

    def overlaps(self, other: Self) -> bool:
        """Check if this match overlaps with another match."""
        return self.start < other.end and other.start < self.end


@dataclass(slots=True)
class DetectionResult:
    """Aggregates all PII matches from processing a text.

    Attributes:
        original_text: The input text that was analyzed.
        matches: List of all PII matches found.
        processing_time_ms: Time taken to process in milliseconds.
    """

    original_text: str
    matches: list[PIIMatch] = field(default_factory=list)
    processing_time_ms: float = 0.0

    @property
    def has_pii(self) -> bool:
        """Check if any PII was detected."""
        return len(self.matches) > 0

    @property
    def pii_count(self) -> int:
        """Total number of PII matches found."""
        return len(self.matches)

    def get_matches_by_type(self, pii_type: PIIType) -> list[PIIMatch]:
        """Get all matches of a specific PII type."""
        return [m for m in self.matches if m.type == pii_type]

    def get_types_found(self) -> set[PIIType]:
        """Get set of all PII types detected."""
        return {m.type for m in self.matches}

    def sorted_matches(self) -> list[PIIMatch]:
        """Get matches sorted by position (start index)."""
        return sorted(self.matches, key=lambda m: m.start)

    def to_dict(self) -> dict:
        """Convert result to dictionary for JSON serialization."""
        return {
            "original_text": self.original_text,
            "matches": [
                {
                    "type": m.type.value,
                    "text": m.text,
                    "start": m.start,
                    "end": m.end,
                    "confidence": m.confidence,
                    "detector": m.detector,
                }
                for m in self.matches
            ],
            "processing_time_ms": self.processing_time_ms,
            "summary": {
                "total_pii_found": self.pii_count,
                "types_found": [t.value for t in self.get_types_found()],
            },
        }
