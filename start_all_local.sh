#!/bin/bash

set -euo pipefail

PROJECT_ROOT="/home/mehdi/ecommerce2/test1fonctionne"
BACKEND_PORT="${PORT:-8000}"
FRONTEND_PORT="${FRONTEND_PORT:-3000}"
API_URL_DEFAULT="http://localhost:${BACKEND_PORT}"

cd "$PROJECT_ROOT"

echo "🧹 Stopping old processes..."
pkill -f "python main.py" 2>/dev/null || true
pkill -f "uvicorn" 2>/dev/null || true
pkill -f "react-scripts start" 2>/dev/null || true

if lsof -ti:${BACKEND_PORT} >/dev/null 2>&1; then
  kill -9 $(lsof -ti:${BACKEND_PORT}) 2>/dev/null || true
fi
if lsof -ti:${FRONTEND_PORT} >/dev/null 2>&1; then
  kill -9 $(lsof -ti:${FRONTEND_PORT}) 2>/dev/null || true
fi

echo "🐍 Preparing Python env..."
if [ ! -d "venv" ]; then
  python3 -m venv venv
fi
source venv/bin/activate
python -m pip install --upgrade pip >/dev/null
pip install -r requirements.txt >/dev/null

echo "🎭 Ensuring Playwright Chromium is installed..."
python -m playwright install chromium >/dev/null || true

echo "🚀 Starting backend (FastAPI)..."
export PORT=${BACKEND_PORT}
nohup python main.py > backend.log 2>&1 &
BACKEND_PID=$!

echo "⏳ Waiting for API on http://localhost:${BACKEND_PORT} ..."
ATTEMPTS=0
until curl -sSf "http://localhost:${BACKEND_PORT}/" >/dev/null 2>&1; do
  ATTEMPTS=$((ATTEMPTS+1))
  if [ $ATTEMPTS -gt 60 ]; then
    echo "❌ API didn't start in time. Check backend.log"
    exit 1
  fi
  sleep 1
done
echo "✅ API is up: http://localhost:${BACKEND_PORT} (docs: /docs)"

echo "⚛️ Preparing frontend env..."
API_URL_TO_USE="${REACT_APP_API_URL:-${API_URL_DEFAULT}}"
mkdir -p frontend
cat > frontend/.env.local << EOF
REACT_APP_API_URL=${API_URL_TO_USE}
GENERATE_SOURCEMAP=false
EOF

echo "📦 Installing frontend deps (if needed)..."
pushd frontend >/dev/null
if [ ! -d "node_modules" ]; then
  npm install --legacy-peer-deps
fi

echo "🎨 Starting frontend (React dev server)..."
PORT=${FRONTEND_PORT} BROWSER=none nohup npm start > ../frontend.log 2>&1 &
FRONTEND_PID=$!
popd >/dev/null

echo "⏳ Waiting for frontend on http://localhost:${FRONTEND_PORT} ..."
ATTEMPTS=0
until curl -sSf "http://localhost:${FRONTEND_PORT}" >/dev/null 2>&1; do
  ATTEMPTS=$((ATTEMPTS+1))
  if [ $ATTEMPTS -gt 60 ]; then
    echo "❌ Frontend didn't start in time. Check frontend.log"
    break
  fi
  sleep 1
done

echo ""
echo "✅ Services started"
echo "- Backend API:   http://localhost:${BACKEND_PORT}"
echo "- API Docs:      http://localhost:${BACKEND_PORT}/docs"
echo "- Frontend:      http://localhost:${FRONTEND_PORT}"
echo "- Backend PID:   ${BACKEND_PID} (logs: backend.log)"
echo "- Frontend PID:  ${FRONTEND_PID} (logs: frontend.log)"
echo ""
echo "To stop: kill ${BACKEND_PID} ${FRONTEND_PID} (or Ctrl+C)"

cleanup() {
  echo "\n🛑 Stopping services..."
  kill ${BACKEND_PID} 2>/dev/null || true
  kill ${FRONTEND_PID} 2>/dev/null || true
  echo "✅ Stopped"
}
trap cleanup SIGINT SIGTERM
wait ${BACKEND_PID} ${FRONTEND_PID} 2>/dev/null || true


