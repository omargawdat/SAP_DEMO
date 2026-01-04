"""Hashing strategy for GDPR-compliant pseudonymization."""

import hashlib

from pii_shield.core import PIIMatch
from pii_shield.strategies.base import Strategy


class HashingStrategy(Strategy):
    """Pseudonymize PII with consistent SHA-256 hashing.

    Same input + same salt always produces the same hash,
    allowing entity tracking without exposing actual PII.

    Different salts produce different hashes (unlinkability for GDPR).
    """

    def __init__(self, salt: str = "", length: int = 16):
        """Initialize hashing strategy.

        Args:
            salt: Optional salt for hash. Different salts = unlinkable data.
            length: Length of hash output (default 16 hex chars).
        """
        self.salt = salt
        self.length = length

    def apply(self, text: str, matches: list[PIIMatch]) -> str:
        """Replace PII with consistent hashes."""
        for match in sorted(matches, key=lambda m: m.start, reverse=True):
            hash_input = (self.salt + match.text).encode()
            hash_output = hashlib.sha256(hash_input).hexdigest()[: self.length]
            text = text[: match.start] + hash_output + text[match.end :]
        return text
