from nexusdocs.generation.base import LLMProvider
from nexusdocs.rag.models import RagResponse, RagSource
from nexusdocs.retrieval.base import RetrievalProvider


class RagService:
    """Orchestrate retrieval and grounded answer generation."""

    FALLBACK_MESSAGE = "Não encontrei essa informação nos documentos disponíveis."

    def __init__(
        self,
        retrieval_service: RetrievalProvider,
        llm_provider: LLMProvider,
    ) -> None:
        self._retrieval_service = retrieval_service
        self._llm_provider = llm_provider

    def answer(
        self,
        question: str,
    ) -> RagResponse:
        results = self._retrieval_service.retrieve(question)

        if not results:
            return RagResponse(
                answer=self.FALLBACK_MESSAGE,
                sources=(),
                answered=False,
            )

        context = "\n\n".join(
            (
                f"[SOURCE {index}]\n"
                f"Document: {result.document_id}\n"
                f"Chunk: {result.chunk_id}\n"
                f"Content:\n{result.text}"
            )
            for index, result in enumerate(
                results,
                start=1,
            )
        )

        answer = self._llm_provider.generate(
            question=question,
            context=context,
        )

        sources = tuple(
            RagSource(
                chunk_id=result.chunk_id,
                document_id=result.document_id,
                score=result.score,
                metadata=result.metadata,
            )
            for result in results
        )

        return RagResponse(
            answer=answer,
            sources=sources,
            answered=True,
        )
