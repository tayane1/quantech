"""
URLs pour l'application recruitment.

Ce fichier configure les routes REST pour les endpoints de recruitment :
- /api/recruitment/job-positions/ : Gestion des offres d'emploi
- /api/recruitment/candidates/ : Gestion des candidats
- /api/recruitment/talent-requests/ : Gestion des demandes de talents
- /api/recruitment/hiring-process/ : Gestion du processus d'embauche
- /api/recruitment/statistics/ : Statistiques globales du recrutement

Utilise le DefaultRouter de DRF pour générer automatiquement les routes CRUD.
"""

from django.urls import path
from rest_framework.routers import DefaultRouter
from recruitment.viewsets import (
    JobPositionViewSet,
    CandidateViewSet,
    TalentRequestViewSet,
    HiringProcessViewSet,
)
from recruitment.views import RecruitmentStatisticsView

router = DefaultRouter()
router.register(r"job-positions", JobPositionViewSet, basename="job-position")
router.register(r"candidates", CandidateViewSet, basename="candidate")
router.register(r"talent-requests", TalentRequestViewSet, basename="talent-request")
router.register(r"hiring-process", HiringProcessViewSet, basename="hiring-process")

urlpatterns = [
    path("statistics/", RecruitmentStatisticsView.as_view(), name="recruitment-statistics"),
] + router.urls

