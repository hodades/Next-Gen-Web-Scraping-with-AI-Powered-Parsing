# Next-Gen-Web-Scraping-with-AI-Powered-Parsing

Ce projet automatise l’extraction, la structuration et l’export des fiches produits horlogers depuis [EveryWatch.com](https://everywatch.com), avec un focus sur la marque **Breguet**. Le pipeline utilise Playwright pour simuler une session utilisateur, contourner les blocages, récupérer les données API JSON, puis les transformer en fichiers exploitables (JSON / Excel).

---

## 🚀 Objectifs

- Scraper automatiquement des fiches produits horlogers  
- Simuler un vrai navigateur pour éviter les blocages  
- Accéder aux données via des API JSON dynamiques  
- Exporter les résultats dans un format structuré  
- Faciliter un futur enrichissement via modèles IA (GPT)  
- Fournir un export Excel pour visualisation rapide  

---

## 🧠 Technologies utilisées

- Python 3.10+  
- Playwright (contrôle de navigateur avec session persistante)  
- Requests (requêtes API avec cookies dynamiques)  
- Pandas (manipulation CSV / JSON)  
- Jupyter Notebook (export vers Excel)  
- OpenAI GPT (prévu pour parsing intelligent)  

---

## 📁 Structure du projet

```
everywatch-scraper/
├── README.md
├── requirements.txt
│
├── data/
│   ├── Watchfeed.csv               # Liste de liens à scraper
│   ├── all_watches_data.json       # Résultats du scraping
│
├── scraping/
│   ├── re_logic_bis2.py            # Scraper principal avec gestion de cookies
│   └── cookie_login/
│       ├── login.py                # Script de login via Playwright (Windows)
│       ├── login_mac.py            # Script de login (macOS)
│
├── notebooks/
│   └── remplissage_excel.ipynb     # Export JSON → Excel
```

---

## ⚙️ Installation

### 1. Cloner le dépôt

```bash
git clone https://github.com/ton-compte/everywatch-scraper.git
cd everywatch-scraper
```

### 2. Créer un environnement virtuel

```bash
python -m venv venv
source venv/bin/activate        # macOS/Linux
venv\Scripts\activate           # Windows
```

### 3. Installer les dépendances

```bash
pip install -r requirements.txt
playwright install
```

---

## 🚀 Lancer le scraping

```bash
python scraping/re_logic_bis2.py
```

Le script lit `Watchfeed.csv`, rafraîchit les cookies toutes les 400 requêtes, enregistre les résultats dans `all_watches_data.json`, et gère les blocages (`403`, erreurs API, etc.).

---

## 🔐 Connexion manuelle (si nécessaire)

```bash
python scraping/cookie_login/login.py         # sur Windows
python scraping/cookie_login/login_mac.py     # sur macOS
```

Utilise `page.pause()` pour interagir manuellement ou te connecter si besoin.

---

## 📤 Export vers Excel

Après le scraping :

1. Ouvre le fichier `notebooks/remplissage_excel.ipynb`  
2. Lance les cellules pour convertir `all_watches_data.json` en tableau Excel `.xlsx`

---

## ✅ Fonctionnalités clés

- Scraping dynamique via Playwright  
- Cookies et sessions utilisateurs gérés automatiquement  
- Accès à l’API Next.js du site pour données structurées  
- Résilience aux blocages automatiques  
- Export JSON et Excel exploitables immédiatement  

---

## 💡 Applications possibles

- Analyse de marché horloger  
- Enrichissement de fiches produit e-commerce  
- Pricing algorithmique  
- Veille concurrentielle  
- Préparation de données pour NLP/IA  


