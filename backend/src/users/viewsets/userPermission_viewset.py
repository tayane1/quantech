"""
ViewSet pour la gestion des permissions utilisateur (UserPermission).

Ce ViewSet implémente les opérations CRUD complètes pour les permissions granulaires :
- Liste, détail, création, modification, suppression
- Actions personnalisées : permissions d'un utilisateur, permissions par module
- Permissions : seuls les admins peuvent gérer les permissions
"""

from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from django.db.models import Count

from users.models import UserPermission
from users.serializers.userPermission_serializer import UserPermissionSerializer


class UserPermissionViewSet(viewsets.ModelViewSet):
    """
    ViewSet pour les permissions utilisateur.

    Endpoints disponibles :
    - GET /api/users/user-permissions/ : Liste des permissions
    - POST /api/users/user-permissions/ : Créer une permission (admin seulement)
    - GET /api/users/user-permissions/{id}/ : Détails d'une permission
    - PUT/PATCH /api/users/user-permissions/{id}/ : Modifier une permission (admin seulement)
    - DELETE /api/users/user-permissions/{id}/ : Supprimer une permission (admin seulement)
    - GET /api/users/user-permissions/by-user/{user_id}/ : Permissions d'un utilisateur
    - GET /api/users/user-permissions/by-module/{module}/ : Permissions par module
    - GET /api/users/user-permissions/statistics/ : Statistiques des permissions
    """

    queryset = UserPermission.objects.select_related("user", "granted_by").all()
    serializer_class = UserPermissionSerializer
    permission_classes = [permissions.IsAdminUser]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ["user", "module", "action", "granted"]
    search_fields = ["module", "action"]
    ordering_fields = ["granted_date", "module"]
    ordering = ["-granted_date"]

    def perform_create(self, serializer):
        """Personnalise la création d'une permission."""
        # Enregistrer qui a accordé la permission
        serializer.save(granted_by=self.request.user)

    @action(detail=False, methods=["get"], url_path="by-user/(?P<user_id>[^/.]+)")
    def by_user(self, request, user_id=None):
        """
        Action personnalisée : Récupérer les permissions d'un utilisateur spécifique.
        GET /api/users/user-permissions/by-user/{user_id}/
        """
        from users.models import CustomUser

        try:
            user = CustomUser.objects.get(pk=user_id)
        except CustomUser.DoesNotExist:
            return Response(
                {"detail": "Utilisateur non trouvé."},
                status=status.HTTP_404_NOT_FOUND,
            )

        permissions = self.get_queryset().filter(user=user)

        page = self.paginate_queryset(permissions)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(permissions, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=["get"], url_path="by-module/(?P<module>[^/.]+)")
    def by_module(self, request, module=None):
        """
        Action personnalisée : Récupérer les permissions par module.
        GET /api/users/user-permissions/by-module/{module}/
        """
        permissions = self.get_queryset().filter(module=module)

        page = self.paginate_queryset(permissions)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(permissions, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=["get"], url_path="statistics")
    def statistics(self, request):
        """
        Action personnalisée : Statistiques sur les permissions.
        GET /api/users/user-permissions/statistics/
        """
        queryset = self.get_queryset()

        stats = {
            "total": queryset.count(),
            "granted": queryset.filter(granted=True).count(),
            "revoked": queryset.filter(granted=False).count(),
            "by_module": queryset.values("module")
            .annotate(count=Count("id"))
            .order_by("-count"),
            "by_action": queryset.values("action")
            .annotate(count=Count("id"))
            .order_by("-count"),
        }

        return Response(stats)
