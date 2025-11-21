"""Serializer pour le modèle LoginAttempt (tentatives de connexion)."""

from rest_framework import serializers
from login.models.login_attempt import LoginAttempt


class LoginAttemptSerializer(serializers.ModelSerializer):
    """Serializer pour les tentatives de connexion (protection brute force)."""

    is_locked = serializers.SerializerMethodField()

    class Meta:
        model = LoginAttempt
        fields = [
            "id",
            "email",
            "ip_address",
            "failed_attempts",
            "last_attempt",
            "locked_until",
            "is_locked",
        ]
        read_only_fields = [
            "id",
            "failed_attempts",
            "last_attempt",
            "locked_until",
        ]

    def get_is_locked(self, obj):
        """Vérifie si le compte/IP est verrouillé."""
        from django.utils import timezone

        if obj.locked_until:
            return timezone.now() < obj.locked_until
        return False

