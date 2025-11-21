"""ViewSets pour l'application employee."""

from .employee_viewset import EmployeeViewSet
from .employee_history_viewset import EmployeeHistoryViewSet

__all__ = [
    "EmployeeViewSet",
    "EmployeeHistoryViewSet",
]

