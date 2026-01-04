"""Credit card number detector with Luhn validation."""

import re

from pii_shield.core import PIIMatch, PIIType
from pii_shield.detectors.base import Detector


class CreditCardDetector(Detector):
    """Detect credit card numbers in text.

    Supports major card types:
    - Visa: 4xxx (13 or 16 digits)
    - Mastercard: 51-55xx or 2221-2720 (16 digits)
    - Amex: 34xx or 37xx (15 digits)
    - Discover: 6011, 65xx (16 digits)

    Validates using Luhn algorithm.
    """

    # Pattern: 13-19 digits with optional separators (spaces, hyphens)
    PATTERN = re.compile(
        r"\b(\d{4}[\s\-]?\d{4}[\s\-]?\d{4}[\s\-]?\d{1,7}|\d{13,19})\b"
    )

    def detect(self, text: str) -> list[PIIMatch]:
        """Find all credit card numbers in text."""
        matches = []
        for match in self.PATTERN.finditer(text):
            card_text = match.group()
            digits = re.sub(r"[\s\-]", "", card_text)

            # Skip if not valid card length
            if len(digits) < 13 or len(digits) > 19:
                continue

            # Validate with Luhn algorithm
            is_valid = self._luhn_check(digits)

            # Skip if Luhn fails (likely not a credit card)
            if not is_valid:
                continue

            matches.append(
                PIIMatch(
                    type=PIIType.CREDIT_CARD,
                    text=card_text,
                    start=match.start(),
                    end=match.end(),
                    confidence=1.0,
                    detector="credit_card",
                )
            )
        return matches

    def _luhn_check(self, digits: str) -> bool:
        """Validate card number using Luhn algorithm.

        1. Double every second digit from right
        2. If doubled digit > 9, subtract 9
        3. Sum all digits
        4. Valid if sum % 10 == 0
        """
        total = 0
        reverse_digits = digits[::-1]

        for i, char in enumerate(reverse_digits):
            digit = int(char)
            if i % 2 == 1:  # Every second digit (from right)
                digit *= 2
                if digit > 9:
                    digit -= 9
            total += digit

        return total % 10 == 0
