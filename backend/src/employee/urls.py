"""
URLs pour l'application employee.

Ce fichier configure les routes REST pour les endpoints d'employés :
- /api/employee/employees/ : Gestion des employés
- /api/employee/history/ : Historique des changements

Utilise le DefaultRouter de DRF pour générer automatiquement les routes CRUD.
"""

from rest_framework.routers import DefaultRouter
from employee.viewsets import EmployeeViewSet, EmployeeHistoryViewSet

router = DefaultRouter()
router.register(r"employees", EmployeeViewSet, basename="employee")
router.register(r"history", EmployeeHistoryViewSet, basename="employee-history")

urlpatterns = router.urls

