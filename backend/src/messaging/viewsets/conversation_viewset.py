"""
ViewSet pour la gestion des conversations.

Sécurité robuste :
- Filtrage strict des conversations (uniquement celles de l'utilisateur)
- Validation stricte des participants
- Protection contre les conversations vides
- Rate limiting (à implémenter)
"""

from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from django.utils import timezone
from django.db.models import Q, Count, Max

from messaging.models import Conversation, Message, MessageReadStatus
from users.models import CustomUser
from messaging.serializers import (
    ConversationSerializer,
    ConversationListSerializer,
    ConversationCreateSerializer,
)
from messaging.permissions import IsParticipantOrAdmin


class ConversationViewSet(viewsets.ModelViewSet):
    """
    ViewSet pour les conversations.
    
    Endpoints disponibles :
    - GET /api/messages/conversations/ : Liste des conversations de l'utilisateur
    - POST /api/messages/conversations/ : Créer une conversation
    - GET /api/messages/conversations/{id}/ : Détails d'une conversation
    - PATCH /api/messages/conversations/{id}/ : Modifier une conversation
    - DELETE /api/messages/conversations/{id}/ : Supprimer une conversation (soft delete)
    - POST /api/messages/conversations/{id}/mark-read/ : Marquer comme lue
    - POST /api/messages/conversations/{id}/archive/ : Archiver une conversation
    - GET /api/messages/conversations/unread/ : Conversations non lues
    - GET /api/messages/conversations/with-user/{user_id}/ : Conversation avec un utilisateur spécifique
    """
    
    queryset = Conversation.objects.filter(is_deleted=False).prefetch_related(
        "participants",
        "messages"
    ).annotate(
        unread_count=Count("messages", filter=Q(messages__is_read=False))
    ).order_by("-last_message_at", "-created_at")
    
    permission_classes = [permissions.IsAuthenticated, IsParticipantOrAdmin]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ["conversation_type", "is_archived"]
    search_fields = ["subject"]
    ordering_fields = ["last_message_at", "created_at"]
    ordering = ["-last_message_at"]
    
    def get_serializer_class(self):
        """Utilise un serializer différent selon l'action."""
        if self.action == "list":
            return ConversationListSerializer
        if self.action == "create":
            return ConversationCreateSerializer
        return ConversationSerializer
    
    def get_queryset(self):
        """
        Filtre strictement les conversations.
        
        Sécurité :
        - Un utilisateur ne voit que ses propres conversations
        - Les admins voient toutes les conversations (pour modération)
        """
        queryset = super().get_queryset()
        
        # Les admins voient tout (pour modération)
        if self.request.user.is_staff or self.request.user.is_superuser:
            return queryset
        
        # Les utilisateurs ne voient que leurs conversations
        return queryset.filter(participants=self.request.user)
    
    def perform_create(self, serializer):
        """Créer une conversation avec validation stricte."""
        # Le serializer définit déjà created_by
        serializer.save(created_by=self.request.user)
    
    @action(detail=True, methods=["post"], url_path="mark-read")
    def mark_read(self, request, pk=None):
        """
        Action personnalisée : Marquer tous les messages comme lus.
        POST /api/messages/conversations/{id}/mark-read/
        """
        conversation = self.get_object()
        
        # Marquer tous les messages non lus comme lus
        conversation.mark_as_read_for_user(request.user)
        
        # Mettre à jour les statuts de lecture
        MessageReadStatus.objects.filter(
            message__conversation=conversation,
            user=request.user,
            is_read=False
        ).update(is_read=True, read_at=timezone.now())
        
        return Response({
            "message": "Conversation marquée comme lue.",
            "conversation_id": conversation.id
        })
    
    @action(detail=True, methods=["post"], url_path="archive")
    def archive(self, request, pk=None):
        """
        Action personnalisée : Archiver une conversation.
        POST /api/messages/conversations/{id}/archive/
        """
        conversation = self.get_object()
        conversation.is_archived = True
        conversation.save(update_fields=["is_archived", "updated_at"])
        
        serializer = self.get_serializer(conversation)
        return Response(serializer.data)
    
    @action(detail=True, methods=["post"], url_path="unarchive")
    def unarchive(self, request, pk=None):
        """
        Action personnalisée : Désarchiver une conversation.
        POST /api/messages/conversations/{id}/unarchive/
        """
        conversation = self.get_object()
        conversation.is_archived = False
        conversation.save(update_fields=["is_archived", "updated_at"])
        
        serializer = self.get_serializer(conversation)
        return Response(serializer.data)
    
    @action(detail=False, methods=["get"], url_path="unread")
    def unread(self, request):
        """
        Action personnalisée : Conversations avec messages non lus.
        GET /api/messages/conversations/unread/
        """
        queryset = self.get_queryset().annotate(
            unread_messages=Count(
                "messages",
                filter=Q(messages__is_read=False, messages__is_deleted=False) &
                       ~Q(messages__sender=request.user)
            )
        ).filter(unread_messages__gt=0)
        
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=["get"], url_path="with-user/(?P<user_id>[^/.]+)")
    def with_user(self, request, user_id=None):
        """
        Action personnalisée : Trouver ou créer une conversation directe avec un utilisateur.
        GET /api/messages/conversations/with-user/{user_id}/
        """
        try:
            other_user = CustomUser.objects.get(pk=user_id, is_active=True)
        except CustomUser.DoesNotExist:
            return Response(
                {"detail": "Utilisateur non trouvé."},
                status=status.HTTP_404_NOT_FOUND
            )
        
        if other_user == request.user:
            return Response(
                {"detail": "Vous ne pouvez pas créer une conversation avec vous-même."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Chercher une conversation directe existante
        conversation = Conversation.objects.filter(
            conversation_type="direct",
            participants=request.user
        ).filter(
            participants=other_user
        ).distinct().first()
        
        if not conversation:
            # Créer une nouvelle conversation directe
            conversation = Conversation.objects.create(
                conversation_type="direct",
                created_by=request.user
            )
            conversation.participants.add(request.user, other_user)
        
        serializer = self.get_serializer(conversation)
        return Response(serializer.data)
    
    def destroy(self, request, *args, **kwargs):
        """
        Soft delete : marquer comme supprimé au lieu de supprimer réellement.
        """
        conversation = self.get_object()
        conversation.is_deleted = True
        conversation.deleted_at = timezone.now()
        conversation.save(update_fields=["is_deleted", "deleted_at", "updated_at"])
        
        return Response(status=status.HTTP_204_NO_CONTENT)

