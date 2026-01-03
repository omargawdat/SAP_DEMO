from enum import Enum


class PIIType(str, Enum):
    """Types of Personally Identifiable Information that can be detected."""

    EMAIL = "EMAIL"
    PHONE = "PHONE"
    IBAN = "IBAN"
    CREDIT_CARD = "CREDIT_CARD"
    GERMAN_ID = "GERMAN_ID"  # Personalausweis
    IP_ADDRESS = "IP_ADDRESS"
    NAME = "NAME"
    ADDRESS = "ADDRESS"
    DATE_OF_BIRTH = "DATE_OF_BIRTH"
    UNKNOWN = "UNKNOWN"
