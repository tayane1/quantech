"""
Signaux Django pour l'application messages.

Gère les actions automatiques lors de la création/modification
de conversations et messages.
"""

from django.db.models.signals import post_save, pre_delete
from django.dispatch import receiver
from django.utils import timezone
from messages.models import Conversation, Message, MessageReadStatus


@receiver(post_save, sender=Message)
def update_conversation_last_message(sender, instance, created, **kwargs):
    """
    Met à jour la date du dernier message de la conversation
    lorsqu'un nouveau message est créé.
    """
    if created and not instance.is_deleted:
        conversation = instance.conversation
        conversation.last_message_at = timezone.now()
        conversation.save(update_fields=["last_message_at", "updated_at"])


@receiver(pre_delete, sender=Conversation)
def soft_delete_conversation_messages(sender, instance, **kwargs):
    """
    Soft delete des messages lors de la suppression d'une conversation.
    """
    instance.messages.filter(is_deleted=False).update(
        is_deleted=True,
        deleted_at=timezone.now()
    )

