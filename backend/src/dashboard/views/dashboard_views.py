"""
Vues personnalisées pour le dashboard.

Ces vues fournissent des endpoints agrégés pour le dashboard :
- Vue d'ensemble complète du dashboard
- Statistiques consolidées
"""

from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.db.models import Count, Q
from django.utils import timezone
from datetime import timedelta

from employee.models.employee import Employee
from recruitment.models.job_position import JobPosition
from recruitment.models.candidate import Candidate
from recruitment.models.talent_request import TalentRequest
from schedule.models.schedule_task import Schedule
from schedule.models.meeting import Meeting
from dashboard.models.activity import Activity
from dashboard.models.dashboard_metric import DashboardMetric


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def dashboard_overview(request):
    """
    Vue d'ensemble complète du dashboard.
    
    GET /api/dashboard/overview/
    
    Retourne :
    - Métriques principales
    - Activités récentes
    - Statistiques consolidées
    """
    # Récalculer les métriques si nécessaire (optionnel)
    # metric_viewset = DashboardMetricViewSet()
    # metric_viewset._calculate_all_metrics()

    # Récupérer les métriques
    metrics = DashboardMetric.objects.all()
    metrics_data = {
        metric.metric_type: {
            "value": metric.value,
            "previous_value": metric.previous_value,
            "change_percentage": metric.change_percentage,
        }
        for metric in metrics
    }

    # Récupérer les activités récentes (10 dernières)
    recent_activities = Activity.objects.select_related(
        "user", "related_position", "related_candidate", "related_employee"
    ).order_by("-created_at")[:10]

    from dashboard.serializers.activity_serializer import ActivitySerializer

    activities_serializer = ActivitySerializer(recent_activities, many=True)

    # Statistiques supplémentaires
    today = timezone.now().date()
    week_ago = today - timedelta(days=7)

    stats = {
        "employees": {
            "total": Employee.objects.count(),
            "active": Employee.objects.filter(status=Employee.STATUS_ACTIVE).count(),
            "new_this_week": Employee.objects.filter(hire_date__gte=week_ago).count(),
        },
        "recruitment": {
            "open_positions": JobPosition.objects.filter(
                status=JobPosition.STATUS_OPEN
            ).count(),
            "urgent_positions": JobPosition.objects.filter(
                status=JobPosition.STATUS_OPEN, urgency=True
            ).count(),
            "active_candidates": Candidate.objects.exclude(
                status__in=[Candidate.STATUS_REJECTED, Candidate.STATUS_HIRED]
            ).count(),
            "pending_requests": TalentRequest.objects.filter(
                status=TalentRequest.STATUS_PENDING
            ).count(),
        },
        "schedule": {
            "upcoming_tasks": Schedule.objects.filter(
                completed=False, scheduled_date__gte=timezone.now()
            ).count(),
            "upcoming_meetings": Meeting.objects.filter(
                start_time__gte=timezone.now()
            ).count(),
        },
    }

    return Response(
        {
            "metrics": metrics_data,
            "recent_activities": activities_serializer.data,
            "statistics": stats,
        },
        status=status.HTTP_200_OK,
    )

