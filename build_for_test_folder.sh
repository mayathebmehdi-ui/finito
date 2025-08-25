#!/bin/bash

echo "🔧 BUILDING FOR HOSTINGER /test/ FOLDER"
echo "======================================="

# Demander l'URL de l'API
echo "🌐 Enter your API URL from Cloudflare tunnel:"
read -p "API URL: " API_URL

if [ -z "$API_URL" ]; then
    echo "❌ API URL is required!"
    exit 1
fi

echo "✅ Using API URL: $API_URL"

# Créer la configuration pour sous-dossier
echo "🔧 Creating configuration for /test/ subdirectory..."
cat > frontend/.env.production << EOF
REACT_APP_API_URL=$API_URL
PUBLIC_URL=/test
GENERATE_SOURCEMAP=false
EOF

# Build le frontend
echo "🔨 Building React app for /test/ folder..."
cd frontend
npm run build
cd ..

# Créer le dossier de déploiement
echo "📁 Preparing for Hostinger /test/ deployment..."
rm -rf hostinger_test_deploy
mkdir -p hostinger_test_deploy

# Copier tous les fichiers
cp -r frontend/build/* hostinger_test_deploy/

# Créer .htaccess spécial pour sous-dossier
cat > hostinger_test_deploy/.htaccess << 'EOF'
# React Router pour sous-dossier /test/
RewriteEngine On
RewriteBase /test/

# Handle React routes
RewriteRule ^index\.html$ - [L]
RewriteCond %{REQUEST_FILENAME} !-f
RewriteCond %{REQUEST_FILENAME} !-d
RewriteRule . /test/index.html [L]

# CORS headers pour API externe
<IfModule mod_headers.c>
    Header always set Access-Control-Allow-Origin "*"
    Header always set Access-Control-Allow-Methods "GET, POST, OPTIONS, DELETE, PUT"
    Header always set Access-Control-Allow-Headers "Content-Type, Authorization"
</IfModule>
EOF

echo ""
echo "🎉 BUILD READY FOR /test/ FOLDER!"
echo "================================"
echo "📁 Upload contents of 'hostinger_test_deploy/' to public_html/test/"
echo "🌐 Your site will be: https://mehdia.dev/test/"
echo "📡 Connected to API: $API_URL"
echo ""
echo "📋 UPLOAD INSTRUCTIONS:"
echo "1. Hostinger cPanel → File Manager"
echo "2. public_html/test/ (create test folder if needed)"
echo "3. Upload ALL contents of 'hostinger_test_deploy/'"
echo "4. Access: https://mehdia.dev/test/"
