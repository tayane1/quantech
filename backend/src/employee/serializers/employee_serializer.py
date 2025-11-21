"""Serializer pour le modèle Employee (employés)."""

from rest_framework import serializers
from employee.models.employee import Employee


class EmployeeSerializer(serializers.ModelSerializer):
    """Serializer pour les employés avec informations contextuelles."""

    full_name = serializers.SerializerMethodField()
    gender_display = serializers.CharField(
        source="get_gender_display", read_only=True
    )
    status_display = serializers.CharField(
        source="get_status_display", read_only=True
    )
    department_name = serializers.CharField(
        source="department.name", read_only=True, allow_null=True
    )
    position_name = serializers.CharField(
        source="position.name", read_only=True, allow_null=True
    )
    manager_name = serializers.SerializerMethodField()
    subordinates_count = serializers.IntegerField(
        source="subordinates.count", read_only=True
    )
    age = serializers.SerializerMethodField()
    years_of_service = serializers.SerializerMethodField()

    class Meta:
        model = Employee
        fields = [
            "id",
            "first_name",
            "last_name",
            "full_name",
            "email",
            "phone",
            "date_of_birth",
            "age",
            "gender",
            "gender_display",
            "profile_picture",
            "employee_id",
            "hire_date",
            "years_of_service",
            "position",
            "position_name",
            "department",
            "department_name",
            "manager",
            "manager_name",
            "subordinates_count",
            "salary",
            "status",
            "status_display",
            "address",
            "city",
            "country",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["created_at", "updated_at", "employee_id"]

    def get_full_name(self, obj):
        """Retourne le nom complet de l'employé."""
        return f"{obj.first_name} {obj.last_name}"

    def get_manager_name(self, obj):
        """Retourne le nom complet du manager."""
        if obj.manager:
            return f"{obj.manager.first_name} {obj.manager.last_name}"
        return None

    def get_age(self, obj):
        """Calcule l'âge de l'employé."""
        from datetime import date

        today = date.today()
        return (
            today.year
            - obj.date_of_birth.year
            - ((today.month, today.day) < (obj.date_of_birth.month, obj.date_of_birth.day))
        )

    def get_years_of_service(self, obj):
        """Calcule les années de service."""
        from datetime import date

        today = date.today()
        return (
            today.year
            - obj.hire_date.year
            - ((today.month, today.day) < (obj.hire_date.month, obj.hire_date.day))
        )

    def to_representation(self, instance):
        """Convertir l'URL de l'image en URL absolue."""
        representation = super().to_representation(instance)
        if representation.get('profile_picture') and instance.profile_picture:
            request = self.context.get('request')
            if request:
                representation['profile_picture'] = request.build_absolute_uri(instance.profile_picture.url)
            else:
                # En cas d'absence de request, retourner l'URL relative
                # Le frontend devra construire l'URL complète avec l'URL de base de l'API
                representation['profile_picture'] = instance.profile_picture.url if hasattr(instance.profile_picture, 'url') else str(instance.profile_picture)
        return representation

    def validate_email(self, value):
        """Valide l'unicité de l'email."""
        queryset = Employee.objects.filter(email=value)
        if self.instance:
            queryset = queryset.exclude(pk=self.instance.pk)
        if queryset.exists():
            raise serializers.ValidationError(
                "Un employé avec cet email existe déjà."
            )
        return value

    def validate_employee_id(self, value):
        """Valide l'unicité de l'ID employé."""
        queryset = Employee.objects.filter(employee_id=value)
        if self.instance:
            queryset = queryset.exclude(pk=self.instance.pk)
        if queryset.exists():
            raise serializers.ValidationError(
                "Un employé avec cet ID existe déjà."
            )
        return value

    def validate_salary(self, value):
        """Valide que le salaire est positif."""
        if value <= 0:
            raise serializers.ValidationError(
                "Le salaire doit être supérieur à 0."
            )
        return value

    def validate(self, attrs):
        """Valide la cohérence des données."""
        # Vérifier que la date de naissance est dans le passé
        date_of_birth = attrs.get("date_of_birth") or (
            self.instance.date_of_birth if self.instance else None
        )
        if date_of_birth:
            from datetime import date

            if date_of_birth >= date.today():
                raise serializers.ValidationError(
                    "La date de naissance doit être dans le passé."
                )

        # Vérifier que la date d'embauche est dans le passé
        hire_date = attrs.get("hire_date") or (
            self.instance.hire_date if self.instance else None
        )
        if hire_date:
            from datetime import date

            if hire_date > date.today():
                raise serializers.ValidationError(
                    "La date d'embauche ne peut pas être dans le futur."
                )

        # Vérifier qu'un employé n'est pas son propre manager
        manager = attrs.get("manager") or (
            self.instance.manager if self.instance else None
        )
        if manager and self.instance:
            if manager.id == self.instance.id:
                raise serializers.ValidationError(
                    "Un employé ne peut pas être son propre manager."
                )

        return attrs


class EmployeeListSerializer(serializers.ModelSerializer):
    """Serializer simplifié pour les listes d'employés."""

    full_name = serializers.SerializerMethodField()
    department_name = serializers.CharField(
        source="department.name", read_only=True, allow_null=True
    )
    position_name = serializers.CharField(
        source="position.name", read_only=True, allow_null=True
    )

    class Meta:
        model = Employee
        fields = [
            "id",
            "employee_id",
            "first_name",
            "last_name",
            "full_name",
            "email",
            "phone",
            "department_name",
            "position_name",
            "status",
            "hire_date",
            "profile_picture",
        ]

    def get_full_name(self, obj):
        """Retourne le nom complet de l'employé."""
        return f"{obj.first_name} {obj.last_name}"

    def to_representation(self, instance):
        """Convertir l'URL de l'image en URL absolue."""
        representation = super().to_representation(instance)
        if representation.get('profile_picture') and instance.profile_picture:
            request = self.context.get('request')
            if request:
                representation['profile_picture'] = request.build_absolute_uri(instance.profile_picture.url)
            else:
                # En cas d'absence de request, retourner l'URL relative
                # Le frontend devra construire l'URL complète avec l'URL de base de l'API
                representation['profile_picture'] = instance.profile_picture.url if hasattr(instance.profile_picture, 'url') else str(instance.profile_picture)
        return representation

