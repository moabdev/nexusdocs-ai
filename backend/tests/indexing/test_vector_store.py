from nexusdocs.indexing.domain.models import (
    SearchResult,
    VectorDocument,
)
from nexusdocs.indexing.vectorstores.base import VectorStore


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
        return tuple(
            SearchResult(
                chunk_id=document.chunk_id,
                document_id=document.document_id,
                text=document.text,
                score=1.0,
                metadata=document.metadata,
            )
            for document in self.documents[:limit]
        )

    def delete_by_document_id(
        self,
        document_id: str,
    ) -> None:
        self.documents = tuple(
            document
            for document in self.documents
            if document.document_id != document_id
        )


def test_fake_vector_store_satisfies_protocol() -> None:
    store: VectorStore = FakeVectorStore()

    document = VectorDocument(
        chunk_id="KB-007:0",
        document_id="KB-007",
        text="Velox Logistics architecture.",
        vector=(0.1, 0.2, 0.3),
    )

    store.add((document,))

    results = store.search(
        query_vector=(0.1, 0.2, 0.3),
    )

    assert len(results) == 1
    assert results[0].chunk_id == "KB-007:0"


def test_vector_store_can_delete_document_vectors() -> None:
    store = FakeVectorStore()

    store.add(
        (
            VectorDocument(
                chunk_id="KB-007:0",
                document_id="KB-007",
                text="Architecture.",
                vector=(0.1, 0.2),
            ),
            VectorDocument(
                chunk_id="KB-008:0",
                document_id="KB-008",
                text="Delivery performance.",
                vector=(0.3, 0.4),
            ),
        )
    )

    store.delete_by_document_id("KB-007")

    assert len(store.documents) == 1
    assert store.documents[0].document_id == "KB-008"
