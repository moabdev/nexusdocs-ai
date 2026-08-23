from collections.abc import Iterable

from fastembed import TextEmbedding


class FastEmbedEmbeddingProvider:
    """Generate local dense embeddings using FastEmbed."""

    def __init__(
        self,
        model_name: str,
    ) -> None:
        if not model_name.strip():
            raise ValueError("model_name cannot be empty")

        self._model_name = model_name
        self._model = TextEmbedding(
            model_name=model_name,
        )

    @property
    def model_name(self) -> str:
        return self._model_name

    def embed_text(
        self,
        text: str,
    ) -> tuple[float, ...]:
        """Generate an embedding for a single text."""
        if not text.strip():
            raise ValueError("text cannot be empty")

        embeddings = self._model.embed((text,))

        vector = next(iter(embeddings))

        return self._to_vector(vector)

    def embed_documents(
        self,
        texts: tuple[str, ...],
    ) -> tuple[tuple[float, ...], ...]:
        """Generate embeddings for multiple documents."""
        if not texts:
            return ()

        if any(not text.strip() for text in texts):
            raise ValueError("texts cannot contain empty values")

        embeddings = self._model.embed(texts)

        return tuple(self._to_vector(vector) for vector in embeddings)

    @staticmethod
    def _to_vector(
        vector: Iterable[float],
    ) -> tuple[float, ...]:
        return tuple(float(value) for value in vector)
