from typing import Protocol

from nexusdocs.ingestion.domain.models import DocumentContent, SourceDocument


class DocumentLoader(Protocol):
    """Contract implemented by document loaders."""

    def supports(self, source: SourceDocument) -> bool:
        """Return whether this loader supports the given source."""
        ...

    def load(self, source: SourceDocument) -> DocumentContent:
        """Extract and return the document content."""
        ...
