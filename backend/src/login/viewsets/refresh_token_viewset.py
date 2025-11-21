"""
ViewSet pour la gestion des tokens de rafraîchissement (RefreshToken).

Ce ViewSet permet de gérer les tokens de rafraîchissement :
- Les utilisateurs peuvent voir/révoquer leurs propres tokens
- Les admins peuvent voir tous les tokens
"""

from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import OrderingFilter

from login.models.refresh_token import RefreshToken
from login.serializers.refresh_token_serializer import RefreshTokenSerializer


class IsOwnerOrAdmin(permissions.BasePermission):
    """
    Permission personnalisée :
    - Les admins peuvent voir tout
    - Les utilisateurs peuvent voir/révoquer uniquement leurs propres tokens
    """

    def has_object_permission(self, request, view, obj):
        if request.user.is_staff or request.user.is_superuser:
            return True
        return obj.user == request.user

    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated


class RefreshTokenViewSet(viewsets.ModelViewSet):
    """
    ViewSet pour les tokens de rafraîchissement.
    
    Endpoints disponibles :
    - GET /api/login/refresh-tokens/ : Liste des tokens
    - GET /api/login/refresh-tokens/{id}/ : Détails d'un token
    - DELETE /api/login/refresh-tokens/{id}/ : Révoquer un token
    - POST /api/login/refresh-tokens/{id}/revoke/ : Révoquer un token
    - GET /api/login/refresh-tokens/my-tokens/ : Mes tokens
    - POST /api/login/refresh-tokens/revoke-all/ : Révoquer tous mes tokens
    """
    
    serializer_class = RefreshTokenSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrAdmin]
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ["revoked"]
    ordering_fields = ["created_at", "expires_at"]
    ordering = ["-created_at"]

    def get_queryset(self):
        """Filtre le queryset selon les permissions."""
        queryset = RefreshToken.objects.select_related("user").all()
        
        # Si admin, retourner tout
        if self.request.user.is_staff or self.request.user.is_superuser:
            return queryset
        
        # Sinon, filtrer par utilisateur
        return queryset.filter(user=self.request.user)

    def perform_create(self, serializer):
        """Les tokens sont créés automatiquement lors du login, pas via API."""
        return Response(
            {"detail": "Les tokens sont créés automatiquement lors de la connexion."},
            status=status.HTTP_405_METHOD_NOT_ALLOWED,
        )

    @action(detail=True, methods=["post"], url_path="revoke")
    def revoke(self, request, pk=None):
        """
        Action personnalisée : Révoquer un token.
        POST /api/login/refresh-tokens/{id}/revoke/
        """
        token = self.get_object()
        if token.revoked:
            return Response(
                {"detail": "Ce token est déjà révoqué."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        from django.utils import timezone

        token.revoked = True
        token.revoked_at = timezone.now()
        token.save()

        serializer = self.get_serializer(token)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=False, methods=["get"], url_path="my-tokens")
    def my_tokens(self, request):
        """
        Action personnalisée : Récupérer mes tokens.
        GET /api/login/refresh-tokens/my-tokens/
        """
        queryset = self.get_queryset().filter(user=request.user)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=["post"], url_path="revoke-all")
    def revoke_all(self, request):
        """
        Action personnalisée : Révoquer tous mes tokens.
        POST /api/login/refresh-tokens/revoke-all/
        """
        from django.utils import timezone

        count = self.get_queryset().filter(
            user=request.user, revoked=False
        ).update(revoked=True, revoked_at=timezone.now())

        return Response(
            {"detail": f"{count} token(s) révoqué(s)."}, status=status.HTTP_200_OK
        )

