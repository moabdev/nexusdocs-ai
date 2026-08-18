import csv
from typing import Any

from nexusdocs.ingestion.domain.models import (
    SourceDocument,
    TabularDocument,
    TabularRecord,
)
from nexusdocs.ingestion.exceptions import (
    DocumentNotFoundError,
    EmptyDocumentError,
    UnsupportedDocumentError,
)


class CsvDocumentLoader:
    """Load structured records from CSV documents."""

    SUPPORTED_CONTENT_TYPES = frozenset(
        {
            "text/csv",
            "application/csv",
        }
    )

    def supports(self, source: SourceDocument) -> bool:
        return (
            source.content_type.lower() in self.SUPPORTED_CONTENT_TYPES
            or source.path.suffix.lower() == ".csv"
        )

    def load(self, source: SourceDocument) -> TabularDocument:
        if not source.path.is_file():
            raise DocumentNotFoundError(f"Document not found: {source.path}")

        if not self.supports(source):
            raise UnsupportedDocumentError(
                f"Unsupported document type: {source.content_type}"
            )

        with source.path.open(
            "r",
            encoding="utf-8-sig",
            newline="",
        ) as file:
            reader = csv.DictReader(file)

            if not reader.fieldnames:
                raise EmptyDocumentError(
                    f"No CSV header found in document: {source.path}"
                )

            columns = tuple(reader.fieldnames)

            records = tuple(
                TabularRecord(
                    index=index,
                    values=self._normalize_record(row),
                )
                for index, row in enumerate(reader)
            )

        if not records:
            raise EmptyDocumentError(f"No records found in document: {source.path}")

        metadata = {
            **source.metadata,
            "loader": "csv",
            "row_count": len(records),
            "column_count": len(columns),
        }

        return TabularDocument(
            document_id=source.document_id,
            columns=columns,
            records=records,
            metadata=metadata,
        )

    @staticmethod
    def _normalize_record(
        record: dict[str, str | None],
    ) -> dict[str, Any]:
        return {
            key: value.strip() if value is not None else None
            for key, value in record.items()
        }
