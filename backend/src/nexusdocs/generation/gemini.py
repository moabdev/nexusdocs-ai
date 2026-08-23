from google import genai

from nexusdocs.generation.base import LLMProvider


class GeminiLLMProvider(LLMProvider):
    """Generate grounded answers using the Gemini API."""

    def __init__(
        self,
        api_key: str,
        model: str = "gemini-2.5-flash",
    ) -> None:
        if not api_key.strip():
            raise ValueError("Gemini API key cannot be empty")

        self._client = genai.Client(api_key=api_key)
        self._model = model

    def generate(
        self,
        *,
        question: str,
        context: str,
    ) -> str:
        prompt = f"""
You are NexusDocs AI, an enterprise knowledge assistant.

Answer the user's question exclusively from the CONTEXT below.

Rules:
- Do not use external knowledge.
- Do not invent information.
- If the context does not contain enough information, say clearly that
  the information was not found in the available documents.
- Answer in the same language as the user's question.
- Be concise and factual.
- Do not invent document names or citations. Sources are handled
  separately by the application.

CONTEXT:
{context}

QUESTION:
{question}

ANSWER:
""".strip()

        response = self._client.models.generate_content(
            model=self._model,
            contents=prompt,
        )

        if not response.text:
            raise RuntimeError("Gemini returned an empty response")

        return response.text.strip()
