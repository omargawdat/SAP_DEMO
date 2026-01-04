"""API route handlers."""

from fastapi import APIRouter, HTTPException

from pii_shield.api.models import (
    AnonymizeRequest,
    AnonymizeResponse,
    DetectRequest,
    DetectResponse,
    HealthResponse,
    PIIMatchSchema,
    SummarySchema,
)
from pii_shield.detectors import EmailDetector
from pii_shield.pipeline import TextProcessor
from pii_shield.strategies import RedactionStrategy

router = APIRouter(prefix="/api/v1")

# Available detectors
DETECTORS = [EmailDetector()]

# Available strategies
STRATEGIES = {
    "redaction": RedactionStrategy(),
}


def _build_match_schemas(matches: list) -> list[PIIMatchSchema]:
    """Convert PIIMatch objects to Pydantic schemas."""
    return [
        PIIMatchSchema(
            type=m.type.value,
            text=m.text,
            start=m.start,
            end=m.end,
            confidence=m.confidence,
            detector=m.detector,
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
    summary="Anonymize PII in text",
    description="""
Detect and de-identify PII in text using the specified strategy.

**Available strategies:**
- `redaction`: Replace PII with type placeholders like `[EMAIL]`, `[PHONE]`
- `masking`: Partially hide PII (e.g., `h***@sap.com`) - coming soon
- `hashing`: Replace with consistent hash for pseudonymization - coming soon

Returns both the original and processed text, along with details of what was anonymized.
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
    """Detect and de-identify PII in text."""
    strategy = STRATEGIES.get(request.strategy)
    if strategy is None:
        raise HTTPException(
            status_code=400,
            detail=f"Unknown strategy: {request.strategy}. Available: {list(STRATEGIES.keys())}",
        )

    processor = TextProcessor(detectors=DETECTORS, strategy=strategy)
    report = processor.process(request.text)

    return AnonymizeResponse(
        original_text=report.original_text,
        processed_text=report.processed_text,
        matches=_build_match_schemas(report.matches),
        summary=_build_summary(report),
        processing_time_ms=report.processing_time_ms,
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
