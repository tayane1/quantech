# Module Dashboard - Documentation Technique

## 📋 Vue d'ensemble

Le module `dashboard` gère le tableau de bord principal de l'application WeHR. Il inclut la gestion des métriques (statistiques agrégées), des activités (timeline des événements), et fournit une vue d'ensemble consolidée pour les utilisateurs.

## 🏗️ Architecture

### Structure des fichiers

```
dashboard/
├── models/
│   ├── dashboard_metric.py      # Modèle DashboardMetric (métriques)
│   └── activity.py               # Modèle Activity (activités)
├── serializers/
│   ├── dashboard_metric_serializer.py
│   ├── activity_serializer.py
│   └── __init__.py
├── viewsets/
│   ├── dashboard_metric_viewset.py
│   ├── activity_viewset.py
│   └── __init__.py
├── views/
│   ├── dashboard_views.py        # Vue d'ensemble consolidée
│   └── __init__.py
├── urls.py                        # Configuration des routes
└── README_DASHBOARD.md            # Cette documentation
```

## 🔧 Composants

### 1. Serializers

#### `DashboardMetricSerializer`
- **Fichier** : `serializers/dashboard_metric_serializer.py`
- **Responsabilité** : Sérialisation des métriques avec calculs de tendances
- **Fonctionnalités** :
  - Calcul automatique de la direction du changement (up/down/neutral)
  - Label lisible pour le changement (ex: "+5.2%", "-3.1%")
  - Inclusion des valeurs précédentes et pourcentages

#### `ActivitySerializer`
- **Fichier** : `serializers/activity_serializer.py`
- **Responsabilité** : Sérialisation des activités avec informations contextuelles
- **Fonctionnalités** :
  - Inclusion des noms des utilisateurs, candidats, employés concernés
  - Titres des offres d'emploi associées
  - Affichage lisible des types d'activités

### 2. ViewSets

#### `DashboardMetricViewSet`
- **Fichier** : `viewsets/dashboard_metric_viewset.py`
- **Permissions** : `IsAdminOrHR` (lecture pour tous, modification pour admins/HR)
- **Endpoints CRUD** :
  - `GET /api/dashboard/metrics/` : Liste des métriques
  - `GET /api/dashboard/metrics/{id}/` : Détails d'une métrique

- **Actions personnalisées** :
  - `POST /api/dashboard/metrics/recalculate/` : Recalculer toutes les métriques
  - `POST /api/dashboard/metrics/recalculate/{metric_type}/` : Recalculer une métrique spécifique

- **Métriques calculées automatiquement** :
  - `total_employees` : Nombre total d'employés
  - `active_employees` : Nombre d'employés actifs
  - `available_positions` : Nombre d'offres ouvertes
  - `urgent_positions` : Nombre d'offres urgentes
  - `total_candidates` : Nombre total de candidats
  - `active_candidates` : Nombre de candidats actifs
  - `talent_requests` : Nombre total de demandes de talents
  - `pending_talent_requests` : Nombre de demandes en attente

#### `ActivityViewSet`
- **Fichier** : `viewsets/activity_viewset.py`
- **Permissions** : `IsAdminOrHR` (création pour tous, consultation filtrée)
- **Endpoints CRUD** :
  - `GET /api/dashboard/activities/` : Liste des activités
  - `POST /api/dashboard/activities/` : Créer une activité
  - `GET /api/dashboard/activities/{id}/` : Détails
  - `DELETE /api/dashboard/activities/{id}/` : Supprimer

- **Actions personnalisées** :
  - `GET /api/dashboard/activities/recent/` : Activités récentes (7 jours)
  - `GET /api/dashboard/activities/today/` : Activités d'aujourd'hui
  - `GET /api/dashboard/activities/by-type/{type}/` : Activités par type
  - `GET /api/dashboard/activities/my-activities/` : Mes activités

- **Types d'activités** :
  - `job_posted` : Offre postée
  - `candidate_applied` : Candidature reçue
  - `employee_added` : Employé ajouté
  - `announcement_posted` : Annonce publiée
  - `schedule_created` : Tâche créée
  - `meeting_scheduled` : Réunion planifiée

### 3. Vues personnalisées

#### `dashboard_overview`
- **Fichier** : `views/dashboard_views.py`
- **Endpoint** : `GET /api/dashboard/overview/`
- **Fonctionnalités** :
  - Vue d'ensemble consolidée du dashboard
  - Métriques principales
  - Activités récentes (10 dernières)
  - Statistiques supplémentaires (employés, recrutement, planning)

## 🔐 Sécurité

### Permissions

1. **Métriques** :
   - Lecture : tous les utilisateurs authentifiés
   - Modification/Recalcul : admins/HR uniquement

2. **Activités** :
   - Création : tous les utilisateurs authentifiés
   - Consultation : utilisateurs voient leurs activités, admins voient tout
   - Suppression : admins/HR uniquement

## 📡 Endpoints API

### Vue d'ensemble

```bash
# Vue d'ensemble complète du dashboard
GET /api/dashboard/overview/
# Retourne :
# - metrics : toutes les métriques avec tendances
# - recent_activities : 10 dernières activités
# - statistics : statistiques consolidées (employés, recrutement, planning)
```

### Métriques

```bash
# Liste des métriques
GET /api/dashboard/metrics/

# Recalculer toutes les métriques
POST /api/dashboard/metrics/recalculate/

# Recalculer une métrique spécifique
POST /api/dashboard/metrics/recalculate/total_employees/
```

### Activités

```bash
# Liste des activités
GET /api/dashboard/activities/

# Créer une activité
POST /api/dashboard/activities/
{
  "user": 1,
  "activity_type": "job_posted",
  "description": "Nouvelle offre publiée : Développeur Full Stack",
  "related_position": 5
}

# Activités récentes (7 jours)
GET /api/dashboard/activities/recent/

# Activités d'aujourd'hui
GET /api/dashboard/activities/today/

# Activités par type
GET /api/dashboard/activities/by-type/job_posted/

# Mes activités
GET /api/dashboard/activities/my-activities/
```

## 🎯 Bonnes pratiques appliquées

1. **Calcul automatique des métriques** :
   - Méthodes privées pour calculer chaque métrique
   - Calcul du pourcentage de changement
   - Mise à jour automatique avec `update_or_create`

2. **Optimisation des requêtes** :
   - `select_related()` pour les ForeignKey
   - Limitation des résultats (10 activités récentes)
   - Requêtes agrégées pour les statistiques

3. **Vue d'ensemble consolidée** :
   - Endpoint unique pour récupérer toutes les données du dashboard
   - Réduction du nombre de requêtes côté client
   - Données structurées et prêtes à l'emploi

4. **Traçabilité** :
   - Enregistrement de toutes les activités importantes
   - Relations avec les entités concernées
   - Timeline complète des événements

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
    path("api/department/", include("department.urls")),
    path("api/dashboard/", include("dashboard.urls")),  # Ajouter cette ligne
]
```

### Dépendances requises

- `django-filter` : Pour le filtrage avancé
- `djangorestframework` : Framework REST

### Configuration recommandée

Pour automatiser la mise à jour des métriques, vous pouvez créer une tâche périodique (cron job ou Celery) :

```python
# Exemple avec Celery
@periodic_task(run_every=crontab(hours=1))
def update_dashboard_metrics():
    viewset = DashboardMetricViewSet()
    viewset._calculate_all_metrics()
```

## 📝 Exemples d'utilisation

### Workflow complet du dashboard

```python
# 1. Récupérer la vue d'ensemble
GET /api/dashboard/overview/
# → Toutes les données nécessaires pour afficher le dashboard

# 2. Recalculer les métriques (admin/HR)
POST /api/dashboard/metrics/recalculate/
# → Met à jour toutes les métriques avec les dernières données

# 3. Consulter les activités récentes
GET /api/dashboard/activities/recent/
# → Activités des 7 derniers jours

# 4. Créer une activité (automatique ou manuelle)
POST /api/dashboard/activities/
{
  "activity_type": "employee_added",
  "description": "Nouvel employé ajouté : John Doe",
  "related_employee": 10
}
```

### Intégration avec d'autres modules

Les activités peuvent être créées automatiquement via des signaux Django :

```python
# Exemple dans recruitment/signals.py
from django.db.models.signals import post_save
from django.dispatch import receiver
from recruitment.models import JobPosition
from dashboard.models import Activity

@receiver(post_save, sender=JobPosition)
def create_job_posted_activity(sender, instance, created, **kwargs):
    if created:
        Activity.objects.create(
            user=instance.department.manager if instance.department else None,
            activity_type=Activity.ACTIVITY_JOB_POSTED,
            description=f"Nouvelle offre publiée : {instance.title}",
            related_position=instance,
        )
```

## 🔍 Tests recommandés

1. **Tests unitaires** :
   - Calcul des métriques
   - Calcul des pourcentages de changement
   - Validation des serializers

2. **Tests d'intégration** :
   - Recalcul complet des métriques
   - Création d'activités
   - Vue d'ensemble consolidée

3. **Tests de performance** :
   - Temps de calcul des métriques
   - Optimisation des requêtes
   - Cache des métriques (optionnel)

## 📚 Références

- [Django REST Framework - ViewSets](https://www.django-rest-framework.org/api-guide/viewsets/)
- [Django Signals](https://docs.djangoproject.com/en/stable/topics/signals/)
- [Django Aggregation](https://docs.djangoproject.com/en/stable/topics/db/aggregation/)
- [Celery - Periodic Tasks](https://docs.celeryproject.org/en/stable/userguide/periodic-tasks.html)

