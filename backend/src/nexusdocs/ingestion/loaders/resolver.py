from collections.abc import Sequence

from nexusdocs.ingestion.domain.models import SourceDocument
from nexusdocs.ingestion.exceptions import DocumentLoaderNotFoundError
from nexusdocs.ingestion.loaders.base import DocumentLoader


class DocumentLoaderResolver:
    """Resolve the appropriate loader for a source document."""

    def __init__(
        self,
        loaders: Sequence[DocumentLoader],
    ) -> None:
        self._loaders = tuple(loaders)

    def resolve(
        self,
        source: SourceDocument,
    ) -> DocumentLoader:
        for loader in self._loaders:
            if loader.supports(source):
                return loader

        raise DocumentLoaderNotFoundError(
            f"No document loader found for: {source.path}"
        )
