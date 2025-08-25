# 📍 OÙ CHANGER L'URL DANS HOSTINGER

## 🎯 **CHEMIN EXACT :**

```
public_html/static/js/main.XXXXXXX.js
```

## 🔍 **COMMENT TROUVER LE FICHIER :**

1. **Hostinger cPanel** → **File Manager**
2. **public_html** → **static** → **js**
3. **Cherche le fichier :** `main.XXXXXXX.js` (le plus gros fichier, ~500KB)

## ✏️ **QUOI CHANGER :**

### **Cherche cette ligne :**
```javascript
baseURL:"http://172.25.5.81:8000"
```

### **Remplace par :**
```javascript
baseURL:"https://ton-nouveau-tunnel.trycloudflare.com"
```

## 🔧 **MÉTHODE RAPIDE :**

### **Dans l'éditeur Hostinger :**
1. **Ctrl+F** pour chercher
2. **Tape :** `baseURL:"`
3. **Remplace** l'URL entre les guillemets
4. **Save**

## ⚡ **EXEMPLE COMPLET :**

### **AVANT :**
```javascript
baseURL:"http://172.25.5.81:8000"
```

### **APRÈS :**
```javascript
baseURL:"https://textiles-workforce-elder-tim.trycloudflare.com"
```

## 🎉 **C'EST TOUT !**

- ✅ **1 seul fichier** à modifier
- ✅ **1 seule ligne** à changer  
- ✅ **30 secondes** max

**Ton site Hostinger sera immédiatement connecté à ton nouveau tunnel !** 🚀

---

## 💡 **ALTERNATIVE - SCRIPT AUTOMATIQUE :**

Si tu préfères, utilise :
```bash
./quick_build.sh
```
Et re-upload tout le dossier `hostinger_deploy/`
