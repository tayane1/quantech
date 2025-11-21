"""
URLs pour l'application dashboard.

Ce fichier configure les routes REST pour les endpoints du dashboard :
- /api/dashboard/metrics/ : Gestion des métriques
- /api/dashboard/activities/ : Gestion des activités
- /api/dashboard/overview/ : Vue d'ensemble complète

Utilise le DefaultRouter de DRF pour générer automatiquement les routes CRUD.
"""

from django.urls import path
from rest_framework.routers import DefaultRouter
from dashboard.viewsets import DashboardMetricViewSet, ActivityViewSet
from dashboard.views import dashboard_overview

router = DefaultRouter()
router.register(r"metrics", DashboardMetricViewSet, basename="dashboard-metric")
router.register(r"activities", ActivityViewSet, basename="activity")

urlpatterns = [
    path("overview/", dashboard_overview, name="dashboard-overview"),
] + router.urls

