import os
from typing import Any

import httpx
import streamlit as st

API_URL = os.getenv(
    "NEXUSDOCS_API_URL",
    "http://localhost:8000",
)

REQUEST_TIMEOUT = 60.0


def ask_nexusdocs(question: str) -> dict[str, Any]:
    """Send a question to the NexusDocs API."""
    response = httpx.post(
        f"{API_URL}/query",
        json={
            "question": question,
        },
        timeout=REQUEST_TIMEOUT,
    )

    response.raise_for_status()

    return response.json()


def render_sources(
    sources: list[dict[str, Any]],
) -> None:
    """Render the sources used to generate an answer."""
    if not sources:
        return

    with st.expander(
        f"Fontes consultadas ({len(sources)})",
        expanded=False,
    ):
        for index, source in enumerate(
            sources,
            start=1,
        ):
            document_id = source.get(
                "document_id",
                "Documento desconhecido",
            )

            chunk_id = source.get(
                "chunk_id",
                "N/A",
            )

            score = source.get("score")

            st.markdown(f"**{index}. {document_id}**")

            st.caption(f"Chunk: {chunk_id}")

            if isinstance(
                score,
                (int, float),
            ):
                normalized_score = max(
                    0.0,
                    min(
                        float(score),
                        1.0,
                    ),
                )

                st.progress(
                    normalized_score,
                    text=f"Relevância: {float(score):.1%}",
                )

            metadata = source.get("metadata") or {}

            if metadata:
                st.json(metadata)

            if index < len(sources):
                st.divider()


def render_sidebar() -> None:
    """Render application information."""
    with st.sidebar:
        st.title("NexusDocs AI")

        st.caption("Enterprise Knowledge Intelligence")

        st.divider()

        st.markdown(
            """
### Sobre

O **NexusDocs AI** utiliza Retrieval-Augmented Generation
(RAG) para responder perguntas com base na documentação
corporativa.

### Pipeline

**Documentos**

↓

**Extração e normalização**

↓

**Chunking**

↓

**Embeddings**

↓

**Qdrant**

↓

**Recuperação semântica**

↓

**Gemini**

↓

**Resposta fundamentada**
"""
        )

        st.divider()

        st.caption(
            "As respostas são geradas por inteligência "
            "artificial e devem ser validadas nas fontes "
            "indicadas."
        )


def initialize_session() -> None:
    """Initialize Streamlit session state."""
    if "messages" not in st.session_state:
        st.session_state.messages = []


def render_history() -> None:
    """Render conversation history."""
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

            if message["role"] == "assistant":
                render_sources(
                    message.get(
                        "sources",
                        [],
                    )
                )


def main() -> None:
    """Run the NexusDocs Streamlit application."""
    st.set_page_config(
        page_title="NexusDocs AI",
        page_icon="📚",
        layout="wide",
    )

    render_sidebar()

    st.title("NexusDocs AI")

    st.markdown(
        """
### Assistente de conhecimento corporativo

Faça perguntas sobre a base de conhecimento da organização.

O NexusDocs utiliza recuperação semântica para localizar
informações relevantes e gerar respostas fundamentadas nos
documentos disponíveis.
"""
    )

    st.info(
        "Você está conversando com um agente de inteligência "
        "artificial. Confira as fontes antes de tomar decisões "
        "importantes."
    )

    initialize_session()
    render_history()

    question = st.chat_input("Pergunte algo sobre os documentos...")

    if not question:
        return

    question = question.strip()

    if not question:
        return

    st.session_state.messages.append(
        {
            "role": "user",
            "content": question,
        }
    )

    with st.chat_message("user"):
        st.markdown(question)

    with (
        st.chat_message("assistant"),
        st.spinner("Consultando a base de conhecimento..."),
    ):
        try:
            result = ask_nexusdocs(question)

            answer = result.get(
                "answer",
                "Não foi possível gerar uma resposta.",
            )

            sources = result.get(
                "sources",
                [],
            )

            st.markdown(answer)

            render_sources(sources)

            st.session_state.messages.append(
                {
                    "role": "assistant",
                    "content": answer,
                    "sources": sources,
                }
            )

        except httpx.HTTPStatusError as exc:
            status_code = exc.response.status_code

            error_message = f"A API do NexusDocs retornou um erro ({status_code})."

            st.error(error_message)

            st.session_state.messages.append(
                {
                    "role": "assistant",
                    "content": error_message,
                    "sources": [],
                }
            )

        except httpx.RequestError:
            error_message = (
                "Não foi possível conectar à API do "
                "NexusDocs. Verifique se o backend está "
                "em execução."
            )

            st.error(error_message)

            st.session_state.messages.append(
                {
                    "role": "assistant",
                    "content": error_message,
                    "sources": [],
                }
            )


if __name__ == "__main__":
    main()
