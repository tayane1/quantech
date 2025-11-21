"""Serializer pour le modèle Department (départements)."""

from rest_framework import serializers
from department.models import Department


class DepartmentSerializer(serializers.ModelSerializer):
    """Serializer pour les départements avec statistiques."""

    manager_name = serializers.SerializerMethodField()
    manager_email = serializers.CharField(
        source="manager.email", read_only=True, allow_null=True
    )
    employee_count = serializers.IntegerField(read_only=True)
    total_employees = serializers.IntegerField(
        source="employees.count", read_only=True
    )
    active_employees = serializers.SerializerMethodField()
    job_positions_count = serializers.IntegerField(
        source="job_positions.count", read_only=True
    )
    open_positions_count = serializers.SerializerMethodField()

    class Meta:
        model = Department
        fields = [
            "id",
            "name",
            "code",
            "description",
            "manager",
            "manager_name",
            "manager_email",
            "location",
            "budget",
            "employee_count",
            "total_employees",
            "active_employees",
            "job_positions_count",
            "open_positions_count",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["created_at", "updated_at"]

    def get_manager_name(self, obj):
        """Retourne le nom complet du manager."""
        if obj.manager:
            return f"{obj.manager.first_name} {obj.manager.last_name}"
        return None

    def get_active_employees(self, obj):
        """Retourne le nombre d'employés actifs."""
        from employee.models.employee import Employee

        return obj.employees.filter(status=Employee.STATUS_ACTIVE).count()

    def get_open_positions_count(self, obj):
        """Retourne le nombre d'offres d'emploi ouvertes."""
        from recruitment.models.job_position import JobPosition

        return obj.job_positions.filter(status=JobPosition.STATUS_OPEN).count()

    def validate_code(self, value):
        """Valide l'unicité du code."""
        queryset = Department.objects.filter(code=value)
        if self.instance:
            queryset = queryset.exclude(pk=self.instance.pk)
        if queryset.exists():
            raise serializers.ValidationError(
                "Un département avec ce code existe déjà."
            )
        return value

    def validate_budget(self, value):
        """Valide que le budget est positif ou nul."""
        if value < 0:
            raise serializers.ValidationError(
                "Le budget ne peut pas être négatif."
            )
        return value


class DepartmentListSerializer(serializers.ModelSerializer):
    """Serializer simplifié pour les listes de départements."""

    manager_name = serializers.SerializerMethodField()
    employee_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = Department
        fields = [
            "id",
            "name",
            "code",
            "manager_name",
            "location",
            "employee_count",
            "budget",
        ]

    def get_manager_name(self, obj):
        """Retourne le nom complet du manager."""
        if obj.manager:
            return f"{obj.manager.first_name} {obj.manager.last_name}"
        return None

