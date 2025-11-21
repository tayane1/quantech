"""
ViewSet pour la gestion des activités utilisateur (UserActivity).

Ce ViewSet implémente les opérations de lecture pour les activités (audit trail) :
- Liste, détail uniquement (pas de création/modification/suppression manuelle)
- Actions personnalisées : activités d'un utilisateur, activités par module
- Permissions : utilisateurs peuvent voir leurs propres activités, admins peuvent tout voir
"""

from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from django.db.models import Count

from users.models import UserActivity
from users.serializers.userActivity_serializer import UserActivitySerializer


class IsOwnerOrAdmin(permissions.BasePermission):
    """
    Permission personnalisée :
    - Les admins peuvent tout voir
    - Les utilisateurs peuvent voir leurs propres activités
    """

    def has_permission(self, request, view):
        """Vérifie la permission au niveau de la vue."""
        return request.user and request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        """Vérifie la permission au niveau de l'objet."""
        # Les admins peuvent tout voir
        if request.user.is_staff or request.user.is_superuser:
            return True

        # Les utilisateurs peuvent voir leurs propres activités
        return obj.user == request.user


class UserActivityViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet pour les activités utilisateur (lecture seule - audit trail).

    Endpoints disponibles :
    - GET /api/users/user-activities/ : Liste des activités
    - GET /api/users/user-activities/{id}/ : Détails d'une activité
    - GET /api/users/user-activities/by-user/{user_id}/ : Activités d'un utilisateur
    - GET /api/users/user-activities/by-module/{module}/ : Activités par module
    - GET /api/users/user-activities/recent/ : Activités récentes
    - GET /api/users/user-activities/statistics/ : Statistiques des activités
    """

    queryset = UserActivity.objects.select_related("user").all()
    serializer_class = UserActivitySerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrAdmin]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ["user", "module", "ip_address"]
    search_fields = ["action", "module"]
    ordering_fields = ["timestamp"]
    ordering = ["-timestamp"]

    def get_queryset(self):
        """Filtre le queryset selon les permissions."""
        queryset = super().get_queryset()

        # Les admins voient toutes les activités
        if self.request.user.is_staff or self.request.user.is_superuser:
            return queryset

        # Les utilisateurs ne voient que leurs propres activités
        return queryset.filter(user=self.request.user)

    @action(detail=False, methods=["get"], url_path="by-user/(?P<user_id>[^/.]+)")
    def by_user(self, request, user_id=None):
        """
        Action personnalisée : Récupérer les activités d'un utilisateur spécifique.
        GET /api/users/user-activities/by-user/{user_id}/
        """
        from users.models import CustomUser

        try:
            user = CustomUser.objects.get(pk=user_id)
        except CustomUser.DoesNotExist:
            return Response(
                {"detail": "Utilisateur non trouvé."},
                status=status.HTTP_404_NOT_FOUND,
            )

        # Vérifier que l'utilisateur peut voir ces activités
        if not (request.user.is_staff or request.user == user):
            return Response(
                {"detail": "Vous n'avez pas la permission de voir ces activités."},
                status=status.HTTP_403_FORBIDDEN,
            )

        activities = self.get_queryset().filter(user=user)

        page = self.paginate_queryset(activities)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(activities, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=["get"], url_path="by-module/(?P<module>[^/.]+)")
    def by_module(self, request, module=None):
        """
        Action personnalisée : Récupérer les activités par module.
        GET /api/users/user-activities/by-module/{module}/
        """
        activities = self.get_queryset().filter(module=module)

        page = self.paginate_queryset(activities)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(activities, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=["get"], url_path="recent")
    def recent(self, request):
        """
        Action personnalisée : Récupérer les activités récentes.
        GET /api/users/user-activities/recent/
        """
        limit = int(request.query_params.get("limit", 10))
        activities = self.get_queryset()[:limit]

        serializer = self.get_serializer(activities, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=["get"], url_path="statistics")
    def statistics(self, request):
        """
        Action personnalisée : Statistiques sur les activités.
        GET /api/users/user-activities/statistics/
        """
        queryset = self.get_queryset()

        stats = {
            "total": queryset.count(),
            "by_module": queryset.values("module")
            .annotate(count=Count("id"))
            .order_by("-count"),
            "by_user": queryset.values("user__username")
            .annotate(count=Count("id"))
            .order_by("-count")[:10],
            "recent_activities": queryset.order_by("-timestamp")[:10].values(
                "id", "user__username", "action", "module", "timestamp"
            ),
        }

        return Response(stats)
