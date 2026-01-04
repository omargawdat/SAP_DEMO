"""PII detectors - rule-based and ML-powered."""

from pii_shield.detectors.base import Detector
from pii_shield.detectors.email import EmailDetector

__all__ = ["Detector", "EmailDetector"]
