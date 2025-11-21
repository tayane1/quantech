"""Serializer pour le modèle Activity (activités du dashboard)."""

from rest_framework import serializers
from dashboard.models.activity import Activity


class ActivitySerializer(serializers.ModelSerializer):
    """Serializer pour les activités du dashboard avec informations contextuelles."""

    user_name = serializers.SerializerMethodField()
    activity_type_display = serializers.CharField(
        source="get_activity_type_display", read_only=True
    )
    related_position_title = serializers.CharField(
        source="related_position.title", read_only=True, allow_null=True
    )
    related_candidate_name = serializers.SerializerMethodField()
    related_employee_name = serializers.SerializerMethodField()

    class Meta:
        model = Activity
        fields = [
            "id",
            "user",
            "user_name",
            "activity_type",
            "activity_type_display",
            "description",
            "related_position",
            "related_position_title",
            "related_candidate",
            "related_candidate_name",
            "related_employee",
            "related_employee_name",
            "created_at",
        ]
        read_only_fields = ["created_at"]

    def get_user_name(self, obj):
        """Retourne le nom complet de l'utilisateur."""
        return f"{obj.user.first_name} {obj.user.last_name}"

    def get_related_candidate_name(self, obj):
        """Retourne le nom complet du candidat si présent."""
        if obj.related_candidate:
            return f"{obj.related_candidate.first_name} {obj.related_candidate.last_name}"
        return None

    def get_related_employee_name(self, obj):
        """Retourne le nom complet de l'employé si présent."""
        if obj.related_employee:
            return f"{obj.related_employee.first_name} {obj.related_employee.last_name}"
        return None

