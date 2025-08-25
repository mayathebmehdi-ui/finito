# Walmart Scraper

Ce script Python permet de scraper la page d'aide Walmart Protection Plans by Allstate.

## Installation

1. Créer un environnement virtuel :
```bash
python3 -m venv venv
source venv/bin/activate  # Sur Linux/Mac
# ou
venv\Scripts\activate     # Sur Windows
```

2. Installer les dépendances :
```bash
pip install -r requirements.txt
```

## Utilisation

```bash
python walmart_scraper.py
```

Le script va :
- Scraper la page Walmart Protection Plans
- Extraire le contenu principal (titres, paragraphes, liens, sections)
- Sauvegarder les données en JSON et CSV
- Afficher un résumé des résultats

## Fichiers de sortie

- `walmart_scraped_data.json` : Données complètes au format JSON
- `walmart_scraped_data.csv` : Résumé des données au format CSV

## Fonctionnalités

- Extraction des titres et sous-titres
- Récupération de tous les paragraphes
- Collecte des liens avec leurs URLs complètes
- Organisation du contenu par sections
- Gestion des erreurs et timeouts
- Headers HTTP réalistes pour éviter la détection
- Sauvegarde en multiple formats

## Structure des données

Le script extrait :
- **Titre de la page**
- **Contenu principal** : titres, paragraphes, listes, liens
- **Liens de navigation**
- **Sections d'aide** organisées par catégories
- **Métadonnées** : URL, timestamp du scraping

## Dépendances

- `requests` : Pour les requêtes HTTP
- `beautifulsoup4` : Pour le parsing HTML
- `lxml` : Parser XML/HTML rapide
