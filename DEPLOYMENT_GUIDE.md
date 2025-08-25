# 🚀 Guide de Déploiement - E-commerce Policy Analyzer

## 🎯 COMMANDE SIMPLE POUR DÉMARRER L'API

**À chaque fois que tu démarres ton ordi, utilise cette commande :**

```bash
./start_api_server.sh
```

C'est tout ! Tes clients pourront utiliser l'API à distance.

---

## 📡 Configuration pour Hostinger

### 1. Obtenir ton IP serveur
```bash
./get_server_info.sh
```

### 2. Configurer le frontend
```bash
# Édite le fichier de configuration
nano frontend/env.production

# Remplace YOUR_SERVER_IP par ton IP (ex: 192.168.1.100)
REACT_APP_API_URL=http://192.168.1.100:8000
```

### 3. Build le frontend pour Hostinger
```bash
./build_for_hostinger.sh
```

### 4. Upload sur Hostinger
- Va dans ton cPanel Hostinger
- File Manager → public_html
- Upload tout le contenu du dossier `hostinger_deploy/`

---

## 🌐 Accès Client

### Pour tes clients locaux (même réseau)
```
http://TON_IP_LOCAL:8000
```

### Pour tes clients externes (internet)
```
http://TON_IP_PUBLIQUE:8000
```
⚠️ **Important :** Ouvre le port 8000 dans ton routeur/firewall

### Frontend hébergé sur Hostinger
```
https://ton-site.hostinger.com
```

---

## 📚 Documentation API

Tes clients peuvent voir la doc complète ici :
```
http://TON_IP:8000/docs
```

---

## 🔧 Dépannage

### Si l'API ne démarre pas :
```bash
# Vérifie si le port est libre
sudo netstat -tlnp | grep :8000

# Redémarre proprement
pkill -f "python main.py"
./start_api_server.sh
```

### Si les clients ne peuvent pas se connecter :
1. Vérifie ton firewall : `sudo ufw allow 8000`
2. Vérifie ton IP : `./get_server_info.sh`
3. Teste localement : `curl http://localhost:8000`

---

## 🎉 C'est prêt !

1. **Démarre l'API :** `./start_api_server.sh`
2. **Build le frontend :** `./build_for_hostinger.sh`  
3. **Upload sur Hostinger**
4. **Partage ton IP** aux clients

Tes clients auront une interface web professionnelle sur Hostinger qui communique avec ton API ! 🚀
