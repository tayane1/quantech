# Module Department - Documentation Technique

## 📋 Vue d'ensemble

Le module `department` gère les départements de l'organisation dans l'application WeHR. Il inclut la gestion des départements, leurs managers, budgets, et fournit des statistiques complètes sur les employés et les offres d'emploi associées.

## 🏗️ Architecture

### Structure des fichiers

```
department/
├── models.py                    # Modèle Department
├── serializers/
│   ├── department_serializer.py
│   └── __init__.py
├── viewsets/
│   ├── department_viewset.py
│   └── __init__.py
├── urls.py                       # Configuration des routes
└── README_DEPARTMENT.md          # Cette documentation
```

## 🔧 Composants

### 1. Serializers

#### `DepartmentSerializer`
- **Fichier** : `serializers/department_serializer.py`
- **Responsabilité** : Sérialisation complète des départements
- **Fonctionnalités** :
  - Statistiques intégrées (nombre d'employés, offres d'emploi)
  - Informations du manager (nom, email)
  - Compteurs d'employés actifs
  - Compteurs d'offres ouvertes
  - Validation de l'unicité du code
  - Validation du budget (positif ou nul)

#### `DepartmentListSerializer`
- **Fichier** : `serializers/department_serializer.py`
- **Responsabilité** : Sérialisation simplifiée pour les listes
- **Optimisation** : Moins de données pour améliorer les performances

### 2. ViewSets

#### `DepartmentViewSet`
- **Fichier** : `viewsets/department_viewset.py`
- **Permissions** : `IsHRManagerOrAdmin` (lecture pour tous, modification pour admins/HR)
- **Endpoints CRUD** :
  - `GET /api/department/departments/` : Liste des départements
  - `POST /api/department/departments/` : Créer un département
  - `GET /api/department/departments/{id}/` : Détails
  - `PUT/PATCH /api/department/departments/{id}/` : Modifier
  - `DELETE /api/department/departments/{id}/` : Supprimer

- **Actions personnalisées** :
  - `GET /api/department/departments/{id}/employees/` : Employés du département
  - `GET /api/department/departments/{id}/job-positions/` : Offres d'emploi du département
  - `GET /api/department/departments/{id}/statistics/` : Statistiques détaillées
  - `GET /api/department/departments/statistics/` : Statistiques globales

- **Filtrage** :
  - Par manager : `?manager=1`
  - Par localisation : `?location=Paris`
  - Recherche : `?search=IT`
  - Tri : `?ordering=-budget`

### 3. Permissions personnalisées

#### `IsHRManagerOrAdmin`
- **Localisation** : `viewsets/department_viewset.py`
- **Logique** :
  - Admins et HR managers : accès complet
  - Autres utilisateurs : lecture seule
  - Empêche la modification non autorisée des départements

## 🔐 Sécurité

### Validations implémentées

1. **Données département** :
   - Unicité du code
   - Budget positif ou nul
   - Validation des champs requis

2. **Permissions** :
   - Modification réservée aux admins/HR
   - Lecture pour tous les utilisateurs authentifiés

## 📡 Endpoints API

### Départements (Department)

```bash
# Liste des départements
GET /api/department/departments/

# Créer un département
POST /api/department/departments/
{
  "name": "Développement",
  "code": "DEV",
  "description": "Département de développement logiciel",
  "manager": 1,
  "location": "Paris",
  "budget": "500000.00"
}

# Détails d'un département
GET /api/department/departments/1/

# Modifier un département
PATCH /api/department/departments/1/
{
  "budget": "550000.00"
}

# Employés du département
GET /api/department/departments/1/employees/

# Offres d'emploi du département
GET /api/department/departments/1/job-positions/

# Statistiques détaillées d'un département
GET /api/department/departments/1/statistics/
# Retourne :
# - Informations du département
# - Statistiques des employés (total, par statut/genre, salaires)
# - Statistiques des offres (total, par statut, urgentes, candidats)

# Statistiques globales
GET /api/department/departments/statistics/
# Retourne :
# - Total départements
# - Budget total
# - Total employés
# - Total offres d'emploi
# - Statistiques par département
```

## 🎯 Bonnes pratiques appliquées

1. **Séparation des responsabilités** :
   - Serializers pour validation/sérialisation
   - ViewSets pour logique métier
   - Permissions pour sécurité

2. **Optimisation des requêtes** :
   - `select_related()` pour ForeignKey (manager)
   - `prefetch_related()` pour les relations inverses (employees, job_positions)
   - Serializer simplifié pour les listes
   - Évite les requêtes N+1

3. **Statistiques agrégées** :
   - Calculs optimisés avec `aggregate()` et `annotate()`
   - Statistiques détaillées par département
   - Statistiques globales

4. **Relations avec autres modules** :
   - Intégration avec Employee (employés du département)
   - Intégration avec Recruitment (offres d'emploi)
   - Utilisation des serializers des autres modules pour les relations

## 🚀 Intégration

### Dans `backend/urls.py`

```python
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path("api/users/", include("users.urls")),
    path("api/schedule/", include("schedule.urls")),
    path("api/recruitment/", include("recruitment.urls")),
    path("api/login/", include("login.urls")),
    path("api/employee/", include("employee.urls")),
    path("api/department/", include("department.urls")),  # Ajouter cette ligne
]
```

### Dépendances requises

- `django-filter` : Pour le filtrage avancé
- `djangorestframework` : Framework REST

## 📝 Exemples d'utilisation

### Workflow complet de gestion de département

```python
# 1. Créer un département
POST /api/department/departments/
{
  "name": "Ressources Humaines",
  "code": "RH",
  "description": "Gestion des ressources humaines",
  "manager": 5,
  "location": "Lyon",
  "budget": "300000.00"
}

# 2. Consulter les employés du département
GET /api/department/departments/1/employees/
# → Liste de tous les employés avec serializer simplifié

# 3. Consulter les offres d'emploi
GET /api/department/departments/1/job-positions/
# → Liste de toutes les offres avec statistiques

# 4. Consulter les statistiques détaillées
GET /api/department/departments/1/statistics/
# → Vue complète : employés, offres, budgets, etc.

# 5. Consulter les statistiques globales
GET /api/department/departments/statistics/
# → Vue d'ensemble de tous les départements
```

### Filtrage et recherche

```bash
# Rechercher un département
GET /api/department/departments/?search=IT

# Filtrer par manager
GET /api/department/departments/?manager=5

# Filtrer par localisation
GET /api/department/departments/?location=Paris

# Trier par budget décroissant
GET /api/department/departments/?ordering=-budget
```

## 🔍 Tests recommandés

1. **Tests unitaires** :
   - Validation des serializers
   - Unicité du code
   - Validation du budget
   - Permissions

2. **Tests d'intégration** :
   - Workflow complet de création/modification
   - Relations avec Employee et Recruitment
   - Statistiques agrégées

3. **Tests de sécurité** :
   - Accès non autorisé
   - Filtrage selon les permissions

## 📚 Références

- [Django REST Framework - ViewSets](https://www.django-rest-framework.org/api-guide/viewsets/)
- [Django Filter](https://django-filter.readthedocs.io/)
- [DRF Permissions](https://www.django-rest-framework.org/api-guide/permissions/)
- [Django Aggregation](https://docs.djangoproject.com/en/stable/topics/db/aggregation/)

