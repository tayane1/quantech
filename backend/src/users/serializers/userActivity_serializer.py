"""Serializer pour le modèle UserActivity (activités utilisateur)."""

from rest_framework import serializers
from users.models import UserActivity


class UserActivitySerializer(serializers.ModelSerializer):
    """
    Serializer pour les activités utilisateur (audit trail).

    Inclut :
    - Informations de l'utilisateur
    - Action effectuée
    - Module concerné
    - Informations techniques (IP, user agent)
    """

    user_name = serializers.SerializerMethodField()
    user_email = serializers.CharField(source="user.email", read_only=True)

    class Meta:
        model = UserActivity
        fields = [
            "id",
            "user",
            "user_name",
            "user_email",
            "action",
            "module",
            "ip_address",
            "user_agent",
            "timestamp",
        ]
        read_only_fields = ["timestamp"]

    def get_user_name(self, obj):
        """Retourne le nom complet de l'utilisateur."""
        if obj.user:
            return f"{obj.user.first_name} {obj.user.last_name}"
        return None
