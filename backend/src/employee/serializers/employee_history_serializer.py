"""Serializer pour le modèle EmployeeHistory (historique des changements)."""

from rest_framework import serializers
from employee.models.employee_history import EmployeeHistory


class EmployeeHistorySerializer(serializers.ModelSerializer):
    """Serializer pour l'historique des changements d'un employé."""

    employee_name = serializers.SerializerMethodField()
    changed_by_name = serializers.SerializerMethodField()

    def get_employee_name(self, obj):
        """Retourne le nom complet de l'employé."""
        return f"{obj.employee.first_name} {obj.employee.last_name}"

    class Meta:
        model = EmployeeHistory
        fields = [
            "id",
            "employee",
            "employee_name",
            "change_type",
            "old_value",
            "new_value",
            "changed_by",
            "changed_by_name",
            "changed_at",
        ]
        read_only_fields = ["changed_at"]

    def get_changed_by_name(self, obj):
        """Retourne le nom complet de la personne qui a effectué le changement."""
        if obj.changed_by:
            return f"{obj.changed_by.first_name} {obj.changed_by.last_name}"
        return None

