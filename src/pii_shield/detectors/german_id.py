"""German ID (Personalausweis) detector."""

import re

from pii_shield.core import PIIMatch, PIIType
from pii_shield.detectors.base import Detector


class GermanIDDetector(Detector):
    """Detect German ID card numbers (Personalausweis).

    Format: 9 or 10 alphanumeric characters
    - First char: L, M, N, P, R, T, V, W, X, Y (issuing authority)
    - Chars 2-9: alphanumeric serial number
    - Char 10 (optional): check digit

    Example: L01X00T471
    """

    # Pattern: Letter followed by 8 alphanumeric chars, optionally followed by check digit
    # Valid first letters for German ID
    PATTERN = re.compile(
        r"\b([LMNPRTVWXY][A-Z0-9]{8})(\d)?\b",
        re.IGNORECASE,
    )

    # Character values for check digit calculation
    CHAR_VALUES = {
        "0": 0, "1": 1, "2": 2, "3": 3, "4": 4,
        "5": 5, "6": 6, "7": 7, "8": 8, "9": 9,
        "A": 10, "B": 11, "C": 12, "D": 13, "E": 14,
        "F": 15, "G": 16, "H": 17, "I": 18, "J": 19,
        "K": 20, "L": 21, "M": 22, "N": 23, "O": 24,
        "P": 25, "Q": 26, "R": 27, "S": 28, "T": 29,
        "U": 30, "V": 31, "W": 32, "X": 33, "Y": 34,
        "Z": 35,
    }

    # Weights for check digit calculation
    WEIGHTS = [7, 3, 1, 7, 3, 1, 7, 3, 1]

    def detect(self, text: str) -> list[PIIMatch]:
        """Find all German ID numbers in text."""
        matches = []
        for match in self.PATTERN.finditer(text):
            id_number = match.group(1).upper()
            check_digit = match.group(2)

            # Filter out pure alphabetic matches (likely words, not IDs)
            # Real German IDs contain digits (e.g., L01X00T471)
            digit_count = sum(1 for c in id_number if c.isdigit())
            if digit_count < 2:
                continue  # Skip - real IDs have at least 2 digits

            # Calculate confidence based on check digit validation
            if check_digit:
                expected = self._calculate_check_digit(id_number)
                is_valid = int(check_digit) == expected
                confidence = 1.0 if is_valid else 0.6
            else:
                confidence = 0.8

            matches.append(
                PIIMatch(
                    type=PIIType.GERMAN_ID,
                    text=match.group(),
                    start=match.start(),
                    end=match.end(),
                    confidence=confidence,
                    detector="german_id",
                )
            )
        return matches

    def _calculate_check_digit(self, id_number: str) -> int:
        """Calculate check digit using weighted sum mod 10.

        Each character is multiplied by weight (7, 3, 1 repeating),
        then summed and taken mod 10.
        """
        total = 0
        for i, char in enumerate(id_number[:9]):
            value = self.CHAR_VALUES.get(char.upper(), 0)
            total += value * self.WEIGHTS[i]
        return total % 10
