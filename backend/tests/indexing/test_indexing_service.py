import pytest

from nexusdocs.indexing.domain.models import (
    SearchResult,
    VectorDocument,
)
from nexusdocs.indexing.service import IndexingService
from nexusdocs.ingestion.domain.models import DocumentChunk


class FakeEmbeddingProvider:
    def embed_text(
        self,
        text: str,
    ) -> tuple[float, ...]:
        return (float(len(text)),)

    def embed_documents(
        self,
        texts: tuple[str, ...],
    ) -> tuple[tuple[float, ...], ...]:
        return tuple(self.embed_text(text) for text in texts)


class FakeVectorStore:
    def __init__(self) -> None:
        self.documents: tuple[VectorDocument, ...] = ()

    def add(
        self,
        documents: tuple[VectorDocument, ...],
    ) -> None:
        self.documents += documents

    def search(
        self,
        query_vector: tuple[float, ...],
        limit: int = 5,
    ) -> tuple[SearchResult, ...]:
        return ()

    def delete_by_document_id(
        self,
        document_id: str,
    ) -> None:
        self.documents = tuple(
            document
            for document in self.documents
            if document.document_id != document_id
        )


def test_indexing_service_generates_and_stores_vectors() -> None:
    provider = FakeEmbeddingProvider()
    store = FakeVectorStore()

    service = IndexingService(
        embedding_provider=provider,
        vector_store=store,
    )

    chunks = (
        DocumentChunk(
            chunk_id="KB-007:0",
            document_id="KB-007",
            text="Architecture",
            index=0,
            metadata={
                "classification": "CONFIDENTIAL",
            },
        ),
        DocumentChunk(
            chunk_id="KB-007:1",
            document_id="KB-007",
            text="Kafka integration",
            index=1,
            metadata={
                "classification": "CONFIDENTIAL",
            },
        ),
    )

    documents = service.index(chunks)

    assert len(documents) == 2
    assert len(store.documents) == 2

    assert documents[0].chunk_id == "KB-007:0"
    assert documents[0].vector == (12.0,)
    assert documents[0].metadata == {
        "classification": "CONFIDENTIAL",
    }

    assert documents[1].chunk_id == "KB-007:1"
    assert documents[1].vector == (17.0,)


def test_indexing_service_returns_empty_result_for_no_chunks() -> None:
    service = IndexingService(
        embedding_provider=FakeEmbeddingProvider(),
        vector_store=FakeVectorStore(),
    )

    result = service.index(())

    assert result == ()


class InvalidEmbeddingProvider:
    def embed_text(
        self,
        text: str,
    ) -> tuple[float, ...]:
        return (1.0,)

    def embed_documents(
        self,
        texts: tuple[str, ...],
    ) -> tuple[tuple[float, ...], ...]:
        return ((1.0,),)


def test_indexing_service_rejects_embedding_count_mismatch() -> None:
    service = IndexingService(
        embedding_provider=InvalidEmbeddingProvider(),
        vector_store=FakeVectorStore(),
    )

    chunks = (
        DocumentChunk(
            chunk_id="KB-001:0",
            document_id="KB-001",
            text="First chunk",
            index=0,
        ),
        DocumentChunk(
            chunk_id="KB-001:1",
            document_id="KB-001",
            text="Second chunk",
            index=1,
        ),
    )

    with pytest.raises(
        ValueError,
        match="different number",
    ):
        service.index(chunks)


class InconsistentDimensionEmbeddingProvider:
    def embed_text(
        self,
        text: str,
    ) -> tuple[float, ...]:
        return (1.0,)

    def embed_documents(
        self,
        texts: tuple[str, ...],
    ) -> tuple[tuple[float, ...], ...]:
        return (
            (0.1, 0.2, 0.3),
            (0.4, 0.5),
        )


def test_indexing_service_rejects_inconsistent_vector_dimensions() -> None:
    service = IndexingService(
        embedding_provider=InconsistentDimensionEmbeddingProvider(),
        vector_store=FakeVectorStore(),
    )

    chunks = (
        DocumentChunk(
            chunk_id="KB-001:0",
            document_id="KB-001",
            text="First chunk",
            index=0,
        ),
        DocumentChunk(
            chunk_id="KB-001:1",
            document_id="KB-001",
            text="Second chunk",
            index=1,
        ),
    )

    with pytest.raises(
        ValueError,
        match="inconsistent dimensions",
    ):
        service.index(chunks)


class EmptyVectorEmbeddingProvider:
    def embed_text(
        self,
        text: str,
    ) -> tuple[float, ...]:
        return ()

    def embed_documents(
        self,
        texts: tuple[str, ...],
    ) -> tuple[tuple[float, ...], ...]:
        return tuple(() for _ in texts)


def test_indexing_service_rejects_empty_vectors() -> None:
    service = IndexingService(
        embedding_provider=EmptyVectorEmbeddingProvider(),
        vector_store=FakeVectorStore(),
    )

    chunks = (
        DocumentChunk(
            chunk_id="KB-001:0",
            document_id="KB-001",
            text="Knowledge",
            index=0,
        ),
    )

    with pytest.raises(
        ValueError,
        match="empty vectors",
    ):
        service.index(chunks)
