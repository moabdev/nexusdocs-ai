from typing import Protocol


class LLMProvider(Protocol):
    """Contract implemented by language model providers."""

    def generate(
        self,
        *,
        question: str,
        context: str,
    ) -> str:
        """Generate an answer grounded in the provided context."""
        ...
