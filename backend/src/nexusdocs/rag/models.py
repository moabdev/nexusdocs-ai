from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True, slots=True)
class RagSource:
    chunk_id: str
    document_id: str
    score: float
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True, slots=True)
class RagResponse:
    answer: str
    sources: tuple[RagSource, ...]
    answered: bool
