from nexusdocs.ingestion.domain.models import (
    DocumentChunk,
    DocumentContent,
)


class RecursiveTextChunker:
    """Split textual documents into overlapping semantic chunks."""

    def __init__(
        self,
        chunk_size: int = 1000,
        chunk_overlap: int = 200,
    ) -> None:
        if chunk_size <= 0:
            raise ValueError("chunk_size must be greater than zero")

        if chunk_overlap < 0:
            raise ValueError("chunk_overlap cannot be negative")

        if chunk_overlap >= chunk_size:
            raise ValueError("chunk_overlap must be smaller than chunk_size")

        self._chunk_size = chunk_size
        self._chunk_overlap = chunk_overlap

    def chunk(
        self,
        document: DocumentContent,
    ) -> tuple[DocumentChunk, ...]:
        if not document.text.strip():
            return ()

        pieces = self._split_text(document.text)

        return tuple(
            DocumentChunk(
                chunk_id=f"{document.document_id}:{index}",
                document_id=document.document_id,
                text=text,
                index=index,
                metadata={
                    **document.metadata,
                    "chunk_index": index,
                },
            )
            for index, text in enumerate(pieces)
        )

    def _split_text(self, text: str) -> tuple[str, ...]:
        chunks: list[str] = []

        start = 0
        text_length = len(text)

        while start < text_length:
            maximum_end = min(
                start + self._chunk_size,
                text_length,
            )

            end = self._find_split_position(
                text=text,
                start=start,
                maximum_end=maximum_end,
            )

            chunk = text[start:end].strip()

            if chunk:
                chunks.append(chunk)

            if end >= text_length:
                break

            start = self._find_overlap_start(
                text=text,
                current_start=start,
                end=end,
            )

        return tuple(chunks)

    def _find_overlap_start(
        self,
        text: str,
        current_start: int,
        end: int,
    ) -> int:
        if self._chunk_overlap == 0:
            return end

        target = max(
            current_start + 1,
            end - self._chunk_overlap,
        )

        separators = (
            "\n\n",
            "\n",
            ". ",
            " ",
        )

        for separator in separators:
            position = text.find(
                separator,
                target,
                end,
            )

            if position != -1:
                candidate = position + len(separator)

                if candidate < end:
                    return candidate

        return target

    @staticmethod
    def _find_split_position(
        text: str,
        start: int,
        maximum_end: int,
    ) -> int:
        if maximum_end >= len(text):
            return len(text)

        separators = (
            "\n\n",
            "\n",
            ". ",
            " ",
        )

        for separator in separators:
            position = text.rfind(
                separator,
                start,
                maximum_end,
            )

            if position > start:
                return position + len(separator)

        return maximum_end
