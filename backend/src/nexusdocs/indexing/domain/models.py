from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True, slots=True)
class VectorDocument:
    """Chunk enriched with its vector embedding."""

    chunk_id: str
    document_id: str
    text: str
    vector: tuple[float, ...]
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True, slots=True)
class SearchResult:
    """Result returned by a vector similarity search."""

    chunk_id: str
    document_id: str
    text: str
    score: float
    metadata: dict[str, Any] = field(default_factory=dict)
