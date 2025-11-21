"""
ViewSet pour la gestion des paramètres système (SystemSettings).

Ce ViewSet implémente les opérations CRUD pour les paramètres système :
- Lecture, modification uniquement (pas de création/suppression - singleton)
- Actions personnalisées : réinitialisation, export/import
- Permissions : seuls les admins peuvent modifier les paramètres
"""

from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.filters import SearchFilter, OrderingFilter

from settings.models import SystemSettings
from settings.serializers.system_settings_serializer import SystemSettingsSerializer


class SystemSettingsViewSet(viewsets.ModelViewSet):
    """
    ViewSet pour les paramètres système.
    
    Endpoints disponibles :
    - GET /api/settings/system-settings/ : Récupérer les paramètres
    - PUT/PATCH /api/settings/system-settings/{id}/ : Modifier les paramètres (admin seulement)
    - POST /api/settings/system-settings/reset/ : Réinitialiser les paramètres par défaut (admin seulement)
    - GET /api/settings/system-settings/export/ : Exporter les paramètres (admin seulement)
    """
    
    queryset = SystemSettings.objects.all()
    serializer_class = SystemSettingsSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [SearchFilter, OrderingFilter]
    http_method_names = ["get", "put", "patch", "head", "options"]

    def get_permissions(self):
        """Détermine les permissions selon l'action."""
        if self.action in ["update", "partial_update", "reset", "export"]:
            # Seuls les admins peuvent modifier
            return [permissions.IsAdminUser()]
        # Tous les utilisateurs authentifiés peuvent lire
        return [permissions.IsAuthenticated()]

    def get_object(self):
        """Retourne toujours l'instance unique des paramètres système."""
        return SystemSettings.get_settings()

    def list(self, request, *args, **kwargs):
        """Redirige vers l'instance unique."""
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    @action(detail=False, methods=["post"], url_path="reset")
    def reset(self, request):
        """
        Action personnalisée : Réinitialiser les paramètres aux valeurs par défaut.
        POST /api/settings/system-settings/reset/
        """
        settings = self.get_object()
        
        # Réinitialiser aux valeurs par défaut
        settings.company_name = "Mon Entreprise"
        settings.company_email = "contact@entreprise.com"
        settings.site_name = "WeHR"
        settings.maintenance_mode = False
        settings.maintenance_message = ""
        settings.password_min_length = 8
        settings.password_require_uppercase = True
        settings.password_require_lowercase = True
        settings.password_require_numbers = True
        settings.password_require_special = True
        settings.session_timeout_minutes = 30
        settings.max_login_attempts = 5
        settings.lockout_duration_minutes = 15
        settings.email_enabled = True
        settings.email_port = 587
        settings.email_use_tls = True
        settings.enable_email_notifications = True
        settings.enable_sms_notifications = False
        settings.enable_push_notifications = True
        settings.max_upload_size_mb = 10
        settings.updated_by = request.user
        settings.save()
        
        serializer = self.get_serializer(settings)
        return Response(
            {"message": "Les paramètres ont été réinitialisés aux valeurs par défaut.", "settings": serializer.data}
        )

    @action(detail=False, methods=["get"], url_path="export")
    def export(self, request):
        """
        Action personnalisée : Exporter les paramètres système.
        GET /api/settings/system-settings/export/
        """
        settings = self.get_object()
        serializer = self.get_serializer(settings)
        return Response(serializer.data)

