"""Tests for LLM validator."""

import os
from unittest.mock import MagicMock, patch

import pytest

from pii_shield.core.models import PIIMatch
from pii_shield.core.types import PIIType
from pii_shield.detectors.llm_validator import LLMValidator, ValidationResult


class TestValidationResult:
    """Tests for ValidationResult dataclass."""

    def test_creation(self) -> None:
        """Test creating a validation result."""
        result = ValidationResult(
            is_pii=True,
            confidence=0.95,
            reason="This is a personal name",
        )
        assert result.is_pii is True
        assert result.confidence == 0.95
        assert result.reason == "This is a personal name"


class TestLLMValidator:
    """Tests for LLMValidator class."""

    @pytest.fixture
    def validator(self) -> LLMValidator:
        """Create a validator instance."""
        return LLMValidator(api_key="test-key")

    @pytest.fixture
    def sample_match(self) -> PIIMatch:
        """Create a sample PII match."""
        return PIIMatch(
            type=PIIType.NAME,
            text="Hans Müller",
            start=10,
            end=21,
            confidence=0.85,
            detector="presidio",
        )

    def test_init_with_api_key(self) -> None:
        """Test initialization with API key."""
        validator = LLMValidator(api_key="test-key")
        assert validator.api_key == "test-key"
        assert validator.model == "claude-haiku-4-5-20250929"

    def test_init_with_custom_model(self) -> None:
        """Test initialization with custom model."""
        validator = LLMValidator(api_key="test-key", model="sonnet")
        assert validator.model == "claude-sonnet-4-5-20250929"

    def test_is_available_without_key(self) -> None:
        """Test availability check without API key."""
        validator = LLMValidator(api_key=None)
        # Without anthropic package or API key, should not be available
        assert not validator.is_available()


class TestSentenceExtraction:
    """Tests for sentence extraction functionality."""

    @pytest.fixture
    def validator(self) -> LLMValidator:
        """Create a validator instance."""
        return LLMValidator(api_key="test-key")

    def test_extract_sentence_simple(self, validator: LLMValidator) -> None:
        """Test extracting a simple sentence."""
        text = "Hello world. Hans Müller is here. Goodbye."
        match = PIIMatch(
            type=PIIType.NAME,
            text="Hans Müller",
            start=13,
            end=24,
            confidence=0.8,
            detector="presidio",
        )
        sentence, start = validator._extract_sentence(text, match)
        assert "Hans Müller is here" in sentence
        assert start <= 13  # Start of sentence is before or at match start

    def test_extract_sentence_at_start(self, validator: LLMValidator) -> None:
        """Test extracting sentence at the start of text."""
        text = "Hans Müller is here. Goodbye."
        match = PIIMatch(
            type=PIIType.NAME,
            text="Hans Müller",
            start=0,
            end=11,
            confidence=0.8,
            detector="presidio",
        )
        sentence, start = validator._extract_sentence(text, match)
        assert sentence == "Hans Müller is here."
        assert start == 0

    def test_extract_sentence_at_end(self, validator: LLMValidator) -> None:
        """Test extracting sentence at the end of text."""
        text = "Hello. Contact Hans Müller"
        match = PIIMatch(
            type=PIIType.NAME,
            text="Hans Müller",
            start=15,
            end=26,
            confidence=0.8,
            detector="presidio",
        )
        sentence, start = validator._extract_sentence(text, match)
        assert "Contact Hans Müller" in sentence
        assert start <= 15  # Start of sentence is before or at match start


class TestGroupBySentence:
    """Tests for grouping matches by sentence."""

    @pytest.fixture
    def validator(self) -> LLMValidator:
        """Create a validator instance."""
        return LLMValidator(api_key="test-key")

    def test_group_single_sentence(self, validator: LLMValidator) -> None:
        """Test grouping matches in a single sentence."""
        text = "Hans Müller and Anna Schmidt work together."
        matches = [
            PIIMatch(type=PIIType.NAME, text="Hans Müller", start=0, end=11, confidence=0.8, detector="presidio"),
            PIIMatch(type=PIIType.NAME, text="Anna Schmidt", start=16, end=28, confidence=0.75, detector="presidio"),
        ]
        groups = validator._group_by_sentence(text, matches)
        assert len(groups) == 1
        assert len(groups[0][2]) == 2  # Two matches in same sentence

    def test_group_multiple_sentences(self, validator: LLMValidator) -> None:
        """Test grouping matches across sentences."""
        text = "Hans Müller is here. Anna Schmidt is there."
        matches = [
            PIIMatch(type=PIIType.NAME, text="Hans Müller", start=0, end=11, confidence=0.8, detector="presidio"),
            PIIMatch(type=PIIType.NAME, text="Anna Schmidt", start=21, end=33, confidence=0.75, detector="presidio"),
        ]
        groups = validator._group_by_sentence(text, matches)
        assert len(groups) == 2  # Two separate sentences


class TestValidateLowConfidence:
    """Tests for the main validate_low_confidence method."""

    @pytest.fixture
    def validator(self) -> LLMValidator:
        """Create a validator instance."""
        return LLMValidator(api_key="test-key")

    @patch.dict(os.environ, {"ANTHROPIC_API_KEY": ""}, clear=False)
    def test_high_confidence_auto_approved(self) -> None:
        """Test that high-confidence matches are auto-approved."""
        validator = LLMValidator(api_key=None)
        matches = [
            PIIMatch(type=PIIType.EMAIL, text="test@example.com", start=0, end=16, confidence=1.0, detector="email"),
            PIIMatch(type=PIIType.NAME, text="Hans", start=20, end=24, confidence=0.95, detector="presidio"),
        ]
        results = validator.validate_low_confidence(
            text="test@example.com and Hans",
            matches=matches,
            threshold=0.85,
        )
        assert len(results) == 2
        # High confidence matches should be auto-approved
        assert results[0][1].reason == "High confidence - auto-approved"
        assert results[1][1].reason == "High confidence - auto-approved"

    @patch.dict(os.environ, {"ANTHROPIC_API_KEY": ""}, clear=False)
    def test_low_confidence_without_llm(self) -> None:
        """Test low-confidence matches when LLM is unavailable."""
        validator = LLMValidator(api_key=None)
        matches = [
            PIIMatch(type=PIIType.NAME, text="Hans", start=0, end=4, confidence=0.7, detector="presidio"),
        ]
        results = validator.validate_low_confidence(
            text="Hans is here",
            matches=matches,
            threshold=0.85,
        )
        assert len(results) == 1
        reason_lower = results[0][1].reason.lower()
        assert "unavailable" in reason_lower or "error" in reason_lower

    @patch.dict(os.environ, {"ANTHROPIC_API_KEY": ""}, clear=False)
    def test_mixed_confidence_filtering(self) -> None:
        """Test that only low-confidence matches are sent to LLM."""
        validator = LLMValidator(api_key=None)
        matches = [
            PIIMatch(type=PIIType.EMAIL, text="test@example.com", start=0, end=16, confidence=1.0, detector="email"),
            PIIMatch(type=PIIType.NAME, text="Hans", start=20, end=24, confidence=0.7, detector="presidio"),
        ]
        results = validator.validate_low_confidence(
            text="test@example.com and Hans",
            matches=matches,
            threshold=0.85,
        )
        assert len(results) == 2
        # First should be auto-approved (high conf)
        assert results[0][1].reason == "High confidence - auto-approved"
        # Second should show unavailable or error (low conf, no LLM)
        reason_lower = results[1][1].reason.lower()
        assert "unavailable" in reason_lower or "error" in reason_lower

    def test_empty_matches(self, validator: LLMValidator) -> None:
        """Test with empty matches list."""
        results = validator.validate_low_confidence(text="Some text", matches=[])
        assert results == []

    @patch.object(LLMValidator, "client", new_callable=lambda: MagicMock())
    def test_sentence_validation_success(self, mock_client: MagicMock) -> None:
        """Test successful sentence validation with mocked API."""
        validator = LLMValidator(api_key="test-key")
        validator._client = mock_client

        matches = [
            PIIMatch(type=PIIType.NAME, text="Hans Müller", start=0, end=11, confidence=0.75, detector="presidio"),
            PIIMatch(type=PIIType.NAME, text="SAP", start=25, end=28, confidence=0.65, detector="presidio"),
        ]

        # Mock API response
        mock_response = MagicMock()
        mock_response.content = [
            MagicMock(
                text='[{"text": "Hans Müller", "is_pii": true, "confidence": 0.95, "reason": "Personal name"}, '
                '{"text": "SAP", "is_pii": false, "confidence": 0.1, "reason": "Company name"}]'
            )
        ]
        mock_client.messages.create.return_value = mock_response

        results = validator.validate_low_confidence(
            text="Hans Müller arbeitet bei SAP.",
            matches=matches,
            threshold=0.85,
        )

        # Verify API was called
        assert mock_client.messages.create.call_count >= 1

        # Should have results for both matches
        assert len(results) == 2

        # First should be confirmed as PII
        assert results[0][1].is_pii is True
        assert results[0][1].confidence == 0.95

        # Second should be rejected (not PII)
        assert results[1][1].is_pii is False
        assert results[1][1].confidence == 0.1


class TestParseSentenceResponse:
    """Tests for parsing LLM sentence responses."""

    @pytest.fixture
    def validator(self) -> LLMValidator:
        """Create a validator instance."""
        return LLMValidator(api_key="test-key")

    def test_parse_valid_json(self, validator: LLMValidator) -> None:
        """Test parsing valid JSON response."""
        matches = [
            PIIMatch(type=PIIType.NAME, text="Hans", start=0, end=4, confidence=0.8, detector="presidio"),
        ]
        response = '[{"text": "Hans", "is_pii": true, "confidence": 0.95, "reason": "Personal name"}]'
        results = validator._parse_sentence_response(response, matches)

        assert len(results) == 1
        assert results[0][1].is_pii is True
        assert results[0][1].confidence == 0.95
        assert results[0][1].reason == "Personal name"

    def test_parse_with_markdown(self, validator: LLMValidator) -> None:
        """Test parsing response with markdown code blocks."""
        matches = [
            PIIMatch(type=PIIType.NAME, text="Hans", start=0, end=4, confidence=0.8, detector="presidio"),
        ]
        response = '''```json
[{"text": "Hans", "is_pii": true, "confidence": 0.9, "reason": "Name"}]
```'''
        results = validator._parse_sentence_response(response, matches)

        assert len(results) == 1
        assert results[0][1].is_pii is True
        assert results[0][1].confidence == 0.9

    def test_parse_missing_match(self, validator: LLMValidator) -> None:
        """Test parsing when a match is missing from response."""
        matches = [
            PIIMatch(type=PIIType.NAME, text="Hans", start=0, end=4, confidence=0.8, detector="presidio"),
            PIIMatch(type=PIIType.NAME, text="Anna", start=10, end=14, confidence=0.75, detector="presidio"),
        ]
        # Response only contains Hans, missing Anna
        response = '[{"text": "Hans", "is_pii": true, "confidence": 0.95, "reason": "Name"}]'
        results = validator._parse_sentence_response(response, matches)

        assert len(results) == 2
        assert results[0][1].confidence == 0.95
        # Missing match should use original confidence
        assert results[1][1].confidence == 0.75
        assert "not in LLM response" in results[1][1].reason

    def test_parse_invalid_json(self, validator: LLMValidator) -> None:
        """Test parsing invalid JSON response."""
        matches = [
            PIIMatch(type=PIIType.NAME, text="Hans", start=0, end=4, confidence=0.8, detector="presidio"),
        ]
        response = "This is not valid JSON"
        results = validator._parse_sentence_response(response, matches)

        assert len(results) == 1
        assert results[0][1].is_pii is True
        assert results[0][1].confidence == 0.8
        assert "parse" in results[0][1].reason.lower()

    def test_parse_case_insensitive_matching(self, validator: LLMValidator) -> None:
        """Test that match text comparison is case-insensitive."""
        matches = [
            PIIMatch(type=PIIType.NAME, text="HANS", start=0, end=4, confidence=0.8, detector="presidio"),
        ]
        response = '[{"text": "hans", "is_pii": true, "confidence": 0.9, "reason": "Name"}]'
        results = validator._parse_sentence_response(response, matches)

        assert len(results) == 1
        assert results[0][1].confidence == 0.9  # Should match despite case difference
