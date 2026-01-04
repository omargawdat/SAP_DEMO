"""Tests for hashing strategy."""

from pii_shield.core import PIIMatch, PIIType
from pii_shield.strategies.hashing import HashingStrategy


class TestHashingStrategy:
    """Tests for HashingStrategy."""

    def test_hashes_single_match(self):
        strategy = HashingStrategy()
        matches = [PIIMatch(PIIType.EMAIL, "test@example.com", 0, 16, 1.0, "email")]
        result = strategy.apply("test@example.com", matches)
        assert result != "test@example.com"
        assert len(result) == 16  # Default hash length

    def test_consistent_hash_same_input(self):
        strategy = HashingStrategy()
        matches = [PIIMatch(PIIType.EMAIL, "test@example.com", 0, 16, 1.0, "email")]
        result1 = strategy.apply("test@example.com", matches)
        result2 = strategy.apply("test@example.com", matches)
        assert result1 == result2

    def test_different_hash_with_salt(self):
        matches = [PIIMatch(PIIType.EMAIL, "test@example.com", 0, 16, 1.0, "email")]
        result1 = HashingStrategy(salt="salt1").apply("test@example.com", matches)
        result2 = HashingStrategy(salt="salt2").apply("test@example.com", matches)
        assert result1 != result2

    def test_configurable_length(self):
        strategy = HashingStrategy(length=8)
        matches = [PIIMatch(PIIType.EMAIL, "test@example.com", 0, 16, 1.0, "email")]
        result = strategy.apply("test@example.com", matches)
        assert len(result) == 8

    def test_hashes_multiple_matches(self):
        strategy = HashingStrategy()
        text = "Contact a@b.com or c@d.com"
        matches = [
            PIIMatch(PIIType.EMAIL, "a@b.com", 8, 15, 1.0, "email"),
            PIIMatch(PIIType.EMAIL, "c@d.com", 19, 26, 1.0, "email"),
        ]
        result = strategy.apply(text, matches)
        assert "a@b.com" not in result
        assert "c@d.com" not in result

    def test_preserves_surrounding_text(self):
        strategy = HashingStrategy()
        text = "Email: test@example.com please"
        matches = [PIIMatch(PIIType.EMAIL, "test@example.com", 7, 23, 1.0, "email")]
        result = strategy.apply(text, matches)
        assert result.startswith("Email: ")
        assert result.endswith(" please")

    def test_empty_matches(self):
        strategy = HashingStrategy()
        result = strategy.apply("no pii here", [])
        assert result == "no pii here"
