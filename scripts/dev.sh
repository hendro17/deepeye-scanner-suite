#!/bin/bash
set -e

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

echo "🛡  DeepEye Scanner Suite — Dev Mode"
echo ""

# 1. Backend
echo "[1/3] Starting FastAPI backend (:8000)..."
.venv/bin/python -m uvicorn api.main:app --reload --port 8000 &
API_PID=$!

# 2. Frontend
echo "[2/3] Starting Vue dev server (:5173)..."
cd web && pnpm dev &
WEB_PID=$!
cd "$ROOT"

# 3. Test target (optional)
echo "[3/3] Test target: run 'npx juice-shop' in separate terminal if needed"
echo ""
echo "Backend:  http://localhost:8000/api/health"
echo "Frontend: http://localhost:5173"
echo ""
echo "Press Ctrl+C to stop."

trap "kill $API_PID $WEB_PID 2>/dev/null; exit 0" INT TERM
wait
