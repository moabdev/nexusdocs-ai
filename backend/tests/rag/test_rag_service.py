from nexusdocs.indexing.domain.models import SearchResult
from nexusdocs.rag.service import RagService


class FakeRetrievalService:
    """Test double for the retrieval provider."""

    def __init__(
        self,
        results: tuple[SearchResult, ...],
    ) -> None:
        self._results = results
        self.question = ""

    def retrieve(
        self,
        question: str,
    ) -> tuple[SearchResult, ...]:
        self.question = question
        return self._results


class FakeLLMProvider:
    """Test double for the LLM provider."""

    def __init__(self) -> None:
        self.called = False
        self.question = ""
        self.context = ""

    def generate(
        self,
        *,
        question: str,
        context: str,
    ) -> str:
        self.called = True
        self.question = question
        self.context = context

        return "Kafka consumers devem processar eventos de forma idempotente."


def test_rag_generates_answer_from_retrieved_context() -> None:
    results = (
        SearchResult(
            chunk_id="KB-007:5",
            document_id="KB-007",
            text=(
                "Kafka consumers must use idempotency "
                "to avoid duplicate business effects."
            ),
            score=0.91,
            metadata={
                "classification": "CONFIDENTIAL",
            },
        ),
    )

    retrieval = FakeRetrievalService(results)
    llm = FakeLLMProvider()

    service = RagService(
        retrieval_service=retrieval,
        llm_provider=llm,
    )

    question = "Como lidar com eventos duplicados do Kafka?"

    response = service.answer(question)

    assert response.answered is True

    assert retrieval.question == question

    assert llm.called is True
    assert llm.question == question

    assert "Kafka consumers" in llm.context
    assert "KB-007" in llm.context
    assert "KB-007:5" in llm.context

    assert len(response.sources) == 1

    source = response.sources[0]

    assert source.document_id == "KB-007"
    assert source.chunk_id == "KB-007:5"
    assert source.score == 0.91
    assert source.metadata == {
        "classification": "CONFIDENTIAL",
    }


def test_rag_returns_fallback_without_calling_llm() -> None:
    retrieval = FakeRetrievalService(())
    llm = FakeLLMProvider()

    service = RagService(
        retrieval_service=retrieval,
        llm_provider=llm,
    )

    question = "Qual é a política de férias?"

    response = service.answer(question)

    assert retrieval.question == question

    assert response.answered is False
    assert response.sources == ()

    assert llm.called is False
    assert llm.question == ""
    assert llm.context == ""

    assert response.answer == (
        "Não encontrei essa informação nos documentos disponíveis."
    )
