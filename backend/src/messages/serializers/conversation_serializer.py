"""
Serializer pour les conversations.

Valide strictement les données et assure la sécurité :
- Validation des participants
- Protection contre les conversations vides
- Vérification des permissions
"""

from rest_framework import serializers
from django.utils import timezone
from django.core.exceptions import ValidationError
from messages.models import Conversation, Message
from users.models import CustomUser


class ConversationSerializer(serializers.ModelSerializer):
    """
    Serializer complet pour une conversation.
    
    Inclut :
    - Tous les détails de la conversation
    - Liste des participants avec informations
    - Dernier message
    - Nombre de messages non lus pour l'utilisateur connecté
    """
    
    participants = serializers.SerializerMethodField()
    participants_ids = serializers.PrimaryKeyRelatedField(
        source="participants",
        many=True,
        queryset=CustomUser.objects.all(),
        write_only=True,
        required=True
    )
    participants_names = serializers.SerializerMethodField()
    participants_count = serializers.SerializerMethodField()
    last_message = serializers.SerializerMethodField()
    unread_count = serializers.SerializerMethodField()
    created_by_name = serializers.CharField(source="created_by.get_full_name", read_only=True)
    
    class Meta:
        model = Conversation
        fields = [
            "id",
            "participants",
            "participants_ids",
            "participants_names",
            "participants_count",
            "created_by",
            "created_by_name",
            "subject",
            "conversation_type",
            "is_archived",
            "is_deleted",
            "last_message",
            "unread_count",
            "last_message_at",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "created_by",
            "created_at",
            "updated_at",
            "last_message_at",
        ]
    
    def get_participants(self, obj):
        """Retourne les informations des participants."""
        return [
            {
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "full_name": user.get_full_name() or user.username,
                "profile_picture": user.profile_picture.url if user.profile_picture else None,
            }
            for user in obj.participants.all()
        ]
    
    def get_participants_names(self, obj):
        """Retourne les noms des participants."""
        return [user.get_full_name() or user.username for user in obj.participants.all()]
    
    def get_participants_count(self, obj):
        """Retourne le nombre de participants."""
        return obj.participants.count()
    
    def get_last_message(self, obj):
        """Retourne le dernier message de la conversation."""
        last_message = obj.messages.filter(is_deleted=False).last()
        if last_message:
            return {
                "id": last_message.id,
                "content": last_message.content[:100] + "..." if len(last_message.content) > 100 else last_message.content,
                "sender": last_message.sender.get_full_name() or last_message.sender.username,
                "sender_id": last_message.sender.id,
                "created_at": last_message.created_at,
            }
        return None
    
    def get_unread_count(self, obj):
        """Retourne le nombre de messages non lus pour l'utilisateur connecté."""
        request = self.context.get("request")
        if request and request.user:
            return obj.get_unread_count_for_user(request.user)
        return 0
    
    def validate_participants_ids(self, value):
        """Valide les participants."""
        if not value or len(value) < 2:
            raise serializers.ValidationError("Une conversation doit avoir au moins 2 participants.")
        
        # Vérifier que l'utilisateur connecté est dans les participants
        request = self.context.get("request")
        if request and request.user:
            if request.user not in value:
                raise serializers.ValidationError("Vous devez être un participant de la conversation.")
        
        # Vérifier qu'il n'y a pas de doublons
        if len(value) != len(set(value)):
            raise serializers.ValidationError("Les participants ne peuvent pas être dupliqués.")
        
        return value
    
    def validate_conversation_type(self, value):
        """Valide le type de conversation."""
        participants = self.initial_data.get("participants_ids", [])
        if value == "direct" and len(participants) != 2:
            raise serializers.ValidationError("Une conversation directe doit avoir exactement 2 participants.")
        
        return value
    
    def create(self, validated_data):
        """Créer une conversation avec validation stricte."""
        request = self.context.get("request")
        participants = validated_data.pop("participants", [])
        
        # Créer la conversation
        conversation = Conversation.objects.create(
            created_by=request.user if request else None,
            **validated_data
        )
        
        # Ajouter les participants
        conversation.participants.set(participants)
        
        # Validation finale
        try:
            conversation.full_clean()
        except ValidationError as e:
            conversation.delete()
            raise serializers.ValidationError(str(e))
        
        return conversation


class ConversationListSerializer(serializers.ModelSerializer):
    """
    Serializer simplifié pour la liste des conversations.
    
    Utilisé pour améliorer les performances lors du listing.
    """
    
    participants_count = serializers.SerializerMethodField()
    participants_preview = serializers.SerializerMethodField()
    last_message_preview = serializers.SerializerMethodField()
    unread_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Conversation
        fields = [
            "id",
            "subject",
            "conversation_type",
            "participants_count",
            "participants_preview",
            "last_message_preview",
            "unread_count",
            "last_message_at",
            "created_at",
        ]
    
    def get_participants_count(self, obj):
        """Retourne le nombre de participants."""
        return obj.participants.count()
    
    def get_participants_preview(self, obj):
        """Retourne un aperçu des participants (max 3)."""
        request = self.context.get("request")
        participants = list(obj.participants.all())
        
        # Exclure l'utilisateur connecté de la liste
        if request and request.user in participants:
            participants = [p for p in participants if p != request.user]
        
        return [
            {
                "id": user.id,
                "name": user.get_full_name() or user.username,
                "profile_picture": user.profile_picture.url if user.profile_picture else None,
            }
            for user in participants[:3]
        ]
    
    def get_last_message_preview(self, obj):
        """Retourne un aperçu du dernier message."""
        last_message = obj.messages.filter(is_deleted=False).last()
        if last_message:
            return {
                "content": last_message.content[:50] + "..." if len(last_message.content) > 50 else last_message.content,
                "sender": last_message.sender.get_full_name() or last_message.sender.username,
                "created_at": last_message.created_at,
            }
        return None
    
    def get_unread_count(self, obj):
        """Retourne le nombre de messages non lus."""
        request = self.context.get("request")
        if request and request.user:
            return obj.get_unread_count_for_user(request.user)
        return 0


class ConversationCreateSerializer(serializers.ModelSerializer):
    """
    Serializer pour la création d'une conversation.
    
    Validation stricte lors de la création.
    """
    
    participants_ids = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=CustomUser.objects.all(),
        required=True,
        write_only=True
    )
    
    class Meta:
        model = Conversation
        fields = [
            "participants_ids",
            "subject",
            "conversation_type",
        ]
    
    def validate_participants_ids(self, value):
        """Valide les participants avec sécurité renforcée."""
        if not value or len(value) < 2:
            raise serializers.ValidationError("Une conversation doit avoir au moins 2 participants.")
        
        if len(value) > 50:  # Limite de sécurité
            raise serializers.ValidationError("Une conversation ne peut pas avoir plus de 50 participants.")
        
        # Vérifier que l'utilisateur connecté est dans les participants
        request = self.context.get("request")
        if request and request.user:
            if request.user not in value:
                raise serializers.ValidationError("Vous devez être un participant de la conversation.")
            
            # Vérifier que l'utilisateur existe et est actif
            for user in value:
                if not user.is_active:
                    raise serializers.ValidationError(f"L'utilisateur {user.username} n'est pas actif.")
        
        # Vérifier qu'il n'y a pas de doublons
        if len(value) != len(set(value)):
            raise serializers.ValidationError("Les participants ne peuvent pas être dupliqués.")
        
        return value
    
    def validate(self, data):
        """Validation globale."""
        participants = data.get("participants_ids", [])
        conversation_type = data.get("conversation_type", "direct")
        
        if conversation_type == "direct" and len(participants) != 2:
            raise serializers.ValidationError({
                "conversation_type": "Une conversation directe doit avoir exactement 2 participants."
            })
        
        return data
    
    def create(self, validated_data):
        """Créer une conversation avec validation."""
        request = self.context.get("request")
        participants = validated_data.pop("participants_ids", [])
        
        conversation = Conversation.objects.create(
            created_by=request.user if request else None,
            **validated_data
        )
        
        conversation.participants.set(participants)
        
        try:
            conversation.full_clean()
        except ValidationError as e:
            conversation.delete()
            raise serializers.ValidationError(str(e))
        
        return conversation

