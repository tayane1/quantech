"""
ViewSet pour la gestion de l'historique des employés (EmployeeHistory).

Ce ViewSet permet de consulter l'historique des changements :
- Les utilisateurs peuvent voir l'historique de leur employé associé
- Les admins/HR peuvent voir tout l'historique
- Lecture seule (pas de création/modification via API)
"""

from rest_framework import viewsets, permissions
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter

from employee.models.employee_history import EmployeeHistory
from employee.serializers.employee_history_serializer import (
    EmployeeHistorySerializer,
)


class IsOwnerOrAdmin(permissions.BasePermission):
    """
    Permission personnalisée :
    - Les admins peuvent voir tout
    - Les utilisateurs peuvent voir l'historique de leur employé associé
    """

    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated


class EmployeeHistoryViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet en lecture seule pour l'historique des changements.
    
    Endpoints disponibles :
    - GET /api/employee/history/ : Liste de l'historique
    - GET /api/employee/history/{id}/ : Détails d'une entrée
    - GET /api/employee/history/by-employee/{employee_id}/ : Historique d'un employé
    - GET /api/employee/history/recent/ : Changements récents
    """
    
    serializer_class = EmployeeHistorySerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrAdmin]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ["employee", "change_type", "changed_by"]
    search_fields = ["change_type", "old_value", "new_value"]
    ordering_fields = ["changed_at"]
    ordering = ["-changed_at"]

    def get_queryset(self):
        """Filtre le queryset selon les permissions."""
        queryset = EmployeeHistory.objects.select_related(
            "employee", "changed_by"
        ).all()

        # Si admin/HR, retourner tout
        if self.request.user.is_staff or self.request.user.role in [
            "admin",
            "hr_manager",
        ]:
            return queryset

        # Sinon, filtrer par employé associé
        if hasattr(self.request.user, "employee") and self.request.user.employee:
            return queryset.filter(employee=self.request.user.employee)

        return queryset.none()

    def get_serializer_class(self):
        """Retourne le serializer approprié."""
        return EmployeeHistorySerializer

