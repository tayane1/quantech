"""
ViewSet pour la gestion des préférences utilisateur (UserPreference).

Ce ViewSet implémente les opérations CRUD complètes pour les préférences :
- Liste, détail, création, modification, suppression
- Actions personnalisées : préférences de l'utilisateur connecté
- Permissions : utilisateurs peuvent voir/modifier leurs propres préférences, admins peuvent tout voir
"""

from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter

from users.models import UserPreference
from users.serializers.userPreference_serializer import UserPreferenceSerializer


class IsOwnerOrAdmin(permissions.BasePermission):
    """
    Permission personnalisée :
    - Les admins peuvent tout faire
    - Les utilisateurs peuvent voir/modifier leurs propres préférences
    """

    def has_permission(self, request, view):
        """Vérifie la permission au niveau de la vue."""
        return request.user and request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        """Vérifie la permission au niveau de l'objet."""
        # Les admins peuvent tout faire
        if request.user.is_staff or request.user.is_superuser:
            return True

        # Les utilisateurs peuvent voir/modifier leurs propres préférences
        return obj.user == request.user


class UserPreferenceViewSet(viewsets.ModelViewSet):
    """
    ViewSet pour les préférences utilisateur.

    Endpoints disponibles :
    - GET /api/users/user-preferences/ : Liste des préférences
    - POST /api/users/user-preferences/ : Créer des préférences
    - GET /api/users/user-preferences/{id}/ : Détails des préférences
    - PUT/PATCH /api/users/user-preferences/{id}/ : Modifier des préférences
    - DELETE /api/users/user-preferences/{id}/ : Supprimer des préférences
    - GET /api/users/user-preferences/me/ : Mes préférences (utilisateur connecté)
    - PUT/PATCH /api/users/user-preferences/me/ : Modifier mes préférences
    """

    queryset = UserPreference.objects.select_related("user").all()
    serializer_class = UserPreferenceSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrAdmin]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ["language", "dashboard_theme"]
    search_fields = ["user__username", "user__email"]
    ordering_fields = ["updated_at"]
    ordering = ["-updated_at"]

    def get_queryset(self):
        """Filtre le queryset selon les permissions."""
        queryset = super().get_queryset()

        # Les admins voient toutes les préférences
        if self.request.user.is_staff or self.request.user.is_superuser:
            return queryset

        # Les utilisateurs ne voient que leurs propres préférences
        return queryset.filter(user=self.request.user)

    def perform_create(self, serializer):
        """Personnalise la création de préférences."""
        # Si l'utilisateur n'est pas fourni, utiliser l'utilisateur connecté
        if "user" not in serializer.validated_data:
            serializer.save(user=self.request.user)
        else:
            serializer.save()

    @action(detail=False, methods=["get", "put", "patch"], url_path="me")
    def me(self, request):
        """
        Action personnalisée : Récupérer ou modifier les préférences de l'utilisateur connecté.
        GET /api/users/user-preferences/me/
        PUT/PATCH /api/users/user-preferences/me/
        """
        # Récupérer ou créer les préférences de l'utilisateur
        preferences, created = UserPreference.objects.get_or_create(user=request.user)

        if request.method in ["PUT", "PATCH"]:
            serializer = self.get_serializer(
                preferences, data=request.data, partial=request.method == "PATCH"
            )
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        serializer = self.get_serializer(preferences)
        return Response(serializer.data)
