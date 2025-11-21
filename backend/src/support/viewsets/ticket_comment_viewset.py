"""
ViewSet pour la gestion des commentaires de tickets (TicketComment).

Ce ViewSet implémente les opérations CRUD complètes pour les commentaires :
- Liste, détail, création, modification, suppression
- Actions personnalisées : commentaires d'un ticket
- Permissions : utilisateurs peuvent voir les commentaires non-internes, admins peuvent tout voir
"""

from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter

from support.models import TicketComment
from support.serializers.ticket_comment_serializer import TicketCommentSerializer


class IsOwnerOrAdmin(permissions.BasePermission):
    """
    Permission personnalisée :
    - Les admins peuvent tout faire
    - Les utilisateurs peuvent voir les commentaires non-internes de leurs tickets
    - Les utilisateurs peuvent créer/modifier leurs propres commentaires
    """

    def has_permission(self, request, view):
        """Vérifie la permission au niveau de la vue."""
        return request.user and request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        """Vérifie la permission au niveau de l'objet."""
        # Les admins peuvent tout faire
        if request.user.is_staff or request.user.is_superuser:
            return True
        
        # Les utilisateurs peuvent modifier leurs propres commentaires
        if obj.author == request.user:
            if request.method in ["PUT", "PATCH", "DELETE"]:
                return True
        
        # Les utilisateurs peuvent voir les commentaires non-internes de leurs tickets
        if request.method in permissions.SAFE_METHODS:
            if not obj.is_internal:
                # Si le commentaire n'est pas interne, tout le monde peut le voir
                return True
            # Si le commentaire est interne, seuls les admins et ceux assignés au ticket
            return (
                obj.ticket.assigned_to == request.user
                or obj.ticket.created_by == request.user
            )
        
        return False


class TicketCommentViewSet(viewsets.ModelViewSet):
    """
    ViewSet pour les commentaires de tickets.
    
    Endpoints disponibles :
    - GET /api/support/ticket-comments/ : Liste des commentaires
    - POST /api/support/ticket-comments/ : Créer un commentaire
    - GET /api/support/ticket-comments/{id}/ : Détails d'un commentaire
    - PUT/PATCH /api/support/ticket-comments/{id}/ : Modifier un commentaire
    - DELETE /api/support/ticket-comments/{id}/ : Supprimer un commentaire
    - GET /api/support/ticket-comments/by-ticket/{ticket_id}/ : Commentaires d'un ticket
    """
    
    queryset = TicketComment.objects.select_related(
        "ticket", "author"
    ).all()
    serializer_class = TicketCommentSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrAdmin]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ["ticket", "author", "is_internal"]
    search_fields = ["content"]
    ordering_fields = ["created_at"]
    ordering = ["created_at"]

    def get_queryset(self):
        """Filtre le queryset selon les permissions."""
        queryset = super().get_queryset()
        
        # Les admins voient tous les commentaires
        if self.request.user.is_staff or self.request.user.is_superuser:
            return queryset
        
        # Les utilisateurs voient les commentaires non-internes et ceux de leurs tickets
        return queryset.filter(
            Q(is_internal=False)
            | Q(ticket__created_by=self.request.user)
            | Q(ticket__assigned_to=self.request.user)
        ).distinct()

    def perform_create(self, serializer):
        """Personnalise la création d'un commentaire."""
        # L'auteur est l'utilisateur connecté
        serializer.save(author=self.request.user)

    @action(detail=False, methods=["get"], url_path="by-ticket/(?P<ticket_id>[^/.]+)")
    def by_ticket(self, request, ticket_id=None):
        """Récupère les commentaires d'un ticket spécifique."""
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
        
        comments = self.get_queryset().filter(ticket=ticket)
        
        # Filtrer les commentaires internes pour les non-admins
        if not request.user.is_staff:
            comments = comments.filter(
                Q(is_internal=False)
                | Q(ticket__created_by=request.user)
                | Q(ticket__assigned_to=request.user)
            ).distinct()
        
        page = self.paginate_queryset(comments)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(comments, many=True)
        return Response(serializer.data)

