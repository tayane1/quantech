"""Serializer pour le modèle DashboardMetric (métriques du dashboard)."""

from rest_framework import serializers
from dashboard.models.dashboard_metric import DashboardMetric


class DashboardMetricSerializer(serializers.ModelSerializer):
    """Serializer pour les métriques du dashboard."""

    change_direction = serializers.SerializerMethodField()
    change_label = serializers.SerializerMethodField()

    class Meta:
        model = DashboardMetric
        fields = [
            "id",
            "metric_type",
            "value",
            "previous_value",
            "change_percentage",
            "change_direction",
            "change_label",
            "updated_at",
        ]
        read_only_fields = ["updated_at"]

    def get_change_direction(self, obj):
        """Retourne la direction du changement (up, down, neutral)."""
        if obj.change_percentage is None:
            return "neutral"
        if obj.change_percentage > 0:
            return "up"
        elif obj.change_percentage < 0:
            return "down"
        return "neutral"

    def get_change_label(self, obj):
        """Retourne un label lisible pour le changement."""
        if obj.change_percentage is None:
            return "Aucun changement"
        direction = self.get_change_direction(obj)
        percentage = abs(obj.change_percentage)
        if direction == "up":
            return f"+{percentage:.1f}%"
        elif direction == "down":
            return f"-{percentage:.1f}%"
        return "Aucun changement"

