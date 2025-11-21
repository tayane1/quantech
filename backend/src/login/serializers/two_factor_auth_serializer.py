"""Serializer pour le modèle TwoFactorAuth (authentification à deux facteurs)."""

from rest_framework import serializers
from login.models.two_factor_auth import TwoFactorAuth


class TwoFactorAuthSerializer(serializers.ModelSerializer):
    """Serializer pour la configuration 2FA."""

    user_email = serializers.CharField(source="user.email", read_only=True)
    method_display = serializers.CharField(source="get_method_display", read_only=True)

    class Meta:
        model = TwoFactorAuth
        fields = [
            "id",
            "user",
            "user_email",
            "is_enabled",
            "method",
            "method_display",
            "secret_key",
            "backup_codes",
            "verified",
            "verified_at",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "secret_key",
            "backup_codes",
            "verified",
            "verified_at",
            "created_at",
            "updated_at",
        ]

    def validate(self, attrs):
        """Valide la cohérence des données."""
        # Si 2FA est activé, vérifier qu'il est vérifié
        if attrs.get("is_enabled") and self.instance:
            if not self.instance.verified:
                raise serializers.ValidationError(
                    "La 2FA doit être vérifiée avant d'être activée."
                )
        return attrs


class TwoFactorAuthSetupSerializer(serializers.Serializer):
    """Serializer pour la configuration initiale de la 2FA."""

    method = serializers.ChoiceField(choices=TwoFactorAuth.TYPE_CHOICES)

    def validate_method(self, value):
        """Valide la méthode choisie."""
        if value not in [choice[0] for choice in TwoFactorAuth.TYPE_CHOICES]:
            raise serializers.ValidationError("Méthode 2FA invalide.")
        return value


class TwoFactorAuthVerifySerializer(serializers.Serializer):
    """Serializer pour la vérification du code 2FA."""

    code = serializers.CharField(max_length=10, required=True)

    def validate_code(self, value):
        """Valide le format du code."""
        if not value.isdigit():
            raise serializers.ValidationError("Le code doit être numérique.")
        if len(value) < 4 or len(value) > 8:
            raise serializers.ValidationError(
                "Le code doit contenir entre 4 et 8 chiffres."
            )
        return value

