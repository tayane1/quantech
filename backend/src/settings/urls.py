"""
URLs pour l'application settings.

Ce fichier configure les routes REST pour les endpoints de paramètres :
- /api/settings/system-settings/ : Paramètres système
- /api/settings/email-templates/ : Modèles d'emails
- /api/settings/notification-settings/ : Paramètres de notifications

Utilise le DefaultRouter de DRF pour générer automatiquement les routes CRUD.
"""

from rest_framework.routers import DefaultRouter
from settings.viewsets import (
    SystemSettingsViewSet,
    EmailTemplateViewSet,
    NotificationSettingsViewSet,
)

router = DefaultRouter()
router.register(
    r"system-settings", SystemSettingsViewSet, basename="system-settings"
)
router.register(r"email-templates", EmailTemplateViewSet, basename="email-template")
router.register(
    r"notification-settings",
    NotificationSettingsViewSet,
    basename="notification-settings",
)

urlpatterns = router.urls

