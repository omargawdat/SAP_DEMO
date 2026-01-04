"""API route handlers."""

import time

from fastapi import APIRouter, HTTPException

from pii_shield.api.models import (
    AnonymizeRequest,
    AnonymizeResponse,
    DetectRequest,
    DetectResponse,
    HealthResponse,
    PIIMatchSchema,
    ProcessRequest,
    ProcessResponse,
    SummarySchema,
)
from pii_shield.core import PIIMatch
from pii_shield.core.types import PIIType
from pii_shield.detectors import (
    CreditCardDetector,
    EmailDetector,
    GermanIDDetector,
    IBANDetector,
    IPAddressDetector,
    PhoneDetector,
    PresidioDetector,
)
from pii_shield.pipeline import TextProcessor
from pii_shield.strategies import RedactionStrategy

router = APIRouter(prefix="/api/v1")

# Available detectors
DETECTORS = [
    # Rule-based detectors (fast, high precision)
    EmailDetector(),
    PhoneDetector(),
    IBANDetector(),
    GermanIDDetector(),
    CreditCardDetector(),
    IPAddressDetector(),
    # ML-based detector (NER for names, addresses)
    PresidioDetector(language="de"),
]

# Available strategies
STRATEGIES = {
    "redaction": RedactionStrategy(),
}

# Default confidence threshold for review_required flag
REVIEW_CONFIDENCE_THRESHOLD = 0.85


def _build_match_schemas(
    matches: list, confidence_threshold: float = REVIEW_CONFIDENCE_THRESHOLD
) -> list[PIIMatchSchema]:
    """Convert PIIMatch objects to Pydantic schemas."""
    return [
        PIIMatchSchema(
            type=m.type.value,
            text=m.text,
            start=m.start,
            end=m.end,
            confidence=m.confidence,
            detector=m.detector,
            review_required=m.confidence < confidence_threshold,
        )
        for m in matches
    ]


def _build_summary(report) -> SummarySchema:
    """Build summary schema from report."""
    return SummarySchema(
        pii_found=report.pii_found,
        total_count=report.pii_count,
        by_type={k.value: v for k, v in report.count_by_type().items()},
    )


@router.post(
    "/detect",
    response_model=DetectResponse,
    tags=["PII Detection"],
    summary="Detect PII in text",
    description="""
Analyze text to find all Personally Identifiable Information (PII).

**Supported PII types:**
- Email addresses
- Phone numbers (coming soon)
- IBAN numbers (coming soon)
- German ID numbers (coming soon)

Returns a list of all detected PII with their positions and confidence scores.
Does NOT modify the original text.
""",
    response_description="Detection results with all found PII matches",
)
async def detect_pii(request: DetectRequest) -> DetectResponse:
    """Detect PII in text without de-identification."""
    processor = TextProcessor(detectors=DETECTORS, strategy=None)
    report = processor.process(request.text)

    return DetectResponse(
        matches=_build_match_schemas(report.matches),
        summary=_build_summary(report),
        processing_time_ms=report.processing_time_ms,
    )


@router.post(
    "/anonymize",
    response_model=AnonymizeResponse,
    tags=["PII Anonymization"],
    summary="Anonymize specific matches in text",
    description="""
Apply de-identification strategy to specific matches. **Does not perform detection.**

**Workflow:**
1. First call `/detect` to get PII matches with confidence scores
2. Review matches (especially those with `review_required: true`)
3. Call this endpoint with the matches you want to anonymize

**Available strategies:**
- `redaction`: Replace PII with type placeholders like `[EMAIL]`, `[PHONE]`
- `masking`: Partially hide PII (e.g., `h***@sap.com`) - coming soon
- `hashing`: Replace with consistent hash for pseudonymization - coming soon

For one-shot detection + anonymization, use `/process` instead.
""",
    response_description="Anonymization results with original and processed text",
    responses={
        400: {
            "description": "Unknown strategy specified",
            "content": {
                "application/json": {
                    "example": {
                        "detail": "Unknown strategy: invalid. Available: ['redaction']"
                    }
                }
            },
        }
    },
)
async def anonymize_text(request: AnonymizeRequest) -> AnonymizeResponse:
    """Apply anonymization strategy to specified matches."""
    start_time = time.perf_counter()

    strategy = STRATEGIES.get(request.strategy)
    if strategy is None:
        raise HTTPException(
            status_code=400,
            detail=f"Unknown strategy: {request.strategy}. Available: {list(STRATEGIES.keys())}",
        )

    # Convert input matches to PIIMatch objects
    matches = [
        PIIMatch(
            type=PIIType(m.type),
            text=request.text[m.start : m.end],
            start=m.start,
            end=m.end,
            confidence=1.0,  # User confirmed = full confidence
            detector="manual",
        )
        for m in request.matches
    ]

    # Apply strategy
    processed_text = strategy.apply(request.text, matches)
    elapsed_ms = (time.perf_counter() - start_time) * 1000

    # Build summary
    by_type: dict[str, int] = {}
    for m in matches:
        by_type[m.type.value] = by_type.get(m.type.value, 0) + 1

    return AnonymizeResponse(
        original_text=request.text,
        processed_text=processed_text,
        matches=_build_match_schemas(matches),
        summary=SummarySchema(
            pii_found=len(matches) > 0,
            total_count=len(matches),
            by_type=by_type,
        ),
        processing_time_ms=elapsed_ms,
    )


@router.post(
    "/process",
    response_model=ProcessResponse,
    tags=["Full Pipeline"],
    summary="Detect and anonymize PII in one call",
    description="""
One-shot endpoint that detects and anonymizes PII in a single call.

**Use this for:**
- Batch processing
- Automated pipelines
- When manual review is not required

**Available strategies:**
- `redaction`: Replace PII with type placeholders like `[EMAIL]`, `[PHONE]`
- `masking`: Partially hide PII (e.g., `h***@sap.com`) - coming soon
- `hashing`: Replace with consistent hash for pseudonymization - coming soon

**Confidence filtering:**
Use `min_confidence` to only anonymize high-confidence matches. Set to 0 (default) to anonymize all detected PII.

For manual review workflow, use `/detect` + `/anonymize` instead.
""",
    response_description="Processed text with all detected PII anonymized",
    responses={
        400: {
            "description": "Unknown strategy specified",
            "content": {
                "application/json": {
                    "example": {
                        "detail": "Unknown strategy: invalid. Available: ['redaction']"
                    }
                }
            },
        }
    },
)
async def process_text(request: ProcessRequest) -> ProcessResponse:
    """Detect and anonymize PII in a single call."""
    start_time = time.perf_counter()

    strategy = STRATEGIES.get(request.strategy)
    if strategy is None:
        raise HTTPException(
            status_code=400,
            detail=f"Unknown strategy: {request.strategy}. Available: {list(STRATEGIES.keys())}",
        )

    # Run detection
    processor = TextProcessor(detectors=DETECTORS, strategy=None)
    report = processor.process(request.text)

    # Filter matches by confidence threshold
    filtered_matches = [
        m for m in report.matches if m.confidence >= request.min_confidence
    ]

    # Apply strategy to filtered matches
    if filtered_matches:
        processed_text = strategy.apply(request.text, filtered_matches)
    else:
        processed_text = request.text

    elapsed_ms = (time.perf_counter() - start_time) * 1000

    # Build summary for filtered matches
    by_type: dict[str, int] = {}
    for m in filtered_matches:
        by_type[m.type.value] = by_type.get(m.type.value, 0) + 1

    return ProcessResponse(
        original_text=request.text,
        processed_text=processed_text,
        matches=_build_match_schemas(filtered_matches),
        summary=SummarySchema(
            pii_found=len(filtered_matches) > 0,
            total_count=len(filtered_matches),
            by_type=by_type,
        ),
        processing_time_ms=elapsed_ms,
    )


@router.get(
    "/health",
    response_model=HealthResponse,
    tags=["System"],
    summary="Health check",
    description="Check if the API service is running and healthy. Use for monitoring and load balancer health checks.",
    response_description="Service health status",
)
async def health_check() -> HealthResponse:
    """Health check endpoint."""
    return HealthResponse(status="healthy", version="0.1.0")
