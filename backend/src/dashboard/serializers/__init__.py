"""Serializers pour l'application dashboard."""

from .activity_serializer import ActivitySerializer
from .dashboard_metric_serializer import DashboardMetricSerializer

__all__ = [
    "DashboardMetricSerializer",
    "ActivitySerializer",
]

