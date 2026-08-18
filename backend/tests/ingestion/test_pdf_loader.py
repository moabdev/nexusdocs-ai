from pathlib import Path

import pytest
from pypdf import PdfWriter

from nexusdocs.ingestion.domain.models import SourceDocument
from nexusdocs.ingestion.exceptions import (
    DocumentNotFoundError,
    EmptyDocumentError,
    UnsupportedDocumentError,
)
from nexusdocs.ingestion.loaders.pdf import PdfDocumentLoader


def test_pdf_loader_supports_pdf_content_type() -> None:
    loader = PdfDocumentLoader()

    source = SourceDocument(
        path=Path("document"),
        document_id="KB-TEST",
        content_type="application/pdf",
    )

    assert loader.supports(source)


def test_pdf_loader_supports_pdf_extension() -> None:
    loader = PdfDocumentLoader()

    source = SourceDocument(
        path=Path("document.pdf"),
        document_id="KB-TEST",
        content_type="application/octet-stream",
    )

    assert loader.supports(source)


def test_pdf_loader_rejects_unsupported_document() -> None:
    loader = PdfDocumentLoader()

    source = SourceDocument(
        path=Path("document.csv"),
        document_id="KB-TEST",
        content_type="text/csv",
    )

    assert not loader.supports(source)


def test_pdf_loader_raises_error_when_file_does_not_exist(
    tmp_path: Path,
) -> None:
    loader = PdfDocumentLoader()

    source = SourceDocument(
        path=tmp_path / "missing.pdf",
        document_id="KB-TEST",
        content_type="application/pdf",
    )

    with pytest.raises(
        DocumentNotFoundError,
        match="Document not found",
    ):
        loader.load(source)


def test_pdf_loader_raises_error_for_unsupported_document(
    tmp_path: Path,
) -> None:
    loader = PdfDocumentLoader()

    path = tmp_path / "document.csv"
    path.write_text(
        "id,name\n1,NexusDocs",
        encoding="utf-8",
    )

    source = SourceDocument(
        path=path,
        document_id="KB-TEST",
        content_type="text/csv",
    )

    with pytest.raises(
        UnsupportedDocumentError,
        match="Unsupported document type",
    ):
        loader.load(source)


def test_pdf_loader_raises_error_when_pdf_has_no_text(
    tmp_path: Path,
) -> None:
    path = tmp_path / "empty.pdf"

    writer = PdfWriter()
    writer.add_blank_page(
        width=612,
        height=792,
    )

    with path.open("wb") as file:
        writer.write(file)

    source = SourceDocument(
        path=path,
        document_id="KB-TEST",
        content_type="application/pdf",
    )

    loader = PdfDocumentLoader()

    with pytest.raises(
        EmptyDocumentError,
        match="No textual content found",
    ):
        loader.load(source)
