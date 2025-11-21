"""
Serializer pour les messages.

Validation stricte et sécurité renforcée :
- Validation du contenu
- Protection contre les messages vides
- Vérification des permissions
- Limitation de la longueur
"""

from rest_framework import serializers
from django.utils import timezone
from django.core.exceptions import ValidationError
from messaging.models import Message, Conversation, MessageReadStatus
from users.models import CustomUser


class MessageSerializer(serializers.ModelSerializer):
    """
    Serializer complet pour un message.
    
    Inclut :
    - Tous les détails du message
    - Informations de l'expéditeur et destinataire
    - Statut de lecture
    """
    
    sender_name = serializers.CharField(source="sender.get_full_name", read_only=True)
    sender_email = serializers.EmailField(source="sender.email", read_only=True)
    sender_avatar = serializers.SerializerMethodField()
    recipient_name = serializers.SerializerMethodField()
    conversation_subject = serializers.CharField(source="conversation.subject", read_only=True)
    
    class Meta:
        model = Message
        fields = [
            "id",
            "conversation",
            "conversation_subject",
            "sender",
            "sender_name",
            "sender_email",
            "sender_avatar",
            "recipient",
            "recipient_name",
            "content",
            "attachment",
            "is_read",
            "read_at",
            "is_deleted",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "sender",
            "is_read",
            "read_at",
            "is_deleted",
            "created_at",
            "updated_at",
        ]
    
    def get_sender_avatar(self, obj):
        """Retourne l'avatar de l'expéditeur."""
        if obj.sender.profile_picture:
            request = self.context.get("request")
            if request:
                return request.build_absolute_uri(obj.sender.profile_picture.url)
            return obj.sender.profile_picture.url
        return None
    
    def get_recipient_name(self, obj):
        """Retourne le nom du destinataire."""
        if obj.recipient:
            return obj.recipient.get_full_name() or obj.recipient.username
        return None


class MessageListSerializer(serializers.ModelSerializer):
    """
    Serializer simplifié pour la liste des messages.
    
    Utilisé pour améliorer les performances.
    """
    
    sender_name = serializers.CharField(source="sender.get_full_name", read_only=True)
    sender_avatar = serializers.SerializerMethodField()
    
    class Meta:
        model = Message
        fields = [
            "id",
            "sender",
            "sender_name",
            "sender_avatar",
            "recipient",
            "content",
            "is_read",
            "read_at",
            "created_at",
        ]
    
    def get_sender_avatar(self, obj):
        """Retourne l'avatar de l'expéditeur."""
        if obj.sender.profile_picture:
            request = self.context.get("request")
            if request:
                return request.build_absolute_uri(obj.sender.profile_picture.url)
            return obj.sender.profile_picture.url
        return None


class MessageCreateSerializer(serializers.ModelSerializer):
    """
    Serializer pour la création d'un message.
    
    Validation stricte :
    - Contenu non vide
    - Longueur limitée
    - Vérification des permissions
    """
    
    class Meta:
        model = Message
        fields = [
            "conversation",
            "recipient",
            "content",
            "attachment",
        ]
    
    def validate_content(self, value):
        """Validation stricte du contenu."""
        if not value or not value.strip():
            raise serializers.ValidationError("Le message ne peut pas être vide.")
        
        content_stripped = value.strip()
        if len(content_stripped) < 1:
            raise serializers.ValidationError("Le message doit contenir au moins 1 caractère.")
        
        if len(value) > 5000:
            raise serializers.ValidationError("Le message ne peut pas dépasser 5000 caractères.")
        
        # Protection contre les contenus suspects
        suspicious_patterns = ["<script", "javascript:", "onerror=", "onclick="]
        content_lower = value.lower()
        for pattern in suspicious_patterns:
            if pattern in content_lower:
                raise serializers.ValidationError("Le contenu du message contient des éléments non autorisés.")
        
        return value
    
    def validate_conversation(self, value):
        """Validation de la conversation."""
        if value.is_deleted:
            raise serializers.ValidationError("Cette conversation a été supprimée.")
        
        # Vérifier que l'utilisateur connecté est un participant
        request = self.context.get("request")
        if request and request.user:
            if request.user not in value.participants.all():
                raise serializers.ValidationError("Vous n'êtes pas autorisé à envoyer un message dans cette conversation.")
        
        return value
    
    def validate_recipient(self, value):
        """Validation du destinataire."""
        conversation = self.initial_data.get("conversation")
        if conversation:
            # Convertir l'ID en objet si nécessaire
            if isinstance(conversation, int):
                try:
                    conversation_obj = Conversation.objects.get(pk=conversation)
                except Conversation.DoesNotExist:
                    raise serializers.ValidationError("La conversation spécifiée n'existe pas.")
            else:
                conversation_obj = conversation
            
            # Pour les conversations directes, vérifier le destinataire
            if conversation_obj.conversation_type == "direct":
                if not value:
                    raise serializers.ValidationError("Un message direct doit avoir un destinataire.")
                
                request = self.context.get("request")
                if request and request.user:
                    if value == request.user:
                        raise serializers.ValidationError("Vous ne pouvez pas vous envoyer un message à vous-même.")
                
                if value not in conversation_obj.participants.all():
                    raise serializers.ValidationError("Le destinataire doit être un participant de la conversation.")
        
        return value
    
    def validate(self, data):
        """Validation globale."""
        conversation = data.get("conversation")
        recipient = data.get("recipient")
        
        if conversation and conversation.conversation_type == "direct":
            if not recipient:
                raise serializers.ValidationError({
                    "recipient": "Un message dans une conversation directe doit avoir un destinataire."
                })
        
        return data
    
    def create(self, validated_data):
        """Créer un message avec validation et sécurité."""
        request = self.context.get("request")
        
        # Définir automatiquement l'expéditeur
        message = Message.objects.create(
            sender=request.user if request else None,
            **validated_data
        )
        
        # Validation finale
        try:
            message.full_clean()
        except ValidationError as e:
            message.delete()
            raise serializers.ValidationError(str(e))
        
        # Créer le statut de lecture pour les autres participants
        conversation = message.conversation
        for participant in conversation.participants.all():
            if participant != request.user:
                MessageReadStatus.objects.get_or_create(
                    message=message,
                    user=participant,
                    defaults={"is_read": False}
                )
            else:
                # L'expéditeur a déjà lu son propre message
                MessageReadStatus.objects.get_or_create(
                    message=message,
                    user=participant,
                    defaults={"is_read": True, "read_at": timezone.now()}
                )
        
        return message

