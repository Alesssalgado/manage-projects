#!/usr/bin/env bash
set -e   # si algo falla, el script para

echo "→ Ruff lint..."
ruff check .

echo "→ Ruff format check..."
ruff format --check .

echo "→ Compilación Python..."
python -m compileall -q .

echo "✓ Todo OK"