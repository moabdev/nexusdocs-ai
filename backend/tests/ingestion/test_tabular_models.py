from nexusdocs.ingestion.domain.models import (
    TabularDocument,
    TabularRecord,
)


def test_tabular_document_exposes_columns_and_records() -> None:
    records = (
        TabularRecord(
            index=0,
            values={
                "shipment_id": "SHP-001",
                "region": "Northeast",
                "delay_days": 2,
            },
        ),
        TabularRecord(
            index=1,
            values={
                "shipment_id": "SHP-002",
                "region": "Southeast",
                "delay_days": 0,
            },
        ),
    )

    document = TabularDocument(
        document_id="KB-008",
        columns=(
            "shipment_id",
            "region",
            "delay_days",
        ),
        records=records,
        metadata={
            "classification": "INTERNAL",
        },
    )

    assert document.document_id == "KB-008"
    assert document.row_count == 2
    assert document.columns == (
        "shipment_id",
        "region",
        "delay_days",
    )
    assert document.records[0].values["region"] == "Northeast"
    assert document.metadata["classification"] == "INTERNAL"


def test_tabular_document_can_be_empty() -> None:
    document = TabularDocument(
        document_id="KB-TEST",
        columns=("id", "value"),
        records=(),
    )

    assert document.row_count == 0
