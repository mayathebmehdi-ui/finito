#!/bin/bash

# Script pour obtenir les informations du serveur
echo "🌐 SERVER INFORMATION FOR CLIENTS"
echo "================================="

# IP locale
LOCAL_IP=$(hostname -I | awk '{print $1}')
echo "🏠 Local Network IP: $LOCAL_IP"
echo "   Clients on same network: http://$LOCAL_IP:8000"

# IP publique (si accessible)
echo ""
echo "🌍 Checking public IP..."
PUBLIC_IP=$(curl -s ifconfig.me 2>/dev/null || echo "Unable to get public IP")
if [ "$PUBLIC_IP" != "Unable to get public IP" ]; then
    echo "🌍 Public IP: $PUBLIC_IP"
    echo "   External clients: http://$PUBLIC_IP:8000"
    echo "   ⚠️  Make sure port 8000 is open in your router/firewall"
else
    echo "❌ Could not determine public IP"
fi

echo ""
echo "📚 API Documentation will be available at:"
echo "   http://$LOCAL_IP:8000/docs"
echo ""
echo "🔧 To update frontend configuration:"
echo "   Edit frontend/env.production"
echo "   Replace YOUR_SERVER_IP with: $LOCAL_IP"
