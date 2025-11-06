#!/bin/bash
# Start the AetherLink API server

cd "$(dirname "$0")"
export PYTHONPATH="$(pwd)"

echo "🚀 Starting AetherLink API Server..."
echo "📍 Working directory: $(pwd)"
echo "🐍 Python: /home/rlong/Sandbox/aetherlink/.venv/bin/python"
echo ""

/home/rlong/Sandbox/aetherlink/.venv/bin/python -m uvicorn app.main:app \
    --reload \
    --host 0.0.0.0 \
    --port 8000
