import pytest
from qdrant_client import QdrantClient

from nexusdocs.indexing.domain.models import VectorDocument
from nexusdocs.indexing.vectorstores.qdrant import QdrantVectorStore


def create_store(
    vector_size: int = 3,
) -> tuple[QdrantClient, QdrantVectorStore]:
    client = QdrantClient(":memory:")

    store = QdrantVectorStore(
        client=client,
        collection_name="test_documents",
        vector_size=vector_size,
    )

    return client, store


def test_qdrant_vector_store_creates_collection_and_adds_documents() -> None:
    client, store = create_store()

    documents = (
        VectorDocument(
            chunk_id="KB-007:0",
            document_id="KB-007",
            text="Kafka provides asynchronous messaging.",
            vector=(0.1, 0.2, 0.3),
            metadata={
                "classification": "CONFIDENTIAL",
                "chunk_index": 0,
            },
        ),
        VectorDocument(
            chunk_id="KB-007:1",
            document_id="KB-007",
            text="Redis provides bounded caching.",
            vector=(0.4, 0.5, 0.6),
            metadata={
                "classification": "CONFIDENTIAL",
                "chunk_index": 1,
            },
        ),
    )

    store.add(documents)

    assert client.collection_exists(
        collection_name="test_documents",
    )

    records, _ = client.scroll(
        collection_name="test_documents",
        limit=10,
        with_payload=True,
        with_vectors=True,
    )

    assert len(records) == 2

    payloads = [record.payload for record in records]

    chunk_ids = {payload["chunk_id"] for payload in payloads if payload is not None}

    assert chunk_ids == {
        "KB-007:0",
        "KB-007:1",
    }


def test_qdrant_vector_store_preserves_document_metadata() -> None:
    client, store = create_store()

    document = VectorDocument(
        chunk_id="KB-007:0",
        document_id="KB-007",
        text="Velox Logistics architecture.",
        vector=(0.1, 0.2, 0.3),
        metadata={
            "version": "2.3",
            "status": "ACTIVE",
            "classification": "CONFIDENTIAL",
            "chunk_index": 0,
        },
    )

    store.add((document,))

    records, _ = client.scroll(
        collection_name="test_documents",
        limit=10,
        with_payload=True,
    )

    assert len(records) == 1

    payload = records[0].payload

    assert payload is not None

    assert payload["chunk_id"] == "KB-007:0"
    assert payload["document_id"] == "KB-007"
    assert payload["text"] == "Velox Logistics architecture."
    assert payload["version"] == "2.3"
    assert payload["status"] == "ACTIVE"
    assert payload["classification"] == "CONFIDENTIAL"
    assert payload["chunk_index"] == 0


def test_qdrant_vector_store_searches_by_similarity() -> None:
    _, store = create_store()

    store.add(
        (
            VectorDocument(
                chunk_id="KB-007:0",
                document_id="KB-007",
                text="Kafka messaging",
                vector=(1.0, 0.0, 0.0),
                metadata={
                    "classification": "CONFIDENTIAL",
                },
            ),
            VectorDocument(
                chunk_id="KB-007:1",
                document_id="KB-007",
                text="Redis caching",
                vector=(0.0, 1.0, 0.0),
                metadata={
                    "classification": "CONFIDENTIAL",
                },
            ),
        )
    )

    results = store.search(
        query_vector=(1.0, 0.0, 0.0),
        limit=2,
    )

    assert len(results) == 2

    assert results[0].chunk_id == "KB-007:0"
    assert results[0].document_id == "KB-007"
    assert results[0].text == "Kafka messaging"
    assert results[0].metadata == {
        "classification": "CONFIDENTIAL",
    }

    assert results[0].score > results[1].score


def test_qdrant_vector_store_respects_search_limit() -> None:
    _, store = create_store()

    store.add(
        (
            VectorDocument(
                chunk_id="KB-001:0",
                document_id="KB-001",
                text="First",
                vector=(1.0, 0.0, 0.0),
            ),
            VectorDocument(
                chunk_id="KB-001:1",
                document_id="KB-001",
                text="Second",
                vector=(0.9, 0.1, 0.0),
            ),
            VectorDocument(
                chunk_id="KB-001:2",
                document_id="KB-001",
                text="Third",
                vector=(0.0, 1.0, 0.0),
            ),
        )
    )

    results = store.search(
        query_vector=(1.0, 0.0, 0.0),
        limit=2,
    )

    assert len(results) == 2


def test_qdrant_vector_store_returns_empty_search_for_missing_collection() -> None:
    _, store = create_store()

    results = store.search(
        query_vector=(1.0, 0.0, 0.0),
    )

    assert results == ()


def test_qdrant_vector_store_deletes_vectors_by_document_id() -> None:
    client, store = create_store()

    store.add(
        (
            VectorDocument(
                chunk_id="KB-007:0",
                document_id="KB-007",
                text="Architecture",
                vector=(1.0, 0.0, 0.0),
            ),
            VectorDocument(
                chunk_id="KB-007:1",
                document_id="KB-007",
                text="Kafka",
                vector=(0.9, 0.1, 0.0),
            ),
            VectorDocument(
                chunk_id="KB-008:0",
                document_id="KB-008",
                text="Delivery performance",
                vector=(0.0, 1.0, 0.0),
            ),
        )
    )

    store.delete_by_document_id("KB-007")

    records, _ = client.scroll(
        collection_name="test_documents",
        limit=10,
        with_payload=True,
    )

    assert len(records) == 1

    payload = records[0].payload

    assert payload is not None
    assert payload["document_id"] == "KB-008"


def test_qdrant_vector_store_delete_is_safe_for_missing_collection() -> None:
    _, store = create_store()

    store.delete_by_document_id("KB-007")


def test_qdrant_vector_store_rejects_invalid_vector_dimension() -> None:
    _, store = create_store()

    document = VectorDocument(
        chunk_id="KB-007:0",
        document_id="KB-007",
        text="Architecture",
        vector=(0.1, 0.2),
    )

    with pytest.raises(
        ValueError,
        match="expected 3",
    ):
        store.add((document,))


def test_qdrant_vector_store_rejects_invalid_query_dimension() -> None:
    _, store = create_store()

    with pytest.raises(
        ValueError,
        match="expected 3",
    ):
        store.search(
            query_vector=(0.1, 0.2),
        )


def test_qdrant_vector_store_rejects_invalid_search_limit() -> None:
    _, store = create_store()

    with pytest.raises(
        ValueError,
        match="limit must be greater than zero",
    ):
        store.search(
            query_vector=(0.1, 0.2, 0.3),
            limit=0,
        )


def test_qdrant_vector_store_rejects_empty_document_id_for_deletion() -> None:
    _, store = create_store()

    with pytest.raises(
        ValueError,
        match="document_id cannot be empty",
    ):
        store.delete_by_document_id("   ")


def test_qdrant_vector_store_rejects_invalid_vector_size() -> None:
    client = QdrantClient(":memory:")

    with pytest.raises(
        ValueError,
        match="vector_size must be greater than zero",
    ):
        QdrantVectorStore(
            client=client,
            collection_name="test_documents",
            vector_size=0,
        )


def test_qdrant_vector_store_rejects_empty_collection_name() -> None:
    client = QdrantClient(":memory:")

    with pytest.raises(
        ValueError,
        match="collection_name cannot be empty",
    ):
        QdrantVectorStore(
            client=client,
            collection_name="   ",
            vector_size=3,
        )


def test_qdrant_vector_store_does_nothing_for_empty_documents() -> None:
    client, store = create_store()

    store.add(())

    assert not client.collection_exists(
        collection_name="test_documents",
    )


def test_qdrant_vector_store_uses_deterministic_point_ids() -> None:
    first = QdrantVectorStore._point_id("KB-007:0")
    second = QdrantVectorStore._point_id("KB-007:0")
    different = QdrantVectorStore._point_id("KB-007:1")

    assert first == second
    assert first != different
