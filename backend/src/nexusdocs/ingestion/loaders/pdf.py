from pypdf import PdfReader

from nexusdocs.ingestion.domain.models import DocumentContent, SourceDocument
from nexusdocs.ingestion.exceptions import (
    DocumentNotFoundError,
    EmptyDocumentError,
    UnsupportedDocumentError,
)


class PdfDocumentLoader:
    """Extract textual content from PDF documents."""

    SUPPORTED_CONTENT_TYPES = frozenset(
        {
            "application/pdf",
        }
    )

    def supports(self, source: SourceDocument) -> bool:
        return (
            source.content_type.lower() in self.SUPPORTED_CONTENT_TYPES
            or source.path.suffix.lower() == ".pdf"
        )

    def load(self, source: SourceDocument) -> DocumentContent:
        if not source.path.is_file():
            raise DocumentNotFoundError(f"Document not found: {source.path}")

        if not self.supports(source):
            raise UnsupportedDocumentError(
                f"Unsupported document type: {source.content_type}"
            )

        reader = PdfReader(source.path)

        pages = [
            text.strip()
            for page in reader.pages
            if (text := page.extract_text()) and text.strip()
        ]

        if not pages:
            raise EmptyDocumentError(
                f"No textual content found in document: {source.path}"
            )

        metadata = {
            **source.metadata,
            "page_count": len(reader.pages),
            "loader": "pypdf",
        }

        return DocumentContent(
            document_id=source.document_id,
            text="\n\n".join(pages),
            metadata=metadata,
        )
