# 🖥️ Serveur E-commerce Policy Analyzer

## 📡 Informations de connexion

**Votre IP locale :** `172.25.5.81`
**Port :** `8000`
**URL complète :** `http://172.25.5.81:8000`

## 🚀 Démarrage du serveur

```bash
# Démarrage rapide
./server_setup.sh

# Ou manuellement
source venv/bin/activate
python main.py
```

## 📋 Pour vos clients

**Envoyez-leur le fichier `client_guide.md`** qui contient :
- URL de l'API : `http://172.25.5.81:8000`
- Documentation interactive : `http://172.25.5.81:8000/docs`
- Exemples d'utilisation avec curl et JavaScript
- Format des réponses

## 🔧 Test rapide

```bash
# Tester l'API
curl http://172.25.5.81:8000/

# Lancer une analyse
curl -X POST "http://172.25.5.81:8000/analyze" \
  -H "Content-Type: application/json" \
  -d '{"url": "https://us.princesspolly.com"}'
```

## ⚠️ Points importants

1. **Gardez votre ordinateur allumé** pour que vos clients puissent accéder à l'API
2. **Votre IP peut changer** après un redémarrage du routeur
3. **Pare-feu configuré** pour le port 8000
4. **Base de données locale** dans `ecommerce_analyzer.db`

## 📊 Surveillance

- **Logs en temps réel** : visibles dans le terminal
- **Statistiques** : `http://172.25.5.81:8000/stats`
- **Résultats** : `http://172.25.5.81:8000/results`

## 🛠️ Maintenance

```bash
# Redémarrer le serveur
pkill -f "python main.py"
./server_setup.sh

# Vider la base de données
rm ecommerce_analyzer.db
# Le serveur recréera automatiquement la DB
```

## 🌐 Accès depuis Internet (optionnel)

Pour que vos clients accèdent depuis Internet :
1. Configurez le **port forwarding** sur votre routeur (port 8000)
2. Utilisez votre **IP publique** : `192.214.240.161:8000`
3. ⚠️ Attention à la sécurité !

## 📁 Fichiers importants

- `main.py` : Application principale
- `scraper.py` : Scraper web
- `analyzer.py` : Analyseur IA
- `.env` : Variables d'environnement (clés API)
- `client_guide.md` : Guide pour vos clients
