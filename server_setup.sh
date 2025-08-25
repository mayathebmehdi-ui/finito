#!/bin/bash

# Configuration serveur local pour clients externes
echo "🖥️ Configuration de votre ordinateur comme serveur API..."

# Arrêter les anciens processus
echo "🛑 Arrêt des anciens processus..."
pkill -f "python main.py" 2>/dev/null || true
pkill -f "uvicorn" 2>/dev/null || true

# Créer l'environnement virtuel
echo "🔧 Configuration de l'environnement Python..."
python3 -m venv venv
source venv/bin/activate

# Installer les dépendances
echo "📦 Installation des dépendances..."
pip install --upgrade pip
pip install -r requirements.txt

# Installer les navigateurs Playwright
echo "🎭 Installation des navigateurs Playwright..."
python -m playwright install chromium

# Vérifier que le fichier .env existe
if [ ! -f .env ]; then
    echo "⚠️ Fichier .env manquant ! Création automatique..."
    echo "OPENAI_API_KEY=your_openai_key_here" > .env
    echo "DATABASE_URL=sqlite:///./ecommerce_analyzer.db" >> .env
    echo "CORS_ORIGINS=*" >> .env
    echo "PORT=8000" >> .env
fi

# Obtenir l'adresse IP locale
LOCAL_IP=$(hostname -I | awk '{print $1}')
echo "📡 Votre adresse IP locale : $LOCAL_IP"

# Démarrer le serveur
echo "🚀 Démarrage du serveur API..."
echo "🌐 API accessible sur :"
echo "   - Local: http://localhost:8000"
echo "   - Réseau: http://$LOCAL_IP:8000"
echo ""
echo "📋 Pour vos clients, utilisez : http://$LOCAL_IP:8000"
echo ""
echo "⚠️ Assurez-vous que le port 8000 est ouvert dans votre pare-feu !"
echo ""
echo "Appuyez sur Ctrl+C pour arrêter le serveur"

# Démarrer avec uvicorn
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
