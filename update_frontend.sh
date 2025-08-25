#!/bin/bash

# Script pour mettre à jour le frontend avec la nouvelle URL
echo "🔧 UPDATING FRONTEND FOR HOSTINGER"
echo "=================================="

# Lire l'URL actuelle du tunnel
if [ -f "tunnel_output.log" ]; then
    PUBLIC_URL=$(grep -o 'https://[^[:space:]]*\.trycloudflare\.com' tunnel_output.log | head -1)
    
    if [ -n "$PUBLIC_URL" ]; then
        echo "🌍 Current API URL: $PUBLIC_URL"
        
        # Mettre à jour la configuration frontend
        echo "REACT_APP_API_URL=$PUBLIC_URL" > frontend/env.production
        echo "✅ Frontend configuration updated!"
        
        # Build le frontend pour Hostinger
        echo "🔨 Building frontend for Hostinger..."
        cd frontend
        
        # Copier la config en .env pour le build
        cp env.production .env.production
        
        npm run build
        
        # Créer le dossier de déploiement
        mkdir -p ../hostinger_deploy
        cp -r build/* ../hostinger_deploy/
        
        cd ..
        
        echo ""
        echo "🎉 FRONTEND READY FOR HOSTINGER!"
        echo "==============================="
        echo "📁 Upload contents of 'hostinger_deploy/' to your Hostinger public_html"
        echo "🌐 Your clients will access: https://ton-site.hostinger.com"
        echo "📡 Which will connect to: $PUBLIC_URL"
        
    else
        echo "❌ No tunnel URL found. Make sure ./START_SERVER.sh is running"
    fi
else
    echo "❌ No tunnel log found. Run ./START_SERVER.sh first"
fi
