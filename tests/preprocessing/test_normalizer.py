"""Tests for text normalizer."""

from pii_shield.preprocessing import TextNormalizer


class TestTextNormalizer:
    """Tests for TextNormalizer."""

    def test_collapses_multiple_spaces(self):
        normalizer = TextNormalizer()
        result = normalizer.process("hello    world")
        assert result == "hello world"

    def test_removes_leading_trailing_whitespace(self):
        normalizer = TextNormalizer()
        result = normalizer.process("  hello world  ")
        assert result == "hello world"

    def test_normalizes_tabs_and_newlines(self):
        normalizer = TextNormalizer()
        result = normalizer.process("hello\t\nworld")
        assert result == "hello world"

    def test_unicode_nfc_normalization(self):
        normalizer = TextNormalizer()
        # é as two code points (e + combining accent) -> single é
        decomposed = "caf\u0065\u0301"  # cafe with combining accent
        result = normalizer.process(decomposed)
        assert result == "café"

    def test_preserves_normal_text(self):
        normalizer = TextNormalizer()
        result = normalizer.process("hello world")
        assert result == "hello world"

    def test_empty_string(self):
        normalizer = TextNormalizer()
        result = normalizer.process("")
        assert result == ""
