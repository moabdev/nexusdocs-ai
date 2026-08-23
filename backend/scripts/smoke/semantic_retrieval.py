from pathlib import Path

from qdrant_client import QdrantClient

from nexusdocs.indexing.domain.models import VectorDocument
from nexusdocs.indexing.embeddings.fastembed import FastEmbedEmbeddingProvider
from nexusdocs.indexing.vectorstores.qdrant import QdrantVectorStore
from nexusdocs.ingestion.domain.models import (
    DocumentContent,
    SourceDocument,
)
from nexusdocs.ingestion.loaders.markdown import MarkdownDocumentLoader
from nexusdocs.ingestion.processing.chunker import RecursiveTextChunker
from nexusdocs.ingestion.processing.normalizer import TextNormalizer

MODEL = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
COLLECTION = "nexusdocs-semantic-smoke-test"
VECTOR_SIZE = 384

KNOWLEDGE_BASE_PATH = Path(
    "../knowledge-base/velox-logistics/technology/sources/"
    "technology-platform-handbook.md"
)

QUERIES = (
    "Como o sistema deve lidar com eventos duplicados do Kafka?",
    "Para que o Redis é utilizado?",
    "Como os serviços devem lidar com falhas?",
    "Como funciona o rastreamento distribuído?",
    "Quem é responsável pelos dados de cada serviço?",
)


def load_document() -> DocumentContent:
    source = SourceDocument(
        path=KNOWLEDGE_BASE_PATH,
        document_id="KB-007",
        content_type="text/markdown",
        metadata={
            "version": "2.3",
            "status": "ACTIVE",
            "classification": "CONFIDENTIAL",
        },
    )

    return MarkdownDocumentLoader().load(source)


def normalize_document(
    document: DocumentContent,
) -> DocumentContent:
    normalizer = TextNormalizer()

    return DocumentContent(
        document_id=document.document_id,
        text=normalizer.normalize(document.text),
        metadata=document.metadata,
    )


def main() -> None:
    print("=" * 80)
    print("NEXUSDOCS — REAL SEMANTIC RETRIEVAL")
    print("=" * 80)

    document = load_document()

    print(f"\nDocument loaded: {document.document_id}")
    print(f"Characters:      {len(document.text)}")

    normalized_document = normalize_document(document)

    print(f"Normalized:      {len(normalized_document.text)} characters")

    chunker = RecursiveTextChunker(
        chunk_size=1000,
        chunk_overlap=200,
    )

    chunks = chunker.chunk(normalized_document)

    print(f"Chunks:          {len(chunks)}")

    print("\nGenerating embeddings...")

    provider = FastEmbedEmbeddingProvider(
        model_name=MODEL,
    )

    texts = tuple(chunk.text for chunk in chunks)

    vectors = provider.embed_documents(texts)

    if len(vectors) != len(chunks):
        raise RuntimeError("Embedding count does not match chunk count")

    if not vectors:
        raise RuntimeError("No embeddings generated")

    vector_size = len(vectors[0])

    if vector_size != VECTOR_SIZE:
        raise RuntimeError(f"Expected {VECTOR_SIZE} dimensions, received {vector_size}")

    if any(len(vector) != vector_size for vector in vectors):
        raise RuntimeError("Embedding vectors have inconsistent dimensions")

    print(f"Embeddings:      {len(vectors)}")
    print(f"Dimensions:      {vector_size}")

    vector_documents = tuple(
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

    client = QdrantClient(
        url="http://localhost:6333",
    )

    if client.collection_exists(COLLECTION):
        client.delete_collection(COLLECTION)

    store = QdrantVectorStore(
        client=client,
        collection_name=COLLECTION,
        vector_size=vector_size,
    )

    store.add(vector_documents)

    info = client.get_collection(COLLECTION)

    print("\nQDRANT")
    print("-" * 80)
    print(f"Collection:      {COLLECTION}")
    print(f"Points stored:   {info.points_count}")

    if info.points_count != len(chunks):
        raise RuntimeError("Qdrant point count does not match chunk count")

    for query in QUERIES:
        print("\n" + "=" * 80)
        print(f"QUERY: {query}")
        print("=" * 80)

        query_vector = provider.embed_text(query)

        results = store.search(
            query_vector=query_vector,
            limit=3,
        )

        if not results:
            raise RuntimeError(f"No search results for query: {query}")

        for position, result in enumerate(
            results,
            start=1,
        ):
            preview = " ".join(result.text[:350].split())

            print()
            print(f"{position}. {result.chunk_id} | score={result.score:.4f}")
            print(preview)

    print("\n" + "=" * 80)
    print("REAL SEMANTIC RETRIEVAL: OK")
    print("=" * 80)


if __name__ == "__main__":
    main()
