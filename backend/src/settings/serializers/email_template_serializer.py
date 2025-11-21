"""Serializer pour le modèle EmailTemplate (modèles d'emails)."""

from rest_framework import serializers
from settings.models import EmailTemplate


class EmailTemplateSerializer(serializers.ModelSerializer):
    """
    Serializer complet pour les modèles d'emails.
    
    Inclut :
    - Toutes les informations du modèle
    - Type de template avec display
    """

    template_type_display = serializers.CharField(
        source="get_template_type_display", read_only=True
    )

    class Meta:
        model = EmailTemplate
        fields = [
            "id",
            "name",
            "template_type",
            "template_type_display",
            "subject",
            "body_html",
            "body_text",
            "is_active",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["created_at", "updated_at"]

    def validate_name(self, value):
        """Valide que le nom du modèle est unique."""
        queryset = EmailTemplate.objects.filter(name=value)
        if self.instance:
            queryset = queryset.exclude(pk=self.instance.pk)
        if queryset.exists():
            raise serializers.ValidationError(
                "Un modèle d'email avec ce nom existe déjà."
            )
        return value


class EmailTemplateListSerializer(serializers.ModelSerializer):
    """
    Serializer simplifié pour les listes de modèles d'emails.
    
    Utilisé pour optimiser les performances lors de l'affichage
    de listes avec moins de données.
    """

    template_type_display = serializers.CharField(
        source="get_template_type_display", read_only=True
    )

    class Meta:
        model = EmailTemplate
        fields = [
            "id",
            "name",
            "template_type",
            "template_type_display",
            "subject",
            "is_active",
            "created_at",
            "updated_at",
        ]

