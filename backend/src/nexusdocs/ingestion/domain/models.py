from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


@dataclass(frozen=True, slots=True)
class SourceDocument:
    path: Path
    document_id: str
    content_type: str
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True, slots=True)
class DocumentContent:
    document_id: str
    text: str
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True, slots=True)
class DocumentChunk:
    chunk_id: str
    document_id: str
    text: str
    index: int
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True, slots=True)
class TabularRecord:
    """A single record extracted from a structured document."""

    index: int
    values: dict[str, Any]


@dataclass(frozen=True, slots=True)
class TabularDocument:
    """Structured representation of a tabular source document."""

    document_id: str
    columns: tuple[str, ...]
    records: tuple[TabularRecord, ...]
    metadata: dict[str, Any] = field(default_factory=dict)

    @property
    def row_count(self) -> int:
        return len(self.records)
