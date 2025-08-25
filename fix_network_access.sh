#!/bin/bash

echo "🔧 FIXING NETWORK ACCESS FOR CLIENTS"
echo "====================================="

# 1. Ouvrir le port dans le firewall local
echo "🛡️ Opening port 8000 in local firewall..."
sudo ufw allow 8000/tcp
sudo ufw reload

# 2. Vérifier si le service écoute bien
echo ""
echo "👂 Checking if API is listening on port 8000..."
netstat -tlnp | grep :8000

# 3. Afficher les informations réseau
echo ""
echo "🌐 NETWORK CONFIGURATION:"
echo "========================"

LOCAL_IP=$(hostname -I | awk '{print $1}')
echo "🏠 Local IP: $LOCAL_IP"
echo "   ✅ Local clients: http://$LOCAL_IP:8000"

# 4. Vérifier la connectivité locale
echo ""
echo "🧪 Testing local connection..."
curl -s http://localhost:8000 > /dev/null
if [ $? -eq 0 ]; then
    echo "✅ Local API is working"
else
    echo "❌ Local API is not responding"
fi

echo ""
echo "⚠️  POUR L'ACCÈS EXTERNE, TU DOIS:"
echo "1. 🏠 Configurer ton ROUTEUR:"
echo "   - Ouvrir le port 8000"
echo "   - Port forwarding: 8000 → $LOCAL_IP:8000"
echo ""
echo "2. 🌐 Ou utiliser un TUNNEL (plus simple):"
echo "   - Ngrok, Cloudflare Tunnel, etc."
echo ""
echo "3. 📱 Pour tes clients LOCAUX (même WiFi):"
echo "   - Utilise: http://$LOCAL_IP:8000"
echo "   - Ça marche déjà ! ✅"
