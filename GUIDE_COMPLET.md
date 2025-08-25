# 🎯 Guide Complet - E-commerce Policy Analyzer

## 🚀 Démarrage Rapide

### Option 1: Démarrage Full Stack (Recommandé)
```bash
./start_fullstack.sh
```
Cette commande démarre :
- ✅ Backend API sur `http://172.25.5.81:8000`
- ✅ Frontend Web sur `http://localhost:3000`

### Option 2: Démarrage Séparé

**Backend seulement (pour vos clients API) :**
```bash
./server_setup.sh
```

**Frontend seulement :**
```bash
cd frontend && npm start
```

## 🌐 URLs d'Accès

| Service | URL | Description |
|---------|-----|-------------|
| **Frontend Web** | `http://localhost:3000` | Interface utilisateur complète |
| **Backend API** | `http://172.25.5.81:8000` | API REST pour vos clients |
| **Documentation API** | `http://172.25.5.81:8000/docs` | Documentation interactive |

## 👥 Pour Vos Clients

### 🔧 Développeurs (API)
- **Fichier à envoyer :** `client_guide.md`
- **URL API :** `http://172.25.5.81:8000`
- **Test rapide :** `node test_connection.js`

### 🖥️ Utilisateurs (Interface Web)
- **URL :** `http://localhost:3000`
- Interface complète avec dashboard, statistiques, export CSV

## 🧪 Tests et Validation

### Test de l'API
```bash
# Test de base
curl http://172.25.5.81:8000/

# Lancer une analyse
curl -X POST "http://172.25.5.81:8000/analyze" \
  -H "Content-Type: application/json" \
  -d '{"url": "https://example-store.com"}'

# Voir les statistiques
curl http://172.25.5.81:8000/stats
```

### Test du Frontend
```bash
# Vérifier la connexion
node test_connection.js

# Accès direct
curl http://localhost:3000/
```

## 📊 Fonctionnalités Disponibles

### 🔍 Analyse de Sites
- **Scraping intelligent** avec Playwright
- **Détection Shopify** automatique
- **IA GPT-4** pour extraction précise
- **Support JavaScript/SPA**
- **Anti-bot avancé**

### 📈 Interface Web (Frontend)
- **Dashboard** avec statistiques en temps réel
- **Historique** de toutes les analyses
- **Recherche et filtrage** des résultats
- **Export CSV** des données
- **Suivi des jobs** en temps réel

### 🔌 API REST (Backend)
- **Analyse asynchrone** de sites
- **Suivi des jobs** avec statuts
- **CRUD complet** des résultats
- **Export de données**
- **Statistiques globales**

## 🛠️ Maintenance

### Redémarrage des Services
```bash
# Arrêter tous les processus
pkill -f "python main.py"
pkill -f "npm start"

# Redémarrer
./start_fullstack.sh
```

### Nettoyage de la Base de Données
```bash
# Supprimer toutes les données
rm ecommerce_analyzer.db
# La DB sera recréée automatiquement
```

### Mise à Jour des Dépendances
```bash
# Backend
source venv/bin/activate
pip install --upgrade -r requirements.txt

# Frontend
cd frontend && npm update
```

## 🔧 Configuration

### Variables d'Environnement (.env)
```
OPENAI_API_KEY=votre_clé_openai
DATABASE_URL=sqlite:///./ecommerce_analyzer.db
CORS_ORIGINS=*
PORT=8000
```

### Configuration Frontend (.env.local)
```
REACT_APP_API_URL=http://172.25.5.81:8000
```

## 📱 Accès Réseau

### Depuis Votre Réseau Local
- **Votre IP :** `172.25.5.81`
- **Port Backend :** `8000`
- **Port Frontend :** `3000`

### Depuis Internet (Optionnel)
1. **Configuration routeur :** Port forwarding 8000
2. **IP publique :** `192.214.240.161`
3. **URL externe :** `http://192.214.240.161:8000`

## 🚨 Résolution de Problèmes

### Backend ne démarre pas
```bash
# Vérifier Python et dépendances
source venv/bin/activate
python --version
pip list | grep fastapi

# Vérifier les ports
ss -tlnp | grep 8000
```

### Frontend ne démarre pas
```bash
# Vérifier Node.js
node --version
npm --version

# Réinstaller dépendances
cd frontend
rm -rf node_modules package-lock.json
npm install
```

### API non accessible
```bash
# Vérifier pare-feu
sudo ufw status
sudo ufw allow 8000/tcp

# Tester connexion
curl -v http://172.25.5.81:8000/
```

## 📋 Checklist de Déploiement

- ✅ Backend API démarré et accessible
- ✅ Frontend React démarré et fonctionnel
- ✅ Connexion frontend-backend testée
- ✅ Pare-feu configuré (port 8000)
- ✅ Variables d'environnement configurées
- ✅ Tests de connexion réussis
- ✅ Guide client préparé

## 🎯 Prochaines Étapes

1. **Tester avec vos clients** en leur envoyant `client_guide.md`
2. **Surveiller les performances** via les logs
3. **Sauvegarder régulièrement** la base de données
4. **Mettre à jour les clés API** si nécessaire

---

**🎉 Votre plateforme E-commerce Policy Analyzer est maintenant opérationnelle !**
