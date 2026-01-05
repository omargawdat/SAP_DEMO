"""Pydantic models for API requests and responses."""

from typing import Literal

from pydantic import BaseModel, Field

StrategyType = Literal["redaction", "masking", "hashing"]
ClaudeModelType = Literal["haiku", "sonnet", "opus"]


class MatchInput(BaseModel):
    """Input schema for specifying a match to anonymize."""

    type: str = Field(
        ...,
        description="PII type to apply (EMAIL, PHONE, etc.)",
        examples=["EMAIL"],
    )
    start: int = Field(
        ...,
        description="Start position (character index) in the text",
        ge=0,
        examples=[8],
    )
    end: int = Field(
        ...,
        description="End position (character index) in the text",
        ge=0,
        examples=[20],
    )


class PIIMatchSchema(BaseModel):
    """Schema for a single PII match."""

    type: str = Field(
        ...,
        description="Type of PII detected (EMAIL, PHONE, IBAN, etc.)",
        examples=["EMAIL"],
    )
    text: str = Field(
        ...,
        description="The actual PII text that was detected",
        examples=["hans@sap.com"],
    )
    start: int = Field(
        ...,
        description="Start position (character index) in the original text",
        examples=[8],
    )
    end: int = Field(
        ...,
        description="End position (character index) in the original text",
        examples=[20],
    )
    confidence: float = Field(
        ...,
        description="Confidence score of the detection (0.0 to 1.0)",
        ge=0.0,
        le=1.0,
        examples=[1.0],
    )
    detector: str = Field(
        ...,
        description="Name of the detector that found this match",
        examples=["email"],
    )
    review_required: bool = Field(
        ...,
        description="Whether this match needs manual review (confidence below threshold)",
        examples=[False],
    )
    llm_reason: str | None = Field(
        default=None,
        description="LLM explanation for the validation (only present if use_llm=true)",
        examples=["This is a personal email address format"],
    )

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "type": "EMAIL",
                    "text": "hans@sap.com",
                    "start": 8,
                    "end": 20,
                    "confidence": 1.0,
                    "detector": "email",
                    "review_required": False,
                    "llm_reason": None,
                }
            ]
        }
    }


class SummarySchema(BaseModel):
    """Summary statistics for detection results."""

    pii_found: bool = Field(
        ...,
        description="Whether any PII was detected in the text",
        examples=[True],
    )
    total_count: int = Field(
        ...,
        description="Total number of PII instances found",
        examples=[2],
    )
    by_type: dict[str, int] = Field(
        ...,
        description="Count of PII instances grouped by type",
        examples=[{"EMAIL": 2, "PHONE": 1}],
    )


class DetectRequest(BaseModel):
    """Request body for /detect endpoint."""

    text: str = Field(
        ...,
        min_length=1,
        description="Text to analyze for PII. Can be any length.",
        examples=["Contact hans@sap.com or anna@sap.de for support."],
    )
    use_llm: bool = Field(
        default=False,
        description="Use LLM (Claude) to validate low-confidence detections. Requires ANTHROPIC_API_KEY.",
        examples=[False],
    )
    llm_model: ClaudeModelType = Field(
        default="haiku",
        description="Claude model to use for LLM validation. haiku=fast/cheap, sonnet=balanced, opus=most capable.",
        examples=["haiku"],
    )

    model_config = {
        "json_schema_extra": {
            "examples": [
                {"text": "Contact hans@sap.com for support."},
                {"text": "My email is test@example.com and phone is +49 123 456789", "use_llm": True, "llm_model": "sonnet"},
            ]
        }
    }


class DetectResponse(BaseModel):
    """Response body for /detect endpoint."""

    matches: list[PIIMatchSchema] = Field(
        ...,
        description="List of all PII matches found in the text",
    )
    summary: SummarySchema = Field(
        ...,
        description="Summary statistics of the detection results",
    )
    processing_time_ms: float = Field(
        ...,
        description="Time taken to process the request in milliseconds",
        examples=[1.5],
    )


class AnonymizeRequest(BaseModel):
    """Request body for /anonymize endpoint.

    Use this endpoint to apply anonymization to specific matches.
    First call /detect to get matches, then pass confirmed ones here.
    """

    text: str = Field(
        ...,
        min_length=1,
        description="Text containing PII to be anonymized",
        examples=["Contact hans@sap.com for help."],
    )
    matches: list[MatchInput] = Field(
        ...,
        min_length=1,
        description="List of matches to anonymize. Get these from /detect endpoint, then pass the ones you want to anonymize.",
        examples=[[{"type": "EMAIL", "start": 8, "end": 20}]],
    )
    strategy: StrategyType = Field(
        default="redaction",
        description="De-identification strategy to apply",
        examples=["redaction"],
    )

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "text": "Contact hans@sap.com for help.",
                    "matches": [{"type": "EMAIL", "start": 8, "end": 20}],
                    "strategy": "redaction",
                },
            ]
        }
    }


class AnonymizeResponse(BaseModel):
    """Response body for /anonymize endpoint."""

    original_text: str = Field(
        ...,
        description="The original input text before anonymization",
        examples=["Contact hans@sap.com for help."],
    )
    processed_text: str = Field(
        ...,
        description="The anonymized text with PII replaced/masked",
        examples=["Contact [EMAIL] for help."],
    )
    matches: list[PIIMatchSchema] = Field(
        ...,
        description="List of all PII matches that were anonymized",
    )
    summary: SummarySchema = Field(
        ...,
        description="Summary statistics of what was anonymized",
    )
    processing_time_ms: float = Field(
        ...,
        description="Time taken to process the request in milliseconds",
        examples=[2.3],
    )


class ProcessRequest(BaseModel):
    """Request body for /process endpoint.

    One-shot endpoint that detects and anonymizes PII in a single call.
    Use this for batch/automated processing when manual review is not needed.
    """

    text: str = Field(
        ...,
        min_length=1,
        description="Text to process (detect and anonymize PII)",
        examples=["Contact hans@sap.com for help."],
    )
    strategy: StrategyType = Field(
        default="redaction",
        description="De-identification strategy to apply",
        examples=["redaction"],
    )
    min_confidence: float = Field(
        default=0.0,
        ge=0.0,
        le=1.0,
        description="Minimum confidence threshold. Only matches with confidence >= this value will be anonymized. Set to 0 to anonymize all detected PII.",
        examples=[0.85],
    )

    model_config = {
        "json_schema_extra": {
            "examples": [
                {"text": "Contact hans@sap.com for help."},
                {"text": "Contact hans@sap.com", "strategy": "redaction", "min_confidence": 0.85},
            ]
        }
    }


class ProcessResponse(BaseModel):
    """Response body for /process endpoint."""

    original_text: str = Field(
        ...,
        description="The original input text before processing",
        examples=["Contact hans@sap.com for help."],
    )
    processed_text: str = Field(
        ...,
        description="The anonymized text with PII replaced/masked",
        examples=["Contact [EMAIL] for help."],
    )
    matches: list[PIIMatchSchema] = Field(
        ...,
        description="List of all PII matches that were anonymized",
    )
    summary: SummarySchema = Field(
        ...,
        description="Summary statistics of what was processed",
    )
    processing_time_ms: float = Field(
        ...,
        description="Time taken to process the request in milliseconds",
        examples=[2.3],
    )


class HealthResponse(BaseModel):
    """Response body for /health endpoint."""

    status: str = Field(
        ...,
        description="Current health status of the service",
        examples=["healthy"],
    )
    version: str = Field(
        ...,
        description="API version number",
        examples=["0.1.0"],
    )