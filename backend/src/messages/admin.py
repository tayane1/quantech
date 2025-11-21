"""
Configuration de l'admin Django pour les messages.

Permet aux admins de gérer les conversations et messages
avec des options de modération.
"""

from django.contrib import admin
from messages.models import Conversation, Message, MessageReadStatus


@admin.register(Conversation)
class ConversationAdmin(admin.ModelAdmin):
    """Admin pour les conversations."""
    
    list_display = ["id", "subject", "conversation_type", "created_by", "participants_count", "last_message_at", "is_deleted", "created_at"]
    list_filter = ["conversation_type", "is_archived", "is_deleted", "created_at"]
    search_fields = ["subject", "participants__username", "participants__email"]
    readonly_fields = ["created_at", "updated_at", "last_message_at", "deleted_at"]
    filter_horizontal = ["participants"]
    
    def participants_count(self, obj):
        """Retourne le nombre de participants."""
        return obj.participants.count()
    participants_count.short_description = "Participants"


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    """Admin pour les messages."""
    
    list_display = ["id", "conversation", "sender", "recipient", "content_preview", "is_read", "is_deleted", "created_at"]
    list_filter = ["is_read", "is_deleted", "created_at"]
    search_fields = ["content", "sender__username", "recipient__username", "conversation__subject"]
    readonly_fields = ["created_at", "updated_at", "read_at", "deleted_at"]
    
    def content_preview(self, obj):
        """Aperçu du contenu."""
        return obj.content[:50] + "..." if len(obj.content) > 50 else obj.content
    content_preview.short_description = "Contenu"


@admin.register(MessageReadStatus)
class MessageReadStatusAdmin(admin.ModelAdmin):
    """Admin pour les statuts de lecture."""
    
    list_display = ["id", "message", "user", "is_read", "read_at", "created_at"]
    list_filter = ["is_read", "read_at", "created_at"]
    search_fields = ["user__username", "message__content"]
    readonly_fields = ["created_at"]
