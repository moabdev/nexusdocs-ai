import re


class TextNormalizer:
    """Normalize textual documents while preserving semantic structure."""

    _EXCESSIVE_BLANK_LINES = re.compile(r"\n{3,}")

    def normalize(self, text: str) -> str:
        normalized = text.replace("\r\n", "\n").replace("\r", "\n")

        lines = (line.rstrip() for line in normalized.splitlines())

        normalized = "\n".join(lines)
        normalized = self._EXCESSIVE_BLANK_LINES.sub(
            "\n\n",
            normalized,
        )

        return normalized.strip()
