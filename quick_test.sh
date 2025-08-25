#!/bin/bash

# Test rapide Firecrawl - optimisé pour éviter les blocages

set -euo pipefail

PROJECT_ROOT="/home/mehdi/ecommerce2/test1fonctionne"
cd "$PROJECT_ROOT"

echo "⚡ TEST RAPIDE FIRECRAWL FALLBACK"
echo "================================"

# Nettoyer
pkill -f "python main.py" 2>/dev/null || true
sleep 1

# Démarrer API
echo "🚀 Démarrage API optimisée..."
source venv/bin/activate
export PORT=8001
python main.py &
API_PID=$!

# Attendre démarrage
sleep 5

# Test avec un site simple
echo ""
echo "🧪 Test avec Best Buy (site rapide)..."
echo "======================================"

# Lancer analyse
echo "📤 Envoi requête..."
response=$(curl -s -X POST "http://localhost:8001/analyze" \
    -H "Content-Type: application/json" \
    -d '{"url": "https://www.bestbuy.com"}')

echo "✅ Réponse: $response"

# Extraire job_id
job_id=$(echo "$response" | grep -o '"job_id":"[^"]*"' | cut -d'"' -f4)

if [ -n "$job_id" ]; then
    echo "🎯 Job ID: $job_id"
    echo ""
    echo "⏳ Analyse en cours - REGARDEZ LES LOGS CI-DESSUS !"
    echo "    Cherchez ces messages Firecrawl:"
    echo "    🔍 'Checking if Firecrawl fallback needed'"
    echo "    🤖 'OpenAI decision for Firecrawl'"
    echo "    🔥 'Firecrawl searching for'"
    echo "    ✅ 'Firecrawl found'"
    echo ""
    
    # Attendre un peu
    sleep 20
    
    # Vérifier résultat
    echo "📊 Status du job..."
    curl -s "http://localhost:8001/job/$job_id" | grep -o '"status":"[^"]*"' | cut -d'"' -f4
    
    echo ""
    echo "🎉 Analyse terminée ! Résultat:"
    curl -s "http://localhost:8001/results" | tail -c 500
    
else
    echo "❌ Erreur job"
fi

echo ""
echo "🛑 Arrêt de l'API..."
kill $API_PID 2>/dev/null || true

echo "✅ Test terminé !"
