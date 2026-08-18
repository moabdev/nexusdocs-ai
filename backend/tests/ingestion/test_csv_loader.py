from pathlib import Path

import pytest

from nexusdocs.ingestion.domain.models import SourceDocument
from nexusdocs.ingestion.exceptions import (
    DocumentNotFoundError,
    EmptyDocumentError,
    UnsupportedDocumentError,
)
from nexusdocs.ingestion.loaders.csv import CsvDocumentLoader


def test_csv_loader_supports_csv_content_type() -> None:
    loader = CsvDocumentLoader()

    source = SourceDocument(
        path=Path("document"),
        document_id="KB-TEST",
        content_type="text/csv",
    )

    assert loader.supports(source)


def test_csv_loader_supports_csv_extension() -> None:
    loader = CsvDocumentLoader()

    source = SourceDocument(
        path=Path("document.csv"),
        document_id="KB-TEST",
        content_type="application/octet-stream",
    )

    assert loader.supports(source)


def test_csv_loader_rejects_unsupported_document() -> None:
    loader = CsvDocumentLoader()

    source = SourceDocument(
        path=Path("document.pdf"),
        document_id="KB-TEST",
        content_type="application/pdf",
    )

    assert not loader.supports(source)


def test_csv_loader_loads_structured_records(
    tmp_path: Path,
) -> None:
    path = tmp_path / "deliveries.csv"

    path.write_text(
        ("shipment_id,region,delay_days\nSHP-001,Northeast,2\nSHP-002,Southeast,0\n"),
        encoding="utf-8",
    )

    source = SourceDocument(
        path=path,
        document_id="KB-008",
        content_type="text/csv",
        metadata={
            "classification": "INTERNAL",
        },
    )

    loader = CsvDocumentLoader()
    document = loader.load(source)

    assert document.document_id == "KB-008"

    assert document.columns == (
        "shipment_id",
        "region",
        "delay_days",
    )

    assert document.row_count == 2

    assert document.records[0].values == {
        "shipment_id": "SHP-001",
        "region": "Northeast",
        "delay_days": "2",
    }

    assert document.metadata == {
        "classification": "INTERNAL",
        "loader": "csv",
        "row_count": 2,
        "column_count": 3,
    }


def test_csv_loader_raises_error_when_file_does_not_exist(
    tmp_path: Path,
) -> None:
    source = SourceDocument(
        path=tmp_path / "missing.csv",
        document_id="KB-TEST",
        content_type="text/csv",
    )

    loader = CsvDocumentLoader()

    with pytest.raises(
        DocumentNotFoundError,
        match="Document not found",
    ):
        loader.load(source)


def test_csv_loader_raises_error_for_unsupported_document(
    tmp_path: Path,
) -> None:
    path = tmp_path / "document.pdf"
    path.write_text("not a pdf", encoding="utf-8")

    source = SourceDocument(
        path=path,
        document_id="KB-TEST",
        content_type="application/pdf",
    )

    loader = CsvDocumentLoader()

    with pytest.raises(
        UnsupportedDocumentError,
        match="Unsupported document type",
    ):
        loader.load(source)


def test_csv_loader_raises_error_when_csv_has_no_records(
    tmp_path: Path,
) -> None:
    path = tmp_path / "empty.csv"
    path.write_text(
        "shipment_id,region,delay_days\n",
        encoding="utf-8",
    )

    source = SourceDocument(
        path=path,
        document_id="KB-TEST",
        content_type="text/csv",
    )

    loader = CsvDocumentLoader()

    with pytest.raises(
        EmptyDocumentError,
        match="No records found",
    ):
        loader.load(source)
