# 🛍️ E-commerce Policy Analyzer API - Guide Client

## 📡 Accès à l'API

**URL de base :** `http://172.25.5.81:8000`

## 🚀 Endpoints Disponibles

### 1. Analyser un site e-commerce
```bash
POST /analyze
Content-Type: application/json

{
    "url": "https://example-store.com"
}
```

**Réponse :**
```json
{
    "job_id": "uuid-123-456",
    "status": "started",
    "message": "Analysis started successfully"
}
```

### 2. Vérifier le statut d'une analyse
```bash
GET /job/{job_id}
```

**Réponse :**
```json
{
    "job_id": "uuid-123-456",
    "url": "https://example-store.com",
    "status": "completed",
    "created_at": "2025-08-21T05:00:00",
    "completed_at": "2025-08-21T05:02:30",
    "error_message": null
}
```

### 3. Obtenir tous les résultats
```bash
GET /results
```

### 4. Obtenir un résultat spécifique
```bash
GET /results/{result_id}
```

### 5. Exporter en CSV
```bash
GET /export/csv
```

### 6. Statistiques
```bash
GET /stats
```

## 📋 Exemple d'utilisation avec curl

```bash
# 1. Lancer une analyse
curl -X POST "http://172.25.5.81:8000/analyze" \
  -H "Content-Type: application/json" \
  -d '{"url": "https://us.princesspolly.com"}'

# 2. Vérifier le statut (remplacer JOB_ID)
curl "http://172.25.5.81:8000/job/JOB_ID"

# 3. Voir tous les résultats
curl "http://172.25.5.81:8000/results"
```

## 🔧 Exemple avec JavaScript/Fetch

```javascript
// Analyser un site
const response = await fetch('http://172.25.5.81:8000/analyze', {
    method: 'POST',
    headers: {
        'Content-Type': 'application/json',
    },
    body: JSON.stringify({
        url: 'https://example-store.com'
    })
});

const result = await response.json();
console.log('Job ID:', result.job_id);

// Vérifier le statut
const statusResponse = await fetch(`http://172.25.5.81:8000/job/${result.job_id}`);
const status = await statusResponse.json();
console.log('Status:', status.status);
```

## 📊 Format des Résultats

Chaque analyse retourne :
- **shipping_policy** : Politique d'expédition détaillée
- **return_policy** : Politique de retour
- **self_help_returns** : Options de retour en libre-service
- **insurance** : Informations sur l'assurance expédition
- **URLs** : Liens vers les pages de politique

## ⚡ Temps de Traitement

- Sites simples : 30-60 secondes
- Sites complexes : 1-3 minutes
- Sites avec beaucoup de JavaScript : 2-5 minutes

## 🆘 Support

En cas de problème, vérifiez :
1. L'URL est accessible
2. Le site n'est pas bloqué par des mesures anti-bot
3. Le job_id est correct pour vérifier le statut
