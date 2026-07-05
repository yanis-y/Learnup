# Flashcards — Répétition espacée (SM-2)

Application web de flashcards avec algorithme SM-2, déployable sur Railway.

## Choix techniques

**Django + PostgreSQL** servi par Gunicorn, templates Django pour le frontend (un seul service Railway). Whitenoise sert les fichiers statiques sans CDN. Les sessions Django (base de données) stockent la file de révision en cours. SQLite est utilisé localement pour le développement, PostgreSQL en production via `DATABASE_URL`.

## Lancer en local

```bash
# 1. Créer et activer un environnement virtuel
python -m venv .venv
source .venv/bin/activate      # Linux/macOS
.venv\Scripts\activate         # Windows

# 2. Installer les dépendances
pip install -r requirements.txt

# 3. Appliquer les migrations (crée db.sqlite3)
python manage.py migrate

# 4. (Optionnel) Créer un superutilisateur pour accéder à /admin/
python manage.py createsuperuser

# 5. Lancer le serveur de développement
python manage.py runserver
```

Accéder à : http://127.0.0.1:8000

## Déployer sur Railway

### 1. Créer le dépôt GitHub

```bash
cd flashcards
git init
git add .
git commit -m "Initial commit"
git remote add origin https://github.com/<utilisateur>/<repo>.git
git push -u origin main
```

### 2. Créer le projet Railway

1. Aller sur [railway.app](https://railway.app) → **New Project**
2. Choisir **Deploy from GitHub repo** et sélectionner votre dépôt
3. Railway détecte automatiquement Python et utilise le `Procfile`

### 3. Ajouter PostgreSQL

1. Dans le projet Railway → **+ New** → **Database** → **PostgreSQL**
2. Railway injecte automatiquement `DATABASE_URL` dans les variables d'environnement du service web

### 4. Configurer les variables d'environnement

Dans Railway → votre service web → **Variables** :

| Variable | Valeur | Requis |
|---|---|---|
| `SECRET_KEY` | chaîne aléatoire longue (ex. 50 caractères) | **Oui** |
| `DEBUG` | `False` | Recommandé |

> `DATABASE_URL` est injectée automatiquement par Railway quand PostgreSQL est lié au service.

### 5. Déployer

Chaque `git push origin main` déclenche un redéploiement automatique.  
Le `Procfile` exécute `migrate` + `collectstatic` avant de démarrer Gunicorn.

## Structure du projet

```
flashcards/
├── flashcards/        # Configuration Django (settings, urls, wsgi)
├── cards/             # Application principale
│   ├── models.py      # Theme, Card, ReviewLog
│   ├── views.py       # Toutes les vues
│   └── urls.py        # Routes
├── templates/         # Templates HTML
├── static/            # CSS
├── Procfile           # Commandes Railway (release + web)
├── requirements.txt
└── runtime.txt        # Version Python
```

## Export / Import

- **Export** : `/export/` → télécharge un fichier JSON avec tous les thèmes et cartes (y compris les données SM-2)
- **Import** : formulaire en bas du tableau de bord → importe un fichier JSON exporté depuis cette application

## Raccourcis clavier (session de révision)

| Touche | Action |
|---|---|
| `Espace` ou `Entrée` | Afficher la réponse |
| `1` | Echec |
| `2` | Approximatif |
| `3` | Valide |
