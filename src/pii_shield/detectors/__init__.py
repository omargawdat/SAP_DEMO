"""PII detectors - rule-based and ML-powered."""

from pii_shield.detectors.base import Detector
from pii_shield.detectors.credit_card import CreditCardDetector
from pii_shield.detectors.email import EmailDetector
from pii_shield.detectors.german_id import GermanIDDetector
from pii_shield.detectors.iban import IBANDetector
from pii_shield.detectors.ip import IPAddressDetector
from pii_shield.detectors.phone import PhoneDetector
from pii_shield.detectors.presidio import PresidioDetector

__all__ = [
    "Detector",
    "CreditCardDetector",
    "EmailDetector",
    "GermanIDDetector",
    "IBANDetector",
    "IPAddressDetector",
    "PhoneDetector",
    "PresidioDetector",
]
