"""Presidio-based NER detector for names, addresses, and other context-dependent PII."""

from pii_shield.core import PIIMatch, PIIType
from pii_shield.detectors.base import Detector

# Presidio/spaCy may not be available on all Python versions (3.14+ has issues)
try:
    from presidio_analyzer import AnalyzerEngine
    from presidio_analyzer.nlp_engine import NlpEngineProvider

    PRESIDIO_AVAILABLE = True
except (ImportError, Exception):
    # Catch all exceptions - spaCy/pydantic compatibility issues on Python 3.14+
    PRESIDIO_AVAILABLE = False
    AnalyzerEngine = None
    NlpEngineProvider = None


class PresidioDetector(Detector):
    """Detect PII using Microsoft Presidio with spaCy NER.

    This detector uses machine learning (NER) to find PII that
    regex-based detectors cannot reliably detect:
    - Person names (Hans Müller, Angela Schmidt)
    - Addresses (Hauptstraße 123, 10115 Berlin)
    - Dates in context (born on 15.03.1990)

    Runs 100% locally - no data leaves the processing environment.
    """

    # Map Presidio entity types to our PIIType enum
    ENTITY_MAPPING = {
        "PERSON": PIIType.NAME,
        "EMAIL_ADDRESS": PIIType.EMAIL,
        "PHONE_NUMBER": PIIType.PHONE,
        "IBAN_CODE": PIIType.IBAN,
        "CREDIT_CARD": PIIType.CREDIT_CARD,
        "IP_ADDRESS": PIIType.IP_ADDRESS,
        "LOCATION": PIIType.ADDRESS,
        "DATE_TIME": PIIType.DATE_OF_BIRTH,
    }

    # Only detect these entities (skip ones our regex detectors handle better)
    ENTITIES_TO_DETECT = ["PERSON", "LOCATION", "DATE_TIME"]

    def __init__(self, language: str = "de"):
        """Initialize Presidio analyzer with spaCy German model.

        Args:
            language: Language code for NER model. Default "de" for German.
        """
        self.language = language
        self.analyzer = None

        if not PRESIDIO_AVAILABLE:
            return

        try:
            # Configure spaCy NLP engine
            configuration = {
                "nlp_engine_name": "spacy",
                "models": [{"lang_code": language, "model_name": f"{language}_core_news_sm"}],
            }

            provider = NlpEngineProvider(nlp_configuration=configuration)
            nlp_engine = provider.create_engine()

            self.analyzer = AnalyzerEngine(nlp_engine=nlp_engine, supported_languages=[language])
        except Exception:
            # Model not available - detector will return empty results
            pass

    def detect(self, text: str) -> list[PIIMatch]:
        """Find PII using NER-based detection.

        Args:
            text: Input text to analyze.

        Returns:
            List of detected PII matches.
        """
        if self.analyzer is None:
            return []

        results = self.analyzer.analyze(
            text=text,
            language=self.language,
            entities=self.ENTITIES_TO_DETECT,
        )

        matches = []
        for result in results:
            pii_type = self.ENTITY_MAPPING.get(result.entity_type)
            if pii_type is None:
                continue

            matches.append(
                PIIMatch(
                    type=pii_type,
                    text=text[result.start : result.end],
                    start=result.start,
                    end=result.end,
                    confidence=result.score,
                    detector="presidio",
                )
            )

        return matches
