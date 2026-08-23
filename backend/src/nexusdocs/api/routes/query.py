from typing import Annotated, Any

from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field

from nexusdocs.api.dependencies import get_rag_service
from nexusdocs.rag.service import RagService

router = APIRouter(
    prefix="/query",
    tags=["RAG"],
)


class QueryRequest(BaseModel):
    question: str = Field(
        min_length=1,
        max_length=2000,
    )


class SourceResponse(BaseModel):
    chunk_id: str
    document_id: str
    score: float
    metadata: dict[str, Any]


class QueryResponse(BaseModel):
    answer: str
    answered: bool
    sources: list[SourceResponse]


RagServiceDependency = Annotated[
    RagService,
    Depends(get_rag_service),
]


@router.post(
    "",
    response_model=QueryResponse,
)
def query(
    request: QueryRequest,
    rag_service: RagServiceDependency,
) -> QueryResponse:
    result = rag_service.answer(request.question)

    return QueryResponse(
        answer=result.answer,
        answered=result.answered,
        sources=[
            SourceResponse(
                chunk_id=source.chunk_id,
                document_id=source.document_id,
                score=source.score,
                metadata=source.metadata,
            )
            for source in result.sources
        ],
    )
