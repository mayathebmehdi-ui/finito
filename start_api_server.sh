#!/bin/bash

# 🚀 COMMANDE SIMPLE POUR DÉMARRER L'API POUR TES CLIENTS
# Utilise cette commande à chaque fois que tu démarres ton ordi

echo "🚀 Starting E-commerce Policy Analyzer API for clients..."

# Aller dans le bon dossier
cd /home/mehdi/ecommerce2/test1fonctionne

# Arrêter les anciens processus
echo "🛑 Stopping old processes..."
pkill -f "python main.py" 2>/dev/null || true
pkill -f "uvicorn" 2>/dev/null || true

# Attendre un peu
sleep 2

# Activer l'environnement virtuel
echo "🐍 Activating virtual environment..."
source venv/bin/activate

# Démarrer l'API sur toutes les interfaces (0.0.0.0) pour l'accès distant
echo "🌐 Starting API server on all interfaces..."
echo "📡 Clients can access via: http://YOUR_IP:8000"
echo "📚 API Documentation: http://YOUR_IP:8000/docs"
echo ""
echo "🔧 To stop the server: Press Ctrl+C"
echo "----------------------------------------"

# Démarrer le serveur
python main.py

echo "✅ API server stopped."
