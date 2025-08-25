# 🚀 GUIDE FINAL - E-COMMERCE ANALYZER

## 🎯 **COMMANDE SIMPLE À CHAQUE DÉMARRAGE D'ORDI**

```bash
./START_SERVER.sh
```

**C'est tout !** Cette commande fait TOUT automatiquement :
- ✅ Démarre l'API
- ✅ Créé le tunnel public
- ✅ Met à jour la config frontend
- ✅ Affiche l'URL publique

---

## 📱 **POUR METTRE À JOUR LE FRONTEND HOSTINGER**

```bash
./update_frontend.sh
```

Puis upload le dossier `hostinger_deploy/` sur Hostinger.

---

## ❓ **RÉPONSE À TA 2ÈME QUESTION : EST-CE QUE LE LIEN RESTE LE MÊME ?**

### 🔴 **NON, le lien change à chaque redémarrage**

**Cloudflare Tunnel gratuit** génère une nouvelle URL à chaque fois :
- ❌ `https://textiles-workforce-elder-tim.trycloudflare.com/` (aujourd'hui)
- ❌ `https://autre-nom-random.trycloudflare.com/` (demain)

### 🟡 **SOLUTIONS POUR GARDER LA MÊME URL :**

#### **Option 1: Cloudflare Tunnel avec compte (GRATUIT)**
```bash
# S'inscrire sur cloudflare.com (gratuit)
# Créer un tunnel nommé
cloudflared tunnel login
cloudflared tunnel create mon-tunnel
# URL fixe : https://mon-tunnel.ton-domaine.com
```

#### **Option 2: Ngrok avec compte (GRATUIT)**
```bash
# S'inscrire sur ngrok.com (gratuit)
ngrok config add-authtoken TON_TOKEN
ngrok http 8000 --domain=ton-nom.ngrok-free.app
# URL fixe : https://ton-nom.ngrok-free.app
```

#### **Option 3: Utiliser ton routeur (Port forwarding)**
```bash
# Configurer ton routeur : port 8000 → ton PC
# URL fixe : http://TON_IP_PUBLIQUE:8000
```

---

## 🎯 **RECOMMANDATION**

**Pour commencer :** Utilise `./START_SERVER.sh` et mets à jour le frontend à chaque redémarrage.

**Pour la production :** Crée un compte Cloudflare gratuit pour avoir une URL fixe.

---

## 📋 **RÉSUMÉ WORKFLOW**

1. **Démarrer l'ordi :** `./START_SERVER.sh`
2. **Noter la nouvelle URL** (affichée dans le terminal)
3. **Mettre à jour Hostinger :** `./update_frontend.sh` puis upload
4. **Partager la nouvelle URL** aux clients

**Temps total :** 2 minutes ! 🚀
