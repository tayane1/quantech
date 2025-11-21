"""
ViewSet pour la gestion des notifications utilisateur (UserNotification).

Ce ViewSet implémente les opérations CRUD complètes pour les notifications :
- Liste, détail, création, modification, suppression
- Actions personnalisées : marquer comme lue, marquer toutes comme lues, notifications non lues
- Permissions : utilisateurs peuvent voir/modifier leurs propres notifications, admins peuvent tout voir
"""

from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from django.utils import timezone
from django.db.models import Count, Q

from users.models import UserNotification
from users.serializers.userNotification_serializer import (
    UserNotificationSerializer,
    UserNotificationListSerializer,
)


class IsOwnerOrAdmin(permissions.BasePermission):
    """
    Permission personnalisée :
    - Les admins peuvent tout faire
    - Les utilisateurs peuvent voir/modifier leurs propres notifications
    """

    def has_permission(self, request, view):
        """Vérifie la permission au niveau de la vue."""
        return request.user and request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        """Vérifie la permission au niveau de l'objet."""
        # Les admins peuvent tout faire
        if request.user.is_staff or request.user.is_superuser:
            return True

        # Les utilisateurs peuvent voir/modifier leurs propres notifications
        return obj.user == request.user


class UserNotificationViewSet(viewsets.ModelViewSet):
    """
    ViewSet pour les notifications utilisateur.

    Endpoints disponibles :
    - GET /api/users/user-notifications/ : Liste des notifications
    - POST /api/users/user-notifications/ : Créer une notification (admin seulement)
    - GET /api/users/user-notifications/{id}/ : Détails d'une notification
    - PUT/PATCH /api/users/user-notifications/{id}/ : Modifier une notification
    - DELETE /api/users/user-notifications/{id}/ : Supprimer une notification
    - POST /api/users/user-notifications/{id}/mark-read/ : Marquer comme lue
    - POST /api/users/user-notifications/{id}/mark-unread/ : Marquer comme non lue
    - POST /api/users/user-notifications/mark-all-read/ : Marquer toutes comme lues
    - GET /api/users/user-notifications/unread/ : Notifications non lues
    - GET /api/users/user-notifications/unread-count/ : Nombre de notifications non lues
    - GET /api/users/user-notifications/statistics/ : Statistiques des notifications
    """

    queryset = UserNotification.objects.select_related("user").all()
    serializer_class = UserNotificationSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrAdmin]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ["notification_type", "is_read", "user"]
    search_fields = ["title", "message"]
    ordering_fields = ["created_at", "read_at"]
    ordering = ["-created_at"]

    def get_serializer_class(self):
        """Utilise un serializer simplifié pour les listes."""
        if self.action == "list":
            return UserNotificationListSerializer
        return UserNotificationSerializer

    def get_queryset(self):
        """Filtre le queryset selon les permissions."""
        queryset = super().get_queryset()

        # Les admins voient toutes les notifications
        if self.request.user.is_staff or self.request.user.is_superuser:
            return queryset

        # Les utilisateurs ne voient que leurs propres notifications
        return queryset.filter(user=self.request.user)

    def perform_create(self, serializer):
        """Personnalise la création d'une notification."""
        # Si l'utilisateur n'est pas fourni et que ce n'est pas un admin, utiliser l'utilisateur connecté
        if "user" not in serializer.validated_data:
            if not (self.request.user.is_staff or self.request.user.is_superuser):
                serializer.save(user=self.request.user)
            else:
                serializer.save()
        else:
            serializer.save()

    @action(detail=True, methods=["post"], url_path="mark-read")
    def mark_read(self, request, pk=None):
        """
        Action personnalisée : Marquer une notification comme lue.
        POST /api/users/user-notifications/{id}/mark-read/
        """
        notification = self.get_object()
        notification.is_read = True
        notification.read_at = timezone.now()
        notification.save()

        serializer = self.get_serializer(notification)
        return Response(serializer.data)

    @action(detail=True, methods=["post"], url_path="mark-unread")
    def mark_unread(self, request, pk=None):
        """
        Action personnalisée : Marquer une notification comme non lue.
        POST /api/users/user-notifications/{id}/mark-unread/
        """
        notification = self.get_object()
        notification.is_read = False
        notification.read_at = None
        notification.save()

        serializer = self.get_serializer(notification)
        return Response(serializer.data)

    @action(detail=False, methods=["post"], url_path="mark-all-read")
    def mark_all_read(self, request):
        """
        Action personnalisée : Marquer toutes les notifications comme lues.
        POST /api/users/user-notifications/mark-all-read/
        """
        queryset = self.get_queryset().filter(is_read=False)
        count = queryset.update(is_read=True, read_at=timezone.now())

        return Response(
            {
                "message": f"{count} notification(s) marquée(s) comme lue(s).",
                "updated_count": count,
            }
        )

    @action(detail=False, methods=["get"], url_path="unread")
    def unread(self, request):
        """
        Action personnalisée : Récupérer les notifications non lues.
        GET /api/users/user-notifications/unread/
        """
        queryset = self.get_queryset().filter(is_read=False)

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=["get"], url_path="unread-count")
    def unread_count(self, request):
        """
        Action personnalisée : Retourner le nombre de notifications non lues.
        GET /api/users/user-notifications/unread-count/
        """
        queryset = self.get_queryset().filter(is_read=False)
        count = queryset.count()

        return Response({"count": count})

    @action(detail=False, methods=["get"], url_path="statistics")
    def statistics(self, request):
        """
        Action personnalisée : Statistiques sur les notifications.
        GET /api/users/user-notifications/statistics/
        """
        queryset = self.get_queryset()

        stats = {
            "total": queryset.count(),
            "unread": queryset.filter(is_read=False).count(),
            "read": queryset.filter(is_read=True).count(),
            "by_type": queryset.values("notification_type")
            .annotate(count=Count("id"))
            .order_by("-count"),
            "recent": queryset.order_by("-created_at")[:10].count(),
        }

        return Response(stats)
