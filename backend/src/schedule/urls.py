"""
URLs pour l'application schedule.

Ce fichier configure les routes REST pour les endpoints de schedule :
- /api/schedule/tasks/ : Gestion des tâches planifiées
- /api/schedule/meetings/ : Gestion des réunions

Utilise le DefaultRouter de DRF pour générer automatiquement les routes CRUD.
"""

from rest_framework.routers import DefaultRouter
from schedule.viewsets import ScheduleViewSet, MeetingViewSet

router = DefaultRouter()
router.register(r"tasks", ScheduleViewSet, basename="schedule-task")
router.register(r"meetings", MeetingViewSet, basename="meeting")

urlpatterns = router.urls
