"""
ViewSet pour la gestion des utilisateurs (CustomUser).

Ce ViewSet implémente les opérations CRUD complètes pour les utilisateurs :
- Liste, détail, création, modification, suppression
- Actions personnalisées : profil, changement de mot de passe, statistiques
- Permissions : admins peuvent tout faire, utilisateurs peuvent voir/modifier leur propre profil
"""

from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from django.db.models import Count, Q
from django.contrib.auth import update_session_auth_hash
from django.utils import timezone

from users.models import CustomUser
from users.serializers.customUser_serializer import (
    CustomUserSerializer,
    CustomUserListSerializer,
    CustomUserPasswordSerializer,
)


class IsAdminOrSelf(permissions.BasePermission):
    """
    Permission personnalisée :
    - Les admins peuvent tout faire (CRUD complet)
    - Les utilisateurs peuvent voir et modifier leur propre profil
    """

    def has_permission(self, request, view):
        """Vérifie la permission au niveau de la vue."""
        if request.method in permissions.SAFE_METHODS:
            return request.user and request.user.is_authenticated

        # Pour la création, seuls les admins peuvent créer
        if request.method == "POST":
            return request.user and (request.user.is_staff or request.user.is_superuser)

        # Pour la modification, on vérifie au niveau de l'objet
        return request.user and request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        """Vérifie la permission au niveau de l'objet."""
        # Les admins peuvent tout faire
        if request.user.is_staff or request.user.is_superuser:
            return True

        # Les utilisateurs peuvent voir et modifier leur propre profil
        return obj == request.user


class CustomUserViewSet(viewsets.ModelViewSet):
    """
    ViewSet pour les utilisateurs.

    Endpoints disponibles :
    - GET /api/users/custom-users/ : Liste des utilisateurs
    - POST /api/users/custom-users/ : Créer un utilisateur (admin seulement)
    - GET /api/users/custom-users/{id}/ : Détails d'un utilisateur
    - PUT/PATCH /api/users/custom-users/{id}/ : Modifier un utilisateur
    - DELETE /api/users/custom-users/{id}/ : Supprimer un utilisateur (admin seulement)
    - GET /api/users/custom-users/me/ : Mon profil (utilisateur connecté)
    - PUT/PATCH /api/users/custom-users/me/ : Modifier mon profil
    - POST /api/users/custom-users/{id}/change-password/ : Changer le mot de passe
    - GET /api/users/custom-users/statistics/ : Statistiques globales
    """

    queryset = (
        CustomUser.objects.select_related("employee")
        .prefetch_related("preferences", "notifications")
        .all()
    )
    serializer_class = CustomUserSerializer
    permission_classes = [permissions.IsAuthenticated, IsAdminOrSelf]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ["role", "is_active", "is_staff"]
    search_fields = ["username", "email", "first_name", "last_name"]
    ordering_fields = ["created_at", "last_login", "username"]
    ordering = ["-created_at"]

    def get_serializer_class(self):
        """Utilise un serializer simplifié pour les listes."""
        if self.action == "list":
            return CustomUserListSerializer
        return CustomUserSerializer

    def get_queryset(self):
        """Filtre le queryset selon les permissions."""
        queryset = super().get_queryset()

        # Les admins voient tous les utilisateurs
        if self.request.user.is_staff or self.request.user.is_superuser:
            return queryset

        # Les utilisateurs normaux ne voient que leur propre profil
        return queryset.filter(id=self.request.user.id)

    @action(detail=False, methods=["get", "put", "patch"], url_path="me")
    def me(self, request):
        """
        Action personnalisée : Récupérer ou modifier le profil de l'utilisateur connecté.
        GET /api/users/custom-users/me/
        PUT/PATCH /api/users/custom-users/me/
        """
        user = request.user
        serializer_class = self.get_serializer_class()

        if request.method in ["PUT", "PATCH"]:
            serializer = serializer_class(
                user, data=request.data, partial=request.method == "PATCH"
            )
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        serializer = serializer_class(user)
        return Response(serializer.data)

    @action(detail=True, methods=["post"], url_path="change-password")
    def change_password(self, request, pk=None):
        """
        Action personnalisée : Changer le mot de passe d'un utilisateur.
        POST /api/users/custom-users/{id}/change-password/

        Pour les utilisateurs non-admin, ils ne peuvent changer que leur propre mot de passe.
        """
        user = self.get_object()

        # Vérifier que l'utilisateur peut modifier ce compte
        if not (request.user.is_staff or request.user == user):
            return Response(
                {"detail": "Vous n'avez pas la permission de modifier ce compte."},
                status=status.HTTP_403_FORBIDDEN,
            )

        serializer = CustomUserPasswordSerializer(data=request.data)
        if serializer.is_valid():
            # Vérifier l'ancien mot de passe (sauf pour les admins qui changent le mot de passe d'autrui)
            if not request.user.is_staff or request.user == user:
                if not user.check_password(serializer.validated_data["old_password"]):
                    return Response(
                        {"old_password": "L'ancien mot de passe est incorrect."},
                        status=status.HTTP_400_BAD_REQUEST,
                    )

            # Changer le mot de passe
            user.set_password(serializer.validated_data["new_password"])
            user.save()

            # Mettre à jour la session pour éviter la déconnexion
            if request.user == user:
                update_session_auth_hash(request, user)

            return Response({"message": "Le mot de passe a été changé avec succès."})

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=["get"], url_path="statistics")
    def statistics(self, request):
        """
        Action personnalisée : Statistiques globales sur les utilisateurs.
        GET /api/users/custom-users/statistics/
        """
        queryset = self.get_queryset()

        stats = {
            "total_users": queryset.count(),
            "active_users": queryset.filter(is_active=True).count(),
            "inactive_users": queryset.filter(is_active=False).count(),
            "staff_users": queryset.filter(is_staff=True).count(),
            "by_role": queryset.values("role")
            .annotate(count=Count("id"))
            .order_by("-count"),
            "recent_users": queryset.order_by("-created_at")[:10].values(
                "id", "username", "email", "role", "created_at"
            ),
        }

        return Response(stats)

    @action(detail=True, methods=["post"], url_path="activate")
    def activate(self, request, pk=None):
        """
        Action personnalisée : Activer un utilisateur.
        POST /api/users/custom-users/{id}/activate/
        """
        user = self.get_object()
        user.is_active = True
        user.save()

        serializer = self.get_serializer(user)
        return Response(serializer.data)

    @action(detail=True, methods=["post"], url_path="deactivate")
    def deactivate(self, request, pk=None):
        """
        Action personnalisée : Désactiver un utilisateur.
        POST /api/users/custom-users/{id}/deactivate/
        """
        user = self.get_object()
        user.is_active = False
        user.save()

        serializer = self.get_serializer(user)
        return Response(serializer.data)
