from fastapi.testclient import TestClient

from nexusdocs.api.dependencies import get_rag_service
from nexusdocs.main import app
from nexusdocs.rag.models import RagResponse, RagSource


class FakeRagService:
    def answer(
        self,
        question: str,
    ) -> RagResponse:
        return RagResponse(
            answer=(
                "Kafka consumers devem usar idempotência "
                "para evitar efeitos duplicados."
            ),
            answered=True,
            sources=(
                RagSource(
                    chunk_id="KB-007:5",
                    document_id="KB-007",
                    score=0.91,
                    metadata={
                        "classification": "CONFIDENTIAL",
                    },
                ),
            ),
        )


def override_rag_service() -> FakeRagService:
    return FakeRagService()


app.dependency_overrides[get_rag_service] = override_rag_service

client = TestClient(app)


def test_query_returns_grounded_answer() -> None:
    response = client.post(
        "/query",
        json={"question": ("Como lidar com eventos duplicados do Kafka?")},
    )

    assert response.status_code == 200

    payload = response.json()

    assert payload["answered"] is True

    assert payload["answer"] == (
        "Kafka consumers devem usar idempotência para evitar efeitos duplicados."
    )

    assert len(payload["sources"]) == 1

    source = payload["sources"][0]

    assert source["document_id"] == "KB-007"
    assert source["chunk_id"] == "KB-007:5"
    assert source["score"] == 0.91

    assert source["metadata"]["classification"] == ("CONFIDENTIAL")


def test_query_rejects_empty_question() -> None:
    response = client.post(
        "/query",
        json={
            "question": "",
        },
    )

    assert response.status_code == 422
