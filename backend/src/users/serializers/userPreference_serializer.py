"""Serializer pour le modèle UserPreference (préférences utilisateur)."""

from rest_framework import serializers
from users.models import UserPreference


class UserPreferenceSerializer(serializers.ModelSerializer):
    """
    Serializer pour les préférences utilisateur.

    Inclut :
    - Paramètres de langue et timezone
    - Paramètres de notifications
    - Paramètres d'affichage du dashboard
    """

    user_name = serializers.CharField(source="user.get_full_name", read_only=True)
    user_email = serializers.CharField(source="user.email", read_only=True)
    theme_display = serializers.CharField(
        source="get_dashboard_theme_display", read_only=True
    )

    class Meta:
        model = UserPreference
        fields = [
            "id",
            "user",
            "user_name",
            "user_email",
            "language",
            "timezone",
            "email_notifications",
            "in_app_notifications",
            "sms_notifications",
            "dashboard_theme",
            "theme_display",
            "show_welcome_message",
            "updated_at",
        ]
        read_only_fields = ["updated_at"]

    def validate_timezone(self, value):
        """Valide que la timezone est valide."""
        # Validation basique - peut être améliorée avec pytz si disponible
        if not value:
            return value
        # Liste des timezones courantes
        common_timezones = [
            "UTC",
            "Europe/Paris",
            "America/New_York",
            "America/Los_Angeles",
            "Asia/Tokyo",
            "Asia/Shanghai",
            "Australia/Sydney",
        ]
        # Pour une validation plus stricte, installer pytz :
        # import pytz
        # try:
        #     pytz.timezone(value)
        # except pytz.exceptions.UnknownTimeZoneError:
        #     raise serializers.ValidationError(f"La timezone '{value}' n'est pas valide.")
        return value

    def validate_language(self, value):
        """Valide que la langue est supportée."""
        supported_languages = ["fr", "en", "es", "de"]
        if value not in supported_languages:
            raise serializers.ValidationError(
                f"La langue '{value}' n'est pas supportée. Langues disponibles : {', '.join(supported_languages)}"
            )
        return value
