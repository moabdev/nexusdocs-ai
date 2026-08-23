from nexusdocs.ingestion.domain.models import DocumentContent, SourceDocument
from nexusdocs.ingestion.exceptions import (
    DocumentNotFoundError,
    EmptyDocumentError,
    UnsupportedDocumentError,
)


class MarkdownDocumentLoader:
    """Load textual content from Markdown documents."""

    SUPPORTED_CONTENT_TYPES = frozenset(
        {
            "text/markdown",
            "text/x-markdown",
        }
    )

    def supports(self, source: SourceDocument) -> bool:
        return (
            source.content_type.lower() in self.SUPPORTED_CONTENT_TYPES
            or source.path.suffix.lower() in {".md", ".markdown"}
        )

    def load(self, source: SourceDocument) -> DocumentContent:
        if not source.path.is_file():
            raise DocumentNotFoundError(f"Document not found: {source.path}")

        if not self.supports(source):
            raise UnsupportedDocumentError(
                f"Unsupported document type: {source.content_type}"
            )

        text = source.path.read_text(encoding="utf-8").strip()

        if not text:
            raise EmptyDocumentError(
                f"No textual content found in document: {source.path}"
            )

        metadata = {
            **source.metadata,
            "loader": "markdown",
        }

        return DocumentContent(
            document_id=source.document_id,
            text=text,
            metadata=metadata,
        )
