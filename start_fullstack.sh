#!/bin/bash

echo "🚀 Démarrage de la plateforme E-commerce Policy Analyzer (Full Stack)"
echo "================================================================="

# Fonction pour nettoyer les processus à l'arrêt
cleanup() {
    echo ""
    echo "🛑 Arrêt des services..."
    pkill -f "python main.py" 2>/dev/null || true
    pkill -f "npm start" 2>/dev/null || true
    pkill -f "react-scripts start" 2>/dev/null || true
    exit 0
}

# Capturer Ctrl+C
trap cleanup SIGINT SIGTERM

# Obtenir l'IP locale
LOCAL_IP=$(hostname -I | awk '{print $1}')

echo "📡 Configuration réseau :"
echo "  - IP locale : $LOCAL_IP"
echo "  - Backend API : http://$LOCAL_IP:8000"
echo "  - Frontend : http://localhost:3000"
echo ""

# Vérifier que l'environnement virtuel existe
if [ ! -d "venv" ]; then
    echo "🔧 Création de l'environnement virtuel..."
    python3 -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
    python -m playwright install chromium
fi

# Démarrer le backend
echo "🖥️ Démarrage du backend API..."
source venv/bin/activate
python main.py &
BACKEND_PID=$!

# Attendre que le backend soit prêt
echo "⏳ Attente du démarrage du backend..."
sleep 5

# Vérifier que le backend fonctionne
if curl -s http://localhost:8000/ > /dev/null; then
    echo "✅ Backend API démarré avec succès"
else
    echo "❌ Erreur : Backend API non accessible"
    kill $BACKEND_PID 2>/dev/null
    exit 1
fi

# Démarrer le frontend
echo "🌐 Démarrage du frontend React..."
cd frontend
BROWSER=none npm start &
FRONTEND_PID=$!
cd ..

echo ""
echo "🎉 Plateforme démarrée avec succès !"
echo "=================================="
echo ""
echo "📱 Interfaces utilisateur :"
echo "  🌐 Frontend (Interface Web) : http://localhost:3000"
echo "  🔧 API Documentation : http://$LOCAL_IP:8000/docs"
echo "  📊 API Backend : http://$LOCAL_IP:8000"
echo ""
echo "👥 Pour vos clients :"
echo "  📋 URL API : http://$LOCAL_IP:8000"
echo "  📖 Guide : client_guide.md"
echo ""
echo "⚠️  Gardez cette fenêtre ouverte pour maintenir les services actifs"
echo "🛑 Appuyez sur Ctrl+C pour arrêter tous les services"
echo ""

# Attendre indéfiniment
wait
