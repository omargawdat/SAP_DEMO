"""Base class for text preprocessors."""

from abc import ABC, abstractmethod


class Preprocessor(ABC):
    """Abstract base class for text preprocessing."""

    @abstractmethod
    def process(self, text: str) -> str:
        """Process text and return the result."""
        pass
