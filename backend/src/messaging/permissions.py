"""
Permissions personnalisées pour le système de messagerie.

Sécurité robuste :
- Un utilisateur ne peut voir que ses propres conversations
- Un utilisateur ne peut envoyer des messages que dans ses conversations
- Les admins ont des droits étendus mais contrôlés
"""

from rest_framework import permissions
from messaging.models import Conversation, Message


class IsParticipantOrAdmin(permissions.BasePermission):
    """
    Permission pour les conversations.
    
    Règles :
    - L'utilisateur doit être un participant de la conversation
    - Les admins peuvent voir toutes les conversations
    - Les utilisateurs ne peuvent créer des conversations qu'avec eux-mêmes comme participant
    """
    
    def has_permission(self, request, view):
        """Vérifie la permission au niveau de la vue."""
        if not request.user or not request.user.is_authenticated:
            return False
        
        # Pour la création, vérifier que l'utilisateur est dans les participants
        if request.method == "POST":
            participants_ids = request.data.get("participants_ids", [])
            if isinstance(participants_ids, list) and request.user.id not in participants_ids:
                return False
        
        return True
    
    def has_object_permission(self, request, view, obj):
        """Vérifie la permission au niveau de l'objet."""
        # Les admins peuvent voir toutes les conversations (pour support/modération)
        if request.user.is_staff or request.user.is_superuser:
            return True
        
        # L'utilisateur doit être un participant
        if isinstance(obj, Conversation):
            return obj.participants.filter(id=request.user.id).exists()
        
        return False


class CanSendMessage(permissions.BasePermission):
    """
    Permission pour envoyer des messages.
    
    Règles :
    - L'utilisateur doit être un participant de la conversation
    - Les messages ne peuvent être envoyés que dans des conversations actives
    - Protection contre le spam (rate limiting à ajouter)
    """
    
    def has_permission(self, request, view):
        """Vérifie la permission au niveau de la vue."""
        if not request.user or not request.user.is_authenticated:
            return False
        
        # Pour la création, vérifier que l'utilisateur peut envoyer dans la conversation
        if request.method == "POST":
            conversation_id = request.data.get("conversation")
            if conversation_id:
                try:
                    conversation = Conversation.objects.get(pk=conversation_id)
                    
                    # Vérifier que la conversation n'est pas supprimée
                    if conversation.is_deleted:
                        return False
                    
                    # Vérifier que l'utilisateur est un participant
                    if request.user not in conversation.participants.all():
                        return False
                    
                except Conversation.DoesNotExist:
                    return False
        
        return True
    
    def has_object_permission(self, request, view, obj):
        """Vérifie la permission au niveau de l'objet."""
        # Les admins peuvent tout faire
        if request.user.is_staff or request.user.is_superuser:
            return True
        
        # L'utilisateur peut voir ses propres messages
        if isinstance(obj, Message):
            # L'expéditeur ou le destinataire peut voir le message
            if obj.sender == request.user:
                return True
            if obj.recipient == request.user:
                return True
            
            # Vérifier si l'utilisateur est dans la conversation
            if request.user in obj.conversation.participants.all():
                # Lecture seulement (pas de modification/suppression)
                if request.method in permissions.SAFE_METHODS:
                    return True
            
            return False
        
        return False


class CanModifyMessage(permissions.BasePermission):
    """
    Permission pour modifier/supprimer des messages.
    
    Règles :
    - Seul l'expéditeur peut modifier/supprimer son message
    - Les admins peuvent supprimer n'importe quel message (modération)
    """
    
    def has_object_permission(self, request, view, obj):
        """Vérifie la permission au niveau de l'objet."""
        if not request.user or not request.user.is_authenticated:
            return False
        
        # Les admins peuvent tout faire
        if request.user.is_staff or request.user.is_superuser:
            return True
        
        # Seul l'expéditeur peut modifier/supprimer
        if isinstance(obj, Message):
            return obj.sender == request.user
        
        return False

