from typing import Protocol

from nexusdocs.ingestion.domain.models import (
    DocumentContent,
    SourceDocument,
    TabularDocument,
)

type IngestionResult = DocumentContent | TabularDocument


class DocumentLoader(Protocol):
    """Contract implemented by document loaders."""

    def supports(self, source: SourceDocument) -> bool:
        """Return whether this loader supports the given source."""
        ...

    def load(self, source: SourceDocument) -> IngestionResult:
        """Extract and return the document content."""
        ...
