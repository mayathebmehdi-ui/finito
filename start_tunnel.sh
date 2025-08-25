#!/bin/bash

echo "🚀 STARTING API + TUNNEL FOR CLIENTS"
echo "===================================="

# Arrêter les anciens processus
pkill -f "python main.py" 2>/dev/null || true
pkill -f "ngrok" 2>/dev/null || true

sleep 2

# Démarrer l'API en arrière-plan
echo "🐍 Starting API server..."
cd /home/mehdi/ecommerce2/test1fonctionne
source venv/bin/activate
python main.py &
API_PID=$!

# Attendre que l'API démarre
sleep 5

# Vérifier si l'API fonctionne
echo "🧪 Testing API..."
if curl -s http://localhost:8000 > /dev/null; then
    echo "✅ API is running on localhost:8000"
else
    echo "❌ API failed to start"
    kill $API_PID 2>/dev/null
    exit 1
fi

# Démarrer le tunnel Ngrok
echo ""
echo "🌐 Starting Ngrok tunnel..."
echo "⏳ Please wait..."

ngrok http 8000 &
NGROK_PID=$!

# Attendre que Ngrok démarre
sleep 3

# Récupérer l'URL publique
echo ""
echo "🔍 Getting public URL..."
sleep 2

PUBLIC_URL=$(curl -s http://localhost:4040/api/tunnels | grep -o 'https://[^"]*\.ngrok-free\.app')

if [ -n "$PUBLIC_URL" ]; then
    echo ""
    echo "🎉 SUCCESS! Your API is now accessible worldwide:"
    echo "================================================"
    echo "🌍 Public URL: $PUBLIC_URL"
    echo "📚 API Docs: $PUBLIC_URL/docs"
    echo ""
    echo "✅ Share this URL with your clients!"
    echo ""
    echo "🔧 To update frontend for Hostinger:"
    echo "   Edit frontend/env.production"
    echo "   Change REACT_APP_API_URL=$PUBLIC_URL"
    echo ""
    echo "🛑 To stop: Press Ctrl+C"
    echo "=========================================="
    
    # Garder les processus en vie
    wait
else
    echo "❌ Failed to get public URL"
    echo "💡 Try: ngrok config add-authtoken YOUR_TOKEN"
    kill $API_PID $NGROK_PID 2>/dev/null
fi
