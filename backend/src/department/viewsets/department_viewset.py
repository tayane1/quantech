"""
ViewSet pour la gestion des départements (Department).

Ce ViewSet implémente les opérations CRUD complètes pour les départements :
- Liste, détail, création, modification, suppression
- Actions personnalisées : statistiques, employés, offres d'emploi
- Permissions : admins/HR peuvent tout faire, autres peuvent lire
"""

from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from django.db.models import Count, Sum, Avg

from department.models import Department
from department.serializers.department_serializer import (
    DepartmentSerializer,
    DepartmentListSerializer,
)


class IsHRManagerOrAdmin(permissions.BasePermission):
    """
    Permission personnalisée :
    - Les admins et HR managers peuvent tout faire
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


class DepartmentViewSet(viewsets.ModelViewSet):
    """
    ViewSet pour les départements.
    
    Endpoints disponibles :
    - GET /api/department/departments/ : Liste des départements
    - POST /api/department/departments/ : Créer un département
    - GET /api/department/departments/{id}/ : Détails d'un département
    - PUT/PATCH /api/department/departments/{id}/ : Modifier un département
    - DELETE /api/department/departments/{id}/ : Supprimer un département
    - GET /api/department/departments/{id}/employees/ : Employés du département
    - GET /api/department/departments/{id}/job-positions/ : Offres d'emploi du département
    - GET /api/department/departments/{id}/statistics/ : Statistiques détaillées
    - GET /api/department/departments/statistics/ : Statistiques globales
    """
    
    queryset = Department.objects.select_related("manager").prefetch_related(
        "employees", "job_positions"
    ).all()
    serializer_class = DepartmentSerializer
    permission_classes = [permissions.IsAuthenticated, IsHRManagerOrAdmin]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ["manager", "location"]
    search_fields = ["name", "code", "description", "location"]
    ordering_fields = ["name", "created_at", "budget"]
    ordering = ["name"]

    def get_serializer_class(self):
        """Utilise un serializer simplifié pour les listes."""
        if self.action == "list":
            return DepartmentListSerializer
        return DepartmentSerializer

    @action(detail=True, methods=["get"], url_path="employees")
    def employees(self, request, pk=None):
        """
        Action personnalisée : Récupérer les employés d'un département.
        GET /api/department/departments/{id}/employees/
        """
        department = self.get_object()
        employees = department.employees.select_related(
            "department", "position", "manager"
        ).all()

        from employee.serializers.employee_serializer import EmployeeListSerializer

        serializer = EmployeeListSerializer(employees, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=["get"], url_path="job-positions")
    def job_positions(self, request, pk=None):
        """
        Action personnalisée : Récupérer les offres d'emploi d'un département.
        GET /api/department/departments/{id}/job-positions/
        """
        department = self.get_object()
        job_positions = department.job_positions.select_related(
            "department"
        ).prefetch_related("candidates").all()

        from recruitment.serializers.job_position_serializer import (
            JobPositionSerializer,
        )

        serializer = JobPositionSerializer(job_positions, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=["get"], url_path="statistics")
    def statistics(self, request, pk=None):
        """
        Action personnalisée : Statistiques détaillées d'un département.
        GET /api/department/departments/{id}/statistics/
        """
        department = self.get_object()

        from employee.models.employee import Employee
        from recruitment.models.job_position import JobPosition
        from recruitment.models.candidate import Candidate

        # Statistiques des employés
        employees = department.employees.all()
        employees_stats = {
            "total": employees.count(),
            "by_status": {
                status: employees.filter(status=status).count()
                for status, _ in Employee.STATUS_CHOICES
            },
            "by_gender": {
                gender: employees.filter(gender=gender).count()
                for gender, _ in Employee.GENDER_CHOICES
            },
            "average_salary": float(
                employees.aggregate(avg=Avg("salary"))["avg"] or 0
            ),
            "total_salary": float(
                employees.aggregate(total=Sum("salary"))["total"] or 0
            ),
        }

        # Statistiques des offres d'emploi
        job_positions = department.job_positions.all()
        job_positions_stats = {
            "total": job_positions.count(),
            "by_status": {
                status: job_positions.filter(status=status).count()
                for status, _ in JobPosition.STATUS_CHOICES
            },
            "urgent": job_positions.filter(urgency=True).count(),
            "total_candidates": Candidate.objects.filter(
                position__department=department
            ).count(),
        }

        stats = {
            "department": {
                "id": department.id,
                "name": department.name,
                "code": department.code,
                "budget": float(department.budget),
            },
            "employees": employees_stats,
            "job_positions": job_positions_stats,
        }

        return Response(stats)

    @action(detail=False, methods=["get"], url_path="statistics")
    def global_statistics(self, request):
        """
        Action personnalisée : Statistiques globales de tous les départements.
        GET /api/department/departments/statistics/
        """
        from employee.models.employee import Employee
        from recruitment.models.job_position import JobPosition

        departments = self.get_queryset()

        stats = {
            "total_departments": departments.count(),
            "total_budget": float(
                departments.aggregate(total=Sum("budget"))["total"] or 0
            ),
            "total_employees": Employee.objects.filter(
                department__in=departments
            ).count(),
            "total_job_positions": JobPosition.objects.filter(
                department__in=departments
            ).count(),
            "by_department": [
                {
                    "id": dept.id,
                    "name": dept.name,
                    "code": dept.code,
                    "employee_count": dept.employee_count,
                    "budget": float(dept.budget),
                }
                for dept in departments
            ],
        }

        return Response(stats)

