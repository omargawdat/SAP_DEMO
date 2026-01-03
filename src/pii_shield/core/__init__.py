"""Core domain types and models."""

from pii_shield.core.types import PIIType
from pii_shield.core.models import PIIMatch, DetectionResult

__all__ = ["PIIType", "PIIMatch", "DetectionResult"]
