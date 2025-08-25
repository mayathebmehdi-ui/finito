#!/bin/bash

echo "🌐 Configuration réseau pour serveur API"
echo "======================================="

# Obtenir les adresses IP
echo "📡 Vos adresses IP :"
echo "-------------------"
echo "IP locale (LAN) : $(hostname -I | awk '{print $1}')"
echo "IP publique : $(curl -s ifconfig.me 2>/dev/null || echo "Non disponible")"

# Vérifier le pare-feu
echo ""
echo "🔥 Configuration du pare-feu :"
echo "-----------------------------"

# Pour Ubuntu/Debian avec UFW
if command -v ufw &> /dev/null; then
    echo "UFW détecté. Configuration du port 8000..."
    sudo ufw allow 8000/tcp
    echo "✅ Port 8000 ouvert avec UFW"
fi

# Pour les systèmes avec firewalld
if command -v firewall-cmd &> /dev/null; then
    echo "Firewalld détecté. Configuration du port 8000..."
    sudo firewall-cmd --permanent --add-port=8000/tcp
    sudo firewall-cmd --reload
    echo "✅ Port 8000 ouvert avec firewalld"
fi

# Vérifier si le port est en écoute
echo ""
echo "🔍 Vérification des ports :"
echo "---------------------------"
if command -v ss &> /dev/null; then
    echo "Ports en écoute :"
    ss -tlnp | grep :8000 || echo "Port 8000 pas encore en écoute (normal si le serveur n'est pas démarré)"
fi

echo ""
echo "📋 Instructions pour vos clients :"
echo "===================================="
LOCAL_IP=$(hostname -I | awk '{print $1}')
echo "URL de l'API : http://$LOCAL_IP:8000"
echo "Documentation : http://$LOCAL_IP:8000/docs"
echo ""
echo "⚠️ IMPORTANT :"
echo "- Assurez-vous que votre ordinateur reste allumé"
echo "- Votre IP locale peut changer après un redémarrage du routeur"
echo "- Pour un accès depuis Internet, configurez le port forwarding sur votre routeur"
echo ""
echo "🔧 Pour tester depuis un autre appareil :"
echo "curl http://$LOCAL_IP:8000/"
