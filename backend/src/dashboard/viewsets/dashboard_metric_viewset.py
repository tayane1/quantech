"""
ViewSet pour la gestion des métriques du dashboard (DashboardMetric).

Ce ViewSet gère les métriques affichées sur le dashboard :
- Consultation des métriques
- Calcul et mise à jour automatique des métriques
- Actions personnalisées : recalculer toutes les métriques, métriques spécifiques
"""

from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import OrderingFilter
from django.utils import timezone
from datetime import timedelta
from django.db.models import Count, Q, Sum

from dashboard.models.dashboard_metric import DashboardMetric
from dashboard.serializers.dashboard_metric_serializer import (
    DashboardMetricSerializer,
)
from employee.models.employee import Employee
from recruitment.models.job_position import JobPosition
from recruitment.models.talent_request import TalentRequest
from department.models import Department


class IsAdminOrHR(permissions.BasePermission):
    """
    Permission personnalisée :
    - Les admins et HR peuvent tout faire
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


class DashboardMetricViewSet(viewsets.ModelViewSet):
    """
    ViewSet pour les métriques du dashboard.
    
    Endpoints disponibles :
    - GET /api/dashboard/metrics/ : Liste des métriques
    - GET /api/dashboard/metrics/{id}/ : Détails d'une métrique
    - POST /api/dashboard/metrics/recalculate/ : Recalculer toutes les métriques
    - POST /api/dashboard/metrics/recalculate/{metric_type}/ : Recalculer une métrique spécifique
    - GET /api/dashboard/metrics/aggregated/ : Métriques agrégées pour le dashboard
    """
    
    queryset = DashboardMetric.objects.all()
    serializer_class = DashboardMetricSerializer
    permission_classes = [permissions.IsAuthenticated, IsAdminOrHR]
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ["metric_type"]
    ordering_fields = ["metric_type", "updated_at"]
    ordering = ["metric_type"]

    @action(detail=False, methods=["get"], url_path="aggregated")
    def aggregated(self, request):
        """
        Action personnalisée : Retourner toutes les métriques agrégées pour le dashboard.
        GET /api/dashboard/metrics/aggregated/
        
        Retourne un format structuré avec toutes les métriques nécessaires au dashboard.
        """
        # Récupérer ou calculer toutes les métriques
        self._ensure_all_metrics_exist()
        
        # Récupérer les métriques depuis la base de données
        metrics = DashboardMetric.objects.all()
        metrics_dict = {m.metric_type: m.value for m in metrics}
        
        # Calculer les métriques supplémentaires nécessaires
        employees = Employee.objects.filter(status=Employee.STATUS_ACTIVE)
        total_employees = employees.count()
        men_count = employees.filter(gender='M').count()
        women_count = employees.filter(gender='F').count()
        
        # Calculer les changements
        employees_change = 0
        talent_change = 0
        try:
            total_employees_metric = DashboardMetric.objects.get(metric_type="total_employees")
            if total_employees_metric.change_percentage:
                employees_change = int(total_employees_metric.change_percentage)
        except DashboardMetric.DoesNotExist:
            pass
            
        try:
            talent_requests_metric = DashboardMetric.objects.get(metric_type="talent_requests")
            if talent_requests_metric.change_percentage:
                talent_change = int(talent_requests_metric.change_percentage)
        except DashboardMetric.DoesNotExist:
            pass
        
        # Métriques des positions ouvertes
        job_positions = JobPosition.objects.filter(status=JobPosition.STATUS_OPEN)
        available_positions = job_positions.count()
        urgent_positions = job_positions.filter(urgency=True).count()
        active_hiring = job_positions.filter(status=JobPosition.STATUS_OPEN).count()
        
        # Nouvelles recrues (7 derniers jours)
        seven_days_ago = timezone.now() - timedelta(days=7)
        new_employees = Employee.objects.filter(created_at__gte=seven_days_ago).count()
        departments_count = Department.objects.count()
        
        # Talent requests
        talent_requests = TalentRequest.objects.count()
        # TalentRequest n'a pas de gender_preference, on divise approximativement
        # ou on utilise les candidats associés si disponibles
        talent_men = 0  # À calculer depuis les candidats associés si nécessaire
        talent_women = 0  # À calculer depuis les candidats associés si nécessaire
        
        # Construire la réponse
        aggregated_metrics = {
            "available_positions": available_positions,
            "urgent_positions": urgent_positions,
            "job_open": available_positions,  # Alias
            "active_hiring": active_hiring,
            "new_employees": new_employees,
            "departments_count": departments_count,
            "total_employees": total_employees,
            "men_count": men_count,
            "women_count": women_count,
            "employees_change": employees_change,
            "talent_requests": talent_requests,
            "talent_men": talent_men,
            "talent_women": talent_women,
            "talent_change": talent_change,
        }
        
        return Response(aggregated_metrics)

    def _ensure_all_metrics_exist(self):
        """S'assure que toutes les métriques existent dans la base de données."""
        metrics_to_ensure = [
            "total_employees",
            "active_employees",
            "available_positions",
            "urgent_positions",
            "talent_requests",
        ]
        
        for metric_type in metrics_to_ensure:
            if not DashboardMetric.objects.filter(metric_type=metric_type).exists():
                self._calculate_metric(metric_type)

    @action(detail=False, methods=["post"], url_path="recalculate")
    def recalculate_all(self, request):
        """
        Action personnalisée : Recalculer toutes les métriques.
        POST /api/dashboard/metrics/recalculate/
        """
        self._calculate_all_metrics()
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(
        detail=False,
        methods=["post"],
        url_path="recalculate/(?P<metric_type>[^/.]+)",
    )
    def recalculate_metric(self, request, metric_type=None):
        """
        Action personnalisée : Recalculer une métrique spécifique.
        POST /api/dashboard/metrics/recalculate/{metric_type}/
        """
        self._calculate_metric(metric_type)
        try:
            metric = DashboardMetric.objects.get(metric_type=metric_type)
            serializer = self.get_serializer(metric)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except DashboardMetric.DoesNotExist:
            return Response(
                {"detail": f"Métrique '{metric_type}' non trouvée."},
                status=status.HTTP_404_NOT_FOUND,
            )

    def _calculate_all_metrics(self):
        """Calcule toutes les métriques du dashboard."""
        metrics_to_calculate = [
            "total_employees",
            "active_employees",
            "available_positions",
            "urgent_positions",
            "total_candidates",
            "active_candidates",
            "talent_requests",
            "pending_talent_requests",
        ]

        for metric_type in metrics_to_calculate:
            self._calculate_metric(metric_type)

    def _calculate_metric(self, metric_type):
        """Calcule une métrique spécifique."""
        # Récupérer l'ancienne valeur
        try:
            old_metric = DashboardMetric.objects.get(metric_type=metric_type)
            previous_value = old_metric.value
        except DashboardMetric.DoesNotExist:
            previous_value = None

        # Calculer la nouvelle valeur selon le type
        value = 0
        if metric_type == "total_employees":
            value = Employee.objects.count()
        elif metric_type == "active_employees":
            value = Employee.objects.filter(status=Employee.STATUS_ACTIVE).count()
        elif metric_type == "available_positions":
            value = JobPosition.objects.filter(
                status=JobPosition.STATUS_OPEN
            ).count()
        elif metric_type == "urgent_positions":
            value = JobPosition.objects.filter(
                status=JobPosition.STATUS_OPEN, urgency=True
            ).count()
        elif metric_type == "total_candidates":
            from recruitment.models.candidate import Candidate
            value = Candidate.objects.count()
        elif metric_type == "active_candidates":
            from recruitment.models.candidate import Candidate
            value = Candidate.objects.exclude(
                status__in=[Candidate.STATUS_REJECTED, Candidate.STATUS_HIRED]
            ).count()
        elif metric_type == "talent_requests":
            value = TalentRequest.objects.count()
        elif metric_type == "pending_talent_requests":
            value = TalentRequest.objects.filter(
                status=TalentRequest.STATUS_PENDING
            ).count()
        else:
            return  # Type de métrique inconnu

        # Calculer le pourcentage de changement
        change_percentage = None
        if previous_value is not None and previous_value != 0:
            change_percentage = ((value - previous_value) / previous_value) * 100

        # Créer ou mettre à jour la métrique
        DashboardMetric.objects.update_or_create(
            metric_type=metric_type,
            defaults={
                "value": value,
                "previous_value": previous_value,
                "change_percentage": change_percentage,
            },
        )
