from pathlib import Path

import pytest

from nexusdocs.ingestion.domain.models import (
    DocumentContent,
    SourceDocument,
)
from nexusdocs.ingestion.exceptions import DocumentLoaderNotFoundError
from nexusdocs.ingestion.loaders.resolver import DocumentLoaderResolver


class FakeLoader:
    def __init__(self, supported_content_type: str) -> None:
        self.supported_content_type = supported_content_type

    def supports(self, source: SourceDocument) -> bool:
        return source.content_type == self.supported_content_type

    def load(self, source: SourceDocument) -> DocumentContent:
        return DocumentContent(
            document_id=source.document_id,
            text="fake content",
        )


def test_resolver_returns_loader_that_supports_source() -> None:
    pdf_loader = FakeLoader("application/pdf")
    markdown_loader = FakeLoader("text/markdown")

    resolver = DocumentLoaderResolver(
        loaders=(
            pdf_loader,
            markdown_loader,
        )
    )

    source = SourceDocument(
        path=Path("document.md"),
        document_id="KB-TEST",
        content_type="text/markdown",
    )

    loader = resolver.resolve(source)

    assert loader is markdown_loader


def test_resolver_uses_registration_order() -> None:
    first_loader = FakeLoader("application/pdf")
    second_loader = FakeLoader("application/pdf")

    resolver = DocumentLoaderResolver(
        loaders=(
            first_loader,
            second_loader,
        )
    )

    source = SourceDocument(
        path=Path("document.pdf"),
        document_id="KB-TEST",
        content_type="application/pdf",
    )

    loader = resolver.resolve(source)

    assert loader is first_loader


def test_resolver_raises_error_when_no_loader_supports_source() -> None:
    resolver = DocumentLoaderResolver(
        loaders=(
            FakeLoader("application/pdf"),
            FakeLoader("text/markdown"),
        )
    )

    source = SourceDocument(
        path=Path("document.docx"),
        document_id="KB-TEST",
        content_type=(
            "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        ),
    )

    with pytest.raises(
        DocumentLoaderNotFoundError,
        match="No document loader found",
    ):
        resolver.resolve(source)
