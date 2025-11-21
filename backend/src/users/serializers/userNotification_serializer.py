"""Serializer pour le modèle UserNotification (notifications utilisateur)."""

from rest_framework import serializers
from users.models import UserNotification


class UserNotificationSerializer(serializers.ModelSerializer):
    """
    Serializer complet pour les notifications.

    Inclut :
    - Toutes les informations de la notification
    - Informations de l'utilisateur destinataire
    - Type de notification (info, warning, success, error)
    """

    user_name = serializers.SerializerMethodField()
    user_email = serializers.CharField(source="user.email", read_only=True)
    notification_type_display = serializers.CharField(
        source="get_notification_type_display", read_only=True
    )

    class Meta:
        model = UserNotification
        fields = [
            "id",
            "user",
            "user_name",
            "user_email",
            "title",
            "message",
            "notification_type",
            "notification_type_display",
            "is_read",
            "read_at",
            "related_link",
            "created_at",
        ]
        read_only_fields = ["read_at", "created_at"]

    def get_user_name(self, obj):
        """Retourne le nom complet de l'utilisateur."""
        if obj.user:
            return f"{obj.user.first_name} {obj.user.last_name}"
        return None

    def update(self, instance, validated_data):
        """Met à jour une notification et enregistre la date de lecture si elle est marquée comme lue."""
        from django.utils import timezone

        is_read = validated_data.get("is_read", instance.is_read)

        if is_read and not instance.is_read:
            # Si la notification vient d'être marquée comme lue
            validated_data["read_at"] = timezone.now()
        elif not is_read and instance.is_read:
            # Si la notification est marquée comme non lue
            validated_data["read_at"] = None

        return super().update(instance, validated_data)


class UserNotificationListSerializer(serializers.ModelSerializer):
    """
    Serializer simplifié pour les listes de notifications.

    Utilisé pour optimiser les performances lors de l'affichage
    de listes avec moins de données.
    """

    notification_type_display = serializers.CharField(
        source="get_notification_type_display", read_only=True
    )

    class Meta:
        model = UserNotification
        fields = [
            "id",
            "title",
            "message",
            "notification_type",
            "notification_type_display",
            "is_read",
            "read_at",
            "related_link",
            "created_at",
        ]
