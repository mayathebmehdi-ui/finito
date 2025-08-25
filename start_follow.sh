#!/usr/bin/env bash
set -euo pipefail

PROJECT_DIR="/home/mehdi/ecommerce2/test1fonctionne"
PORT="${PORT:-8000}"
FRONTEND_DIR="$PROJECT_DIR/frontend"
FRONTEND_PORT="${FRONTEND_PORT:-5173}"

cd "$PROJECT_DIR"

echo "============================================"
echo "🚀 Starting E-commerce Policy Analyzer"
echo "📁 Project: $PROJECT_DIR"
echo "🔌 API Port: $PORT"
echo "============================================"

# Activate venv
if [ -d venv ]; then
  # shellcheck disable=SC1091
  source venv/bin/activate
else
  echo "❌ venv not found. Create it first: python3 -m venv venv && source venv/bin/activate && pip install -r requirements.txt"
  exit 1
fi

# Load .env if present
if [ -f .env ]; then
  set -a; . ./.env; set +a
else
  echo "⚠️  .env not found (continuing)."
fi

# Keys presence summary (without printing full secrets)
echo "🔑 OPENAI_API_KEY:    ${OPENAI_API_KEY:+SET}" 
echo "🔑 FIRECRAWL_API_KEY: ${FIRECRAWL_API_KEY:+SET}"

echo ""
echo "🌐 API:        http://localhost:$PORT"
echo "📚 Docs:       http://localhost:$PORT/docs"
echo "📦 Export CSV: http://localhost:$PORT/export/csv"
if [ -d "$FRONTEND_DIR" ]; then
  echo "🖥️  Frontend:   http://localhost:$FRONTEND_PORT (dev server)"
  echo "               or http://localhost:$PORT/app (static if built)"
fi
echo ""

# Ensure log files exist
touch backend.log frontend.log

# Start API (background)
echo "▶️  Starting API (uvicorn)…"
nohup uvicorn main:app --host 0.0.0.0 --port "$PORT" > backend.log 2>&1 &
API_PID=$!
sleep 1

# Optionally start frontend dev server
FE_PID=""
if [ -d "$FRONTEND_DIR" ] && [ -f "$FRONTEND_DIR/package.json" ]; then
  echo "▶️  Starting Frontend dev server…"
  if [ ! -d "$FRONTEND_DIR/node_modules" ]; then
    ( cd "$FRONTEND_DIR" && (npm ci --silent || npm install --silent) ) || echo "⚠️  npm install failed; continuing"
  fi
  if grep -q '"dev"' "$FRONTEND_DIR/package.json"; then
    ( cd "$FRONTEND_DIR" && nohup npm run dev -- --port "$FRONTEND_PORT" > ../frontend.log 2>&1 & )
    FE_PID=$!
  else
    ( cd "$FRONTEND_DIR" && nohup npm start > ../frontend.log 2>&1 & )
    FE_PID=$!
  fi
  sleep 1
else
  echo "ℹ️  Frontend directory not found; skipping dev server."
fi

echo "📝 Following logs (Ctrl+C to stop)…"
tail -n +1 -f backend.log frontend.log


