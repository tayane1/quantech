"""
ViewSet pour la gestion du processus d'embauche (HiringProcess).

Ce ViewSet implémente les opérations CRUD complètes pour les étapes du processus d'embauche :
- Liste, détail, création, modification, suppression
- Actions personnalisées : étapes par candidat, entretiens à venir
- Permissions : tous les utilisateurs authentifiés peuvent voir, seuls les admins/HR peuvent modifier
"""

from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter

from recruitment.models.hiring_process import HiringProcess
from recruitment.serializers.hiring_process_serializer import HiringProcessSerializer


class IsHRManagerOrAdmin(permissions.BasePermission):
    """
    Permission personnalisée :
    - Les admins et HR managers peuvent tout faire
    - Les recruteurs peuvent créer/modifier les étapes
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
                or request.user.role in ["admin", "hr_manager", "recruiter"]
            )
        )


class HiringProcessViewSet(viewsets.ModelViewSet):
    """
    ViewSet pour le processus d'embauche.
    
    Endpoints disponibles :
    - GET /api/recruitment/hiring-process/ : Liste des étapes
    - POST /api/recruitment/hiring-process/ : Créer une étape
    - GET /api/recruitment/hiring-process/{id}/ : Détails d'une étape
    - PUT/PATCH /api/recruitment/hiring-process/{id}/ : Modifier une étape
    - DELETE /api/recruitment/hiring-process/{id}/ : Supprimer une étape
    - GET /api/recruitment/hiring-process/by-candidate/{candidate_id}/ : Étapes par candidat
    - GET /api/recruitment/hiring-process/upcoming/ : Entretiens à venir
    """
    
    serializer_class = HiringProcessSerializer
    permission_classes = [permissions.IsAuthenticated, IsHRManagerOrAdmin]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ["candidate", "interviewer", "stage"]
    search_fields = ["stage", "feedback", "result"]
    ordering_fields = ["scheduled_date", "created_at"]
    ordering = ["-scheduled_date"]

    def get_queryset(self):
        """Retourne toutes les étapes avec relations optimisées."""
        return HiringProcess.objects.select_related(
            "candidate", "candidate__position", "interviewer"
        ).all()

    @action(detail=False, methods=["get"], url_path="by-candidate/(?P<candidate_id>[^/.]+)")
    def by_candidate(self, request, candidate_id=None):
        """
        Action personnalisée : Récupérer les étapes pour un candidat spécifique.
        GET /api/recruitment/hiring-process/by-candidate/{candidate_id}/
        """
        queryset = self.get_queryset().filter(candidate_id=candidate_id)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=["get"], url_path="upcoming")
    def upcoming(self, request):
        """
        Action personnalisée : Récupérer les entretiens à venir.
        GET /api/recruitment/hiring-process/upcoming/
        """
        from django.utils import timezone
        
        queryset = self.get_queryset().filter(
            scheduled_date__gte=timezone.now()
        ).order_by("scheduled_date")
        
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

