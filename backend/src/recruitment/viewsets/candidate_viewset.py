"""
ViewSet pour la gestion des candidats (Candidate).

Ce ViewSet implémente les opérations CRUD complètes pour les candidats :
- Liste, détail, création, modification, suppression
- Actions personnalisées : changer le statut, candidats par offre, candidats actifs
- Permissions : tous les utilisateurs authentifiés peuvent voir, seuls les admins/HR peuvent modifier
"""

from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter

from recruitment.models.candidate import Candidate
from recruitment.serializers.candidate_serializer import CandidateSerializer


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
            and (request.user.is_staff or request.user.role in ["admin", "hr_manager", "recruiter"])
        )


class CandidateViewSet(viewsets.ModelViewSet):
    """
    ViewSet pour les candidats.
    
    Endpoints disponibles :
    - GET /api/recruitment/candidates/ : Liste des candidats
    - POST /api/recruitment/candidates/ : Créer un candidat
    - GET /api/recruitment/candidates/{id}/ : Détails d'un candidat
    - PUT/PATCH /api/recruitment/candidates/{id}/ : Modifier un candidat
    - DELETE /api/recruitment/candidates/{id}/ : Supprimer un candidat
    - POST /api/recruitment/candidates/{id}/change-status/ : Changer le statut
    - GET /api/recruitment/candidates/by-position/{position_id}/ : Candidats par offre
    - GET /api/recruitment/candidates/active/ : Candidats actifs
    """
    
    serializer_class = CandidateSerializer
    permission_classes = [permissions.IsAuthenticated, IsHRManagerOrAdmin]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ["status", "position"]
    search_fields = ["first_name", "last_name", "email", "phone"]
    ordering_fields = ["applied_date", "updated_at", "first_name", "last_name"]
    ordering = ["-applied_date"]

    def get_queryset(self):
        """Retourne tous les candidats avec relations optimisées."""
        return Candidate.objects.select_related(
            "position", "position__department"
        ).prefetch_related("hiring_process").all()

    @action(detail=True, methods=["post"], url_path="change-status")
    def change_status(self, request, pk=None):
        """
        Action personnalisée : Changer le statut d'un candidat.
        POST /api/recruitment/candidates/{id}/change-status/
        Body: {"status": "interview", "notes": "Passage à l'entretien"}
        """
        candidate = self.get_object()
        new_status = request.data.get("status")
        notes = request.data.get("notes", "")

        if not new_status:
            return Response(
                {"detail": "Le statut est requis."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Valider le statut
        valid_statuses = [choice[0] for choice in Candidate.STATUS_CHOICES]
        if new_status not in valid_statuses:
            return Response(
                {"detail": f"Statut invalide. Statuts valides : {valid_statuses}"},
                status=status.HTTP_400_BAD_REQUEST
            )

        candidate.status = new_status
        if notes:
            candidate.notes = f"{candidate.notes}\n{notes}" if candidate.notes else notes
        candidate.save()

        serializer = self.get_serializer(candidate)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=False, methods=["get"], url_path="by-position/(?P<position_id>[^/.]+)")
    def by_position(self, request, position_id=None):
        """
        Action personnalisée : Récupérer les candidats pour une offre spécifique.
        GET /api/recruitment/candidates/by-position/{position_id}/
        """
        queryset = self.get_queryset().filter(position_id=position_id)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=["get"], url_path="active")
    def active(self, request):
        """
        Action personnalisée : Récupérer uniquement les candidats actifs.
        GET /api/recruitment/candidates/active/
        """
        queryset = self.get_queryset().exclude(
            status__in=[Candidate.STATUS_REJECTED, Candidate.STATUS_HIRED]
        )
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

