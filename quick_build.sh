#!/bin/bash

# Script rapide pour build avec une nouvelle URL
echo "🔧 QUICK BUILD FOR HOSTINGER"
echo "============================"

# Demander la nouvelle URL
echo "🌐 Enter your new Cloudflare URL:"
echo "   (Example: https://your-new-url.trycloudflare.com)"
read -p "URL: " NEW_URL

if [ -z "$NEW_URL" ]; then
    echo "❌ No URL provided"
    exit 1
fi

echo "✅ Using URL: $NEW_URL"

# Mettre à jour la config
echo "REACT_APP_API_URL=$NEW_URL" > frontend/.env.production

# Build
echo "🔨 Building frontend..."
cd frontend
npm run build

# Copier vers hostinger_deploy
echo "📁 Preparing for Hostinger..."
cd ..
rm -rf hostinger_deploy
mkdir -p hostinger_deploy
cp -r frontend/build/* hostinger_deploy/

echo ""
echo "🎉 READY FOR HOSTINGER!"
echo "======================"
echo "📁 Upload contents of 'hostinger_deploy/' folder"
echo "🌐 Your frontend will connect to: $NEW_URL"
echo ""
echo "📋 TO UPLOAD:"
echo "1. Go to Hostinger cPanel"
echo "2. File Manager → public_html" 
echo "3. Delete old files"
echo "4. Upload everything from 'hostinger_deploy/'"
