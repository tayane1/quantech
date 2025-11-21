"""
ViewSet pour la gestion des messages.

Sécurité robuste :
- Filtrage strict (uniquement les messages de l'utilisateur)
- Validation stricte du contenu
- Protection contre le spam
- Rate limiting (à implémenter)
"""

from rest_framework import viewsets, permissions, status, serializers
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from django.utils import timezone
from django.db.models import Q

from messages.models import Message, Conversation, MessageReadStatus
from messages.serializers import (
    MessageSerializer,
    MessageListSerializer,
    MessageCreateSerializer,
)
from messages.permissions import CanSendMessage, CanModifyMessage


class MessageViewSet(viewsets.ModelViewSet):
    """
    ViewSet pour les messages.
    
    Endpoints disponibles :
    - GET /api/messages/conversations/{conversation_id}/messages/ : Liste des messages d'une conversation
    - POST /api/messages/conversations/{conversation_id}/messages/ : Envoyer un message
    - GET /api/messages/messages/{id}/ : Détails d'un message
    - PATCH /api/messages/messages/{id}/ : Modifier un message (seulement son propre message)
    - DELETE /api/messages/messages/{id}/ : Supprimer un message (soft delete)
    - POST /api/messages/messages/{id}/mark-read/ : Marquer comme lu
    """
    
    queryset = Message.objects.filter(is_deleted=False).select_related(
        "sender",
        "recipient",
        "conversation"
    ).order_by("created_at")
    
    permission_classes = [permissions.IsAuthenticated, CanSendMessage, CanModifyMessage]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ["conversation", "sender", "recipient", "is_read"]
    search_fields = ["content"]
    ordering_fields = ["created_at"]
    ordering = ["created_at"]
    
    def get_serializer_class(self):
        """Utilise un serializer différent selon l'action."""
        if self.action == "list":
            return MessageListSerializer
        if self.action == "create":
            return MessageCreateSerializer
        return MessageSerializer
    
    def get_queryset(self):
        """
        Filtre strictement les messages.
        
        Sécurité :
        - Un utilisateur ne voit que les messages de ses conversations
        - Les admins voient tous les messages (pour modération)
        """
        queryset = super().get_queryset()
        
        # Filtrer par conversation si fourni dans l'URL
        conversation_id = self.kwargs.get("conversation_id")
        if conversation_id:
            queryset = queryset.filter(conversation_id=conversation_id)
        
        # Les admins voient tout
        if self.request.user.is_staff or self.request.user.is_superuser:
            return queryset
        
        # Les utilisateurs ne voient que les messages de leurs conversations
        return queryset.filter(
            Q(conversation__participants=self.request.user) |
            Q(sender=self.request.user) |
            Q(recipient=self.request.user)
        ).distinct()
    
    def perform_create(self, serializer):
        """Créer un message avec validation et sécurité."""
        # Validation du rate limiting (à implémenter plus en détail)
        # Vérifier le nombre de messages envoyés récemment
        recent_messages_count = Message.objects.filter(
            sender=self.request.user,
            created_at__gte=timezone.now() - timezone.timedelta(minutes=1)
        ).count()
        
        if recent_messages_count > 20:  # Limite de 20 messages par minute
            raise serializers.ValidationError(
                "Trop de messages envoyés récemment. Veuillez patienter."
            )
        
        # Le serializer définit déjà le sender
        serializer.save(sender=self.request.user)
    
    @action(detail=True, methods=["post"], url_path="mark-read")
    def mark_read(self, request, pk=None):
        """
        Action personnalisée : Marquer un message comme lu.
        POST /api/messages/messages/{id}/mark-read/
        """
        message = self.get_object()
        
        # Vérifier que l'utilisateur est le destinataire
        if message.recipient != request.user:
            return Response(
                {"detail": "Vous n'êtes pas autorisé à marquer ce message comme lu."},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Marquer comme lu
        message.mark_as_read()
        
        # Mettre à jour le statut de lecture
        MessageReadStatus.objects.update_or_create(
            message=message,
            user=request.user,
            defaults={"is_read": True, "read_at": timezone.now()}
        )
        
        serializer = self.get_serializer(message)
        return Response(serializer.data)
    
    def destroy(self, request, *args, **kwargs):
        """
        Soft delete : marquer comme supprimé au lieu de supprimer réellement.
        """
        message = self.get_object()
        message.is_deleted = True
        message.deleted_at = timezone.now()
        message.save(update_fields=["is_deleted", "deleted_at", "updated_at"])
        
        return Response(status=status.HTTP_204_NO_CONTENT)
    
    def get_permissions(self):
        """
        Instanciation des permissions selon l'action.
        
        Sécurité :
        - CREATE : Vérifie que l'utilisateur peut envoyer
        - UPDATE/DELETE : Vérifie que l'utilisateur peut modifier
        - READ : Vérifie que l'utilisateur peut voir
        """
        if self.action in ["create"]:
            permission_classes = [permissions.IsAuthenticated, CanSendMessage]
        elif self.action in ["update", "partial_update", "destroy"]:
            permission_classes = [permissions.IsAuthenticated, CanModifyMessage]
        else:
            permission_classes = [permissions.IsAuthenticated, CanSendMessage]
        
        return [permission() for permission in permission_classes]

