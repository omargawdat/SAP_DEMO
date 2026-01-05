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
from pii_shield.detectors.llm_validator import LLMValidator
from pii_shield.pipeline import TextProcessor
from pii_shield.strategies import HashingStrategy, MaskingStrategy, RedactionStrategy

router = APIRouter(prefix="/api/v1")

# LLM validators cache (by model)
_llm_validators: dict[str, LLMValidator] = {}


def get_llm_validator(model: str = "haiku") -> LLMValidator:
    """Get or create LLM validator instance for the specified model."""
    global _llm_validators
    if model not in _llm_validators:
        _llm_validators[model] = LLMValidator(model=model)
    return _llm_validators[model]


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
    "redaction": RedactionStrategy(),  # [EMAIL] - complete removal
    "hashing": HashingStrategy(),  # a3f2b1c4... - pseudonymization
    "masking": MaskingStrategy(),  # han***com - partial visibility
}

# Default confidence threshold for review_required flag and LLM validation
REVIEW_CONFIDENCE_THRESHOLD = 0.90


def _build_match_schemas(
    matches: list,
    confidence_threshold: float = REVIEW_CONFIDENCE_THRESHOLD,
    llm_reasons: dict[int, str] | None = None,
    original_confidences: dict[int, float] | None = None,
    llm_validated_indices: set[int] | None = None,
    llm_rejected_indices: set[int] | None = None,
) -> list[PIIMatchSchema]:
    """Convert PIIMatch objects to Pydantic schemas."""
    llm_reasons = llm_reasons or {}
    original_confidences = original_confidences or {}
    llm_validated_indices = llm_validated_indices or set()
    llm_rejected_indices = llm_rejected_indices or set()
    return [
        PIIMatchSchema(
            type=m.type.value,
            text=m.text,
            start=m.start,
            end=m.end,
            confidence=m.confidence,
            detector=m.detector,
            review_required=m.confidence < confidence_threshold and i not in llm_rejected_indices,
            llm_reason=llm_reasons.get(i),
            original_confidence=original_confidences.get(i),
            llm_validated=i in llm_validated_indices,
            llm_rejected=i in llm_rejected_indices,
        )
        for i, m in enumerate(matches)
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
- Phone numbers (German formats)
- IBAN numbers (with checksum validation)
- German ID numbers (Personalausweis)
- Credit card numbers (with Luhn validation)
- IP addresses (IPv4 and IPv6)
- Names and addresses (via ML/NER)

**LLM Enhancement:**
Set `use_llm: true` to validate low-confidence detections using Claude AI.
This improves accuracy by distinguishing personal names from business names, etc.
Requires ANTHROPIC_API_KEY environment variable.

Returns a list of all detected PII with their positions and confidence scores.
Does NOT modify the original text.
""",
    response_description="Detection results with all found PII matches",
)
async def detect_pii(request: DetectRequest) -> DetectResponse:
    """Detect PII in text without de-identification."""
    start_time = time.perf_counter()

    processor = TextProcessor(detectors=DETECTORS, strategy=None)
    report = processor.process(request.text)

    llm_reasons: dict[int, str] = {}
    original_confidences: dict[int, float] = {}
    llm_validated_indices: set[int] = set()
    llm_rejected_indices: set[int] = set()
    final_matches = list(report.matches)

    # Apply LLM validation if requested (sentence-based batching)
    if request.use_llm:
        validator = get_llm_validator(model=request.llm_model)
        if validator.is_available:
            # Store original confidences before LLM validation
            original_match_confidences = {i: m.confidence for i, m in enumerate(report.matches)}

            # Validate low-confidence matches using sentence-based approach
            results = validator.validate_low_confidence(
                request.text, list(report.matches), threshold=request.llm_threshold
            )

            all_matches = []
            for i, (match, validation) in enumerate(results):
                # Store original confidence
                original_confidences[i] = original_match_confidences.get(i, match.confidence)
                llm_reasons[i] = validation.reason

                # Check if LLM actually validated (not auto-approved)
                was_llm_validated = "auto-approved" not in validation.reason.lower()

                if validation.is_pii:
                    # Match confirmed as PII
                    if was_llm_validated:
                        llm_validated_indices.add(i)

                    detector_name = f"{match.detector}+llm" if was_llm_validated else match.detector
                    updated_match = PIIMatch(
                        type=match.type,
                        text=match.text,
                        start=match.start,
                        end=match.end,
                        confidence=validation.confidence,
                        detector=detector_name,
                    )
                    all_matches.append(updated_match)
                else:
                    # Match rejected by LLM - keep it but mark as rejected
                    llm_validated_indices.add(i)
                    llm_rejected_indices.add(i)

                    rejected_match = PIIMatch(
                        type=match.type,
                        text=match.text,
                        start=match.start,
                        end=match.end,
                        confidence=0.0,  # Set to 0 since rejected
                        detector=f"{match.detector}+llm",
                    )
                    all_matches.append(rejected_match)

            final_matches = all_matches

    elapsed_ms = (time.perf_counter() - start_time) * 1000

    # Rebuild summary for non-rejected matches only
    by_type: dict[str, int] = {}
    non_rejected_count = 0
    for i, m in enumerate(final_matches):
        if i not in llm_rejected_indices:
            by_type[m.type.value] = by_type.get(m.type.value, 0) + 1
            non_rejected_count += 1

    return DetectResponse(
        matches=_build_match_schemas(
            final_matches,
            llm_reasons=llm_reasons,
            original_confidences=original_confidences,
            llm_validated_indices=llm_validated_indices,
            llm_rejected_indices=llm_rejected_indices,
        ),
        summary=SummarySchema(
            pii_found=non_rejected_count > 0,
            total_count=non_rejected_count,
            by_type=by_type,
        ),
        processing_time_ms=elapsed_ms,
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
                    "example": {"detail": "Unknown strategy: invalid. Available: ['redaction']"}
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
                    "example": {"detail": "Unknown strategy: invalid. Available: ['redaction']"}
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
    filtered_matches = [m for m in report.matches if m.confidence >= request.min_confidence]

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
