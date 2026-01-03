"""Shared pytest fixtures."""

import pytest


@pytest.fixture
def sample_text_with_pii() -> str:
    """Sample text containing various PII types for testing."""
    return """
    Contact: john.doe@example.com
    Phone: +49 170 1234567
    IBAN: DE89370400440532013000
    ID: L01X00T471
    Card: 4111111111111111
    IP: 192.168.1.100
    """
