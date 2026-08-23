#!/usr/bin/env bash

set -e

echo "==> Formatting..."
uv run ruff format .

echo "==> Fixing Ruff issues..."
uv run ruff check . --fix

echo
echo "==> Code formatted and lint fixes applied!"
