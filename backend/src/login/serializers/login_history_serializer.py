"""Serializer pour le modèle LoginHistory (historique de connexion)."""

from rest_framework import serializers
from login.models.login_history import LoginHistory


class LoginHistorySerializer(serializers.ModelSerializer):
    """Serializer pour l'historique de connexion avec informations utilisateur."""

    user_email = serializers.CharField(source="user.email", read_only=True)
    user_full_name = serializers.SerializerMethodField()

    class Meta:
        model = LoginHistory
        fields = [
            "id",
            "user",
            "user_email",
            "user_full_name",
            "ip_address",
            "user_agent",
            "device_type",
            "browser",
            "login_time",
            "logout_time",
            "is_successful",
            "failure_reason",
        ]
        read_only_fields = [
            "id",
            "login_time",
            "logout_time",
        ]

    def get_user_full_name(self, obj):
        """Retourne le nom complet de l'utilisateur."""
        return f"{obj.user.first_name} {obj.user.last_name}"

