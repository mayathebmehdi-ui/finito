#!/bin/bash

# Script pour build le frontend pour Hostinger
echo "🚀 Building frontend for Hostinger deployment..."

# 1. Aller dans le dossier frontend
cd frontend

# 2. Installer les dépendances si nécessaire
echo "📦 Installing dependencies..."
npm install

# 3. Build en mode production
echo "🔨 Building for production..."
npm run build

# 4. Créer le dossier de déploiement
echo "📁 Creating deployment folder..."
mkdir -p ../hostinger_deploy

# 5. Copier le build
echo "📋 Copying build files..."
cp -r build/* ../hostinger_deploy/

echo "✅ Frontend ready for Hostinger!"
echo "📁 Upload the contents of 'hostinger_deploy' folder to your Hostinger public_html"
echo ""
echo "🔧 IMPORTANT: Edit env.production and replace YOUR_SERVER_IP with your actual IP"
echo "   Example: REACT_APP_API_URL=http://192.168.1.100:8000"
