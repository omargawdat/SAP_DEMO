"""Text processor - orchestrates detection and de-identification."""

import time

from pii_shield.core import PIIMatch
from pii_shield.detectors.base import Detector
from pii_shield.pipeline.report import ProcessingReport
from pii_shield.strategies.base import Strategy


class TextProcessor:
    """Orchestrates PII detection and de-identification."""

    def __init__(
        self,
        detectors: list[Detector],
        strategy: Strategy | None = None,
    ):
        """Initialize processor with detectors and optional strategy.

        Args:
            detectors: List of detectors to run.
            strategy: De-identification strategy. If None, detection only.
        """
        self.detectors = detectors
        self.strategy = strategy

    def process(self, text: str) -> ProcessingReport:
        """Process text through detection and optional de-identification.

        Args:
            text: Input text to process.

        Returns:
            ProcessingReport with results.
        """
        start_time = time.perf_counter()

        # Run all detectors
        all_matches: list[PIIMatch] = []
        for detector in self.detectors:
            matches = detector.detect(text)
            all_matches.extend(matches)

        # Remove duplicates and sort by position
        unique_matches = self._deduplicate_matches(all_matches)

        # Apply strategy if provided
        if self.strategy and unique_matches:
            processed_text = self.strategy.apply(text, unique_matches)
        else:
            processed_text = text

        elapsed_ms = (time.perf_counter() - start_time) * 1000

        return ProcessingReport(
            original_text=text,
            processed_text=processed_text,
            matches=unique_matches,
            processing_time_ms=elapsed_ms,
        )

    def _deduplicate_matches(self, matches: list[PIIMatch]) -> list[PIIMatch]:
        """Remove duplicate matches at same position.

        When multiple detectors find the same PII, keep the one
        with highest confidence.
        """
        if not matches:
            return []

        # Group by (start, end) position
        by_position: dict[tuple[int, int], PIIMatch] = {}
        for match in matches:
            key = (match.start, match.end)
            if key not in by_position or match.confidence > by_position[key].confidence:
                by_position[key] = match

        # Sort by start position
        return sorted(by_position.values(), key=lambda m: m.start)
