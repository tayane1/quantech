"""Serializer pour le modèle PasswordResetToken (tokens de réinitialisation)."""

from rest_framework import serializers
from login.models.password_reset_token import PasswordResetToken


class PasswordResetTokenSerializer(serializers.ModelSerializer):
    """Serializer pour les tokens de réinitialisation de mot de passe."""

    user_email = serializers.CharField(source="user.email", read_only=True)
    is_expired = serializers.SerializerMethodField()
    is_valid = serializers.SerializerMethodField()

    class Meta:
        model = PasswordResetToken
        fields = [
            "id",
            "user",
            "user_email",
            "token",
            "created_at",
            "expires_at",
            "used",
            "used_at",
            "is_expired",
            "is_valid",
        ]
        read_only_fields = [
            "id",
            "created_at",
            "used_at",
        ]

    def get_is_expired(self, obj):
        """Vérifie si le token est expiré."""
        from django.utils import timezone

        return timezone.now() > obj.expires_at

    def get_is_valid(self, obj):
        """Vérifie si le token est valide (non utilisé et non expiré)."""
        from django.utils import timezone

        return not obj.used and timezone.now() <= obj.expires_at

