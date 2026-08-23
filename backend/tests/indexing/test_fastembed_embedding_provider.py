from collections.abc import Iterable
from unittest.mock import patch

import pytest

from nexusdocs.indexing.embeddings.fastembed import (
    FastEmbedEmbeddingProvider,
)


class FakeTextEmbedding:
    def __init__(
        self,
        model_name: str,
    ) -> None:
        self.model_name = model_name

    def embed(
        self,
        texts: Iterable[str],
    ) -> Iterable[tuple[float, ...]]:
        for text in texts:
            yield (
                float(len(text)),
                float(len(text.split())),
                1.0,
            )


def create_provider() -> FastEmbedEmbeddingProvider:
    with patch(
        "nexusdocs.indexing.embeddings.fastembed.TextEmbedding",
        FakeTextEmbedding,
    ):
        return FastEmbedEmbeddingProvider(
            model_name="test-model",
        )


def test_fastembed_provider_exposes_model_name() -> None:
    provider = create_provider()

    assert provider.model_name == "test-model"


def test_fastembed_provider_embeds_single_text() -> None:
    provider = create_provider()

    vector = provider.embed_text(
        "NexusDocs AI",
    )

    assert vector == (
        12.0,
        2.0,
        1.0,
    )


def test_fastembed_provider_embeds_multiple_documents() -> None:
    provider = create_provider()

    vectors = provider.embed_documents(
        (
            "Kafka messaging",
            "Redis caching",
        )
    )

    assert vectors == (
        (
            15.0,
            2.0,
            1.0,
        ),
        (
            13.0,
            2.0,
            1.0,
        ),
    )


def test_fastembed_provider_returns_empty_batch() -> None:
    provider = create_provider()

    assert provider.embed_documents(()) == ()


def test_fastembed_provider_rejects_empty_text() -> None:
    provider = create_provider()

    with pytest.raises(
        ValueError,
        match="text cannot be empty",
    ):
        provider.embed_text("   ")


def test_fastembed_provider_rejects_empty_text_inside_batch() -> None:
    provider = create_provider()

    with pytest.raises(
        ValueError,
        match="texts cannot contain empty values",
    ):
        provider.embed_documents(
            (
                "Kafka",
                "   ",
                "Redis",
            )
        )


def test_fastembed_provider_rejects_empty_model_name() -> None:
    with pytest.raises(
        ValueError,
        match="model_name cannot be empty",
    ):
        FastEmbedEmbeddingProvider(
            model_name="   ",
        )
