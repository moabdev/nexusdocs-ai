from nexusdocs.indexing.domain.models import VectorDocument
from nexusdocs.indexing.embeddings.base import EmbeddingProvider
from nexusdocs.indexing.vectorstores.base import VectorStore
from nexusdocs.ingestion.domain.models import DocumentChunk


class IndexingService:
    """Generate embeddings and index document chunks."""

    def __init__(
        self,
        embedding_provider: EmbeddingProvider,
        vector_store: VectorStore,
    ) -> None:
        self._embedding_provider = embedding_provider
        self._vector_store = vector_store

    def index(
        self,
        chunks: tuple[DocumentChunk, ...],
    ) -> tuple[VectorDocument, ...]:
        if not chunks:
            return ()

        texts = tuple(chunk.text for chunk in chunks)

        vectors = self._embedding_provider.embed_documents(texts)

        if len(vectors) != len(chunks):
            raise ValueError(
                "Embedding provider returned a different number "
                "of vectors than input chunks"
            )

        dimensions = {len(vector) for vector in vectors}

        if len(dimensions) != 1:
            raise ValueError(
                "Embedding provider returned vectors with inconsistent dimensions"
            )

        if dimensions == {0}:
            raise ValueError("Embedding provider returned empty vectors")

        documents = tuple(
            VectorDocument(
                chunk_id=chunk.chunk_id,
                document_id=chunk.document_id,
                text=chunk.text,
                vector=vector,
                metadata=chunk.metadata,
            )
            for chunk, vector in zip(
                chunks,
                vectors,
                strict=True,
            )
        )

        self._vector_store.add(documents)

        return documents
