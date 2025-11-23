# Quantech - HR Management System

Application de gestion des ressources humaines avec Django (Backend) et Angular (Frontend).

## 🚀 Déploiement rapide avec Docker

### Prérequis

- Docker (version 20.10+)
- Docker Compose (version 2.0+)

### Installation et lancement

```bash
# Cloner le projet et naviguer dans le répertoire
cd quantech-main

# Lancer l'application
docker-compose up -d
```

C'est tout ! L'application sera accessible à :

- **Frontend** : http://localhost
- **Backend API** : http://localhost:8001/api
- **Admin Django** : http://localhost:8001/admin

### Identifiants par défaut

Un compte administrateur est créé automatiquement au premier lancement :

- **Username** : `admin`
- **Password** : `admin123`

**⚠️ Important** : Changez ces identifiants en production !

### Commandes utiles

```bash
# Voir les logs (tous les services)
docker-compose logs -f

# Voir les logs d'un service spécifique
docker-compose logs -f backend
docker-compose logs -f frontend

# Arrêter l'application
docker-compose down

# Arrêter et supprimer les volumes (⚠️ supprime la base de données)
docker-compose down -v

# Reconstruire les images
docker-compose up -d --build

# Accéder au shell du backend
docker-compose exec backend python manage.py shell

# Créer des migrations
docker-compose exec backend python manage.py makemigrations

# Appliquer les migrations
docker-compose exec backend python manage.py migrate

# Remplir la base de données avec des données de test
docker-compose exec backend python manage.py seed_database

# Vider et remplir la base de données
docker-compose exec backend python manage.py seed_database --clear
```

## 🏗️ Architecture

### Backend (Django)

- **Framework** : Django 5.2.8
- **API** : Django REST Framework 3.16.1
- **Authentification** : JWT (Simple JWT 5.5.1)
- **Base de données** : SQLite (par défaut, volumes Docker persistants)
- **Documentation API** : drf-yasg (Swagger/OpenAPI)
- **CORS** : django-cors-headers pour la communication frontend/backend
- **Filtrage** : django-filter pour les requêtes complexes

### Frontend (Angular)

- **Framework** : Angular 21
- **Server** : Nginx (production)
- **Style** : SCSS/CSS
- **SSR** : Support Server-Side Rendering

## Structure du projet

```
quantech-main/
├── backend/
│   ├── src/                # Code source Django
│   ├── Dockerfile          # Image Docker backend
│   ├── docker-entrypoint.sh # Script d'initialisation
│   └── requirements.txt    # Dépendances Python
├── frontend/
│   ├── src/                # Code source Angular
│   ├── Dockerfile          # Image Docker frontend
│   ├── nginx.conf          # Configuration Nginx
│   └── package.json        # Dépendances Node.js
└── docker-compose.yml      # Orchestration des services
```

## ⚙️ Configuration

### Variables d'environnement

Les variables d'environnement sont configurées directement dans `docker-compose.yml`. Pour la production, vous pouvez :

1. **Créer un fichier `.env`** à la racine du projet :

```bash
DEBUG=False
SECRET_KEY=votre-cle-secrete-tres-longue-et-aleatoire
ALLOWED_HOSTS=votre-domaine.com,www.votre-domaine.com
```

2. **Modifier `docker-compose.yml`** pour utiliser le fichier `.env` :

```yaml
environment:
  - DEBUG=${DEBUG}
  - SECRET_KEY=${SECRET_KEY}
  - ALLOWED_HOSTS=${ALLOWED_HOSTS}
```

### Personnalisation

Pour modifier la configuration :

1. **Backend** :
   - Variables d'environnement dans `docker-compose.yml`
   - Settings Django : `backend/src/backend/settings.py` (dev) ou `settings_prod.py` (prod)
2. **Frontend** :
   - `frontend/src/environments/environment.ts` (développement)
   - `frontend/src/environments/environment.prod.ts` (production)

### Volumes Docker

Le projet utilise deux volumes persistants :

- `backend-media` : Stocke les fichiers média (photos de profil, CV, etc.)
- `backend-db` : Contient la base de données SQLite et les fichiers statiques

## Développement

### Lancer en mode développement (sans Docker)

**Backend** :

```bash
cd backend/src
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r ../requirements.txt
python manage.py migrate
python manage.py runserver
```

**Frontend** :

```bash
cd frontend
npm install
npm start
```

## 🚀 Production

Pour un déploiement en production :

1. **Sécurité** :

   - Changez `DEBUG=False` dans les variables d'environnement
   - Définissez une `SECRET_KEY` forte et unique (générez avec `python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"`)
   - Configurez `ALLOWED_HOSTS` avec vos domaines
   - Changez les identifiants admin par défaut

2. **Base de données** :

   - Utilisez PostgreSQL ou MySQL au lieu de SQLite
   - Configurez les variables `DB_NAME`, `DB_USER`, `DB_PASSWORD`, `DB_HOST`, `DB_PORT` dans `settings_prod.py`

3. **Infrastructure** :

   - Configurez un reverse proxy (Nginx/Apache) devant les services
   - Activez HTTPS avec des certificats SSL (Let's Encrypt recommandé)
   - Configurez les volumes Docker pour la persistance des données
   - Mettez en place des sauvegardes régulières de la base de données

4. **Performance** :
   - Activez le cache (Redis/Memcached)
   - Configurez les fichiers statiques pour être servis par Nginx
   - Optimisez les requêtes de base de données

## 📋 Fonctionnalités

### Modules principaux

- **👥 Gestion des utilisateurs** : Authentification JWT, rôles, permissions, profils
- **👨‍💼 Gestion des employés** : Fiches employés, historique des modifications
- **🏢 Gestion des départements** : Organisation, budgets, statistiques
- **📝 Recrutement** : Offres d'emploi, candidats, processus de recrutement, demandes de talents
- **📅 Planning** : Réunions, événements, calendrier
- **💬 Messagerie interne** : Conversations, messages en temps réel
- **📊 Tableau de bord** : Métriques, activités, statistiques
- **📢 Annonces** : Communication interne, notifications
- **🎫 Support technique** : Tickets, catégories, commentaires
- **⚙️ Paramètres système** : Configuration, modèles d'emails, préférences

### Sécurité

- Authentification JWT avec tokens d'accès et de rafraîchissement
- Support 2FA (TOTP) pour l'authentification à deux facteurs
- Rate limiting configuré (100 req/h anonymes, 1000 req/h authentifiés)
- Permissions granulaires par rôle et par module
- Protection CSRF et XSS intégrée

## 📚 Documentation supplémentaire

Chaque module backend contient sa propre documentation :

- `backend/src/dashboard/README_DASHBOARD.md`
- `backend/src/department/README_DEPARTMENT.md`
- `backend/src/employee/README_EMPLOYEE.md`
- `backend/src/login/README_LOGIN.md`
- `backend/src/recruitment/README_RECRUITMENT.md`
- `backend/src/schedule/README_SCHEDULE.md`
- `backend/src/messaging/README.md`

Consultez également `backend/src/README.md` pour la documentation complète du backend.

## 🐛 Dépannage

### Le backend ne démarre pas

```bash
# Vérifier les logs
docker-compose logs backend

# Vérifier que les migrations sont appliquées
docker-compose exec backend python manage.py migrate
```

### Le frontend ne se connecte pas au backend

- Vérifiez que `API_URL` dans `docker-compose.yml` correspond à l'URL du backend
- Vérifiez les paramètres CORS dans `backend/src/backend/settings.py`

### Problèmes de permissions

```bash
# Réinitialiser les permissions Docker
docker-compose down
docker-compose up -d --force-recreate
```

## 🤝 Support

Pour toute question ou problème, consultez la documentation ou créez une issue.

## 📄 Licence

Tous droits réservés.
