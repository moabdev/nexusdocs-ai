from typing import Protocol

from nexusdocs.indexing.domain.models import SearchResult


class RetrievalProvider(Protocol):
    """Contract implemented by retrieval services."""

    def retrieve(
        self,
        question: str,
    ) -> tuple[SearchResult, ...]:
        """Retrieve relevant document chunks for a question."""
        ...
