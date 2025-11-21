"""
ViewSet pour la gestion des tickets de support (SupportTicket).

Ce ViewSet implémente les opérations CRUD complètes pour les tickets :
- Liste, détail, création, modification, suppression
- Actions personnalisées : assigner, résoudre, fermer, statistiques
- Permissions : utilisateurs peuvent créer/voir leurs tickets, admins peuvent tout faire
"""

from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from django.utils import timezone
from django.db.models import Count, Q

from support.models import SupportTicket
from support.serializers.support_ticket_serializer import (
    SupportTicketSerializer,
    SupportTicketListSerializer,
)


class IsOwnerOrAdmin(permissions.BasePermission):
    """
    Permission personnalisée :
    - Les admins peuvent tout faire
    - Les utilisateurs peuvent voir/modifier leurs propres tickets
    - Les utilisateurs assignés peuvent voir/modifier les tickets assignés
    """

    def has_permission(self, request, view):
        """Vérifie la permission au niveau de la vue."""
        return request.user and request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        """Vérifie la permission au niveau de l'objet."""
        # Les admins peuvent tout faire
        if request.user.is_staff or request.user.is_superuser:
            return True
        
        # Les utilisateurs peuvent voir/modifier leurs propres tickets
        if obj.created_by == request.user:
            return True
        
        # Les utilisateurs assignés peuvent voir les tickets
        if obj.assigned_to == request.user:
            return True
        
        return False


class SupportTicketViewSet(viewsets.ModelViewSet):
    """
    ViewSet pour les tickets de support.
    
    Endpoints disponibles :
    - GET /api/support/support-tickets/ : Liste des tickets
    - POST /api/support/support-tickets/ : Créer un ticket
    - GET /api/support/support-tickets/{id}/ : Détails d'un ticket
    - PUT/PATCH /api/support/support-tickets/{id}/ : Modifier un ticket
    - DELETE /api/support/support-tickets/{id}/ : Supprimer un ticket (admin seulement)
    - POST /api/support/support-tickets/{id}/assign/ : Assigner un ticket
    - POST /api/support/support-tickets/{id}/resolve/ : Résoudre un ticket
    - POST /api/support/support-tickets/{id}/close/ : Fermer un ticket
    - POST /api/support/support-tickets/{id}/reopen/ : Rouvrir un ticket
    - GET /api/support/support-tickets/my-tickets/ : Mes tickets
    - GET /api/support/support-tickets/assigned-to-me/ : Tickets assignés à moi
    - GET /api/support/support-tickets/open/ : Tickets ouverts
    - GET /api/support/support-tickets/statistics/ : Statistiques
    """
    
    queryset = SupportTicket.objects.select_related(
        "created_by", "assigned_to", "category"
    ).prefetch_related("comments").all()
    serializer_class = SupportTicketSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrAdmin]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ["status", "priority", "category", "created_by", "assigned_to"]
    search_fields = ["title", "description"]
    ordering_fields = ["created_at", "updated_at", "priority"]
    ordering = ["-created_at"]

    def get_serializer_class(self):
        """Utilise un serializer simplifié pour les listes."""
        if self.action == "list":
            return SupportTicketListSerializer
        return SupportTicketSerializer

    def get_queryset(self):
        """Filtre le queryset selon les permissions."""
        queryset = super().get_queryset()
        
        # Les admins voient tous les tickets
        if self.request.user.is_staff or self.request.user.is_superuser:
            return queryset
        
        # Les utilisateurs voient leurs propres tickets et ceux qui leur sont assignés
        return queryset.filter(
            Q(created_by=self.request.user) | Q(assigned_to=self.request.user)
        ).distinct()

    def perform_create(self, serializer):
        """Personnalise la création d'un ticket."""
        # Le créateur est l'utilisateur connecté
        serializer.save(created_by=self.request.user)

    @action(detail=True, methods=["post"], url_path="assign")
    def assign(self, request, pk=None):
        """Assigner un ticket à un utilisateur."""
        ticket = self.get_object()
        assigned_to_id = request.data.get("assigned_to_id")
        
        if not assigned_to_id:
            return Response(
                {"assigned_to_id": "Ce champ est requis."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        
        from users.models import CustomUser
        try:
            assigned_to = CustomUser.objects.get(pk=assigned_to_id)
        except CustomUser.DoesNotExist:
            return Response(
                {"assigned_to_id": "Utilisateur non trouvé."},
                status=status.HTTP_404_NOT_FOUND,
            )
        
        ticket.assigned_to = assigned_to
        ticket.save()
        
        serializer = self.get_serializer(ticket)
        return Response(serializer.data)

    @action(detail=True, methods=["post"], url_path="resolve")
    def resolve(self, request, pk=None):
        """Résoudre un ticket."""
        ticket = self.get_object()
        resolution = request.data.get("resolution", "")
        
        ticket.status = "resolved"
        ticket.resolution = resolution
        ticket.resolved_at = timezone.now()
        ticket.save()
        
        serializer = self.get_serializer(ticket)
        return Response(serializer.data)

    @action(detail=True, methods=["post"], url_path="close")
    def close(self, request, pk=None):
        """Fermer un ticket."""
        ticket = self.get_object()
        satisfaction_rating = request.data.get("satisfaction_rating")
        satisfaction_feedback = request.data.get("satisfaction_feedback", "")
        
        ticket.status = "closed"
        ticket.closed_at = timezone.now()
        if satisfaction_rating:
            ticket.satisfaction_rating = satisfaction_rating
        if satisfaction_feedback:
            ticket.satisfaction_feedback = satisfaction_feedback
        ticket.save()
        
        serializer = self.get_serializer(ticket)
        return Response(serializer.data)

    @action(detail=True, methods=["post"], url_path="reopen")
    def reopen(self, request, pk=None):
        """Rouvrir un ticket."""
        ticket = self.get_object()
        ticket.status = "open"
        ticket.resolved_at = None
        ticket.closed_at = None
        ticket.save()
        
        serializer = self.get_serializer(ticket)
        return Response(serializer.data)

    @action(detail=False, methods=["get"], url_path="my-tickets")
    def my_tickets(self, request):
        """Récupère les tickets créés par l'utilisateur connecté."""
        tickets = self.get_queryset().filter(created_by=request.user)
        
        page = self.paginate_queryset(tickets)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(tickets, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=["get"], url_path="assigned-to-me")
    def assigned_to_me(self, request):
        """Récupère les tickets assignés à l'utilisateur connecté."""
        tickets = self.get_queryset().filter(assigned_to=request.user)
        
        page = self.paginate_queryset(tickets)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(tickets, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=["get"], url_path="open")
    def open_tickets(self, request):
        """Récupère uniquement les tickets ouverts."""
        tickets = self.get_queryset().filter(
            status__in=["open", "in_progress", "waiting"]
        )
        
        page = self.paginate_queryset(tickets)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(tickets, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=["get"], url_path="statistics")
    def statistics(self, request):
        """Statistiques sur les tickets."""
        queryset = self.get_queryset()
        
        stats = {
            "total": queryset.count(),
            "by_status": queryset.values("status")
            .annotate(count=Count("id"))
            .order_by("-count"),
            "by_priority": queryset.values("priority")
            .annotate(count=Count("id"))
            .order_by("-count"),
            "by_category": queryset.values("category__name")
            .annotate(count=Count("id"))
            .order_by("-count"),
            "open": queryset.filter(status__in=["open", "in_progress", "waiting"]).count(),
            "resolved": queryset.filter(status="resolved").count(),
            "closed": queryset.filter(status="closed").count(),
            "average_resolution_time_days": None,  # À implémenter avec calcul
        }
        
        return Response(stats)

