"""
URLs pour l'application department.

Ce fichier configure les routes REST pour les endpoints de départements :
- /api/department/departments/ : Gestion des départements

Utilise le DefaultRouter de DRF pour générer automatiquement les routes CRUD.
"""

from rest_framework.routers import DefaultRouter
from department.viewsets import DepartmentViewSet

router = DefaultRouter()
router.register(r"departments", DepartmentViewSet, basename="department")

urlpatterns = router.urls

