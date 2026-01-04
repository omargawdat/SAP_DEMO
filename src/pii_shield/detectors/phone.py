"""German phone number detector."""

import re

from pii_shield.core import PIIMatch, PIIType
from pii_shield.detectors.base import Detector


class PhoneDetector(Detector):
    """Detect German phone numbers in text.

    Supports:
    - International format: +49 xxx xxxxxxx, 0049 xxx xxxxxxx
    - National format: 0xxx xxxxxxx
    - Mobile prefixes: 015x, 016x, 017x
    - Landline area codes: 2-5 digits (e.g., 30 Berlin, 89 Munich)
    - Service numbers: 0800, 0180x
    - Various separators: spaces, hyphens, parentheses
    """

    # German mobile prefixes (without leading 0)
    MOBILE_PREFIXES = {"150", "151", "152", "155", "157", "159", "160", "162", "163", "170", "171", "172", "173", "174", "175", "176", "177", "178", "179"}

    # Service number prefixes
    SERVICE_PREFIXES = {"800", "180", "181", "182", "183", "184", "185", "186", "187", "188", "189", "700", "900"}

    # Pattern for German phone numbers
    # Matches: +49/0049/0 followed by area code and subscriber number
    PATTERN = re.compile(
        r"""
        (?<!\d)                           # Not preceded by digit
        (?:
            (?:\+49|0049)                 # International prefix
            [\s\-./]?                     # Optional separator
            \(?(\d{2,4})\)?               # Area/mobile code (capture group 1)
            [\s\-./]?                     # Optional separator
            (\d{3,8})                     # Subscriber number part 1 (capture group 2)
            (?:[\s\-./]?(\d{1,8}))?       # Optional part 2 (capture group 3)
        |
            \(?0                          # National prefix (with optional opening paren)
            (\d{2,5})\)?                  # Area/mobile code (capture group 4)
            [\s\-./]?                     # Optional separator
            (\d{3,8})                     # Subscriber number part 1 (capture group 5)
            (?:[\s\-./]?(\d{1,8}))?       # Optional part 2 (capture group 6)
        )
        (?!\d)                            # Not followed by digit
        """,
        re.VERBOSE,
    )

    def detect(self, text: str) -> list[PIIMatch]:
        """Find all German phone numbers in text."""
        matches = []
        for match in self.PATTERN.finditer(text):
            matched_text = match.group()

            # Determine confidence based on format
            confidence = self._calculate_confidence(match)

            # Skip if confidence too low (likely false positive)
            if confidence < 0.7:
                continue

            matches.append(
                PIIMatch(
                    type=PIIType.PHONE,
                    text=matched_text,
                    start=match.start(),
                    end=match.end(),
                    confidence=confidence,
                    detector="phone",
                )
            )
        return matches

    def _calculate_confidence(self, match: re.Match) -> float:
        """Calculate confidence score based on phone number format."""
        matched_text = match.group()

        # International format with +49 is highest confidence
        if matched_text.startswith("+49"):
            return 1.0

        # International format with 0049
        if matched_text.startswith("0049"):
            return 1.0

        # Extract area code from national format
        area_code = match.group(4)  # National format area code
        if area_code:
            # Known mobile prefix
            if area_code.lstrip("0") in self.MOBILE_PREFIXES:
                return 0.95

            # Known service prefix
            if area_code.lstrip("0") in self.SERVICE_PREFIXES:
                return 0.95

            # Valid length for German area codes (2-5 digits)
            if 2 <= len(area_code) <= 5:
                return 0.9

        return 0.8
