# WeHR - Backend API Documentation

## 📋 Vue d'ensemble

Application backend de gestion des ressources humaines (HR) développée avec Django REST Framework. Fournit des APIs RESTful complètes pour la gestion des employés, départements, recrutement, planning, annonces, support et paramètres système.

## 🏗️ Architecture

### Structure modulaire
```
backend/src/
├── users/          # Utilisateurs, rôles, permissions
├── employee/       # Employés et historique
├── department/     # Départements et statistiques
├── recruitment/    # Recrutement (offres, candidats)
├── schedule/       # Planning et réunions
├── announcement/   # Annonces
├── support/         # Tickets de support
├── settings/       # Paramètres système
├── dashboard/      # Métriques et activités
└── login/          # Authentification (JWT, 2FA)
```

### Séparation des responsabilités
- **Models** : Entités métier (logique métier uniquement)
- **Serializers** : Validation et transformation de données
- **ViewSets** : Logique de contrôle, permissions, actions CRUD
- **URLs** : Configuration des routes RESTful

### Design Patterns appliqués
1. **Repository Pattern** : Via Django ORM (QuerySets)
2. **Serializer Pattern** : DRF serializers avec validation
3. **ViewSet Pattern** : CRUD automatique + actions personnalisées (`@action`)
4. **Permission Pattern** : Classes personnalisées (`IsHRManagerOrAdmin`, etc.)
5. **Factory Pattern** : `get_serializer_class()` pour list/detail

## 🔧 Technologies et justifications

### Stack principale

| Technologie | Version | Justification |
|------------|---------|---------------|
| **Django** | 5.2.8 | Framework mature, ORM puissant, sécurité intégrée, écosystème riche |
| **DRF** | 3.16.1 | Standard industrie, sérialisation auto, ViewSets, permissions intégrées |
| **JWT** | 5.5.1 | Stateless, scalable, mobile-friendly, refresh tokens |
| **django-cors-headers** | 4.9.0 | Frontend séparé (Angular/React), contrôle CORS |
| **django-filter** | 25.2 | Filtrage complexe multi-champs, intégration DRF native |
| **drf-yasg** | 1.21.11 | Documentation Swagger/OpenAPI automatique |
| **Pillow** | 12.0.0 | Upload et traitement d'images (photos profil, CV) |
| **pyotp** | 2.9.0 | Authentification 2FA (TOTP) |

### Base de données
- **Développement** : SQLite (simplicité, portabilité)
- **Production** : PostgreSQL (robustesse, performance, scalabilité)

### Configuration JWT
```python
SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(minutes=5),  # Court = sécurité
    "REFRESH_TOKEN_LIFETIME": timedelta(days=1),    # Long = UX
}
```

## 🔒 Sécurité

### Authentification
- ✅ JWT (access + refresh tokens)
- ✅ 2FA (TOTP compatible Google Authenticator)
- ✅ Réinitialisation de mot de passe sécurisée
- ✅ Historique des connexions et blocage après échecs

### Protection
- ✅ **SQL Injection** : ORM Django (requêtes préparées)
- ✅ **XSS/CSRF** : Middleware Django activé
- ✅ **Rate Limiting** : 100/h (anonymes), 1000/h (authentifiés)
- ✅ **Permissions granulaires** : Par rôle et par module

### Configuration production
Fichier `settings_prod.py` avec :
- HTTPS forcé (HSTS)
- Cookies sécurisés (HttpOnly, Secure, SameSite)
- Logging séparé (sécurité vs général)
- Variables d'environnement obligatoires

## 📊 Fonctionnalités

### Modules (10 modules, 30+ ViewSets, 100+ endpoints)
- **Users** : Gestion utilisateurs, rôles, permissions, préférences
- **Login** : Authentification, sessions, 2FA, reset password
- **Employee** : Employés, historique des modifications
- **Department** : Départements, statistiques, budgets
- **Recruitment** : Offres d'emploi, candidats, processus
- **Schedule** : Planning, réunions, événements
- **Announcement** : Annonces internes
- **Support** : Tickets avec statuts/priorités
- **Settings** : Paramètres système, modèles emails
- **Dashboard** : Métriques, activités, KPIs

### Opérations CRUD
Tous les ViewSets implémentent :
- ✅ **Create** (POST)
- ✅ **Read** (GET list/detail)
- ✅ **Update** (PUT/PATCH)
- ✅ **Delete** (DELETE)
- ✅ **Actions personnalisées** : statistiques, filtrage, recherche

### Optimisations
```python
# Optimisation requêtes (select_related/prefetch_related)
queryset = Department.objects.select_related("manager").prefetch_related(
    "employees", "job_positions"
).all()

# Filtrage et recherche
filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
filterset_fields = ["status", "priority"]
search_fields = ["title", "description"]
```

## 🚀 Démarrage rapide

### Installation
```bash
# Environnement virtuel
python -m venv env
source env/bin/activate  # Windows: env\Scripts\activate

# Dépendances
pip install -r requirements.txt

# Migrations
python manage.py migrate

# Superutilisateur
python manage.py createsuperuser

# Serveur
python manage.py runserver
```

### Structure URLs
```
http://localhost:8000/api/
├── users/           # /api/users/
├── login/           # /api/login/
├── employee/        # /api/employee/
├── department/      # /api/department/
├── recruitment/     # /api/recruitment/
├── schedule/        # /api/schedule/
├── announcement/    # /api/announcement/
├── support/         # /api/support/
├── settings/        # /api/settings/
└── dashboard/        # /api/dashboard/
```

### Exemple API
```bash
# Authentification
POST /api/login/auth/login/
{
    "username": "user",
    "password": "password"
}
# Réponse: { "access": "...", "refresh": "..." }

# Utiliser le token
Authorization: Bearer <access_token>

# CRUD Département
GET    /api/department/departments/          # Liste
POST   /api/department/departments/          # Créer
GET    /api/department/departments/{id}/     # Détail
PUT    /api/department/departments/{id}/     # Modifier
DELETE /api/department/departments/{id}/     # Supprimer
```

## 📈 Statistiques

- **10 modules** principaux
- **30+ ViewSets** implémentés
- **50+ Serializers** créés
- **40+ Modèles** de données
- **100+ Endpoints** API disponibles

## ✅ Points forts

1. **Architecture modulaire** : Séparation claire par domaine métier
2. **Sécurité renforcée** : JWT, 2FA, validations, permissions granulaires
3. **Scalabilité** : Optimisations requêtes, pagination, cache-ready
4. **Maintenabilité** : Code documenté, patterns standardisés
5. **Audit complet** : Historique et traçabilité des actions

## 📚 Documentation

- **Docstrings** : Tous les modules/classes/méthodes documentés
- **README par module** : `README_DEPARTMENT.md`, `README_EMPLOYEE.md`, etc.
- **Swagger/OpenAPI** : Documentation interactive via drf-yasg

## 🔗 Ressources

- [Django Docs](https://docs.djangoproject.com/)
- [DRF Docs](https://www.django-rest-framework.org/)
- [JWT Docs](https://django-rest-framework-simplejwt.readthedocs.io/)

---

**Développé avec ❤️ pour démontrer les meilleures pratiques en développement backend Django REST Framework**
