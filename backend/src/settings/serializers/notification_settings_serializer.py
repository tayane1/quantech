"""Serializer pour le modèle NotificationSettings (paramètres de notifications)."""

from rest_framework import serializers
from settings.models import NotificationSettings


class NotificationSettingsSerializer(serializers.ModelSerializer):
    """
    Serializer pour les paramètres de notifications.
    
    Inclut :
    - Type de notification avec display
    - Options d'envoi (email, SMS, push)
    """

    notification_type_display = serializers.CharField(
        source="get_notification_type_display", read_only=True
    )

    class Meta:
        model = NotificationSettings
        fields = [
            "id",
            "notification_type",
            "notification_type_display",
            "enabled",
            "send_email",
            "send_sms",
            "send_push",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["created_at", "updated_at"]

    def validate_notification_type(self, value):
        """Valide que le type de notification est unique."""
        queryset = NotificationSettings.objects.filter(notification_type=value)
        if self.instance:
            queryset = queryset.exclude(pk=self.instance.pk)
        if queryset.exists():
            raise serializers.ValidationError(
                "Un paramètre de notification pour ce type existe déjà."
            )
        return value

