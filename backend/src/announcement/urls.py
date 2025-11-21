"""
URLs pour l'application announcement.

Ce fichier configure les routes REST pour les endpoints d'annonces :
- /api/announcement/announcements/ : Gestion des annonces

Utilise le DefaultRouter de DRF pour générer automatiquement les routes CRUD.
"""

from rest_framework.routers import DefaultRouter
from announcement.viewsets import AnnouncementViewSet

router = DefaultRouter()
router.register(r"announcements", AnnouncementViewSet, basename="announcement")

urlpatterns = router.urls

