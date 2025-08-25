#!/bin/bash

# 🚀 COMMANDE SIMPLE - À UTILISER À CHAQUE DÉMARRAGE D'ORDI
# =========================================================

echo "🚀 STARTING E-COMMERCE ANALYZER FOR CLIENTS"
echo "============================================"

# Aller dans le bon dossier
cd /home/mehdi/ecommerce2/test1fonctionne

# Arrêter les anciens processus
echo "🛑 Cleaning old processes..."
pkill -f "python main.py" 2>/dev/null || true
pkill -f "cloudflared" 2>/dev/null || true
sleep 2

# Activer l'environnement virtuel et démarrer l'API
echo "🐍 Starting API server..."
source venv/bin/activate
python main.py &
API_PID=$!

# Attendre que l'API démarre
sleep 5

# Vérifier si l'API fonctionne
if curl -s http://localhost:8000 > /dev/null; then
    echo "✅ API is running locally"
else
    echo "❌ API failed to start"
    exit 1
fi

# Démarrer le tunnel Cloudflare
echo ""
echo "🌐 Starting Cloudflare tunnel..."
echo "⏳ Getting your public URL..."
echo ""

# Démarrer le tunnel et capturer l'URL
cloudflared tunnel --url http://localhost:8000 2>&1 | tee tunnel_output.log &
TUNNEL_PID=$!

# Attendre et extraire l'URL
sleep 10

# Extraire l'URL du log
PUBLIC_URL=$(grep -o 'https://[^[:space:]]*\.trycloudflare\.com' tunnel_output.log | head -1)

if [ -n "$PUBLIC_URL" ]; then
    echo ""
    echo "🎉 SUCCESS! Your API is now LIVE worldwide!"
    echo "============================================="
    echo "🌍 Public API URL: $PUBLIC_URL"
    echo "📚 API Documentation: $PUBLIC_URL/docs"
    echo ""
    echo "🔧 FOR HOSTINGER DEPLOYMENT:"
    echo "Run: ./build_hostinger.sh"
    echo "Use this URL: $PUBLIC_URL"
    echo ""
    echo "💡 COPY THIS URL FOR HOSTINGER BUILD! 👆"
    echo ""
    echo "🛑 To stop: Press Ctrl+C"
    echo "=========================================="
    
    # Sauvegarder l'URL pour le frontend
    echo "REACT_APP_API_URL=$PUBLIC_URL" > frontend/env.production
    echo "✅ Frontend configuration updated automatically!"
    
    # Garder les processus en vie
    wait
else
    echo "❌ Failed to get public URL"
    kill $API_PID $TUNNEL_PID 2>/dev/null
fi
