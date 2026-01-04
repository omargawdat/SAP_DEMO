"""Email address detector."""

import re

from pii_shield.core import PIIMatch, PIIType
from pii_shield.detectors.base import Detector


class EmailDetector(Detector):
    """Detect email addresses in text."""

    PATTERN = re.compile(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}")

    def detect(self, text: str) -> list[PIIMatch]:
        """Find all email addresses in text."""
        matches = []
        for match in self.PATTERN.finditer(text):
            matches.append(
                PIIMatch(
                    type=PIIType.EMAIL,
                    text=match.group(),
                    start=match.start(),
                    end=match.end(),
                    confidence=1.0,
                    detector="email",
                )
            )
        return matches
