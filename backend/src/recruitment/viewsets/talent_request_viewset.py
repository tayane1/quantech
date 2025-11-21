"""
ViewSet pour la gestion des demandes de talents (TalentRequest).

Ce ViewSet implémente les opérations CRUD complètes pour les demandes de talents :
- Liste, détail, création, modification, suppression
- Actions personnalisées : approuver, rejeter, marquer comme satisfait, demandes en attente
- Permissions : tous les utilisateurs authentifiés peuvent créer, seuls les admins/HR peuvent approuver
"""

from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter

from recruitment.models.talent_request import TalentRequest
from recruitment.serializers.talent_request_serializer import TalentRequestSerializer


class IsHRManagerOrAdmin(permissions.BasePermission):
    """
    Permission personnalisée :
    - Les admins et HR managers peuvent tout faire
    - Les autres utilisateurs peuvent créer et voir leurs propres demandes
    """

    def has_object_permission(self, request, view, obj):
        # Admins et HR peuvent tout faire
        if request.user.is_staff or request.user.role in ["admin", "hr_manager"]:
            return True
        
        # Les utilisateurs peuvent voir/modifier leurs propres demandes
        if hasattr(request.user, "employee") and obj.requested_by == request.user.employee:
            return request.method in permissions.SAFE_METHODS or request.method == "PATCH"
        
        return False

    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated


class TalentRequestViewSet(viewsets.ModelViewSet):
    """
    ViewSet pour les demandes de talents.
    
    Endpoints disponibles :
    - GET /api/recruitment/talent-requests/ : Liste des demandes
    - POST /api/recruitment/talent-requests/ : Créer une demande
    - GET /api/recruitment/talent-requests/{id}/ : Détails d'une demande
    - PUT/PATCH /api/recruitment/talent-requests/{id}/ : Modifier une demande
    - DELETE /api/recruitment/talent-requests/{id}/ : Supprimer une demande
    - POST /api/recruitment/talent-requests/{id}/approve/ : Approuver une demande
    - POST /api/recruitment/talent-requests/{id}/reject/ : Rejeter une demande
    - POST /api/recruitment/talent-requests/{id}/fulfill/ : Marquer comme satisfait
    - GET /api/recruitment/talent-requests/pending/ : Demandes en attente
    """
    
    serializer_class = TalentRequestSerializer
    permission_classes = [permissions.IsAuthenticated, IsHRManagerOrAdmin]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ["status", "position", "requested_by"]
    search_fields = ["description", "position__title"]
    ordering_fields = ["created_at", "updated_at"]
    ordering = ["-created_at"]

    def get_queryset(self):
        """Filtre le queryset selon les permissions."""
        queryset = TalentRequest.objects.select_related(
            "position", "position__department", "requested_by"
        ).all()
        
        # Si admin/HR, retourner tout
        if self.request.user.is_staff or self.request.user.role in ["admin", "hr_manager"]:
            return queryset
        
        # Sinon, filtrer par demandeur
        if hasattr(self.request.user, "employee"):
            return queryset.filter(requested_by=self.request.user.employee)
        
        return queryset.none()

    def perform_create(self, serializer):
        """Lors de la création, définir automatiquement le demandeur."""
        if not serializer.validated_data.get("requested_by") and hasattr(
            self.request.user, "employee"
        ):
            serializer.save(requested_by=self.request.user.employee)
        else:
            serializer.save()

    @action(detail=True, methods=["post"], url_path="approve")
    def approve(self, request, pk=None):
        """
        Action personnalisée : Approuver une demande de talent.
        POST /api/recruitment/talent-requests/{id}/approve/
        """
        if not (request.user.is_staff or request.user.role in ["admin", "hr_manager"]):
            return Response(
                {"detail": "Vous n'avez pas la permission d'approuver des demandes."},
                status=status.HTTP_403_FORBIDDEN
            )
        
        talent_request = self.get_object()
        talent_request.status = TalentRequest.STATUS_APPROVED
        talent_request.save()
        
        serializer = self.get_serializer(talent_request)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=True, methods=["post"], url_path="reject")
    def reject(self, request, pk=None):
        """
        Action personnalisée : Rejeter une demande de talent.
        POST /api/recruitment/talent-requests/{id}/reject/
        """
        if not (request.user.is_staff or request.user.role in ["admin", "hr_manager"]):
            return Response(
                {"detail": "Vous n'avez pas la permission de rejeter des demandes."},
                status=status.HTTP_403_FORBIDDEN
            )
        
        talent_request = self.get_object()
        talent_request.status = TalentRequest.STATUS_REJECTED
        talent_request.save()
        
        serializer = self.get_serializer(talent_request)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=True, methods=["post"], url_path="fulfill")
    def fulfill(self, request, pk=None):
        """
        Action personnalisée : Marquer une demande comme satisfaite.
        POST /api/recruitment/talent-requests/{id}/fulfill/
        """
        if not (request.user.is_staff or request.user.role in ["admin", "hr_manager"]):
            return Response(
                {"detail": "Vous n'avez pas la permission de marquer comme satisfait."},
                status=status.HTTP_403_FORBIDDEN
            )
        
        talent_request = self.get_object()
        talent_request.status = TalentRequest.STATUS_FULFILLED
        talent_request.save()
        
        serializer = self.get_serializer(talent_request)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=False, methods=["get"], url_path="pending")
    def pending(self, request):
        """
        Action personnalisée : Récupérer les demandes en attente.
        GET /api/recruitment/talent-requests/pending/
        """
        queryset = self.get_queryset().filter(status=TalentRequest.STATUS_PENDING)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

