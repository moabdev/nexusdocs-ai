from typing import Protocol

from nexusdocs.indexing.domain.models import SearchResult


class RetrievalProvider(Protocol):
    """Contract implemented by retrieval providers."""

    def retrieve(
        self,
        question: str,
    ) -> tuple[SearchResult, ...]:
        """Retrieve relevant knowledge-base chunks for a question."""
        ...
