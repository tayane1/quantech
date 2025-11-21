"""
ViewSet pour la gestion des paramètres de notifications (NotificationSettings).

Ce ViewSet implémente les opérations CRUD complètes pour les paramètres de notifications :
- Liste, détail, création, modification, suppression
- Actions personnalisées : activer/désactiver par type
- Permissions : seuls les admins peuvent gérer les paramètres de notifications
"""

from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from django.db.models import Count

from settings.models import NotificationSettings
from settings.serializers.notification_settings_serializer import (
    NotificationSettingsSerializer,
)


class NotificationSettingsViewSet(viewsets.ModelViewSet):
    """
    ViewSet pour les paramètres de notifications.
    
    Endpoints disponibles :
    - GET /api/settings/notification-settings/ : Liste des paramètres
    - POST /api/settings/notification-settings/ : Créer un paramètre (admin seulement)
    - GET /api/settings/notification-settings/{id}/ : Détails d'un paramètre
    - PUT/PATCH /api/settings/notification-settings/{id}/ : Modifier un paramètre (admin seulement)
    - DELETE /api/settings/notification-settings/{id}/ : Supprimer un paramètre (admin seulement)
    - POST /api/settings/notification-settings/{id}/enable/ : Activer un type de notification
    - POST /api/settings/notification-settings/{id}/disable/ : Désactiver un type de notification
    - GET /api/settings/notification-settings/active/ : Notifications actives uniquement
    - GET /api/settings/notification-settings/statistics/ : Statistiques
    """
    
    queryset = NotificationSettings.objects.all()
    serializer_class = NotificationSettingsSerializer
    permission_classes = [permissions.IsAdminUser]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ["notification_type", "enabled"]
    search_fields = ["notification_type"]
    ordering_fields = ["notification_type", "created_at"]
    ordering = ["notification_type"]

    @action(detail=True, methods=["post"], url_path="enable")
    def enable(self, request, pk=None):
        """
        Action personnalisée : Activer un type de notification.
        POST /api/settings/notification-settings/{id}/enable/
        """
        notification_setting = self.get_object()
        notification_setting.enabled = True
        notification_setting.save()
        
        serializer = self.get_serializer(notification_setting)
        return Response(serializer.data)

    @action(detail=True, methods=["post"], url_path="disable")
    def disable(self, request, pk=None):
        """
        Action personnalisée : Désactiver un type de notification.
        POST /api/settings/notification-settings/{id}/disable/
        """
        notification_setting = self.get_object()
        notification_setting.enabled = False
        notification_setting.save()
        
        serializer = self.get_serializer(notification_setting)
        return Response(serializer.data)

    @action(detail=False, methods=["get"], url_path="active")
    def active(self, request):
        """
        Action personnalisée : Récupérer uniquement les notifications actives.
        GET /api/settings/notification-settings/active/
        """
        settings = self.get_queryset().filter(enabled=True)
        
        page = self.paginate_queryset(settings)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(settings, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=["get"], url_path="statistics")
    def statistics(self, request):
        """
        Action personnalisée : Statistiques sur les paramètres de notifications.
        GET /api/settings/notification-settings/statistics/
        """
        queryset = self.get_queryset()
        
        stats = {
            "total": queryset.count(),
            "enabled": queryset.filter(enabled=True).count(),
            "disabled": queryset.filter(enabled=False).count(),
            "by_type": queryset.values("notification_type")
            .annotate(count=Count("id"))
            .order_by("notification_type"),
            "email_enabled": queryset.filter(send_email=True).count(),
            "sms_enabled": queryset.filter(send_sms=True).count(),
            "push_enabled": queryset.filter(send_push=True).count(),
        }
        
        return Response(stats)

