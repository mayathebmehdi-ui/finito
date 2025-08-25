#!/bin/bash

echo "🚀 BUILDING FOR HOSTINGER PRODUCTION"
echo "===================================="

# Nettoyer les anciens builds
echo "🧹 Cleaning old builds..."
rm -rf frontend/build
rm -rf hostinger_deploy

# Demander l'URL de l'API
echo ""
echo "🌐 Enter your API URL from Cloudflare tunnel:"
echo "   (Example: https://your-tunnel.trycloudflare.com)"
read -p "API URL: " API_URL

if [ -z "$API_URL" ]; then
    echo "❌ API URL is required!"
    exit 1
fi

# Valider l'URL
if [[ ! "$API_URL" =~ ^https?:// ]]; then
    echo "❌ URL must start with http:// or https://"
    exit 1
fi

echo "✅ Using API URL: $API_URL"

# Créer la configuration de production
echo "🔧 Creating production config..."
cat > frontend/.env.local << EOF
# Production configuration for Hostinger
REACT_APP_API_URL=$API_URL
GENERATE_SOURCEMAP=false
EOF

# AUSSI créer .env.production pour backup
cat > frontend/.env.production << EOF
# Production configuration for Hostinger
REACT_APP_API_URL=$API_URL
GENERATE_SOURCEMAP=false
EOF

# Build le frontend
echo ""
echo "🔨 Building React app for production..."
cd frontend

# Installer les dépendances si nécessaire
if [ ! -d "node_modules" ]; then
    echo "📦 Installing dependencies..."
    npm install
fi

# Build en mode production
npm run build

if [ $? -ne 0 ]; then
    echo "❌ Build failed!"
    exit 1
fi

cd ..

# Créer le dossier de déploiement Hostinger
echo ""
echo "📁 Preparing Hostinger deployment..."
mkdir -p hostinger_deploy

# Copier tous les fichiers de build
cp -r frontend/build/* hostinger_deploy/

# Créer un fichier .htaccess pour les routes React
cat > hostinger_deploy/.htaccess << 'EOF'
# React Router configuration
<IfModule mod_rewrite.c>
    RewriteEngine On
    
    # Handle Angular and React routes
    RewriteBase /
    RewriteRule ^index\.html$ - [L]
    RewriteCond %{REQUEST_FILENAME} !-f
    RewriteCond %{REQUEST_FILENAME} !-d
    RewriteRule . /index.html [L]
</IfModule>

# Security headers
<IfModule mod_headers.c>
    Header always set X-Content-Type-Options nosniff
    Header always set X-Frame-Options DENY
    Header always set X-XSS-Protection "1; mode=block"
</IfModule>

# Compression
<IfModule mod_deflate.c>
    AddOutputFilterByType DEFLATE text/plain
    AddOutputFilterByType DEFLATE text/html
    AddOutputFilterByType DEFLATE text/xml
    AddOutputFilterByType DEFLATE text/css
    AddOutputFilterByType DEFLATE application/xml
    AddOutputFilterByType DEFLATE application/xhtml+xml
    AddOutputFilterByType DEFLATE application/rss+xml
    AddOutputFilterByType DEFLATE application/javascript
    AddOutputFilterByType DEFLATE application/x-javascript
</IfModule>
EOF

# Créer un fichier de vérification
echo "$API_URL" > hostinger_deploy/api_config.txt

# Afficher les informations finales
echo ""
echo "🎉 HOSTINGER BUILD READY!"
echo "========================="
echo "📁 Folder to upload: hostinger_deploy/"
echo "🌐 API URL configured: $API_URL"
echo "📊 Build size: $(du -sh hostinger_deploy | cut -f1)"
echo ""
echo "📋 NEXT STEPS:"
echo "1. Go to Hostinger cPanel"
echo "2. File Manager → public_html"
echo "3. Delete all existing files"
echo "4. Upload ALL contents of 'hostinger_deploy/' folder"
echo "5. Your site will be live at: https://your-domain.hostinger.com"
echo ""
echo "✅ Ready for upload!"
