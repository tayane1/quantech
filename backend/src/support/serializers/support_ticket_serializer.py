"""Serializer pour le modèle SupportTicket (tickets de support)."""

from rest_framework import serializers
from support.models import SupportTicket


class SupportTicketSerializer(serializers.ModelSerializer):
    """
    Serializer complet pour les tickets de support.
    
    Inclut :
    - Toutes les informations du ticket
    - Informations des utilisateurs (créateur, assigné)
    - Informations de la catégorie
    - Statistiques (durée, nombre de commentaires)
    """

    created_by_name = serializers.SerializerMethodField()
    created_by_email = serializers.CharField(source="created_by.email", read_only=True)
    assigned_to_name = serializers.SerializerMethodField()
    assigned_to_email = serializers.CharField(
        source="assigned_to.email", read_only=True, allow_null=True
    )
    category_name = serializers.CharField(
        source="category.name", read_only=True, allow_null=True
    )
    priority_display = serializers.CharField(
        source="get_priority_display", read_only=True
    )
    status_display = serializers.CharField(
        source="get_status_display", read_only=True
    )
    comments_count = serializers.SerializerMethodField()
    duration_days = serializers.IntegerField(read_only=True)
    is_open = serializers.BooleanField(read_only=True)
    is_resolved = serializers.BooleanField(read_only=True)
    is_closed = serializers.BooleanField(read_only=True)

    class Meta:
        model = SupportTicket
        fields = [
            "id",
            "title",
            "description",
            "category",
            "category_name",
            "priority",
            "priority_display",
            "status",
            "status_display",
            "created_by",
            "created_by_name",
            "created_by_email",
            "assigned_to",
            "assigned_to_name",
            "assigned_to_email",
            "created_at",
            "updated_at",
            "resolved_at",
            "closed_at",
            "attachments",
            "tags",
            "resolution",
            "satisfaction_rating",
            "satisfaction_feedback",
            "comments_count",
            "duration_days",
            "is_open",
            "is_resolved",
            "is_closed",
        ]
        read_only_fields = [
            "created_by",
            "created_at",
            "updated_at",
            "resolved_at",
            "closed_at",
            "duration_days",
        ]

    def get_created_by_name(self, obj):
        """Retourne le nom complet du créateur."""
        if obj.created_by:
            return f"{obj.created_by.first_name} {obj.created_by.last_name}"
        return None

    def get_assigned_to_name(self, obj):
        """Retourne le nom complet de la personne assignée."""
        if obj.assigned_to:
            return f"{obj.assigned_to.first_name} {obj.assigned_to.last_name}"
        return None

    def get_comments_count(self, obj):
        """Retourne le nombre de commentaires sur le ticket."""
        return obj.comments.count()

    def validate_satisfaction_rating(self, value):
        """Valide que la note de satisfaction est entre 1 et 5."""
        if value is not None:
            if value < 1 or value > 5:
                raise serializers.ValidationError(
                    "La note de satisfaction doit être entre 1 et 5."
                )
        return value

    def create(self, validated_data):
        """Crée un nouveau ticket."""
        # Si le créateur n'est pas fourni, utiliser l'utilisateur connecté
        if "created_by" not in validated_data:
            request = self.context.get("request")
            if request and hasattr(request, "user"):
                validated_data["created_by"] = request.user

        return super().create(validated_data)


class SupportTicketListSerializer(serializers.ModelSerializer):
    """
    Serializer simplifié pour les listes de tickets.
    
    Utilisé pour optimiser les performances lors de l'affichage
    de listes avec moins de données.
    """

    created_by_name = serializers.SerializerMethodField()
    assigned_to_name = serializers.SerializerMethodField()
    category_name = serializers.CharField(
        source="category.name", read_only=True, allow_null=True
    )
    priority_display = serializers.CharField(
        source="get_priority_display", read_only=True
    )
    status_display = serializers.CharField(
        source="get_status_display", read_only=True
    )
    comments_count = serializers.SerializerMethodField()

    class Meta:
        model = SupportTicket
        fields = [
            "id",
            "title",
            "category",
            "category_name",
            "priority",
            "priority_display",
            "status",
            "status_display",
            "created_by_name",
            "assigned_to_name",
            "created_at",
            "updated_at",
            "comments_count",
        ]

    def get_created_by_name(self, obj):
        """Retourne le nom complet du créateur."""
        if obj.created_by:
            return f"{obj.created_by.first_name} {obj.created_by.last_name}"
        return None

    def get_assigned_to_name(self, obj):
        """Retourne le nom complet de la personne assignée."""
        if obj.assigned_to:
            return f"{obj.assigned_to.first_name} {obj.assigned_to.last_name}"
        return None

    def get_comments_count(self, obj):
        """Retourne le nombre de commentaires sur le ticket."""
        return obj.comments.count()

