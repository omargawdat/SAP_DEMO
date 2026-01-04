"""Processing report for PII detection and de-identification."""

import json
from dataclasses import dataclass, field

from pii_shield.core import PIIMatch, PIIType


@dataclass
class ProcessingReport:
    """Report containing detection results and processed output."""

    original_text: str
    processed_text: str
    matches: list[PIIMatch] = field(default_factory=list)
    processing_time_ms: float = 0.0

    @property
    def pii_found(self) -> bool:
        """Check if any PII was detected."""
        return len(self.matches) > 0

    @property
    def pii_count(self) -> int:
        """Total number of PII matches found."""
        return len(self.matches)

    def count_by_type(self) -> dict[PIIType, int]:
        """Get count of matches grouped by PII type."""
        counts: dict[PIIType, int] = {}
        for match in self.matches:
            counts[match.type] = counts.get(match.type, 0) + 1
        return counts

    def to_dict(self) -> dict:
        """Convert report to dictionary for JSON serialization."""
        return {
            "original_text": self.original_text,
            "processed_text": self.processed_text,
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
            "summary": {
                "pii_found": self.pii_found,
                "total_count": self.pii_count,
                "by_type": {k.value: v for k, v in self.count_by_type().items()},
            },
            "processing_time_ms": self.processing_time_ms,
        }

    def to_json(self, indent: int = 2) -> str:
        """Export report as JSON string."""
        return json.dumps(self.to_dict(), indent=indent)
