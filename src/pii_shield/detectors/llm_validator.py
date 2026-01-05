"""LLM-based validator for low-confidence PII detections.

Cross-sentence batching approach:
1. Only validate LOW-confidence matches (high-confidence auto-approved)
2. Group matches by sentence
3. Batch multiple sentences into single API calls (BATCH_SIZE sentences per call)
4. Reduces API calls from N sentences to N/BATCH_SIZE calls
"""

import json
import logging
import os
from dataclasses import dataclass
from typing import Literal

from pii_shield.core.models import PIIMatch

logger = logging.getLogger(__name__)

# Claude model mapping: short name -> API model ID
CLAUDE_MODELS: dict[str, str] = {
    "haiku": "claude-haiku-4-5-20250929",
    "sonnet": "claude-sonnet-4-5-20250929",
    "opus": "claude-opus-4-5-20251101",
}

# Max sentences to batch per API call (reduces 26 calls to ~3 calls)
BATCH_SIZE = 10

ClaudeModelName = Literal["haiku", "sonnet", "opus"]


@dataclass
class ValidationResult:
    """Result of LLM validation."""

    is_pii: bool
    confidence: float
    reason: str


class LLMValidator:
    """Validates low-confidence PII detections using Claude API."""

    def __init__(
        self,
        api_key: str | None = None,
        model: ClaudeModelName = "haiku",
    ):
        """
        Initialize LLM validator.

        Args:
            api_key: Anthropic API key. If None, reads from ANTHROPIC_API_KEY env var.
            model: Claude model to use (haiku, sonnet, opus). Defaults to haiku for cost efficiency.
        """
        self.api_key = api_key or os.getenv("ANTHROPIC_API_KEY")
        self.model = CLAUDE_MODELS.get(model, CLAUDE_MODELS["haiku"])
        self._client = None

    @property
    def client(self):
        """Lazy initialization of Anthropic client."""
        if self._client is None:
            try:
                from anthropic import Anthropic

                self._client = Anthropic(
                    api_key=self.api_key,
                    timeout=30.0,
                )
            except ImportError:
                logger.warning("anthropic package not installed. LLM validation disabled.")
                return None
            except Exception as e:
                logger.warning(f"Failed to initialize Anthropic client: {e}")
                return None
        return self._client

    @property
    def is_available(self) -> bool:
        """Check if LLM validation is available."""
        return self.client is not None and self.api_key is not None

    def validate_low_confidence(
        self,
        text: str,
        matches: list[PIIMatch],
        threshold: float = 0.90,
    ) -> list[tuple[PIIMatch, ValidationResult]]:
        """
        Validate only low-confidence matches using sentence-based batching.

        Flow:
        1. Split matches by confidence threshold
        2. Auto-approve high-confidence matches
        3. Group low-confidence matches by sentence
        4. Send 1 API call per sentence
        5. Return all results merged

        Args:
            text: Full original text.
            matches: List of PII matches.
            threshold: Only validate matches below this confidence.

        Returns:
            List of (match, validation_result) tuples.
        """
        results = []

        # Split by confidence
        high_conf = [m for m in matches if m.confidence >= threshold]
        low_conf = [m for m in matches if m.confidence < threshold]

        # Auto-approve high confidence matches
        for match in high_conf:
            results.append((
                match,
                ValidationResult(
                    is_pii=True,
                    confidence=match.confidence,
                    reason="High confidence - auto-approved",
                ),
            ))

        # If no low-confidence matches or LLM unavailable, return early
        if not low_conf:
            return results

        if not self.is_available:
            for match in low_conf:
                results.append((
                    match,
                    ValidationResult(
                        is_pii=True,
                        confidence=match.confidence,
                        reason="LLM validation unavailable",
                    ),
                ))
            return results

        # Group low-confidence matches by sentence
        sentence_groups = self._group_by_sentence(text, low_conf)

        # Batch sentence groups for fewer API calls
        batches = [
            sentence_groups[i : i + BATCH_SIZE]
            for i in range(0, len(sentence_groups), BATCH_SIZE)
        ]

        # Validate each batch (1 API call per batch of ~10 sentences)
        for batch in batches:
            validations = self._validate_batch(batch)
            results.extend(validations)

        return results

    def _extract_sentence(self, text: str, match: PIIMatch) -> tuple[str, int]:
        """
        Extract the sentence containing the match.

        Returns:
            (sentence_text, sentence_start_offset)
        """
        sentence_enders = ".!?\n"

        # Find start of sentence
        start = match.start
        while start > 0 and text[start - 1] not in sentence_enders:
            start -= 1

        # Find end of sentence
        end = match.end
        while end < len(text) and text[end] not in sentence_enders:
            end += 1
        if end < len(text):
            end += 1  # Include the punctuation

        return text[start:end].strip(), start

    def _group_by_sentence(
        self, text: str, matches: list[PIIMatch]
    ) -> list[tuple[str, int, list[PIIMatch]]]:
        """
        Group matches by the sentence they appear in.

        Returns:
            List of (sentence, sentence_start, [matches_in_sentence])
        """
        groups: dict[str, tuple[int, list[PIIMatch]]] = {}

        for match in matches:
            sentence, sentence_start = self._extract_sentence(text, match)
            if sentence not in groups:
                groups[sentence] = (sentence_start, [])
            groups[sentence][1].append(match)

        return [(sent, start, match_list) for sent, (start, match_list) in groups.items()]

    def _validate_batch(
        self,
        batch: list[tuple[str, int, list[PIIMatch]]],
    ) -> list[tuple[PIIMatch, ValidationResult]]:
        """
        Validate multiple sentences in a single API call.

        Args:
            batch: List of (sentence, sentence_start, [matches]) tuples.

        Returns:
            List of (match, validation_result) tuples for all matches in batch.
        """
        # Collect all matches and build prompt with numbered sentences
        all_matches: list[PIIMatch] = []
        prompt_parts: list[str] = []

        for idx, (sentence, _, matches) in enumerate(batch):
            all_matches.extend(matches)
            items_desc = "\n".join(
                f'  - "{m.text}" (type: {m.type.value}, confidence: {m.confidence:.0%})'
                for m in matches
            )
            prompt_parts.append(f"SENTENCE_{idx + 1}: \"{sentence}\"\nITEMS_{idx + 1}:\n{items_desc}")

        sentences_text = "\n\n".join(prompt_parts)

        prompt = f"""Analyze these sentences for PII (Personal Identifiable Information):

{sentences_text}

For each detected item, determine if it is genuine PII identifying a specific individual.
Consider: Could this be a business name, street name, product name, or non-personal reference?

Respond with a JSON array containing one object per detected item (across ALL sentences):
[
  {{"text": "Hans Müller", "is_pii": true, "confidence": 0.95, "reason": "Personal name"}},
  {{"text": "SAP", "is_pii": false, "confidence": 0.1, "reason": "Company name"}}
]

Return ONLY the JSON array, no markdown. Include results for every detected item."""

        # Log the prompt being sent to LLM
        logger.info(f"LLM Prompt ({len(all_matches)} items in {len(batch)} sentences):\n{prompt}")

        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=150 * len(all_matches),  # ~150 tokens per match response
                temperature=0,
                messages=[{"role": "user", "content": prompt}],
            )
            response_text = response.content[0].text
            logger.info(f"LLM Response:\n{response_text}")
            return self._parse_batch_response(response_text, all_matches)

        except Exception as e:
            logger.warning(f"Batch LLM validation failed: {e}")
            return [
                (m, ValidationResult(is_pii=True, confidence=m.confidence, reason=f"LLM error: {e}"))
                for m in all_matches
            ]

    def _parse_batch_response(
        self, response_text: str, matches: list[PIIMatch]
    ) -> list[tuple[PIIMatch, ValidationResult]]:
        """Parse LLM batch response into list of (match, ValidationResult) tuples."""
        try:
            # Handle markdown code blocks
            if "```" in response_text:
                start = response_text.find("[")
                end = response_text.rfind("]") + 1
                if start != -1 and end > start:
                    response_text = response_text[start:end]

            results_data = json.loads(response_text)

            # Match results to original matches by text (case-insensitive)
            results = []
            matched_texts = set()

            for match in matches:
                match_text_lower = match.text.lower()

                # Find result for this match by text
                result_data = next(
                    (r for r in results_data
                     if r.get("text", "").lower() == match_text_lower
                     and r.get("text", "").lower() not in matched_texts),
                    None,
                )

                if result_data:
                    matched_texts.add(result_data.get("text", "").lower())
                    results.append((
                        match,
                        ValidationResult(
                            is_pii=bool(result_data.get("is_pii", True)),
                            confidence=float(result_data.get("confidence", match.confidence)),
                            reason=str(result_data.get("reason", "No reason provided")),
                        ),
                    ))
                else:
                    # Fallback if match not found in response
                    results.append((
                        match,
                        ValidationResult(
                            is_pii=True,
                            confidence=match.confidence,
                            reason="Match not in LLM response",
                        ),
                    ))

            return results

        except (json.JSONDecodeError, KeyError, TypeError) as e:
            logger.warning(f"Failed to parse batch LLM response: {e}. Response: {response_text}")
            return [
                (m, ValidationResult(is_pii=True, confidence=m.confidence, reason="Failed to parse LLM response"))
                for m in matches
            ]

    def _validate_sentence(
        self,
        sentence: str,
        sentence_start: int,
        matches: list[PIIMatch],
    ) -> list[tuple[PIIMatch, ValidationResult]]:
        """
        Validate all matches in a single sentence with one API call.

        Args:
            sentence: The sentence text.
            sentence_start: Offset of sentence in original text.
            matches: List of matches within this sentence.

        Returns:
            List of (match, validation_result) tuples.
        """
        # Build match descriptions
        matches_desc = "\n".join([
            f"- \"{m.text}\" (detected as {m.type.value}, confidence: {m.confidence:.0%})"
            for m in matches
        ])

        prompt = f"""Analyze this sentence for PII (Personal Identifiable Information):

SENTENCE: "{sentence}"

DETECTED ITEMS:
{matches_desc}

For each item, determine if it is genuine PII identifying a specific individual.
Consider: Could this be a business name, street name, product name, or non-personal reference?

Respond with a JSON array (one object per detected item, in order):
[
  {{"text": "Hans Müller", "is_pii": true, "confidence": 0.95, "reason": "Personal name"}},
  {{"text": "SAP", "is_pii": false, "confidence": 0.1, "reason": "Company name"}}
]

Return ONLY the JSON array, no markdown."""

        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=100 * len(matches),
                temperature=0,
                messages=[{"role": "user", "content": prompt}],
            )
            return self._parse_sentence_response(response.content[0].text, matches)

        except Exception as e:
            logger.warning(f"Sentence LLM validation failed: {e}")
            return [
                (m, ValidationResult(is_pii=True, confidence=m.confidence, reason=f"LLM error: {e}"))
                for m in matches
            ]

    def _parse_sentence_response(
        self, response_text: str, matches: list[PIIMatch]
    ) -> list[tuple[PIIMatch, ValidationResult]]:
        """Parse LLM sentence response into list of (match, ValidationResult) tuples."""
        try:
            # Handle markdown code blocks
            if "```" in response_text:
                start = response_text.find("[")
                end = response_text.rfind("]") + 1
                if start != -1 and end > start:
                    response_text = response_text[start:end]

            results_data = json.loads(response_text)

            # Match results to original matches by text
            results = []
            for match in matches:
                # Find result for this match by text
                result_data = next(
                    (r for r in results_data if r.get("text", "").lower() == match.text.lower()),
                    None,
                )

                if result_data:
                    results.append((
                        match,
                        ValidationResult(
                            is_pii=bool(result_data.get("is_pii", True)),
                            confidence=float(result_data.get("confidence", match.confidence)),
                            reason=str(result_data.get("reason", "No reason provided")),
                        ),
                    ))
                else:
                    # Fallback if match not found in response
                    results.append((
                        match,
                        ValidationResult(
                            is_pii=True,
                            confidence=match.confidence,
                            reason="Match not in LLM response",
                        ),
                    ))

            return results

        except (json.JSONDecodeError, KeyError, TypeError) as e:
            logger.warning(f"Failed to parse sentence LLM response: {e}. Response: {response_text}")
            return [
                (m, ValidationResult(is_pii=True, confidence=m.confidence, reason="Failed to parse LLM response"))
                for m in matches
            ]

