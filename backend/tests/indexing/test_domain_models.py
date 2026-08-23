from nexusdocs.indexing.domain.models import (
    SearchResult,
    VectorDocument,
)


def test_vector_document_stores_embedding_and_metadata() -> None:
    document = VectorDocument(
        chunk_id="KB-007:0",
        document_id="KB-007",
        text="Velox Logistics architecture.",
        vector=(0.12, -0.45, 0.78),
        metadata={
            "classification": "CONFIDENTIAL",
            "chunk_index": 0,
        },
    )

    assert document.chunk_id == "KB-007:0"
    assert document.document_id == "KB-007"
    assert document.text == "Velox Logistics architecture."
    assert document.vector == (0.12, -0.45, 0.78)
    assert document.metadata == {
        "classification": "CONFIDENTIAL",
        "chunk_index": 0,
    }


def test_vector_document_has_empty_metadata_by_default() -> None:
    document = VectorDocument(
        chunk_id="KB-001:0",
        document_id="KB-001",
        text="Knowledge content.",
        vector=(0.1, 0.2),
    )

    assert document.metadata == {}


def test_search_result_stores_similarity_score() -> None:
    result = SearchResult(
        chunk_id="KB-007:3",
        document_id="KB-007",
        text="Kafka carries domain and integration events.",
        score=0.91,
        metadata={
            "classification": "CONFIDENTIAL",
        },
    )

    assert result.chunk_id == "KB-007:3"
    assert result.document_id == "KB-007"
    assert result.score == 0.91
    assert result.metadata["classification"] == "CONFIDENTIAL"


def test_search_result_has_empty_metadata_by_default() -> None:
    result = SearchResult(
        chunk_id="KB-001:0",
        document_id="KB-001",
        text="Knowledge content.",
        score=0.85,
    )

    assert result.metadata == {}
