"""
ViewSet pour la gestion de l'historique de connexion (LoginHistory).

Ce ViewSet permet de consulter l'historique des connexions :
- Les utilisateurs peuvent voir uniquement leur propre historique
- Les admins peuvent voir tout l'historique
- Lecture seule (pas de création/modification via API)
"""

from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter

from login.models.login_history import LoginHistory
from login.serializers.login_history_serializer import LoginHistorySerializer


class IsOwnerOrAdmin(permissions.BasePermission):
    """
    Permission personnalisée :
    - Les admins peuvent voir tout
    - Les utilisateurs peuvent voir uniquement leur propre historique
    """

    def has_object_permission(self, request, view, obj):
        if request.user.is_staff or request.user.is_superuser:
            return True
        return obj.user == request.user

    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated


class LoginHistoryViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet en lecture seule pour l'historique de connexion.
    
    Endpoints disponibles :
    - GET /api/login/history/ : Liste de l'historique
    - GET /api/login/history/{id}/ : Détails d'une entrée
    - GET /api/login/history/my-history/ : Mon historique
    - GET /api/login/history/recent/ : Connexions récentes
    """
    
    serializer_class = LoginHistorySerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrAdmin]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ["is_successful", "device_type"]
    search_fields = ["ip_address", "user_agent"]
    ordering_fields = ["login_time", "logout_time"]
    ordering = ["-login_time"]

    def get_queryset(self):
        """Filtre le queryset selon les permissions."""
        queryset = LoginHistory.objects.select_related("user").all()
        
        # Si admin, retourner tout
        if self.request.user.is_staff or self.request.user.is_superuser:
            return queryset
        
        # Sinon, filtrer par utilisateur
        return queryset.filter(user=self.request.user)

    @action(detail=False, methods=["get"], url_path="my-history")
    def my_history(self, request):
        """
        Action personnalisée : Récupérer uniquement mon historique.
        GET /api/login/history/my-history/
        """
        queryset = self.get_queryset().filter(user=request.user)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=["get"], url_path="recent")
    def recent(self, request):
        """
        Action personnalisée : Récupérer les connexions récentes (7 derniers jours).
        GET /api/login/history/recent/
        """
        from django.utils import timezone
        from datetime import timedelta

        seven_days_ago = timezone.now() - timedelta(days=7)
        queryset = self.get_queryset().filter(login_time__gte=seven_days_ago)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

