#!/usr/bin/env bash
set -euo pipefail

# Helper: run with sudo if not root
sudo_if_needed() {
  if [ "${EUID:-$(id -u)}" -ne 0 ]; then
    sudo "$@"
  else
    "$@"
  fi
}

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")"/.. && pwd)"
cd "$PROJECT_ROOT"

echo "[1/6] Freeing port 8000 (local uvicorn) if used..."
fuser -k 8000/tcp 2>/dev/null || true
pkill -f "uvicorn|main:app|python3 main.py" 2>/dev/null || true

echo "[2/6] Starting Docker daemon (dockerd) if not running..."
if ! pgrep -x dockerd >/dev/null 2>&1; then
  sudo_if_needed nohup dockerd > /tmp/dockerd.log 2>&1 &
  sleep 5
fi

echo "[3/6] Checking Docker connectivity..."
if ! sudo_if_needed docker version >/dev/null 2>&1; then
  echo "❌ Docker daemon not reachable. See /tmp/dockerd.log"
  tail -n 100 /tmp/dockerd.log || true
  exit 1
fi

echo "[4/6] Building image policy-analyzer..."
sudo_if_needed docker build -t policy-analyzer -f server/Dockerfile .

echo "[5/6] Reading API keys from .env if present..."
OPENAI="${OPENAI_API_KEY:-}"
FIRE="${FIRECRAWL_API_KEY:-}"
if [ -z "${OPENAI}" ] && [ -f .env ]; then
  OPENAI=$(grep -E '^OPENAI_API_KEY=' .env | cut -d= -f2- || true)
fi
if [ -z "${FIRE}" ] && [ -f .env ]; then
  FIRE=$(grep -E '^FIRECRAWL_API_KEY=' .env | cut -d= -f2- || true)
fi

if [ -z "${OPENAI}" ] || [ -z "${FIRE}" ]; then
  echo "⚠️ Missing OPENAI_API_KEY or FIRECRAWL_API_KEY. Set env vars or .env before running."
  exit 1
fi

echo "[6/6] Running container on port 8001..."
sudo_if_needed docker rm -f policy-analyzer >/dev/null 2>&1 || true
sudo_if_needed docker run -d --name policy-analyzer \
  -p 8001:8000 \
  -e OPENAI_API_KEY="${OPENAI}" \
  -e FIRECRAWL_API_KEY="${FIRE}" \
  -e FIRECRAWL_SEARCH_ONLY=true \
  policy-analyzer >/dev/null

echo "✅ Container started: http://localhost:8001/docs"
sudo_if_needed docker ps --filter name=policy-analyzer


