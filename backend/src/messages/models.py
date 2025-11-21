"""
Modèles pour le système de messagerie.

Ce module définit les modèles pour les conversations et messages
avec une sécurité robuste et des contraintes strictes.
"""

from django.db import models
from django.utils import timezone
from django.core.exceptions import ValidationError
from users.models import CustomUser


class Conversation(models.Model):
    """
    Conversation entre plusieurs utilisateurs.
    
    Sécurité :
    - Un utilisateur ne peut voir que les conversations où il est participant
    - Les conversations sont privées et non accessibles publiquement
    """
    
    participants = models.ManyToManyField(
        CustomUser,
        related_name="conversations",
        verbose_name="Participants"
    )
    
    # Métadonnées
    created_by = models.ForeignKey(
        CustomUser,
        on_delete=models.SET_NULL,
        null=True,
        related_name="created_conversations",
        verbose_name="Créé par"
    )
    
    subject = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name="Sujet"
    )
    
    conversation_type = models.CharField(
        max_length=20,
        choices=[
            ("direct", "Message direct"),
            ("group", "Groupe"),
        ],
        default="direct",
        verbose_name="Type de conversation"
    )
    
    # Sécurité : archivage et suppression
    is_archived = models.BooleanField(default=False, verbose_name="Archivé")
    is_deleted = models.BooleanField(default=False, verbose_name="Supprimé")
    deleted_at = models.DateTimeField(null=True, blank=True, verbose_name="Date de suppression")
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Date de création")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Date de mise à jour")
    last_message_at = models.DateTimeField(null=True, blank=True, verbose_name="Dernier message")
    
    class Meta:
        verbose_name = "Conversation"
        verbose_name_plural = "Conversations"
        ordering = ["-last_message_at", "-created_at"]
        indexes = [
            models.Index(fields=["-last_message_at"]),
            models.Index(fields=["created_at"]),
        ]
    
    def __str__(self):
        if self.subject:
            return f"Conversation: {self.subject}"
        participants_names = ", ".join([u.get_full_name() or u.username for u in self.participants.all()[:3]])
        return f"Conversation: {participants_names}"
    
    def clean(self):
        """Validation stricte des conversations."""
        # Vérifier qu'il y a au moins 2 participants
        if self.participants.count() < 2:
            raise ValidationError("Une conversation doit avoir au moins 2 participants.")
        
        # Pour une conversation directe, vérifier qu'il n'y a que 2 participants
        if self.conversation_type == "direct" and self.participants.count() != 2:
            raise ValidationError("Une conversation directe doit avoir exactement 2 participants.")
    
    def save(self, *args, **kwargs):
        """Override save pour validation."""
        self.full_clean()
        super().save(*args, **kwargs)
    
    def get_unread_count_for_user(self, user):
        """Retourne le nombre de messages non lus pour un utilisateur."""
        return self.messages.filter(
            is_read=False,
            recipient=user
        ).exclude(sender=user).count()
    
    def mark_as_read_for_user(self, user):
        """Marque tous les messages comme lus pour un utilisateur."""
        self.messages.filter(
            is_read=False,
            recipient=user
        ).exclude(sender=user).update(
            is_read=True,
            read_at=timezone.now()
        )


class Message(models.Model):
    """
    Message dans une conversation.
    
    Sécurité :
    - Validation stricte du contenu
    - Protection contre les messages vides
    - Logging des actions
    """
    
    conversation = models.ForeignKey(
        Conversation,
        on_delete=models.CASCADE,
        related_name="messages",
        verbose_name="Conversation"
    )
    
    sender = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name="sent_messages",
        verbose_name="Expéditeur"
    )
    
    recipient = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name="received_messages",
        null=True,
        blank=True,
        verbose_name="Destinataire"
    )
    
    content = models.TextField(
        max_length=5000,
        verbose_name="Contenu"
    )
    
    # Fichiers joints (optionnel)
    attachment = models.FileField(
        upload_to="message_attachments/%Y/%m/%d/",
        blank=True,
        null=True,
        verbose_name="Pièce jointe"
    )
    
    # État du message
    is_read = models.BooleanField(default=False, verbose_name="Lu")
    read_at = models.DateTimeField(null=True, blank=True, verbose_name="Date de lecture")
    
    # Sécurité : suppression
    is_deleted = models.BooleanField(default=False, verbose_name="Supprimé")
    deleted_at = models.DateTimeField(null=True, blank=True, verbose_name="Date de suppression")
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Date de création")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Date de mise à jour")
    
    class Meta:
        verbose_name = "Message"
        verbose_name_plural = "Messages"
        ordering = ["created_at"]
        indexes = [
            models.Index(fields=["conversation", "-created_at"]),
            models.Index(fields=["sender", "-created_at"]),
            models.Index(fields=["recipient", "is_read"]),
        ]
    
    def __str__(self):
        return f"Message de {self.sender.username} - {self.content[:50]}..."
    
    def clean(self):
        """Validation stricte des messages."""
        # Vérifier que le contenu n'est pas vide
        if not self.content or not self.content.strip():
            raise ValidationError("Le message ne peut pas être vide.")
        
        # Vérifier la longueur
        if len(self.content.strip()) < 1:
            raise ValidationError("Le message doit contenir au moins 1 caractère.")
        
        if len(self.content) > 5000:
            raise ValidationError("Le message ne peut pas dépasser 5000 caractères.")
        
        # Vérifier que l'expéditeur est dans les participants de la conversation
        if self.conversation_id and self.sender_id:
            if self.sender not in self.conversation.participants.all():
                raise ValidationError("L'expéditeur doit être un participant de la conversation.")
        
        # Pour les messages directs, vérifier le destinataire
        if self.conversation_id and self.conversation.conversation_type == "direct":
            if not self.recipient_id:
                raise ValidationError("Un message direct doit avoir un destinataire.")
            if self.recipient == self.sender:
                raise ValidationError("Vous ne pouvez pas vous envoyer un message à vous-même.")
            if self.recipient not in self.conversation.participants.all():
                raise ValidationError("Le destinataire doit être un participant de la conversation.")
    
    def save(self, *args, **kwargs):
        """Override save pour validation et mise à jour de la conversation."""
        self.full_clean()
        
        # Mettre à jour la date du dernier message de la conversation
        if not self.pk:  # Nouveau message
            self.conversation.last_message_at = timezone.now()
            self.conversation.save(update_fields=["last_message_at", "updated_at"])
        
        super().save(*args, **kwargs)
    
    def mark_as_read(self):
        """Marque le message comme lu."""
        if not self.is_read:
            self.is_read = True
            self.read_at = timezone.now()
            self.save(update_fields=["is_read", "read_at"])


class MessageReadStatus(models.Model):
    """
    Statut de lecture d'un message par utilisateur.
    
    Permet de suivre précisément qui a lu quel message,
    particulièrement utile pour les conversations de groupe.
    """
    
    message = models.ForeignKey(
        Message,
        on_delete=models.CASCADE,
        related_name="read_statuses",
        verbose_name="Message"
    )
    
    user = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name="message_read_statuses",
        verbose_name="Utilisateur"
    )
    
    is_read = models.BooleanField(default=False, verbose_name="Lu")
    read_at = models.DateTimeField(null=True, blank=True, verbose_name="Date de lecture")
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Date de création")
    
    class Meta:
        verbose_name = "Statut de lecture"
        verbose_name_plural = "Statuts de lecture"
        unique_together = [["message", "user"]]
        indexes = [
            models.Index(fields=["user", "is_read"]),
        ]
    
    def __str__(self):
        return f"{self.user.username} - {self.message.id} - {'Lu' if self.is_read else 'Non lu'}"
