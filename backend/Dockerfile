FROM ghcr.io/astral-sh/uv:python3.12-bookworm-slim

WORKDIR /app

# Configure uv environment
ENV UV_COMPILE_BYTECODE=1
ENV UV_LINK_MODE=copy
ENV PYTHONUNBUFFERED=1

# Copy project specification files
COPY pyproject.toml uv.lock ./

# Install project dependencies
RUN uv sync --frozen --no-dev --no-install-project

# Copy source code and scripts
COPY src ./src
COPY scripts ./scripts
COPY README.md ./

# Install project package
RUN uv sync --frozen --no-dev

# Place virtual environment binaries in PATH
ENV PATH="/app/.venv/bin:$PATH"

EXPOSE 8000 8501

CMD ["uvicorn", "nexusdocs.main:app", "--host", "0.0.0.0", "--port", "8000"]
