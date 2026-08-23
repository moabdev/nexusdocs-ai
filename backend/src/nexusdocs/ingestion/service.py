from nexusdocs.ingestion.domain.models import SourceDocument
from nexusdocs.ingestion.loaders.base import IngestionResult
from nexusdocs.ingestion.loaders.resolver import DocumentLoaderResolver


class IngestionService:
    """Coordinate document ingestion using registered loaders."""

    def __init__(
        self,
        resolver: DocumentLoaderResolver,
    ) -> None:
        self._resolver = resolver

    def ingest(
        self,
        source: SourceDocument,
    ) -> IngestionResult:
        loader = self._resolver.resolve(source)

        return loader.load(source)
