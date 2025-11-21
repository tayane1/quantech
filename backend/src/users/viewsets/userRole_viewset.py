"""
ViewSet pour la gestion des rôles utilisateur (UserRole).

Ce ViewSet implémente les opérations CRUD complètes pour les rôles :
- Liste, détail, création, modification, suppression
- Actions personnalisées : rôles avec permissions
- Permissions : seuls les admins peuvent gérer les rôles
"""

from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from django.db.models import Count

from users.models import UserRole
from users.serializers.userRole_serializer import UserRoleSerializer


class UserRoleViewSet(viewsets.ModelViewSet):
    """
    ViewSet pour les rôles utilisateur.

    Endpoints disponibles :
    - GET /api/users/user-roles/ : Liste des rôles
    - POST /api/users/user-roles/ : Créer un rôle (admin seulement)
    - GET /api/users/user-roles/{id}/ : Détails d'un rôle
    - PUT/PATCH /api/users/user-roles/{id}/ : Modifier un rôle (admin seulement)
    - DELETE /api/users/user-roles/{id}/ : Supprimer un rôle (admin seulement)
    - GET /api/users/user-roles/{id}/permissions/ : Permissions d'un rôle
    - POST /api/users/user-roles/{id}/permissions/ : Ajouter des permissions à un rôle
    - DELETE /api/users/user-roles/{id}/permissions/ : Retirer des permissions d'un rôle
    - GET /api/users/user-roles/statistics/ : Statistiques des rôles
    """

    queryset = UserRole.objects.prefetch_related("permissions").all()
    serializer_class = UserRoleSerializer
    permission_classes = [permissions.IsAdminUser]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ["code"]
    search_fields = ["name", "description"]
    ordering_fields = ["name", "created_at"]
    ordering = ["name"]

    @action(detail=True, methods=["get"], url_path="permissions")
    def permissions(self, request, pk=None):
        """
        Action personnalisée : Récupérer les permissions d'un rôle.
        GET /api/users/user-roles/{id}/permissions/
        """
        role = self.get_object()
        permissions_list = role.permissions.all()

        return Response(
            [
                {
                    "id": perm.id,
                    "name": perm.name,
                    "codename": perm.codename,
                    "content_type": str(perm.content_type),
                }
                for perm in permissions_list
            ]
        )

    @action(
        detail=True,
        methods=["post", "delete"],
        url_path="permissions",
    )
    def manage_permissions(self, request, pk=None):
        """
        Action personnalisée : Ajouter ou retirer des permissions d'un rôle.
        POST /api/users/user-roles/{id}/permissions/ : Ajouter
        DELETE /api/users/user-roles/{id}/permissions/ : Retirer
        """
        from django.contrib.auth.models import Permission

        role = self.get_object()
        permission_ids = request.data.get("permission_ids", [])

        try:
            permissions = Permission.objects.filter(id__in=permission_ids)
        except Exception:
            return Response(
                {"detail": "IDs de permissions invalides."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if request.method == "POST":
            # Ajouter des permissions
            role.permissions.add(*permissions)
            message = f"{permissions.count()} permission(s) ajoutée(s)."
        else:
            # Retirer des permissions
            role.permissions.remove(*permissions)
            message = f"{permissions.count()} permission(s) retirée(s)."

        role.save()
        serializer = self.get_serializer(role)
        return Response({"message": message, "role": serializer.data})

    @action(detail=False, methods=["get"], url_path="statistics")
    def statistics(self, request):
        """
        Action personnalisée : Statistiques sur les rôles.
        GET /api/users/user-roles/statistics/
        """
        queryset = self.get_queryset()

        stats = {
            "total_roles": queryset.count(),
            "roles": [
                {
                    "id": role.id,
                    "name": role.name,
                    "code": role.code,
                    "permissions_count": role.permissions.count(),
                }
                for role in queryset
            ],
        }

        return Response(stats)
