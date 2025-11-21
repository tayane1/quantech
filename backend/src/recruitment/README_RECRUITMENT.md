# Module Recruitment - Documentation Technique

## 📋 Vue d'ensemble

Le module `recruitment` gère le processus complet de recrutement dans l'application WeHR. Il inclut la gestion des offres d'emploi, des candidats, des demandes de talents et du processus d'embauche avec toutes les étapes d'entretien.

## 🏗️ Architecture

### Structure des fichiers

```
recruitment/
├── models/
│   ├── job_position.py         # Modèle JobPosition (offres d'emploi)
│   ├── candidate.py             # Modèle Candidate (candidats)
│   ├── talent_request.py       # Modèle TalentRequest (demandes de talents)
│   └── hiring_process.py       # Modèle HiringProcess (processus d'embauche)
├── serializers/
│   ├── job_position_serializer.py
│   ├── candidate_serializer.py
│   ├── talent_request_serializer.py
│   ├── hiring_process_serializer.py
│   └── __init__.py
├── viewsets/
│   ├── job_position_viewset.py
│   ├── candidate_viewset.py
│   ├── talent_request_viewset.py
│   ├── hiring_process_viewset.py
│   └── __init__.py
├── urls.py                      # Configuration des routes
└── README_RECRUITMENT.md        # Cette documentation
```

## 🔧 Composants

### 1. Serializers

#### `JobPositionSerializer`
- **Fichier** : `serializers/job_position_serializer.py`
- **Responsabilité** : Sérialisation des offres d'emploi
- **Fonctionnalités** :
  - Statistiques intégrées (nombre de candidats, candidats actifs)
  - Validation : impossible de fermer une offre avec des candidatures actives
  - Inclusion du nom du département

#### `CandidateSerializer`
- **Fichier** : `serializers/candidate_serializer.py`
- **Responsabilité** : Sérialisation des candidats
- **Fonctionnalités** :
  - Validation de l'email (unicité)
  - Validation du fichier CV (taille max 5MB, formats PDF/DOC/DOCX)
  - Informations de l'offre associée
  - Nombre d'étapes du processus d'embauche

#### `TalentRequestSerializer`
- **Fichier** : `serializers/talent_request_serializer.py`
- **Responsabilité** : Sérialisation des demandes de talents
- **Fonctionnalités** :
  - Validation du nombre de personnes (doit être > 0)
  - Validation de cohérence avec le statut de l'offre
  - Informations contextuelles (nom du demandeur, département)

#### `HiringProcessSerializer`
- **Fichier** : `serializers/hiring_process_serializer.py`
- **Responsabilité** : Sérialisation des étapes du processus d'embauche
- **Fonctionnalités** :
  - Validation de la date (ne peut pas être dans le passé)
  - Validation : impossible d'ajouter des étapes pour candidats embauchés/rejetés
  - Informations du candidat et de l'interviewer

### 2. ViewSets

#### `JobPositionViewSet`
- **Fichier** : `viewsets/job_position_viewset.py`
- **Permissions** : `IsHRManagerOrAdmin` (lecture pour tous, modification pour admins/HR)
- **Endpoints CRUD** :
  - `GET /api/recruitment/job-positions/` : Liste des offres
  - `POST /api/recruitment/job-positions/` : Créer une offre
  - `GET /api/recruitment/job-positions/{id}/` : Détails
  - `PUT/PATCH /api/recruitment/job-positions/{id}/` : Modifier
  - `DELETE /api/recruitment/job-positions/{id}/` : Supprimer

- **Actions personnalisées** :
  - `GET /api/recruitment/job-positions/urgent/` : Offres urgentes
  - `GET /api/recruitment/job-positions/open/` : Offres ouvertes
  - `GET /api/recruitment/job-positions/{id}/statistics/` : Statistiques détaillées

- **Filtrage** :
  - Par statut : `?status=open`
  - Par urgence : `?urgency=true`
  - Par département : `?department=1`
  - Recherche : `?search=développeur`
  - Tri : `?ordering=-created_at`

#### `CandidateViewSet`
- **Fichier** : `viewsets/candidate_viewset.py`
- **Permissions** : `IsHRManagerOrAdmin` (lecture pour tous, modification pour admins/HR/recruteurs)
- **Endpoints CRUD** : Similaires à JobPositionViewSet

- **Actions personnalisées** :
  - `POST /api/recruitment/candidates/{id}/change-status/` : Changer le statut
  - `GET /api/recruitment/candidates/by-position/{position_id}/` : Candidats par offre
  - `GET /api/recruitment/candidates/active/` : Candidats actifs (non rejetés/embauchés)

- **Filtrage** :
  - Par statut : `?status=interview`
  - Par offre : `?position=1`
  - Recherche : `?search=john`
  - Tri : `?ordering=-applied_date`

#### `TalentRequestViewSet`
- **Fichier** : `viewsets/talent_request_viewset.py`
- **Permissions** : `IsHRManagerOrAdmin` (création pour tous, modification selon propriétaire)
- **Endpoints CRUD** : Similaires aux autres

- **Actions personnalisées** :
  - `POST /api/recruitment/talent-requests/{id}/approve/` : Approuver (admin/HR uniquement)
  - `POST /api/recruitment/talent-requests/{id}/reject/` : Rejeter (admin/HR uniquement)
  - `POST /api/recruitment/talent-requests/{id}/fulfill/` : Marquer comme satisfait
  - `GET /api/recruitment/talent-requests/pending/` : Demandes en attente

#### `HiringProcessViewSet`
- **Fichier** : `viewsets/hiring_process_viewset.py`
- **Permissions** : `IsHRManagerOrAdmin` (lecture pour tous, modification pour admins/HR/recruteurs)
- **Endpoints CRUD** : Similaires aux autres

- **Actions personnalisées** :
  - `GET /api/recruitment/hiring-process/by-candidate/{candidate_id}/` : Étapes par candidat
  - `GET /api/recruitment/hiring-process/upcoming/` : Entretiens à venir

### 3. Permissions personnalisées

#### `IsHRManagerOrAdmin`
- **Localisation** : Dans chaque viewset
- **Logique** :
  - Admins et HR managers : accès complet
  - Recruteurs : peuvent modifier candidats et processus
  - Autres utilisateurs : lecture seule
  - Empêche l'accès non autorisé aux données sensibles

## 🔐 Sécurité

### Validations implémentées

1. **Offres d'emploi** :
   - Impossible de fermer une offre avec des candidatures actives
   - Validation des statuts

2. **Candidats** :
   - Unicité de l'email
   - Validation du fichier CV (taille, format)
   - Protection contre les statuts invalides

3. **Demandes de talents** :
   - Nombre de personnes > 0
   - Cohérence avec le statut de l'offre

4. **Processus d'embauche** :
   - Dates dans le futur
   - Impossible d'ajouter des étapes pour candidats terminés

### Permissions granulaires

- **Création** : Selon le rôle (tous pour demandes, admins/HR pour offres)
- **Modification** : Selon le rôle et la propriété
- **Suppression** : Admins/HR uniquement

## 📡 Endpoints API

### Offres d'emploi (JobPosition)

```bash
# Liste des offres
GET /api/recruitment/job-positions/

# Créer une offre
POST /api/recruitment/job-positions/
{
  "title": "Développeur Full Stack",
  "description": "Recherche développeur expérimenté...",
  "department": 1,
  "status": "open",
  "urgency": true
}

# Offres urgentes
GET /api/recruitment/job-positions/urgent/

# Statistiques d'une offre
GET /api/recruitment/job-positions/1/statistics/
```

### Candidats (Candidate)

```bash
# Liste des candidats
GET /api/recruitment/candidates/

# Créer un candidat
POST /api/recruitment/candidates/
{
  "first_name": "John",
  "last_name": "Doe",
  "email": "john.doe@example.com",
  "phone": "+33123456789",
  "resume": <file>,
  "position": 1
}

# Changer le statut
POST /api/recruitment/candidates/1/change-status/
{
  "status": "interview",
  "notes": "Entretien technique prévu"
}

# Candidats par offre
GET /api/recruitment/candidates/by-position/1/
```

### Demandes de talents (TalentRequest)

```bash
# Créer une demande
POST /api/recruitment/talent-requests/
{
  "position": 1,
  "number_of_people": 2,
  "description": "Besoin urgent de 2 développeurs"
}

# Approuver une demande
POST /api/recruitment/talent-requests/1/approve/

# Demandes en attente
GET /api/recruitment/talent-requests/pending/
```

### Processus d'embauche (HiringProcess)

```bash
# Créer une étape
POST /api/recruitment/hiring-process/
{
  "candidate": 1,
  "stage": "Entretien technique",
  "scheduled_date": "2024-01-20T14:00:00Z",
  "interviewer": 5
}

# Étapes par candidat
GET /api/recruitment/hiring-process/by-candidate/1/

# Entretiens à venir
GET /api/recruitment/hiring-process/upcoming/
```

## 🎯 Bonnes pratiques appliquées

1. **Séparation des responsabilités** :
   - Serializers pour validation/sérialisation
   - ViewSets pour logique métier
   - Permissions pour sécurité

2. **Optimisation des requêtes** :
   - `select_related()` pour ForeignKey
   - `prefetch_related()` pour ManyToMany et relations inverses
   - Évite les requêtes N+1

3. **Actions personnalisées** :
   - Workflow métier (approve, reject, change-status)
   - Filtres métier (urgent, active, pending)
   - Statistiques agrégées

4. **Validation robuste** :
   - Validation au niveau serializer
   - Validation au niveau viewset
   - Messages d'erreur explicites

## 🚀 Intégration

### Dans `backend/urls.py`

```python
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path("api/users/", include("users.urls")),
    path("api/schedule/", include("schedule.urls")),
    path("api/recruitment/", include("recruitment.urls")),  # Ajouter cette ligne
]
```

### Dépendances requises

- `django-filter` : Pour le filtrage avancé
- `djangorestframework` : Framework REST
- `Pillow` : Pour la gestion des fichiers (CV)

## 📝 Exemples d'utilisation

### Workflow complet de recrutement

```python
# 1. Créer une offre
POST /api/recruitment/job-positions/
{
  "title": "Développeur Python",
  "department": 1,
  "urgency": true
}

# 2. Un candidat postule
POST /api/recruitment/candidates/
{
  "first_name": "Jane",
  "last_name": "Smith",
  "email": "jane@example.com",
  "position": 1,
  "resume": <file>
}

# 3. Changer le statut pour entretien
POST /api/recruitment/candidates/1/change-status/
{
  "status": "interview"
}

# 4. Créer une étape d'entretien
POST /api/recruitment/hiring-process/
{
  "candidate": 1,
  "stage": "Entretien technique",
  "scheduled_date": "2024-01-25T10:00:00Z",
  "interviewer": 5
}

# 5. Après l'entretien, mettre à jour
PATCH /api/recruitment/hiring-process/1/
{
  "feedback": "Excellent candidat, très compétent",
  "result": "Pass"
}

# 6. Faire une offre
POST /api/recruitment/candidates/1/change-status/
{
  "status": "offered"
}

# 7. Embaucher
POST /api/recruitment/candidates/1/change-status/
{
  "status": "hired"
}
```

## 🔍 Tests recommandés

1. **Tests unitaires** :
   - Validation des serializers
   - Permissions
   - Actions personnalisées

2. **Tests d'intégration** :
   - Workflow complet de recrutement
   - Gestion des fichiers CV
   - Workflow d'approbation des demandes

3. **Tests de sécurité** :
   - Accès non autorisé
   - Validation des fichiers uploadés
   - Filtrage des données selon les permissions

## 📚 Références

- [Django REST Framework - ViewSets](https://www.django-rest-framework.org/api-guide/viewsets/)
- [Django Filter](https://django-filter.readthedocs.io/)
- [DRF Permissions](https://www.django-rest-framework.org/api-guide/permissions/)
- [File Uploads in DRF](https://www.django-rest-framework.org/api-guide/parsers/#fileuploadparser)

