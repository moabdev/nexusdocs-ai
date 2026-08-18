from pathlib import Path

import pytest

from nexusdocs.ingestion.domain.models import SourceDocument
from nexusdocs.ingestion.exceptions import (
    DocumentNotFoundError,
    EmptyDocumentError,
    UnsupportedDocumentError,
)
from nexusdocs.ingestion.loaders.markdown import MarkdownDocumentLoader


def test_markdown_loader_supports_markdown_content_type() -> None:
    loader = MarkdownDocumentLoader()

    source = SourceDocument(
        path=Path("document"),
        document_id="KB-TEST",
        content_type="text/markdown",
    )

    assert loader.supports(source)


def test_markdown_loader_supports_md_extension() -> None:
    loader = MarkdownDocumentLoader()

    source = SourceDocument(
        path=Path("document.md"),
        document_id="KB-TEST",
        content_type="text/plain",
    )

    assert loader.supports(source)


def test_markdown_loader_rejects_unsupported_document() -> None:
    loader = MarkdownDocumentLoader()

    source = SourceDocument(
        path=Path("document.csv"),
        document_id="KB-TEST",
        content_type="text/csv",
    )

    assert not loader.supports(source)


def test_markdown_loader_loads_document(
    tmp_path: Path,
) -> None:
    path = tmp_path / "document.md"
    path.write_text(
        "# NexusDocs\n\nEnterprise knowledge intelligence.",
        encoding="utf-8",
    )

    source = SourceDocument(
        path=path,
        document_id="KB-TEST",
        content_type="text/markdown",
        metadata={
            "status": "ACTIVE",
            "classification": "INTERNAL",
        },
    )

    loader = MarkdownDocumentLoader()

    document = loader.load(source)

    assert document.document_id == "KB-TEST"
    assert document.text == ("# NexusDocs\n\nEnterprise knowledge intelligence.")
    assert document.metadata == {
        "status": "ACTIVE",
        "classification": "INTERNAL",
        "loader": "markdown",
    }


def test_markdown_loader_raises_error_when_file_does_not_exist(
    tmp_path: Path,
) -> None:
    source = SourceDocument(
        path=tmp_path / "missing.md",
        document_id="KB-TEST",
        content_type="text/markdown",
    )

    loader = MarkdownDocumentLoader()

    with pytest.raises(
        DocumentNotFoundError,
        match="Document not found",
    ):
        loader.load(source)


def test_markdown_loader_raises_error_for_unsupported_document(
    tmp_path: Path,
) -> None:
    path = tmp_path / "document.csv"
    path.write_text("id,name\n1,NexusDocs", encoding="utf-8")

    source = SourceDocument(
        path=path,
        document_id="KB-TEST",
        content_type="text/csv",
    )

    loader = MarkdownDocumentLoader()

    with pytest.raises(
        UnsupportedDocumentError,
        match="Unsupported document type",
    ):
        loader.load(source)


def test_markdown_loader_raises_error_when_document_is_empty(
    tmp_path: Path,
) -> None:
    path = tmp_path / "empty.md"
    path.write_text("   \n\n   ", encoding="utf-8")

    source = SourceDocument(
        path=path,
        document_id="KB-TEST",
        content_type="text/markdown",
    )

    loader = MarkdownDocumentLoader()

    with pytest.raises(
        EmptyDocumentError,
        match="No textual content found",
    ):
        loader.load(source)
