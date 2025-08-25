#!/bin/bash

echo "🌐 STARTING CLOUDFLARE TUNNEL (100% FREE)"
echo "========================================="

# Arrêter les anciens processus
pkill -f "python main.py" 2>/dev/null || true
pkill -f "cloudflared" 2>/dev/null || true

sleep 2

# Installer Cloudflare Tunnel si nécessaire
if ! command -v cloudflared &> /dev/null; then
    echo "📥 Installing Cloudflare Tunnel..."
    wget -O cloudflared https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64
    chmod +x cloudflared
    sudo mv cloudflared /usr/local/bin/
    echo "✅ Cloudflare Tunnel installed!"
fi

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

# Démarrer le tunnel Cloudflare (GRATUIT, pas d'inscription)
echo ""
echo "🌐 Starting Cloudflare tunnel..."
echo "⏳ This will give you a public URL instantly!"
echo ""

cloudflared tunnel --url http://localhost:8000 &
TUNNEL_PID=$!

echo ""
echo "🎉 SUCCESS! Your API is now accessible worldwide!"
echo "================================================"
echo ""
echo "👆 Look above for the PUBLIC URL (https://xxx.trycloudflare.com)"
echo "📚 Add '/docs' to see API documentation"
echo ""
echo "✅ Share this URL with your clients!"
echo ""
echo "🛑 To stop: Press Ctrl+C"
echo "=========================================="

# Garder les processus en vie
wait
