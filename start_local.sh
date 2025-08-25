#!/bin/bash

set -euo pipefail

echo "🚀 Starting E-commerce Policy Analyzer API (local)"

# Go to project directory
cd /home/mehdi/ecommerce2/test1fonctionne

# Stop any previous local servers to free the port
echo "🛑 Stopping any previously running servers..."
pkill -f "python main.py" 2>/dev/null || true
pkill -f "uvicorn" 2>/dev/null || true

# Create and activate virtual environment
if [ ! -d "venv" ]; then
  echo "🐍 Creating virtual environment..."
  python3 -m venv venv
fi
echo "🐍 Activating virtual environment..."
source venv/bin/activate

# Upgrade pip and install dependencies
echo "📦 Installing Python dependencies..."
python -m pip install --upgrade pip >/dev/null
pip install -r requirements.txt >/dev/null

# Ensure Playwright browser is installed (safe to re-run)
echo "🎭 Ensuring Playwright Chromium is installed..."
python -m playwright install chromium >/dev/null || true

# Check OpenAI key presence (env or .env)
if [ -z "${OPENAI_API_KEY:-}" ]; then
  if ! grep -q "^OPENAI_API_KEY=" .env 2>/dev/null; then
    echo "⚠️  OPENAI_API_KEY not found in environment or .env. The analyzer will fail."
    echo "   Add it to .env or export it before running: export OPENAI_API_KEY=\"sk-...\""
  fi
fi

# Force local binding (optional; main.py defaults to 8000)
export PORT=${PORT:-8000}

echo ""
echo "🌐 Local API:   http://localhost:${PORT}"
echo "📚 API Docs:    http://localhost:${PORT}/docs"
echo "🛑 Stop:        Ctrl+C"
echo "----------------------------------------"

# Run API (uvicorn is launched inside main.py)
python main.py

echo "✅ API server stopped."



