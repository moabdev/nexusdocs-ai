from nexusdocs.indexing.domain.models import SearchResult
from nexusdocs.indexing.embeddings.base import EmbeddingProvider
from nexusdocs.indexing.vectorstores.base import VectorStore


class RetrievalService:
    """Retrieve relevant knowledge-base chunks for a question."""

    def __init__(
        self,
        embedding_provider: EmbeddingProvider,
        vector_store: VectorStore,
        *,
        limit: int = 5,
        score_threshold: float = 0.25,
    ) -> None:
        if limit <= 0:
            raise ValueError("limit must be greater than zero")

        if not 0.0 <= score_threshold <= 1.0:
            raise ValueError("score_threshold must be between zero and one")

        self._embedding_provider = embedding_provider
        self._vector_store = vector_store
        self._limit = limit
        self._score_threshold = score_threshold

    def retrieve(
        self,
        question: str,
    ) -> tuple[SearchResult, ...]:
        question = question.strip()

        if not question:
            raise ValueError("question cannot be empty")

        query_vector = self._embedding_provider.embed_text(question)

        if not query_vector:
            raise ValueError("Embedding provider returned an empty query vector")

        results = self._vector_store.search(
            query_vector=query_vector,
            limit=self._limit,
        )

        return tuple(
            result for result in results if result.score >= self._score_threshold
        )
