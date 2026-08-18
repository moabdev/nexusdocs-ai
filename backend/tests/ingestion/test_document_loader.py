from nexusdocs.ingestion.domain.models import DocumentContent, SourceDocument
from nexusdocs.ingestion.loaders.base import DocumentLoader


class FakeDocumentLoader:
    def supports(self, source: SourceDocument) -> bool:
        return source.content_type == "text/plain"

    def load(self, source: SourceDocument) -> DocumentContent:
        return DocumentContent(
            document_id=source.document_id,
            text="fake document content",
            metadata=source.metadata,
        )


def accepts_document_loader(loader: DocumentLoader) -> DocumentLoader:
    return loader


def test_document_loader_protocol_accepts_compatible_loader() -> None:
    loader = FakeDocumentLoader()

    result = accepts_document_loader(loader)

    assert result is loader
