"""
ViewSet pour la gestion de l'authentification à deux facteurs (2FA).

Ce ViewSet gère la configuration et la vérification de la 2FA :
- Configuration initiale (setup)
- Vérification du code
- Activation/désactivation
- Gestion des codes de secours
"""

from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.contrib.auth import get_user_model
from django.utils import timezone
import pyotp
import secrets

from login.models.two_factor_auth import TwoFactorAuth
from login.serializers.two_factor_auth_serializer import (
    TwoFactorAuthSerializer,
    TwoFactorAuthSetupSerializer,
    TwoFactorAuthVerifySerializer,
)

User = get_user_model()


class IsOwnerOrAdmin(permissions.BasePermission):
    """
    Permission personnalisée :
    - Les admins peuvent voir tout
    - Les utilisateurs peuvent gérer uniquement leur propre 2FA
    """

    def has_object_permission(self, request, view, obj):
        if request.user.is_staff or request.user.is_superuser:
            return True
        return obj.user == request.user

    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated


class TwoFactorAuthViewSet(viewsets.ModelViewSet):
    """
    ViewSet pour l'authentification à deux facteurs.
    
    Endpoints disponibles :
    - GET /api/login/2fa/ : Liste des configurations (admin uniquement)
    - GET /api/login/2fa/my-2fa/ : Ma configuration 2FA
    - POST /api/login/2fa/setup/ : Configurer la 2FA
    - POST /api/login/2fa/verify/ : Vérifier un code 2FA
    - POST /api/login/2fa/enable/ : Activer la 2FA
    - POST /api/login/2fa/disable/ : Désactiver la 2FA
    - POST /api/login/2fa/generate-backup-codes/ : Générer des codes de secours
    """
    
    serializer_class = TwoFactorAuthSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrAdmin]
    filter_backends = []

    def get_queryset(self):
        """Filtre le queryset selon les permissions."""
        queryset = TwoFactorAuth.objects.select_related("user").all()
        
        # Si admin, retourner tout
        if self.request.user.is_staff or self.request.user.is_superuser:
            return queryset
        
        # Sinon, filtrer par utilisateur
        return queryset.filter(user=self.request.user)

    @action(detail=False, methods=["get"], url_path="my-2fa")
    def my_2fa(self, request):
        """
        Action personnalisée : Récupérer ma configuration 2FA.
        GET /api/login/2fa/my-2fa/
        """
        try:
            two_fa = TwoFactorAuth.objects.get(user=request.user)
            serializer = self.get_serializer(two_fa)
            return Response(serializer.data)
        except TwoFactorAuth.DoesNotExist:
            return Response(
                {"detail": "La 2FA n'est pas configurée pour cet utilisateur."},
                status=status.HTTP_404_NOT_FOUND,
            )

    @action(detail=False, methods=["post"], url_path="setup")
    def setup(self, request):
        """
        Action personnalisée : Configurer la 2FA.
        POST /api/login/2fa/setup/
        Body: {"method": "totp"}
        """
        serializer = TwoFactorAuthSetupSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        method = serializer.validated_data["method"]

        # Créer ou récupérer la configuration 2FA
        two_fa, created = TwoFactorAuth.objects.get_or_create(
            user=request.user, defaults={"method": method}
        )

        if not created:
            two_fa.method = method
            two_fa.verified = False
            two_fa.secret_key = ""
            two_fa.backup_codes = []
            two_fa.save()

        # Générer le secret pour TOTP
        if method == TwoFactorAuth.TYPE_TOTP:
            secret = pyotp.random_base32()
            two_fa.secret_key = secret
            two_fa.save()

            # Générer l'URL QR code (à utiliser avec une librairie QR code)
            totp = pyotp.TOTP(secret)
            provisioning_uri = totp.provisioning_uri(
                name=request.user.email, issuer_name="WeHR"
            )

            return Response(
                {
                    "secret": secret,
                    "provisioning_uri": provisioning_uri,
                    "message": "Scannez le QR code avec votre application d'authentification.",
                },
                status=status.HTTP_200_OK,
            )

        return Response(
            {"detail": f"Configuration 2FA initialisée avec la méthode {method}."},
            status=status.HTTP_200_OK,
        )

    @action(detail=False, methods=["post"], url_path="verify")
    def verify(self, request):
        """
        Action personnalisée : Vérifier un code 2FA.
        POST /api/login/2fa/verify/
        Body: {"code": "123456"}
        """
        serializer = TwoFactorAuthVerifySerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        code = serializer.validated_data["code"]

        try:
            two_fa = TwoFactorAuth.objects.get(user=request.user)
        except TwoFactorAuth.DoesNotExist:
            return Response(
                {"detail": "La 2FA n'est pas configurée."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Vérifier le code selon la méthode
        is_valid = False

        if two_fa.method == TwoFactorAuth.TYPE_TOTP:
            if two_fa.secret_key:
                totp = pyotp.TOTP(two_fa.secret_key)
                is_valid = totp.verify(code, valid_window=1)
        elif two_fa.method == TwoFactorAuth.TYPE_EMAIL:
            # Ici, vous devriez envoyer un code par email et le vérifier
            # Pour l'instant, on simule
            is_valid = len(code) == 6 and code.isdigit()
        elif two_fa.method == TwoFactorAuth.TYPE_SMS:
            # Ici, vous devriez envoyer un code par SMS et le vérifier
            # Pour l'instant, on simule
            is_valid = len(code) == 6 and code.isdigit()

        if is_valid:
            two_fa.verified = True
            two_fa.verified_at = timezone.now()
            two_fa.save()

            # Générer des codes de secours
            backup_codes = [secrets.token_hex(4) for _ in range(10)]
            two_fa.backup_codes = backup_codes
            two_fa.save()

            return Response(
                {
                    "verified": True,
                    "backup_codes": backup_codes,
                    "message": "2FA vérifiée avec succès. Conservez vos codes de secours.",
                },
                status=status.HTTP_200_OK,
            )

        return Response(
            {"verified": False, "detail": "Code invalide."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    @action(detail=False, methods=["post"], url_path="enable")
    def enable(self, request):
        """
        Action personnalisée : Activer la 2FA.
        POST /api/login/2fa/enable/
        """
        try:
            two_fa = TwoFactorAuth.objects.get(user=request.user)
        except TwoFactorAuth.DoesNotExist:
            return Response(
                {"detail": "La 2FA doit être configurée et vérifiée avant d'être activée."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if not two_fa.verified:
            return Response(
                {"detail": "La 2FA doit être vérifiée avant d'être activée."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        two_fa.is_enabled = True
        two_fa.save()

        serializer = self.get_serializer(two_fa)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=False, methods=["post"], url_path="disable")
    def disable(self, request):
        """
        Action personnalisée : Désactiver la 2FA.
        POST /api/login/2fa/disable/
        """
        try:
            two_fa = TwoFactorAuth.objects.get(user=request.user)
        except TwoFactorAuth.DoesNotExist:
            return Response(
                {"detail": "La 2FA n'est pas configurée."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        two_fa.is_enabled = False
        two_fa.save()

        serializer = self.get_serializer(two_fa)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=False, methods=["post"], url_path="generate-backup-codes")
    def generate_backup_codes(self, request):
        """
        Action personnalisée : Régénérer les codes de secours.
        POST /api/login/2fa/generate-backup-codes/
        """
        try:
            two_fa = TwoFactorAuth.objects.get(user=request.user)
        except TwoFactorAuth.DoesNotExist:
            return Response(
                {"detail": "La 2FA n'est pas configurée."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        backup_codes = [secrets.token_hex(4) for _ in range(10)]
        two_fa.backup_codes = backup_codes
        two_fa.save()

        return Response(
            {
                "backup_codes": backup_codes,
                "message": "Nouveaux codes de secours générés. Conservez-les en sécurité.",
            },
            status=status.HTTP_200_OK,
        )

