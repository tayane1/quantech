"""Serializer pour le modèle Schedule (tâches planifiées)."""

from rest_framework import serializers
from schedule.models.schedule_task import Schedule
from employee.models.employee import Employee


class ScheduleSerializer(serializers.ModelSerializer):
    """Serializer pour les tâches planifiées avec informations des employés."""

    assigned_to_name = serializers.CharField(
        source="assigned_to.get_full_name", read_only=True
    )
    assigned_by_name = serializers.CharField(
        source="assigned_by.get_full_name", read_only=True, allow_null=True
    )

    class Meta:
        model = Schedule
        fields = [
            "id",
            "title",
            "description",
            "assigned_to",
            "assigned_to_name",
            "assigned_by",
            "assigned_by_name",
            "priority",
            "scheduled_date",
            "completed",
            "completed_date",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["created_at", "updated_at", "completed_date"]

    def validate_scheduled_date(self, value):
        """Valide que la date planifiée est dans le futur pour les nouvelles tâches."""
        from django.utils import timezone

        if self.instance is None and value < timezone.now():
            raise serializers.ValidationError(
                "La date planifiée ne peut pas être dans le passé pour une nouvelle tâche."
            )
        return value

    def validate(self, attrs):
        """Valide la cohérence des données."""
        # Si la tâche est marquée comme complétée, définir completed_date
        if attrs.get("completed") and not attrs.get("completed_date"):
            from django.utils import timezone

            attrs["completed_date"] = timezone.now()
        # Si la tâche n'est plus complétée, effacer completed_date
        elif not attrs.get("completed") and self.instance:
            if self.instance.completed:
                attrs["completed_date"] = None
        return attrs

