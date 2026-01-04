"""Pydantic models for API requests and responses."""

from typing import Literal

from pydantic import BaseModel, Field

StrategyType = Literal["redaction", "masking", "hashing"]


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

    model_config = {
        "json_schema_extra": {
            "examples": [
                {"text": "Contact hans@sap.com for support."},
                {"text": "My email is test@example.com and phone is +49 123 456789"},
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
    """Request body for /anonymize endpoint."""

    text: str = Field(
        ...,
        min_length=1,
        description="Text containing PII to be anonymized",
        examples=["Contact hans@sap.com for help."],
    )
    strategy: StrategyType = Field(
        default="redaction",
        description="De-identification strategy to apply",
        examples=["redaction"],
    )

    model_config = {
        "json_schema_extra": {
            "examples": [
                {"text": "Contact hans@sap.com for help.", "strategy": "redaction"},
                {"text": "Email anna@company.de please.", "strategy": "redaction"},
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