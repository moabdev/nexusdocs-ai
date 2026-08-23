from typing import Protocol

from nexusdocs.indexing.domain.models import (
    SearchResult,
    VectorDocument,
)


class VectorStore(Protocol):
    """Contract implemented by vector storage backends."""

    def add(
        self,
        documents: tuple[VectorDocument, ...],
    ) -> None:
        """Store vector documents."""
        ...

    def search(
        self,
        query_vector: tuple[float, ...],
        limit: int = 5,
    ) -> tuple[SearchResult, ...]:
        """Return documents ordered by vector similarity."""
        ...

    def delete_by_document_id(
        self,
        document_id: str,
    ) -> None:
        """Remove vectors associated with a document."""
        ...
