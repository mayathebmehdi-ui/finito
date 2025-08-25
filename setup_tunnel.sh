#!/bin/bash

echo "🌐 SETTING UP FREE TUNNEL FOR CLIENT ACCESS"
echo "==========================================="

# 1. Télécharger Ngrok si pas installé
if ! command -v ngrok &> /dev/null; then
    echo "📥 Downloading Ngrok..."
    
    # Détecter l'architecture
    ARCH=$(uname -m)
    if [[ "$ARCH" == "x86_64" ]]; then
        NGROK_URL="https://bin.equinox.io/c/bNyj1mQVY4c/ngrok-v3-stable-linux-amd64.tgz"
    else
        NGROK_URL="https://bin.equinox.io/c/bNyj1mQVY4c/ngrok-v3-stable-linux-arm64.tgz"
    fi
    
    wget -O ngrok.tgz $NGROK_URL
    tar -xzf ngrok.tgz
    sudo mv ngrok /usr/local/bin/
    rm ngrok.tgz
    
    echo "✅ Ngrok installed!"
else
    echo "✅ Ngrok already installed!"
fi

echo ""
echo "🔧 SETUP INSTRUCTIONS:"
echo "====================="
echo "1. Go to: https://ngrok.com/signup (FREE account)"
echo "2. Get your authtoken"
echo "3. Run: ngrok config add-authtoken YOUR_TOKEN"
echo "4. Then run: ./start_tunnel.sh"
echo ""
echo "💡 Or skip signup and use without auth (limited):"
echo "   Just run: ./start_tunnel.sh"
