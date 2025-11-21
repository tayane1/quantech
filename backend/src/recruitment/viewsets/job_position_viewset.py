"""
ViewSet pour la gestion des offres d'emploi (JobPosition).

Ce ViewSet implémente les opérations CRUD complètes pour les offres d'emploi :
- Liste, détail, création, modification, suppression
- Actions personnalisées : offres urgentes, offres ouvertes, statistiques
- Permissions : tous les utilisateurs authentifiés peuvent voir, seuls les admins/HR peuvent modifier
"""

from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter

from recruitment.models.job_position import JobPosition
from recruitment.serializers.job_position_serializer import JobPositionSerializer


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
            and (request.user.is_staff or request.user.role in ["admin", "hr_manager"])
        )


class JobPositionViewSet(viewsets.ModelViewSet):
    """
    ViewSet pour les offres d'emploi.
    
    Endpoints disponibles :
    - GET /api/recruitment/job-positions/ : Liste des offres
    - POST /api/recruitment/job-positions/ : Créer une offre
    - GET /api/recruitment/job-positions/{id}/ : Détails d'une offre
    - PUT/PATCH /api/recruitment/job-positions/{id}/ : Modifier une offre
    - DELETE /api/recruitment/job-positions/{id}/ : Supprimer une offre
    - GET /api/recruitment/job-positions/urgent/ : Offres urgentes
    - GET /api/recruitment/job-positions/open/ : Offres ouvertes
    - GET /api/recruitment/job-positions/{id}/statistics/ : Statistiques d'une offre
    """
    
    serializer_class = JobPositionSerializer
    permission_classes = [permissions.IsAuthenticated, IsHRManagerOrAdmin]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ["status", "urgency", "department"]
    search_fields = ["title", "description"]
    ordering_fields = ["created_at", "updated_at", "title"]
    ordering = ["-created_at"]

    def get_queryset(self):
        """Retourne toutes les offres avec relations optimisées."""
        return JobPosition.objects.select_related("department").prefetch_related(
            "candidates"
        ).all()

    @action(detail=False, methods=["get"], url_path="urgent")
    def urgent(self, request):
        """
        Action personnalisée : Récupérer uniquement les offres urgentes.
        GET /api/recruitment/job-positions/urgent/
        """
        queryset = self.get_queryset().filter(urgency=True, status=JobPosition.STATUS_OPEN)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=["get"], url_path="open")
    def open_positions(self, request):
        """
        Action personnalisée : Récupérer uniquement les offres ouvertes.
        GET /api/recruitment/job-positions/open/
        """
        queryset = self.get_queryset().filter(status=JobPosition.STATUS_OPEN)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=["get"], url_path="statistics")
    def statistics(self, request, pk=None):
        """
        Action personnalisée : Statistiques détaillées d'une offre.
        GET /api/recruitment/job-positions/{id}/statistics/
        """
        job_position = self.get_object()
        
        from recruitment.models.candidate import Candidate
        
        stats = {
            "total_candidates": job_position.candidates.count(),
            "by_status": {
                status: job_position.candidates.filter(status=status).count()
                for status, _ in Candidate.STATUS_CHOICES
            },
            "active_candidates": job_position.candidates.exclude(
                status__in=[Candidate.STATUS_REJECTED, Candidate.STATUS_HIRED]
            ).count(),
            "hired_count": job_position.candidates.filter(
                status=Candidate.STATUS_HIRED
            ).count(),
        }
        
        return Response(stats)

