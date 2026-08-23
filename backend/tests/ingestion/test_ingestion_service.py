from pathlib import Path

from nexusdocs.ingestion.domain.models import (
    DocumentContent,
    SourceDocument,
    TabularDocument,
    TabularRecord,
)
from nexusdocs.ingestion.loaders.resolver import DocumentLoaderResolver
from nexusdocs.ingestion.service import IngestionService


class FakeLoader:
    def __init__(self) -> None:
        self.loaded = False

    def supports(self, source: SourceDocument) -> bool:
        return source.content_type == "text/plain"

    def load(self, source: SourceDocument) -> DocumentContent:
        self.loaded = True

        return DocumentContent(
            document_id=source.document_id,
            text="NexusDocs content",
            metadata=source.metadata,
        )


def test_ingestion_service_resolves_and_loads_document() -> None:
    loader = FakeLoader()

    resolver = DocumentLoaderResolver(
        loaders=(loader,),
    )

    service = IngestionService(
        resolver=resolver,
    )

    source = SourceDocument(
        path=Path("document.txt"),
        document_id="KB-TEST",
        content_type="text/plain",
        metadata={
            "status": "ACTIVE",
        },
    )

    result = service.ingest(source)

    assert isinstance(result, DocumentContent)
    assert loader.loaded
    assert result.document_id == "KB-TEST"
    assert result.text == "NexusDocs content"
    assert result.metadata == {
        "status": "ACTIVE",
    }


class FakeCsvLoader:
    def supports(self, source: SourceDocument) -> bool:
        return source.content_type == "text/csv"

    def load(self, source: SourceDocument) -> TabularDocument:
        return TabularDocument(
            document_id=source.document_id,
            columns=("shipment_id", "delay_days"),
            records=(
                TabularRecord(
                    index=0,
                    values={
                        "shipment_id": "SHP-001",
                        "delay_days": "2",
                    },
                ),
            ),
            metadata=source.metadata,
        )


def test_ingestion_service_supports_tabular_documents() -> None:
    resolver = DocumentLoaderResolver(
        loaders=(FakeCsvLoader(),),
    )

    service = IngestionService(
        resolver=resolver,
    )

    source = SourceDocument(
        path=Path("deliveries.csv"),
        document_id="KB-008",
        content_type="text/csv",
    )

    result = service.ingest(source)

    assert isinstance(result, TabularDocument)
    assert result.document_id == "KB-008"
    assert result.row_count == 1
    assert result.records[0].values["shipment_id"] == "SHP-001"
