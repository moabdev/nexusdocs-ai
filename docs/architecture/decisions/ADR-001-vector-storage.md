# ADR-002: Vector Storage Strategy

## Status

Accepted

## Context

NexusDocs AI requires persistent vector storage for semantic retrieval over
enterprise knowledge documents.

The vector storage layer must support:

- dense vector similarity search;
- metadata filtering;
- document-level deletion and reindexing;
- deterministic chunk identification;
- scalable approximate nearest-neighbor search;
- local development with containers;
- future hybrid retrieval strategies.

The application core must remain independent from the selected vector database.

## Decision

NexusDocs AI will use Qdrant as its primary vector database.

Application code will interact with vector storage through the `VectorStore`
protocol defined by the indexing layer.

The Qdrant implementation will therefore remain an infrastructure adapter
rather than a dependency of the application core.

## Metadata Strategy

Vector payloads will preserve relevant document and chunk metadata, including:

- document ID;
- chunk ID;
- chunk index;
- document version;
- document status;
- classification;
- source/loader information.

This metadata will later support filtered retrieval and authorization-aware
knowledge access.

## Alternatives Considered

### PostgreSQL with pgvector

pgvector provides vector similarity search directly inside PostgreSQL and
supports exact search, HNSW, IVFFlat, SQL filtering, and hybrid approaches.

It remains a viable alternative when transactional and vector workloads should
share PostgreSQL.

### Qdrant

Qdrant is purpose-built for vector retrieval and provides native vector search,
payload filtering, indexing, and collection management.

Its dedicated vector-search model provides a clear architectural boundary for
the NexusDocs retrieval infrastructure.

## Consequences

### Positive

- Dedicated vector-search infrastructure.
- Strong metadata filtering capabilities.
- Clear separation between application and retrieval infrastructure.
- Easy local deployment using Docker.
- Vector database can be replaced without changing `IndexingService`.

### Negative

- Introduces an additional infrastructure service.
- Requires deployment and operational management separate from PostgreSQL.
- Adds a Qdrant-specific adapter to the infrastructure layer.

## Embedding Strategy

Embedding generation remains independent from vector storage.

The application will continue using the `EmbeddingProvider` protocol so that
local and external embedding providers can be supported without changing the
indexing pipeline.
