# Module Schedule - Documentation Technique

## 📋 Vue d'ensemble

Le module `schedule` gère les tâches planifiées et les réunions dans l'application WeHR. Il implémente une API RESTful complète avec opérations CRUD, filtrage, recherche et actions personnalisées.

## 🏗️ Architecture

### Structure des fichiers

```
schedule/
├── models/
│   ├── schedule_task.py      # Modèle Schedule (tâches planifiées)
│   └── meeting.py             # Modèle Meeting (réunions)
├── serializers/
│   ├── schedule_serializer.py
│   ├── meeting_serializer.py
│   └── __init__.py
├── viewsets/
│   ├── schedule_viewset.py
│   ├── meeting_viewset.py
│   └── __init__.py
├── urls.py                    # Configuration des routes
└── README_SCHEDULE.md         # Cette documentation
```

## 🔧 Composants

### 1. Serializers

#### `ScheduleSerializer`
- **Fichier** : `serializers/schedule_serializer.py`
- **Responsabilité** : Sérialisation/désérialisation des tâches planifiées
- **Fonctionnalités** :
  - Validation de la date planifiée (ne peut pas être dans le passé pour nouvelles tâches)
  - Gestion automatique de `completed_date` lors du changement de statut
  - Inclusion des noms des employés assignés (lecture seule)

#### `MeetingSerializer`
- **Fichier** : `serializers/meeting_serializer.py`
- **Responsabilité** : Sérialisation/désérialisation des réunions
- **Fonctionnalités** :
  - Validation que `end_time` > `start_time`
  - Inclusion des détails des participants (méthode `get_attendees_details`)
  - Compteur de participants

### 2. ViewSets

#### `ScheduleViewSet`
- **Fichier** : `viewsets/schedule_viewset.py`
- **Permissions** : `IsAssignedEmployeeOrAdmin` (custom)
- **Endpoints CRUD** :
  - `GET /api/schedule/tasks/` : Liste des tâches
  - `POST /api/schedule/tasks/` : Créer une tâche
  - `GET /api/schedule/tasks/{id}/` : Détails
  - `PUT/PATCH /api/schedule/tasks/{id}/` : Modifier
  - `DELETE /api/schedule/tasks/{id}/` : Supprimer

- **Actions personnalisées** :
  - `POST /api/schedule/tasks/{id}/complete/` : Marquer comme complétée
  - `GET /api/schedule/tasks/my-tasks/` : Mes tâches assignées
  - `GET /api/schedule/tasks/upcoming/` : Tâches à venir

- **Filtrage** :
  - Par priorité : `?priority=high`
  - Par statut : `?completed=true`
  - Par employé : `?assigned_to=1`
  - Recherche : `?search=meeting`
  - Tri : `?ordering=-scheduled_date`

#### `MeetingViewSet`
- **Fichier** : `viewsets/meeting_viewset.py`
- **Permissions** : `IsAuthenticated` (tous les utilisateurs authentifiés)
- **Endpoints CRUD** : Similaires à ScheduleViewSet

- **Actions personnalisées** :
  - `GET /api/schedule/meetings/upcoming/` : Réunions à venir
  - `GET /api/schedule/meetings/my-meetings/` : Mes réunions (organisateur ou participant)
  - `POST /api/schedule/meetings/{id}/add-attendee/` : Ajouter un participant
  - `POST /api/schedule/meetings/{id}/remove-attendee/` : Retirer un participant

### 3. Permissions personnalisées

#### `IsAssignedEmployeeOrAdmin`
- **Localisation** : `viewsets/schedule_viewset.py`
- **Logique** :
  - Admins : accès complet
  - Employés : uniquement leurs tâches assignées
  - Empêche l'accès non autorisé aux données sensibles

## 🔐 Sécurité

### Validations implémentées

1. **Dates** :
   - Les nouvelles tâches ne peuvent pas avoir une date passée
   - Les réunions doivent avoir `end_time > start_time`

2. **Permissions** :
   - Filtrage automatique du queryset selon le rôle
   - Vérification au niveau objet pour les modifications

3. **Données** :
   - Validation des champs requis
   - Protection contre les injections SQL (via ORM Django)

## 📡 Endpoints API

### Tâches (Schedule)

```bash
# Liste des tâches
GET /api/schedule/tasks/

# Créer une tâche
POST /api/schedule/tasks/
{
  "title": "Réviser les candidatures",
  "description": "Examiner les CV reçus",
  "assigned_to": 1,
  "priority": "high",
  "scheduled_date": "2024-01-15T10:00:00Z"
}

# Détails d'une tâche
GET /api/schedule/tasks/1/

# Modifier une tâche
PATCH /api/schedule/tasks/1/
{
  "completed": true
}

# Marquer comme complétée
POST /api/schedule/tasks/1/complete/

# Mes tâches
GET /api/schedule/tasks/my-tasks/

# Tâches à venir
GET /api/schedule/tasks/upcoming/
```

### Réunions (Meeting)

```bash
# Liste des réunions
GET /api/schedule/meetings/

# Créer une réunion
POST /api/schedule/meetings/
{
  "title": "Réunion équipe",
  "description": "Discussion projet",
  "start_time": "2024-01-15T14:00:00Z",
  "end_time": "2024-01-15T15:00:00Z",
  "location": "Salle A",
  "attendees": [1, 2, 3]
}

# Ajouter un participant
POST /api/schedule/meetings/1/add-attendee/
{
  "employee_id": 5
}

# Mes réunions
GET /api/schedule/meetings/my-meetings/
```

## 🎯 Bonnes pratiques appliquées

1. **Séparation des responsabilités** :
   - Serializers pour la validation/sérialisation
   - ViewSets pour la logique métier
   - Permissions pour la sécurité

2. **Optimisation des requêtes** :
   - `select_related()` pour les ForeignKey
   - `prefetch_related()` pour les ManyToMany
   - Évite les requêtes N+1

3. **Actions personnalisées** :
   - Utilisation du décorateur `@action` de DRF
   - Endpoints métier spécifiques (complete, upcoming, etc.)

4. **Filtrage et recherche** :
   - Intégration de `django-filter`
   - Recherche full-text sur les champs pertinents
   - Tri personnalisable

## 🚀 Intégration

### Dans `backend/urls.py`

```python
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path("api/users/", include("users.urls")),
    path("api/schedule/", include("schedule.urls")),  # Ajouter cette ligne
]
```

### Dépendances requises

- `django-filter` : Pour le filtrage avancé
- `djangorestframework` : Framework REST
- `rest_framework_simplejwt` : Authentification JWT

## 📝 Exemples d'utilisation

### Créer une tâche avec assignation automatique

```python
# L'utilisateur connecté sera automatiquement défini comme assigneur
POST /api/schedule/tasks/
{
  "title": "Nouvelle tâche",
  "assigned_to": 2,
  "priority": "medium",
  "scheduled_date": "2024-01-20T09:00:00Z"
}
```

### Filtrer les tâches urgentes non complétées

```bash
GET /api/schedule/tasks/?priority=high&completed=false
```

### Récupérer les réunions de la semaine

```python
# Utiliser le filtre de date dans le frontend
GET /api/schedule/meetings/upcoming/
# Puis filtrer côté client pour la semaine courante
```

## 🔍 Tests recommandés

1. **Tests unitaires** :
   - Validation des serializers
   - Permissions
   - Actions personnalisées

2. **Tests d'intégration** :
   - Création complète d'une tâche
   - Workflow de complétion
   - Gestion des participants aux réunions

3. **Tests de sécurité** :
   - Accès non autorisé
   - Filtrage des données selon les permissions

## 📚 Références

- [Django REST Framework - ViewSets](https://www.django-rest-framework.org/api-guide/viewsets/)
- [Django Filter](https://django-filter.readthedocs.io/)
- [DRF Permissions](https://www.django-rest-framework.org/api-guide/permissions/)

