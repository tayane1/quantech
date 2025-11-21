"""Point d'entrée des modèles de l'app employee."""

from .models.employee import Employee
from .models.employee_history import EmployeeHistory

__all__ = [
    "Employee",
    "EmployeeHistory",
]
