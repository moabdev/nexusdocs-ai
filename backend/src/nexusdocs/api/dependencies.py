import os
from functools import lru_cache

from qdrant_client import QdrantClient

from nexusdocs.generation.gemini import GeminiLLMProvider
from nexusdocs.indexing.embeddings.fastembed import (
    FastEmbedEmbeddingProvider,
)
from nexusdocs.indexing.vectorstores.qdrant import QdrantVectorStore
from nexusdocs.rag.service import RagService
from nexusdocs.retrieval.service import RetrievalService


@lru_cache
def get_rag_service() -> RagService:
    """Build and cache the production RAG dependency graph."""

    gemini_api_key = os.environ.get("GEMINI_API_KEY", "")

    if not gemini_api_key:
        raise RuntimeError("GEMINI_API_KEY environment variable is required")

    embedding_model = os.environ.get(
        "EMBEDDING_MODEL",
        "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2",
    )

    vector_size = int(
        os.environ.get(
            "EMBEDDING_VECTOR_SIZE",
            "384",
        )
    )

    qdrant_url = os.environ.get(
        "QDRANT_URL",
        "http://localhost:6333",
    )

    collection_name = os.environ.get(
        "QDRANT_COLLECTION",
        "nexusdocs",
    )

    embedding_provider = FastEmbedEmbeddingProvider(
        model_name=embedding_model,
    )

    qdrant_client = QdrantClient(
        url=qdrant_url,
    )

    vector_store = QdrantVectorStore(
        client=qdrant_client,
        collection_name=collection_name,
        vector_size=vector_size,
    )

    retrieval_service = RetrievalService(
        embedding_provider=embedding_provider,
        vector_store=vector_store,
        limit=5,
        score_threshold=0.25,
    )

    llm_provider = GeminiLLMProvider(
        api_key=gemini_api_key,
    )

    return RagService(
        retrieval_service=retrieval_service,
        llm_provider=llm_provider,
    )
