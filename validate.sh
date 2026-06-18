
set -e 

echo "→ Ruff lint..."
ruff check .

echo "→ Ruff format check..."
ruff format --check .

echo "→ Compilaction Python..."
python -m compileall -q .

echo "✓ Todo OK"