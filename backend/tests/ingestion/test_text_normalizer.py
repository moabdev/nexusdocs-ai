from nexusdocs.ingestion.processing.normalizer import TextNormalizer


def test_normalizer_converts_line_endings() -> None:
    normalizer = TextNormalizer()

    text = "NexusDocs\r\nKnowledge\rArchitecture"

    result = normalizer.normalize(text)

    assert result == "NexusDocs\nKnowledge\nArchitecture"


def test_normalizer_removes_trailing_whitespace() -> None:
    normalizer = TextNormalizer()

    text = "NexusDocs   \nKnowledge\t\nArchitecture"

    result = normalizer.normalize(text)

    assert result == "NexusDocs\nKnowledge\nArchitecture"


def test_normalizer_collapses_excessive_blank_lines() -> None:
    normalizer = TextNormalizer()

    text = "NexusDocs\n\n\n\nKnowledge"

    result = normalizer.normalize(text)

    assert result == "NexusDocs\n\nKnowledge"


def test_normalizer_preserves_markdown_structure() -> None:
    normalizer = TextNormalizer()

    text = "# Architecture\n\n## Components\n\n- PostgreSQL\n- Redis\n- Kafka"

    result = normalizer.normalize(text)

    assert result == text


def test_normalizer_removes_surrounding_whitespace() -> None:
    normalizer = TextNormalizer()

    text = "\n\n  NexusDocs AI  \n\n"

    result = normalizer.normalize(text)

    assert result == "NexusDocs AI"
