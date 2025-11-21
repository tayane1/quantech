"""Serializer pour le modèle SystemSettings (paramètres système)."""

from rest_framework import serializers
from settings.models import SystemSettings


class SystemSettingsSerializer(serializers.ModelSerializer):
    """
    Serializer pour les paramètres système.
    
    Inclut :
    - Toutes les configurations de l'entreprise
    - Paramètres de sécurité
    - Paramètres d'email et notifications
    - Paramètres de fichiers
    """

    updated_by_name = serializers.SerializerMethodField()

    class Meta:
        model = SystemSettings
        fields = [
            "id",
            "company_name",
            "company_email",
            "company_phone",
            "company_address",
            "company_logo",
            "site_name",
            "site_url",
            "maintenance_mode",
            "maintenance_message",
            "password_min_length",
            "password_require_uppercase",
            "password_require_lowercase",
            "password_require_numbers",
            "password_require_special",
            "session_timeout_minutes",
            "max_login_attempts",
            "lockout_duration_minutes",
            "email_enabled",
            "email_host",
            "email_port",
            "email_use_tls",
            "email_from",
            "enable_email_notifications",
            "enable_sms_notifications",
            "enable_push_notifications",
            "max_upload_size_mb",
            "allowed_file_types",
            "currency",
            "updated_by",
            "updated_by_name",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["created_at", "updated_at"]

    def get_updated_by_name(self, obj):
        """Retourne le nom complet de celui qui a mis à jour les paramètres."""
        if obj.updated_by:
            return f"{obj.updated_by.first_name} {obj.updated_by.last_name}"
        return None

    def validate_password_min_length(self, value):
        """Valide que la longueur minimale du mot de passe est raisonnable."""
        if value < 6:
            raise serializers.ValidationError(
                "La longueur minimale du mot de passe doit être d'au moins 6 caractères."
            )
        if value > 128:
            raise serializers.ValidationError(
                "La longueur minimale du mot de passe ne peut pas dépasser 128 caractères."
            )
        return value

    def validate_max_upload_size_mb(self, value):
        """Valide que la taille maximale d'upload est raisonnable."""
        if value < 1:
            raise serializers.ValidationError(
                "La taille maximale d'upload doit être d'au moins 1 MB."
            )
        if value > 1000:
            raise serializers.ValidationError(
                "La taille maximale d'upload ne peut pas dépasser 1000 MB."
            )
        return value

    def validate_email_port(self, value):
        """Valide que le port email est valide."""
        if value < 1 or value > 65535:
            raise serializers.ValidationError(
                "Le port email doit être entre 1 et 65535."
            )
        return value

    def validate_currency(self, value):
        """Valide que le code devise est un code ISO 4217 valide."""
        if not value:
            return value
        
        # Vérifier que c'est exactement 3 caractères alphabétiques en majuscules
        # Format standard ISO 4217
        import re
        if not re.match(r'^[A-Z]{3}$', value):
            raise serializers.ValidationError(
                "Le code devise doit être un code ISO 4217 valide (3 lettres majuscules, ex: XOF, EUR, USD)."
            )
        
        return value

    def update(self, instance, validated_data):
        """Met à jour les paramètres système."""
        # Enregistrer qui a fait la mise à jour
        validated_data["updated_by"] = self.context["request"].user
        
        return super().update(instance, validated_data)

