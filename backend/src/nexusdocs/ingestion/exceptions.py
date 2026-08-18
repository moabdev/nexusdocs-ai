class DocumentIngestionError(Exception):
    """Base exception for document ingestion failures."""


class DocumentNotFoundError(DocumentIngestionError):
    """Raised when a source document does not exist."""


class UnsupportedDocumentError(DocumentIngestionError):
    """Raised when a loader does not support the source document."""


class EmptyDocumentError(DocumentIngestionError):
    """Raised when no usable textual content can be extracted."""
