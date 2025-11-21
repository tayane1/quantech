"""
ViewSet pour la gestion des employés (Employee).

Ce ViewSet implémente les opérations CRUD complètes pour les employés :
- Liste, détail, création, modification, suppression
- Actions personnalisées : employés actifs, par département, par manager, statistiques
- Permissions : admins/HR peuvent tout faire, managers peuvent voir leurs équipes
- Historique automatique des changements
"""

from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from django.db.models import Q, Count, Avg, Sum

from employee.models.employee import Employee
from employee.models.employee_history import EmployeeHistory
from employee.serializers.employee_serializer import (
    EmployeeSerializer,
    EmployeeListSerializer,
)


class IsHRManagerOrAdmin(permissions.BasePermission):
    """
    Permission personnalisée :
    - Les admins et HR managers peuvent tout faire
    - Les managers peuvent voir leurs équipes
    - Les autres utilisateurs peuvent uniquement lire
    """

    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return request.user and request.user.is_authenticated
        return (
            request.user
            and request.user.is_authenticated
            and (
                request.user.is_staff
                or request.user.role in ["admin", "hr_manager"]
            )
        )

    def has_object_permission(self, request, view, obj):
        # Admins et HR peuvent tout faire
        if request.user.is_staff or request.user.role in ["admin", "hr_manager"]:
            return True

        # Managers peuvent voir leurs subordonnés
        if hasattr(request.user, "employee") and request.user.employee:
            if obj.manager == request.user.employee:
                return request.method in permissions.SAFE_METHODS

        # Les employés peuvent voir leurs propres informations
        if hasattr(request.user, "employee") and request.user.employee:
            if obj == request.user.employee:
                return request.method in permissions.SAFE_METHODS

        return False


class EmployeeViewSet(viewsets.ModelViewSet):
    """
    ViewSet pour les employés.
    
    Endpoints disponibles :
    - GET /api/employee/employees/ : Liste des employés
    - POST /api/employee/employees/ : Créer un employé
    - GET /api/employee/employees/{id}/ : Détails d'un employé
    - PUT/PATCH /api/employee/employees/{id}/ : Modifier un employé
    - DELETE /api/employee/employees/{id}/ : Supprimer un employé
    - GET /api/employee/employees/active/ : Employés actifs
    - GET /api/employee/employees/by-department/{dept_id}/ : Employés par département
    - GET /api/employee/employees/my-team/ : Mon équipe (si manager)
    - GET /api/employee/employees/statistics/ : Statistiques globales
    - GET /api/employee/employees/{id}/subordinates/ : Subordonnés d'un employé
    """
    
    queryset = Employee.objects.select_related(
        "department", "position", "manager"
    ).prefetch_related("subordinates").all()
    serializer_class = EmployeeSerializer
    permission_classes = [permissions.IsAuthenticated, IsHRManagerOrAdmin]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = [
        "status",
        "gender",
        "department",
        "position",
        "manager",
    ]
    search_fields = [
        "first_name",
        "last_name",
        "email",
        "employee_id",
        "phone",
    ]
    ordering_fields = [
        "last_name",
        "first_name",
        "hire_date",
        "created_at",
        "salary",
    ]
    ordering = ["last_name", "first_name"]

    def get_serializer_class(self):
        """Utilise un serializer simplifié pour les listes."""
        if self.action == "list":
            return EmployeeListSerializer
        return EmployeeSerializer

    def get_queryset(self):
        """Filtre le queryset selon les permissions."""
        queryset = super().get_queryset()

        # Si admin/HR, retourner tout
        if self.request.user.is_staff or self.request.user.role in [
            "admin",
            "hr_manager",
        ]:
            return queryset

        # Si manager, retourner ses subordonnés + lui-même
        if hasattr(self.request.user, "employee") and self.request.user.employee:
            employee = self.request.user.employee
            return queryset.filter(
                Q(id=employee.id) | Q(manager=employee)
            )

        # Sinon, uniquement soi-même
        if hasattr(self.request.user, "employee") and self.request.user.employee:
            return queryset.filter(id=self.request.user.employee.id)

        return queryset.none()

    def perform_create(self, serializer):
        """Lors de la création, générer automatiquement l'employee_id si non fourni."""
        employee = serializer.save()

        # Générer un employee_id unique si non fourni
        if not employee.employee_id:
            from datetime import datetime

            prefix = "EMP"
            timestamp = datetime.now().strftime("%Y%m%d")
            count = Employee.objects.filter(
                employee_id__startswith=f"{prefix}{timestamp}"
            ).count() + 1
            employee.employee_id = f"{prefix}{timestamp}{count:04d}"
            employee.save()

        # Enregistrer dans l'historique
        EmployeeHistory.objects.create(
            employee=employee,
            change_type="created",
            new_value=f"Employé créé : {employee.first_name} {employee.last_name}",
            changed_by=self.request.user.employee
            if hasattr(self.request.user, "employee")
            else None,
        )

    def perform_update(self, serializer):
        """Lors de la mise à jour, enregistrer les changements dans l'historique."""
        old_instance = self.get_object()
        employee = serializer.save()

        # Détecter les changements et les enregistrer
        changes = []
        for field in [
            "first_name",
            "last_name",
            "email",
            "phone",
            "department",
            "position",
            "manager",
            "salary",
            "status",
        ]:
            old_value = getattr(old_instance, field, None)
            new_value = getattr(employee, field, None)

            if old_value != new_value:
                change_type = f"{field}_changed"
                old_str = str(old_value) if old_value else ""
                new_str = str(new_value) if new_value else ""

                EmployeeHistory.objects.create(
                    employee=employee,
                    change_type=change_type,
                    old_value=old_str[:255],
                    new_value=new_str[:255],
                    changed_by=self.request.user.employee
                    if hasattr(self.request.user, "employee")
                    else None,
                )

    def perform_destroy(self, instance):
        """Lors de la suppression, enregistrer dans l'historique."""
        EmployeeHistory.objects.create(
            employee=instance,
            change_type="deleted",
            new_value=f"Employé supprimé : {instance.first_name} {instance.last_name}",
            changed_by=self.request.user.employee
            if hasattr(self.request.user, "employee")
            else None,
        )
        instance.delete()

    @action(detail=False, methods=["get"], url_path="active")
    def active(self, request):
        """
        Action personnalisée : Récupérer uniquement les employés actifs.
        GET /api/employee/employees/active/
        """
        queryset = self.get_queryset().filter(status=Employee.STATUS_ACTIVE)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @action(
        detail=False,
        methods=["get"],
        url_path="by-department/(?P<department_id>[^/.]+)",
    )
    def by_department(self, request, department_id=None):
        """
        Action personnalisée : Récupérer les employés d'un département.
        GET /api/employee/employees/by-department/{department_id}/
        """
        queryset = self.get_queryset().filter(department_id=department_id)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=["get"], url_path="my-team")
    def my_team(self, request):
        """
        Action personnalisée : Récupérer mon équipe (si je suis manager).
        GET /api/employee/employees/my-team/
        """
        if not hasattr(request.user, "employee") or not request.user.employee:
            return Response(
                {"detail": "Vous n'êtes pas associé à un employé."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        manager = request.user.employee
        queryset = self.get_queryset().filter(manager=manager)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=["get"], url_path="statistics")
    def statistics(self, request):
        """
        Action personnalisée : Statistiques globales des employés.
        GET /api/employee/employees/statistics/
        """
        queryset = self.get_queryset()

        stats = {
            "total": queryset.count(),
            "by_status": {
                status: queryset.filter(status=status).count()
                for status, _ in Employee.STATUS_CHOICES
            },
            "by_gender": {
                gender: queryset.filter(gender=gender).count()
                for gender, _ in Employee.GENDER_CHOICES
            },
            "average_salary": float(
                queryset.aggregate(avg=Avg("salary"))["avg"] or 0
            ),
            "total_salary": float(
                queryset.aggregate(total=Sum("salary"))["total"] or 0
            ),
            "by_department": list(
                queryset.values("department__name")
                .annotate(count=Count("id"))
                .order_by("-count")
            ),
        }

        return Response(stats)

    @action(detail=True, methods=["get"], url_path="subordinates")
    def subordinates(self, request, pk=None):
        """
        Action personnalisée : Récupérer les subordonnés d'un employé.
        GET /api/employee/employees/{id}/subordinates/
        """
        employee = self.get_object()
        subordinates = self.get_queryset().filter(manager=employee)
        serializer = self.get_serializer(subordinates, many=True)
        return Response(serializer.data)

