from nexusdocs.indexing.domain.models import SearchResult
from nexusdocs.rag.service import RagService


class FakeRetrievalService:
    def __init__(
        self,
        results: tuple[SearchResult, ...],
    ) -> None:
        self._results = results

    def retrieve(
        self,
        question: str,
    ) -> tuple[SearchResult, ...]:
        return self._results


class FakeLLMProvider:
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

    llm = FakeLLMProvider()

    service = RagService(
        retrieval_service=FakeRetrievalService(results),
        llm_provider=llm,
    )

    response = service.answer("Como lidar com eventos duplicados do Kafka?")

    assert response.answered is True
    assert llm.called is True
    assert "Kafka consumers" in llm.context

    assert response.sources[0].document_id == "KB-007"
    assert response.sources[0].chunk_id == "KB-007:5"


def test_rag_returns_fallback_without_calling_llm() -> None:
    llm = FakeLLMProvider()

    service = RagService(
        retrieval_service=FakeRetrievalService(()),
        llm_provider=llm,
    )

    response = service.answer("Qual é a política de férias?")

    assert response.answered is False
    assert response.sources == ()
    assert llm.called is False

    assert response.answer == (
        "Não encontrei essa informação nos documentos disponíveis."
    )
