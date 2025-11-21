"""
ViewSet pour la gestion des pièces jointes de tickets (TicketAttachment).

Ce ViewSet implémente les opérations CRUD complètes pour les pièces jointes :
- Liste, détail, création, suppression (pas de modification)
- Actions personnalisées : pièces jointes d'un ticket
- Permissions : utilisateurs peuvent voir les pièces jointes de leurs tickets
"""

from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from django.db.models import Q

from support.models import TicketAttachment
from support.serializers.ticket_attachment_serializer import (
    TicketAttachmentSerializer,
)


class IsOwnerOrAdmin(permissions.BasePermission):
    """
    Permission personnalisée :
    - Les admins peuvent tout faire
    - Les utilisateurs peuvent voir les pièces jointes de leurs tickets
    - Les utilisateurs peuvent supprimer leurs propres pièces jointes
    """

    def has_permission(self, request, view):
        """Vérifie la permission au niveau de la vue."""
        return request.user and request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        """Vérifie la permission au niveau de l'objet."""
        # Les admins peuvent tout faire
        if request.user.is_staff or request.user.is_superuser:
            return True
        
        # Les utilisateurs peuvent voir les pièces jointes de leurs tickets
        if request.method in permissions.SAFE_METHODS:
            if obj.ticket:
                return (
                    obj.ticket.created_by == request.user
                    or obj.ticket.assigned_to == request.user
                )
            elif obj.comment:
                return (
                    obj.comment.ticket.created_by == request.user
                    or obj.comment.ticket.assigned_to == request.user
                )
        
        # Les utilisateurs peuvent supprimer leurs propres pièces jointes
        if request.method == "DELETE":
            return obj.uploaded_by == request.user
        
        return False


class TicketAttachmentViewSet(viewsets.ModelViewSet):
    """
    ViewSet pour les pièces jointes de tickets.
    
    Endpoints disponibles :
    - GET /api/support/ticket-attachments/ : Liste des pièces jointes
    - POST /api/support/ticket-attachments/ : Uploader une pièce jointe
    - GET /api/support/ticket-attachments/{id}/ : Détails d'une pièce jointe
    - DELETE /api/support/ticket-attachments/{id}/ : Supprimer une pièce jointe
    - GET /api/support/ticket-attachments/by-ticket/{ticket_id}/ : Pièces jointes d'un ticket
    """
    
    queryset = TicketAttachment.objects.select_related(
        "ticket", "comment", "uploaded_by"
    ).all()
    serializer_class = TicketAttachmentSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrAdmin]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ["ticket", "comment", "uploaded_by"]
    search_fields = ["filename"]
    ordering_fields = ["created_at"]
    ordering = ["-created_at"]
    http_method_names = ["get", "post", "delete", "head", "options"]  # Pas de PUT/PATCH

    def get_queryset(self):
        """Filtre le queryset selon les permissions."""
        queryset = super().get_queryset()
        
        # Les admins voient toutes les pièces jointes
        if self.request.user.is_staff or self.request.user.is_superuser:
            return queryset
        
        # Les utilisateurs voient les pièces jointes de leurs tickets
        return queryset.filter(
            Q(ticket__created_by=self.request.user)
            | Q(ticket__assigned_to=self.request.user)
            | Q(comment__ticket__created_by=self.request.user)
            | Q(comment__ticket__assigned_to=self.request.user)
        ).distinct()

    @action(detail=False, methods=["get"], url_path="by-ticket/(?P<ticket_id>[^/.]+)")
    def by_ticket(self, request, ticket_id=None):
        """Récupère les pièces jointes d'un ticket spécifique."""
        try:
            from support.models import SupportTicket
            ticket = SupportTicket.objects.get(pk=ticket_id)
        except SupportTicket.DoesNotExist:
            return Response(
                {"detail": "Ticket non trouvé."},
                status=status.HTTP_404_NOT_FOUND,
            )
        
        # Vérifier les permissions
        if not (request.user.is_staff or ticket.created_by == request.user or ticket.assigned_to == request.user):
            return Response(
                {"detail": "Vous n'avez pas la permission de voir ce ticket."},
                status=status.HTTP_403_FORBIDDEN,
            )
        
        attachments = self.get_queryset().filter(
            Q(ticket=ticket) | Q(comment__ticket=ticket)
        ).distinct()
        
        page = self.paginate_queryset(attachments)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(attachments, many=True)
        return Response(serializer.data)

