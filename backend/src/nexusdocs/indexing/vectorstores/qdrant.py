from uuid import NAMESPACE_URL, uuid5

from qdrant_client import QdrantClient
from qdrant_client.models import (
    Distance,
    FieldCondition,
    Filter,
    MatchValue,
    PointStruct,
    VectorParams,
)

from nexusdocs.indexing.domain.models import (
    SearchResult,
    VectorDocument,
)


class QdrantVectorStore:
    """Qdrant implementation of the vector store contract."""

    def __init__(
        self,
        client: QdrantClient,
        collection_name: str,
        vector_size: int,
    ) -> None:
        if vector_size <= 0:
            raise ValueError("vector_size must be greater than zero")

        if not collection_name.strip():
            raise ValueError("collection_name cannot be empty")

        self._client = client
        self._collection_name = collection_name
        self._vector_size = vector_size

    def ensure_collection(self) -> None:
        """Create the Qdrant collection when it does not exist."""
        if self._client.collection_exists(
            collection_name=self._collection_name,
        ):
            return

        self._client.create_collection(
            collection_name=self._collection_name,
            vectors_config=VectorParams(
                size=self._vector_size,
                distance=Distance.COSINE,
            ),
        )

    def add(
        self,
        documents: tuple[VectorDocument, ...],
    ) -> None:
        """Store vector documents in Qdrant."""
        if not documents:
            return

        self._validate_vector_dimensions(documents)

        self.ensure_collection()

        points = [
            PointStruct(
                id=self._point_id(document.chunk_id),
                vector=list(document.vector),
                payload={
                    "chunk_id": document.chunk_id,
                    "document_id": document.document_id,
                    "text": document.text,
                    **document.metadata,
                },
            )
            for document in documents
        ]

        self._client.upsert(
            collection_name=self._collection_name,
            points=points,
            wait=True,
        )

    def search(
        self,
        query_vector: tuple[float, ...],
        limit: int = 5,
    ) -> tuple[SearchResult, ...]:
        """Return documents ordered by vector similarity."""
        if limit <= 0:
            raise ValueError("limit must be greater than zero")

        if len(query_vector) != self._vector_size:
            raise ValueError(
                f"Query vector has dimension {len(query_vector)}, "
                f"expected {self._vector_size}"
            )

        if not self._client.collection_exists(
            collection_name=self._collection_name,
        ):
            return ()

        response = self._client.query_points(
            collection_name=self._collection_name,
            query=list(query_vector),
            limit=limit,
            with_payload=True,
        )

        results: list[SearchResult] = []

        for point in response.points:
            payload = point.payload or {}

            chunk_id = payload.get("chunk_id")
            document_id = payload.get("document_id")
            text = payload.get("text")

            if not isinstance(chunk_id, str):
                continue

            if not isinstance(document_id, str):
                continue

            if not isinstance(text, str):
                continue

            metadata = {
                key: value
                for key, value in payload.items()
                if key
                not in {
                    "chunk_id",
                    "document_id",
                    "text",
                }
            }

            results.append(
                SearchResult(
                    chunk_id=chunk_id,
                    document_id=document_id,
                    text=text,
                    score=float(point.score),
                    metadata=metadata,
                )
            )

        return tuple(results)

    def delete_by_document_id(
        self,
        document_id: str,
    ) -> None:
        """Remove all vectors associated with a document."""
        if not document_id.strip():
            raise ValueError("document_id cannot be empty")

        if not self._client.collection_exists(
            collection_name=self._collection_name,
        ):
            return

        self._client.delete(
            collection_name=self._collection_name,
            points_selector=Filter(
                must=[
                    FieldCondition(
                        key="document_id",
                        match=MatchValue(
                            value=document_id,
                        ),
                    ),
                ]
            ),
            wait=True,
        )

    def _validate_vector_dimensions(
        self,
        documents: tuple[VectorDocument, ...],
    ) -> None:
        for document in documents:
            dimension = len(document.vector)

            if dimension != self._vector_size:
                raise ValueError(
                    f"Vector {document.chunk_id} has dimension "
                    f"{dimension}, expected {self._vector_size}"
                )

    @staticmethod
    def _point_id(
        chunk_id: str,
    ) -> str:
        return str(
            uuid5(
                NAMESPACE_URL,
                chunk_id,
            )
        )
