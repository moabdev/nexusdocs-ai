import pytest

from nexusdocs.ingestion.domain.models import DocumentContent
from nexusdocs.ingestion.processing.chunker import RecursiveTextChunker


def test_chunker_returns_single_chunk_for_small_document() -> None:
    document = DocumentContent(
        document_id="KB-001",
        text="NexusDocs provides enterprise knowledge intelligence.",
        metadata={
            "classification": "INTERNAL",
        },
    )

    chunker = RecursiveTextChunker(
        chunk_size=100,
        chunk_overlap=20,
    )

    chunks = chunker.chunk(document)

    assert len(chunks) == 1
    assert chunks[0].chunk_id == "KB-001:0"
    assert chunks[0].document_id == "KB-001"
    assert chunks[0].index == 0
    assert chunks[0].text == document.text


def test_chunker_propagates_document_metadata() -> None:
    document = DocumentContent(
        document_id="KB-007",
        text="Architecture documentation.",
        metadata={
            "status": "ACTIVE",
            "classification": "CONFIDENTIAL",
        },
    )

    chunks = RecursiveTextChunker().chunk(document)

    assert chunks[0].metadata == {
        "status": "ACTIVE",
        "classification": "CONFIDENTIAL",
        "chunk_index": 0,
    }


def test_chunker_splits_large_document() -> None:
    document = DocumentContent(
        document_id="KB-TEST",
        text=(
            "First paragraph contains important architecture information.\n\n"
            "Second paragraph describes reliability and observability.\n\n"
            "Third paragraph explains the integration platform."
        ),
    )

    chunker = RecursiveTextChunker(
        chunk_size=90,
        chunk_overlap=20,
    )

    chunks = chunker.chunk(document)

    assert len(chunks) > 1

    assert all(len(chunk.text) <= 90 for chunk in chunks)


def test_chunker_generates_sequential_identifiers() -> None:
    document = DocumentContent(
        document_id="KB-007",
        text=" ".join(["architecture"] * 100),
    )

    chunker = RecursiveTextChunker(
        chunk_size=100,
        chunk_overlap=20,
    )

    chunks = chunker.chunk(document)

    for index, chunk in enumerate(chunks):
        assert chunk.index == index
        assert chunk.chunk_id == f"KB-007:{index}"


def test_chunker_returns_no_chunks_for_empty_document() -> None:
    document = DocumentContent(
        document_id="KB-TEST",
        text="   ",
    )

    chunks = RecursiveTextChunker().chunk(document)

    assert chunks == ()


@pytest.mark.parametrize(
    ("chunk_size", "chunk_overlap"),
    (
        (0, 0),
        (-1, 0),
        (100, -1),
        (100, 100),
        (100, 101),
    ),
)
def test_chunker_rejects_invalid_configuration(
    chunk_size: int,
    chunk_overlap: int,
) -> None:
    with pytest.raises(ValueError):
        RecursiveTextChunker(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
        )


def test_chunker_overlap_does_not_start_in_middle_of_word() -> None:
    document = DocumentContent(
        document_id="KB-TEST",
        text=(
            "Architecture provides clear service boundaries. "
            "Reliability requires retries and idempotency. "
            "Observability provides metrics and distributed tracing. "
            "Security requires authentication and authorization."
        ),
    )

    chunker = RecursiveTextChunker(
        chunk_size=100,
        chunk_overlap=30,
    )

    chunks = chunker.chunk(document)

    assert len(chunks) > 1

    for chunk in chunks:
        assert not chunk.text.startswith(
            (
                "rchitecture",
                "eliability",
                "bservability",
                "ecurity",
            )
        )
