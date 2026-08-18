#!/usr/bin/env bash

set -e

echo "==> Checking Ruff..."
uv run ruff check .

echo "==> Checking formatting..."
uv run ruff format --check .

echo "==> Running tests..."
uv run pytest

echo
echo "==> All quality checks passed!"
