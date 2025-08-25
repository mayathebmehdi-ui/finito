#!/bin/bash

# Script pour démarrer l'API avec Firecrawl visible en terminal

set -euo pipefail

PROJECT_ROOT="/home/mehdi/ecommerce2/test1fonctionne"
cd "$PROJECT_ROOT"

echo "🔥 DÉMARRAGE API AVEC FIRECRAWL FALLBACK"
echo "======================================="

# Nettoyage des anciens processus
echo "🧹 Nettoyage des anciens processus..."
pkill -f "python main.py" 2>/dev/null || true
pkill -f "uvicorn" 2>/dev/null || true
killall python3 2>/dev/null || true
sleep 2
echo "✅ Nettoyage terminé."

# Activation de l'environnement virtuel
echo "🐍 Activation de l'environnement virtuel..."
source venv/bin/activate

# Installation des dépendances si nécessaire
echo "📦 Vérification des dépendances..."
pip install -q firecrawl-py >/dev/null 2>&1 || true
python -m playwright install chromium >/dev/null 2>&1 || true

# Démarrage de l'API avec Firecrawl
echo "🔥 Démarrage de l'API avec Firecrawl fallback..."
echo "🌐 API sera disponible sur: http://localhost:8001"
echo "📚 Documentation API: http://localhost:8001/docs"
echo ""
echo "🎯 LOGS EN DIRECT - Cherchez les messages Firecrawl:"
echo "    🔍 'Checking if Firecrawl fallback needed'"
echo "    🤖 'OpenAI decision for Firecrawl'"
echo "    🔥 'Using Firecrawl as fallback'"
echo "    ✅ 'Firecrawl found [field]'"
echo ""
echo "⚡ Pour tester: curl -X POST http://localhost:8001/analyze -H 'Content-Type: application/json' -d '{\"url\": \"https://example.com\"}'"
echo ""
echo "🚨 CTRL+C pour arrêter"
echo "======================================="

# Lancer l'API en mode verbose
export PORT=8001
python main.py
