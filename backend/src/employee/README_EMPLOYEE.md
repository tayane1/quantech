# Module Employee - Documentation Technique

## 📋 Vue d'ensemble

Le module `employee` gère la gestion complète des employés dans l'application WeHR. Il inclut les informations personnelles, professionnelles, la hiérarchie (manager/subordonnés), et l'historique automatique de tous les changements.

## 🏗️ Architecture

### Structure des fichiers

```
employee/
├── models/
│   ├── employee.py              # Modèle Employee (employés)
│   └── employee_history.py      # Modèle EmployeeHistory (historique)
├── serializers/
│   ├── employee_serializer.py
│   ├── employee_history_serializer.py
│   └── __init__.py
├── viewsets/
│   ├── employee_viewset.py
│   ├── employee_history_viewset.py
│   └── __init__.py
├── urls.py                       # Configuration des routes
└── README_EMPLOYEE.md            # Cette documentation
```

## 🔧 Composants

### 1. Serializers

#### `EmployeeSerializer`
- **Fichier** : `serializers/employee_serializer.py`
- **Responsabilité** : Sérialisation complète des employés
- **Fonctionnalités** :
  - Calcul automatique de l'âge et des années de service
  - Inclusion des noms des départements, positions, managers
  - Compteur de subordonnés
  - Validation de l'email et de l'employee_id (unicité)
  - Validation du salaire (positif)
  - Validation des dates (naissance dans le passé, embauche pas dans le futur)
  - Protection contre un employé qui serait son propre manager

#### `EmployeeListSerializer`
- **Fichier** : `serializers/employee_serializer.py`
- **Responsabilité** : Sérialisation simplifiée pour les listes
- **Optimisation** : Moins de données pour améliorer les performances

#### `EmployeeHistorySerializer`
- **Fichier** : `serializers/employee_history_serializer.py`
- **Responsabilité** : Sérialisation de l'historique des changements
- **Fonctionnalités** :
  - Inclusion des noms des employés concernés
  - Traçabilité complète (qui a fait quoi, quand)

### 2. ViewSets

#### `EmployeeViewSet`
- **Fichier** : `viewsets/employee_viewset.py`
- **Permissions** : `IsHRManagerOrAdmin` (granulaires selon le rôle)
- **Endpoints CRUD** :
  - `GET /api/employee/employees/` : Liste des employés
  - `POST /api/employee/employees/` : Créer un employé
  - `GET /api/employee/employees/{id}/` : Détails
  - `PUT/PATCH /api/employee/employees/{id}/` : Modifier
  - `DELETE /api/employee/employees/{id}/` : Supprimer

- **Actions personnalisées** :
  - `GET /api/employee/employees/active/` : Employés actifs
  - `GET /api/employee/employees/by-department/{dept_id}/` : Par département
  - `GET /api/employee/employees/my-team/` : Mon équipe (si manager)
  - `GET /api/employee/employees/statistics/` : Statistiques globales
  - `GET /api/employee/employees/{id}/subordinates/` : Subordonnés

- **Fonctionnalités automatiques** :
  - Génération automatique de l'employee_id si non fourni
  - Enregistrement automatique dans l'historique lors de création/modification/suppression
  - Détection des changements de champs importants

- **Filtrage** :
  - Par statut : `?status=active`
  - Par genre : `?gender=M`
  - Par département : `?department=1`
  - Par manager : `?manager=5`
  - Recherche : `?search=john`
  - Tri : `?ordering=-hire_date`

#### `EmployeeHistoryViewSet`
- **Fichier** : `viewsets/employee_history_viewset.py`
- **Permissions** : Lecture seule, filtrée selon les permissions
- **Endpoints** :
  - `GET /api/employee/history/` : Liste de l'historique
  - `GET /api/employee/history/by-employee/{employee_id}/` : Historique d'un employé
  - `GET /api/employee/history/recent/` : Changements récents

### 3. Permissions personnalisées

#### `IsHRManagerOrAdmin`
- **Localisation** : `viewsets/employee_viewset.py`
- **Logique** :
  - Admins et HR managers : accès complet
  - Managers : peuvent voir leurs subordonnés
  - Employés : peuvent voir leurs propres informations
  - Empêche l'accès non autorisé aux données sensibles (salaires, etc.)

## 🔐 Sécurité

### Validations implémentées

1. **Données personnelles** :
   - Unicité de l'email
   - Unicité de l'employee_id
   - Validation des dates (naissance, embauche)

2. **Données professionnelles** :
   - Salaire positif
   - Protection contre un employé qui serait son propre manager
   - Validation de la cohérence département/position

3. **Historique automatique** :
   - Enregistrement de tous les changements importants
   - Traçabilité complète (qui, quoi, quand)
   - Impossible de modifier l'historique via API

### Permissions granulaires

- **Création** : Admins/HR uniquement
- **Modification** : Admins/HR uniquement
- **Lecture** : Selon le rôle (managers voient leurs équipes)
- **Suppression** : Admins/HR uniquement

## 📡 Endpoints API

### Employés (Employee)

```bash
# Liste des employés
GET /api/employee/employees/

# Créer un employé
POST /api/employee/employees/
{
  "first_name": "John",
  "last_name": "Doe",
  "email": "john.doe@example.com",
  "phone": "+33123456789",
  "date_of_birth": "1990-01-15",
  "gender": "M",
  "employee_id": "EMP20240115001",  # Optionnel, généré automatiquement
  "hire_date": "2020-01-15",
  "department": 1,
  "position": 1,
  "manager": 5,
  "salary": "50000.00",
  "status": "active",
  "address": "123 Rue Example",
  "city": "Paris",
  "country": "France"
}

# Détails d'un employé
GET /api/employee/employees/1/

# Modifier un employé
PATCH /api/employee/employees/1/
{
  "salary": "55000.00",
  "status": "active"
}
# → Changement automatiquement enregistré dans l'historique

# Employés actifs
GET /api/employee/employees/active/

# Employés par département
GET /api/employee/employees/by-department/1/

# Mon équipe (si manager)
GET /api/employee/employees/my-team/

# Statistiques globales
GET /api/employee/employees/statistics/
# Retourne : total, par statut, par genre, salaire moyen, total, par département

# Subordonnés d'un employé
GET /api/employee/employees/1/subordinates/
```

### Historique (EmployeeHistory)

```bash
# Liste de l'historique
GET /api/employee/history/

# Historique d'un employé spécifique
GET /api/employee/history/?employee=1

# Changements récents
GET /api/employee/history/recent/
```

## 🎯 Bonnes pratiques appliquées

1. **Séparation des responsabilités** :
   - Serializers pour validation/sérialisation
   - ViewSets pour logique métier
   - Permissions pour sécurité

2. **Optimisation des requêtes** :
   - `select_related()` pour ForeignKey
   - `prefetch_related()` pour les relations inverses
   - Serializer simplifié pour les listes
   - Évite les requêtes N+1

3. **Historique automatique** :
   - Enregistrement transparent des changements
   - Détection automatique des modifications
   - Traçabilité complète

4. **Génération automatique** :
   - Employee_id généré si non fourni
   - Format : EMP + YYYYMMDD + numéro séquentiel

5. **Calculs automatiques** :
   - Âge calculé depuis la date de naissance
   - Années de service calculées depuis la date d'embauche

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
    path("api/employee/", include("employee.urls")),  # Ajouter cette ligne
]
```

### Dépendances requises

- `django-filter` : Pour le filtrage avancé
- `djangorestframework` : Framework REST
- `Pillow` : Pour la gestion des images (profile_picture)

## 📝 Exemples d'utilisation

### Workflow complet de gestion d'employé

```python
# 1. Créer un employé
POST /api/employee/employees/
{
  "first_name": "Jane",
  "last_name": "Smith",
  "email": "jane.smith@example.com",
  "hire_date": "2024-01-15",
  "department": 1,
  "salary": "60000.00"
}
# → employee_id généré automatiquement : EMP20240115001
# → Historique créé : "created"

# 2. Modifier le salaire
PATCH /api/employee/employees/1/
{
  "salary": "65000.00"
}
# → Historique créé automatiquement : "salary_changed" (50000.00 → 65000.00)

# 3. Promouvoir (changer de position)
PATCH /api/employee/employees/1/
{
  "position": 2,
  "salary": "75000.00"
}
# → Historique créé : "position_changed" et "salary_changed"

# 4. Consulter l'historique
GET /api/employee/history/?employee=1
# → Liste de tous les changements avec qui/quoi/quand

# 5. Consulter les statistiques
GET /api/employee/employees/statistics/
# → Vue d'ensemble complète
```

### Gestion hiérarchique

```python
# 1. Créer un manager
POST /api/employee/employees/
{
  "first_name": "Manager",
  "last_name": "Boss",
  "manager": null  # Pas de manager
}

# 2. Créer des subordonnés
POST /api/employee/employees/
{
  "first_name": "Employee",
  "last_name": "One",
  "manager": 1  # ID du manager
}

# 3. Consulter l'équipe d'un manager
GET /api/employee/employees/1/subordinates/
# → Liste de tous les subordonnés

# 4. Si je suis manager, voir mon équipe
GET /api/employee/employees/my-team/
# → Mes subordonnés uniquement
```

## 🔍 Tests recommandés

1. **Tests unitaires** :
   - Validation des serializers
   - Génération automatique de l'employee_id
   - Calculs (âge, années de service)
   - Permissions

2. **Tests d'intégration** :
   - Workflow complet de création/modification
   - Historique automatique
   - Gestion hiérarchique
   - Statistiques

3. **Tests de sécurité** :
   - Accès non autorisé
   - Filtrage selon les permissions
   - Protection des données sensibles

## 📚 Références

- [Django REST Framework - ViewSets](https://www.django-rest-framework.org/api-guide/viewsets/)
- [Django Filter](https://django-filter.readthedocs.io/)
- [DRF Permissions](https://www.django-rest-framework.org/api-guide/permissions/)
- [Django Signals](https://docs.djangoproject.com/en/stable/topics/signals/) (pour automatiser l'historique si besoin)

