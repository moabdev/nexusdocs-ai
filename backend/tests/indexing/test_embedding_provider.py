from nexusdocs.indexing.embeddings.base import EmbeddingProvider


class FakeEmbeddingProvider:
    def embed_text(
        self,
        text: str,
    ) -> tuple[float, ...]:
        return (float(len(text)), 1.0)

    def embed_documents(
        self,
        texts: tuple[str, ...],
    ) -> tuple[tuple[float, ...], ...]:
        return tuple(self.embed_text(text) for text in texts)


def test_fake_embedding_provider_satisfies_protocol() -> None:
    provider: EmbeddingProvider = FakeEmbeddingProvider()

    vector = provider.embed_text("NexusDocs")

    assert vector == (9.0, 1.0)


def test_embedding_provider_supports_batch_generation() -> None:
    provider: EmbeddingProvider = FakeEmbeddingProvider()

    vectors = provider.embed_documents(
        (
            "NexusDocs",
            "Velox",
        )
    )

    assert vectors == (
        (9.0, 1.0),
        (5.0, 1.0),
    )
