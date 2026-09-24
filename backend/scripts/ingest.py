"""Ingest knowledge-base documents into the Qdrant vector store."""

import os
from pathlib import Path
import sys

from dotenv import load_dotenv
from qdrant_client import QdrantClient

from nexusdocs.indexing.domain.models import VectorDocument
from nexusdocs.indexing.embeddings.fastembed import FastEmbedEmbeddingProvider
from nexusdocs.indexing.vectorstores.qdrant import QdrantVectorStore
from nexusdocs.ingestion.domain.models import DocumentContent, SourceDocument
from nexusdocs.ingestion.loaders.markdown import MarkdownDocumentLoader
from nexusdocs.ingestion.loaders.pdf import PdfDocumentLoader
from nexusdocs.ingestion.loaders.resolver import DocumentLoaderResolver
from nexusdocs.ingestion.processing.chunker import RecursiveTextChunker
from nexusdocs.ingestion.processing.normalizer import TextNormalizer


def find_knowledge_base() -> Path:
    """Find knowledge-base directory in common locations."""
    env_dir = os.environ.get("KNOWLEDGE_BASE_DIR")
    candidates = [
        Path(env_dir) if env_dir else None,
        Path("/knowledge-base/velox-logistics"),
        Path("../knowledge-base/velox-logistics"),
        Path("knowledge-base/velox-logistics"),
        (
            Path(__file__).resolve().parent.parent.parent
            / "knowledge-base"
            / "velox-logistics"
        ),
        Path(__file__).resolve().parent.parent / "knowledge-base" / "velox-logistics",
    ]
    for candidate in candidates:
        if candidate and candidate.exists() and candidate.is_dir():
            return candidate.resolve()

    raise FileNotFoundError("Could not find knowledge-base/velox-logistics directory.")


def extract_metadata_from_markdown(text: str) -> dict[str, str]:
    """Extract document control metadata if present in markdown."""
    metadata: dict[str, str] = {}
    for line in text.splitlines():
        line = line.strip()
        if not line or not line.startswith("- **"):
            continue
        if ":**" in line:
            parts = line[4:].split(":**", 1)
            if len(parts) == 2:
                key = parts[0].strip().lower().replace(" ", "_")
                val = parts[1].strip()
                metadata[key] = val
    return metadata


def main() -> None:
    load_dotenv()

    kb_path = find_knowledge_base()
    print(f"Loading knowledge base from: {kb_path}")

    model_name = os.environ.get(
        "EMBEDDING_MODEL",
        "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2",
    )
    vector_size = int(os.environ.get("EMBEDDING_VECTOR_SIZE", "384"))
    qdrant_url = os.environ.get("QDRANT_URL", "http://localhost:6333")
    collection_name = os.environ.get("QDRANT_COLLECTION", "nexusdocs")

    print(f"Qdrant URL:        {qdrant_url}")
    print(f"Collection:        {collection_name}")
    print(f"Embedding model:   {model_name}")

    resolver = DocumentLoaderResolver(
        [
            MarkdownDocumentLoader(),
            PdfDocumentLoader(),
        ]
    )
    normalizer = TextNormalizer()
    chunker = RecursiveTextChunker(
        chunk_size=1000,
        chunk_overlap=200,
    )

    # Search for markdown files in sources directories first
    md_files = list(kb_path.glob("**/sources/*.md"))
    if not md_files:
        md_files = list(kb_path.glob("**/*.md"))

    print(f"Found {len(md_files)} markdown documents to index.")

    all_chunks = []

    for file_path in md_files:
        doc_id = file_path.stem
        raw_text = file_path.read_text(encoding="utf-8")
        extracted_meta = extract_metadata_from_markdown(raw_text)

        document_id = extracted_meta.get("document_id", doc_id)
        source = SourceDocument(
            path=file_path,
            document_id=document_id,
            content_type="text/markdown",
            metadata=extracted_meta,
        )

        try:
            doc = resolver.resolve(source).load(source)
            norm_doc = DocumentContent(
                document_id=doc.document_id,
                text=normalizer.normalize(doc.text),
                metadata=doc.metadata,
            )
            chunks = chunker.chunk(norm_doc)
            all_chunks.extend(chunks)
            print(f"  [+] {document_id} ({file_path.name}): {len(chunks)} chunks")
        except Exception as e:
            print(f"  [-] Error loading {file_path}: {e}", file=sys.stderr)

    if not all_chunks:
        print("No chunks generated. Aborting indexing.")
        return

    print(f"\nTotal chunks to embed: {len(all_chunks)}")
    print("Generating embeddings via FastEmbed...")
    provider = FastEmbedEmbeddingProvider(model_name=model_name)

    texts = tuple(chunk.text for chunk in all_chunks)
    vectors = provider.embed_documents(texts)

    vector_documents = tuple(
        VectorDocument(
            chunk_id=chunk.chunk_id,
            document_id=chunk.document_id,
            text=chunk.text,
            vector=vector,
            metadata=chunk.metadata,
        )
        for chunk, vector in zip(all_chunks, vectors, strict=True)
    )

    print(f"Connecting to Qdrant at {qdrant_url}...")
    client = QdrantClient(url=qdrant_url)

    store = QdrantVectorStore(
        client=client,
        collection_name=collection_name,
        vector_size=vector_size,
    )

    store.ensure_collection()
    store.add(vector_documents)

    info = client.get_collection(collection_name)
    print("\n" + "=" * 50)
    print("INDEXING COMPLETE!")
    print(f"Collection:     {collection_name}")
    print(f"Points stored:  {info.points_count}")
    print("=" * 50)


if __name__ == "__main__":
    main()
