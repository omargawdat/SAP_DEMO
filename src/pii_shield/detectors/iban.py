"""IBAN detector with checksum validation."""

import re

from pii_shield.core import PIIMatch, PIIType
from pii_shield.detectors.base import Detector


class IBANDetector(Detector):
    """Detect IBAN numbers in text.

    Supports all IBAN formats with mod-97 checksum validation.
    German IBANs: DE + 2 check digits + 18 alphanumeric (22 total)
    """

    # IBAN pattern: 2 letters + 2 digits + 4-30 alphanumeric
    PATTERN = re.compile(
        r"\b([A-Z]{2})(\d{2})([A-Z0-9]{4,30})\b",
        re.IGNORECASE,
    )

    # Country-specific IBAN lengths
    IBAN_LENGTHS = {
        "DE": 22,  # Germany
        "AT": 20,  # Austria
        "CH": 21,  # Switzerland
        "FR": 27,  # France
        "NL": 18,  # Netherlands
        "BE": 16,  # Belgium
        "ES": 24,  # Spain
        "IT": 27,  # Italy
        "GB": 22,  # UK
        "PL": 28,  # Poland
    }

    def detect(self, text: str) -> list[PIIMatch]:
        """Find all IBAN numbers in text."""
        matches = []
        for match in self.PATTERN.finditer(text):
            iban = match.group().upper().replace(" ", "")
            country = iban[:2]

            # Check length if country is known
            expected_len = self.IBAN_LENGTHS.get(country)
            if expected_len and len(iban) != expected_len:
                continue

            # Validate checksum
            is_valid = self._validate_checksum(iban)

            matches.append(
                PIIMatch(
                    type=PIIType.IBAN,
                    text=match.group(),
                    start=match.start(),
                    end=match.end(),
                    confidence=1.0 if is_valid else 0.7,
                    detector="iban",
                )
            )
        return matches

    def _validate_checksum(self, iban: str) -> bool:
        """Validate IBAN using mod-97 algorithm.

        1. Move first 4 chars to end
        2. Convert letters to numbers (A=10, B=11, ..., Z=35)
        3. Check if mod 97 == 1
        """
        # Rearrange: move first 4 chars to end
        rearranged = iban[4:] + iban[:4]

        # Convert to numeric string
        numeric = ""
        for char in rearranged:
            if char.isdigit():
                numeric += char
            else:
                # A=10, B=11, ..., Z=35
                numeric += str(ord(char.upper()) - 55)

        # Mod 97 check
        return int(numeric) % 97 == 1
