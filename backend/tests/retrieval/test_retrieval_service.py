import pytest

from nexusdocs.indexing.domain.models import SearchResult
from nexusdocs.retrieval.service import RetrievalService


class FakeEmbeddingProvider:
    def embed_text(
        self,
        text: str,
    ) -> tuple[float, ...]:
        return (1.0, 0.0, 0.0)

    def embed_documents(
        self,
        texts: tuple[str, ...],
    ) -> tuple[tuple[float, ...], ...]:
        return tuple((1.0, 0.0, 0.0) for _ in texts)


class FakeVectorStore:
    def __init__(
        self,
        results: tuple[SearchResult, ...],
    ) -> None:
        self.results = results
        self.query_vector: tuple[float, ...] | None = None
        self.limit: int | None = None

    def search(
        self,
        query_vector: tuple[float, ...],
        limit: int = 5,
    ) -> tuple[SearchResult, ...]:
        self.query_vector = query_vector
        self.limit = limit

        return self.results

    def add(self, documents: tuple) -> None:
        pass

    def delete_by_document_id(
        self,
        document_id: str,
    ) -> None:
        pass


def make_result(
    chunk_id: str,
    score: float,
) -> SearchResult:
    return SearchResult(
        chunk_id=chunk_id,
        document_id="KB-007",
        text="Relevant enterprise knowledge.",
        score=score,
        metadata={
            "classification": "INTERNAL",
        },
    )


def test_retrieval_generates_embedding_and_searches_store() -> None:
    store = FakeVectorStore((make_result("KB-007:0", 0.8),))

    service = RetrievalService(
        embedding_provider=FakeEmbeddingProvider(),
        vector_store=store,
    )

    results = service.retrieve("How does the platform handle failures?")

    assert len(results) == 1
    assert store.query_vector == (1.0, 0.0, 0.0)
    assert store.limit == 5


def test_retrieval_filters_results_below_threshold() -> None:
    store = FakeVectorStore(
        (
            make_result("KB-007:0", 0.85),
            make_result("KB-007:1", 0.40),
            make_result("KB-007:2", 0.10),
        )
    )

    service = RetrievalService(
        embedding_provider=FakeEmbeddingProvider(),
        vector_store=store,
        score_threshold=0.25,
    )

    results = service.retrieve("How does Kafka work?")

    assert len(results) == 2

    assert tuple(result.chunk_id for result in results) == (
        "KB-007:0",
        "KB-007:1",
    )


def test_retrieval_returns_empty_when_nothing_is_relevant() -> None:
    store = FakeVectorStore(
        (
            make_result("KB-007:0", 0.10),
            make_result("KB-007:1", 0.05),
        )
    )

    service = RetrievalService(
        embedding_provider=FakeEmbeddingProvider(),
        vector_store=store,
        score_threshold=0.25,
    )

    results = service.retrieve("What is the vacation policy?")

    assert results == ()


@pytest.mark.parametrize(
    "question",
    (
        "",
        " ",
        "\n",
    ),
)
def test_retrieval_rejects_empty_question(
    question: str,
) -> None:
    service = RetrievalService(
        embedding_provider=FakeEmbeddingProvider(),
        vector_store=FakeVectorStore(()),
    )

    with pytest.raises(
        ValueError,
        match="question cannot be empty",
    ):
        service.retrieve(question)


@pytest.mark.parametrize(
    ("limit", "threshold"),
    (
        (0, 0.25),
        (-1, 0.25),
        (5, -0.1),
        (5, 1.1),
    ),
)
def test_retrieval_rejects_invalid_configuration(
    limit: int,
    threshold: float,
) -> None:
    with pytest.raises(ValueError):
        RetrievalService(
            embedding_provider=FakeEmbeddingProvider(),
            vector_store=FakeVectorStore(()),
            limit=limit,
            score_threshold=threshold,
        )
