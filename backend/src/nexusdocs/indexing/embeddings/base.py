from typing import Protocol


class EmbeddingProvider(Protocol):
    """Contract implemented by embedding providers."""

    def embed_text(
        self,
        text: str,
    ) -> tuple[float, ...]:
        """Generate an embedding for a single text."""
        ...

    def embed_documents(
        self,
        texts: tuple[str, ...],
    ) -> tuple[tuple[float, ...], ...]:
        """Generate embeddings for multiple documents."""
        ...
