"""Serializer pour le modèle RefreshToken (tokens de rafraîchissement)."""

from rest_framework import serializers
from login.models.refresh_token import RefreshToken


class RefreshTokenSerializer(serializers.ModelSerializer):
    """Serializer pour les tokens de rafraîchissement."""

    user_email = serializers.CharField(source="user.email", read_only=True)
    is_expired = serializers.SerializerMethodField()

    class Meta:
        model = RefreshToken
        fields = [
            "id",
            "user",
            "user_email",
            "token",
            "created_at",
            "expires_at",
            "revoked",
            "revoked_at",
            "is_expired",
        ]
        read_only_fields = [
            "id",
            "created_at",
            "revoked_at",
        ]

    def get_is_expired(self, obj):
        """Vérifie si le token est expiré."""
        from django.utils import timezone

        return timezone.now() > obj.expires_at

