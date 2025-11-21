"""Serializer pour le modèle SupportCategory (catégories de support)."""

from rest_framework import serializers
from support.models import SupportCategory


class SupportCategorySerializer(serializers.ModelSerializer):
    """
    Serializer pour les catégories de support.
    
    Inclut :
    - Informations de la catégorie
    - Nombre de tickets dans cette catégorie
    """

    tickets_count = serializers.SerializerMethodField()

    class Meta:
        model = SupportCategory
        fields = [
            "id",
            "name",
            "description",
            "icon",
            "color",
            "is_active",
            "tickets_count",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["created_at", "updated_at"]

    def get_tickets_count(self, obj):
        """Retourne le nombre de tickets dans cette catégorie."""
        return obj.tickets.count()

