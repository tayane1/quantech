"""
ViewSet pour la gestion de la réinitialisation de mot de passe.

Ce ViewSet gère les tokens de réinitialisation et les opérations associées :
- Demande de réinitialisation (création de token)
- Vérification de token
- Réinitialisation effective du mot de passe
"""

from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import OrderingFilter
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta
import secrets

from login.models.password_reset_token import PasswordResetToken
from login.serializers.password_reset_token_serializer import PasswordResetTokenSerializer

User = get_user_model()


class PasswordResetViewSet(viewsets.ModelViewSet):
    """
    ViewSet pour la réinitialisation de mot de passe.
    
    Endpoints disponibles :
    - POST /api/login/password-reset/request/ : Demander une réinitialisation
    - POST /api/login/password-reset/verify/ : Vérifier un token
    - POST /api/login/password-reset/reset/ : Réinitialiser le mot de passe
    - GET /api/login/password-reset/tokens/ : Liste des tokens (admin uniquement)
    """
    
    serializer_class = PasswordResetTokenSerializer
    permission_classes = [permissions.AllowAny]  # Public pour la demande
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ["used"]
    ordering_fields = ["created_at"]
    ordering = ["-created_at"]

    def get_queryset(self):
        """Seuls les admins peuvent voir les tokens."""
        if self.request.user.is_staff or self.request.user.is_superuser:
            return PasswordResetToken.objects.select_related("user").all()
        return PasswordResetToken.objects.none()

    @action(detail=False, methods=["post"], url_path="request")
    def request_reset(self, request):
        """
        Action personnalisée : Demander une réinitialisation de mot de passe.
        POST /api/login/password-reset/request/
        Body: {"email": "user@example.com"}
        """
        email = request.data.get("email")
        if not email:
            return Response(
                {"detail": "L'email est requis."}, status=status.HTTP_400_BAD_REQUEST
            )

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            # Ne pas révéler si l'email existe ou non (sécurité)
            return Response(
                {"detail": "Si cet email existe, un lien de réinitialisation a été envoyé."},
                status=status.HTTP_200_OK,
            )

        # Générer un token unique
        token = secrets.token_urlsafe(32)

        # Créer le token de réinitialisation (valide 1 heure)
        reset_token = PasswordResetToken.objects.create(
            user=user,
            token=token,
            expires_at=timezone.now() + timedelta(hours=1),
        )

        # Ici, vous devriez envoyer un email avec le token
        # Pour l'instant, on retourne juste le token (en dev uniquement)
        # En production, envoyer un email avec le lien

        return Response(
            {
                "detail": "Si cet email existe, un lien de réinitialisation a été envoyé.",
                "token": token,  # À retirer en production
            },
            status=status.HTTP_200_OK,
        )

    @action(detail=False, methods=["post"], url_path="verify")
    def verify_token(self, request):
        """
        Action personnalisée : Vérifier si un token est valide.
        POST /api/login/password-reset/verify/
        Body: {"token": "abc123..."}
        """
        token = request.data.get("token")
        if not token:
            return Response(
                {"detail": "Le token est requis."}, status=status.HTTP_400_BAD_REQUEST
            )

        try:
            reset_token = PasswordResetToken.objects.get(token=token)
        except PasswordResetToken.DoesNotExist:
            return Response(
                {"valid": False, "detail": "Token invalide."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Vérifier si le token est valide
        is_valid = not reset_token.used and timezone.now() <= reset_token.expires_at

        return Response(
            {
                "valid": is_valid,
                "expired": timezone.now() > reset_token.expires_at,
                "used": reset_token.used,
            },
            status=status.HTTP_200_OK,
        )

    @action(detail=False, methods=["post"], url_path="reset")
    def reset_password(self, request):
        """
        Action personnalisée : Réinitialiser le mot de passe.
        POST /api/login/password-reset/reset/
        Body: {"token": "abc123...", "new_password": "newpass123"}
        """
        token = request.data.get("token")
        new_password = request.data.get("new_password")

        if not token or not new_password:
            return Response(
                {"detail": "Le token et le nouveau mot de passe sont requis."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            reset_token = PasswordResetToken.objects.get(token=token)
        except PasswordResetToken.DoesNotExist:
            return Response(
                {"detail": "Token invalide."}, status=status.HTTP_400_BAD_REQUEST
            )

        # Vérifier si le token est valide
        if reset_token.used:
            return Response(
                {"detail": "Ce token a déjà été utilisé."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if timezone.now() > reset_token.expires_at:
            return Response(
                {"detail": "Ce token a expiré."}, status=status.HTTP_400_BAD_REQUEST
            )

        # Valider le mot de passe
        if len(new_password) < 8:
            return Response(
                {"detail": "Le mot de passe doit contenir au moins 8 caractères."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Réinitialiser le mot de passe
        user = reset_token.user
        user.set_password(new_password)
        user.save()

        # Marquer le token comme utilisé
        reset_token.used = True
        reset_token.used_at = timezone.now()
        reset_token.save()

        return Response(
            {"detail": "Mot de passe réinitialisé avec succès."},
            status=status.HTTP_200_OK,
        )

