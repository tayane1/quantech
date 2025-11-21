"""Modèles pour l'application support (tickets de support)."""

from django.db import models
from django.utils import timezone
from users.models import CustomUser


class SupportCategory(models.Model):
    """
    Catégories pour organiser les tickets de support.
    """

    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    icon = models.CharField(max_length=50, blank=True, help_text="Icône (ex: 'bug', 'question', etc.)")
    color = models.CharField(max_length=20, default="#007bff", help_text="Couleur hexadécimale")
    is_active = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Catégorie de support"
        verbose_name_plural = "Catégories de support"
        ordering = ["name"]

    def __str__(self):
        return self.name


class SupportTicket(models.Model):
    """
    Tickets de support pour gérer les demandes d'assistance.
    """

    PRIORITY_CHOICES = [
        ("low", "Basse"),
        ("medium", "Moyenne"),
        ("high", "Haute"),
        ("urgent", "Urgente"),
    ]

    STATUS_CHOICES = [
        ("open", "Ouvert"),
        ("in_progress", "En cours"),
        ("waiting", "En attente"),
        ("resolved", "Résolu"),
        ("closed", "Fermé"),
    ]

    # Informations du ticket
    title = models.CharField(max_length=255)
    description = models.TextField()
    category = models.ForeignKey(
        SupportCategory,
        on_delete=models.SET_NULL,
        null=True,
        related_name="tickets",
    )
    priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES, default="medium")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="open")

    # Utilisateurs impliqués
    created_by = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name="created_tickets",
    )
    assigned_to = models.ForeignKey(
        CustomUser,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="assigned_tickets",
        help_text="Personne assignée pour résoudre le ticket",
    )

    # Dates
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    resolved_at = models.DateTimeField(null=True, blank=True)
    closed_at = models.DateTimeField(null=True, blank=True)

    # Métadonnées
    attachments = models.JSONField(default=list, blank=True, help_text="Liste des fichiers joints")
    tags = models.JSONField(default=list, blank=True, help_text="Tags pour faciliter la recherche")
    
    # Résolution
    resolution = models.TextField(blank=True, help_text="Description de la résolution")
    satisfaction_rating = models.IntegerField(
        null=True,
        blank=True,
        choices=[(i, str(i)) for i in range(1, 6)],
        help_text="Note de satisfaction (1-5)",
    )
    satisfaction_feedback = models.TextField(blank=True)

    class Meta:
        verbose_name = "Ticket de support"
        verbose_name_plural = "Tickets de support"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["-created_at"]),
            models.Index(fields=["status", "-created_at"]),
            models.Index(fields=["priority", "-created_at"]),
        ]

    def __str__(self):
        return f"#{self.id} - {self.title}"

    def save(self, *args, **kwargs):
        """Met à jour automatiquement les dates de résolution/fermeture."""
        if self.pk:
            old_instance = SupportTicket.objects.get(pk=self.pk)
            
            # Si le statut passe à "resolved"
            if self.status == "resolved" and old_instance.status != "resolved":
                if not self.resolved_at:
                    self.resolved_at = timezone.now()
            
            # Si le statut passe à "closed"
            if self.status == "closed" and old_instance.status != "closed":
                if not self.closed_at:
                    self.closed_at = timezone.now()
            
            # Si le statut change de "resolved"/"closed" à autre chose
            if self.status not in ["resolved", "closed"]:
                if old_instance.status in ["resolved", "closed"]:
                    self.resolved_at = None
                    self.closed_at = None
        
        super().save(*args, **kwargs)

    @property
    def is_open(self):
        """Vérifie si le ticket est ouvert."""
        return self.status in ["open", "in_progress", "waiting"]

    @property
    def is_resolved(self):
        """Vérifie si le ticket est résolu."""
        return self.status == "resolved"

    @property
    def is_closed(self):
        """Vérifie si le ticket est fermé."""
        return self.status == "closed"

    @property
    def duration_days(self):
        """Calcule la durée du ticket en jours."""
        if self.closed_at:
            return (self.closed_at - self.created_at).days
        return (timezone.now() - self.created_at).days


class TicketComment(models.Model):
    """
    Commentaires sur les tickets de support.
    
    Permet la communication entre les utilisateurs et le support.
    """

    ticket = models.ForeignKey(
        SupportTicket,
        on_delete=models.CASCADE,
        related_name="comments",
    )
    author = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name="ticket_comments",
    )
    content = models.TextField()
    is_internal = models.BooleanField(
        default=False,
        help_text="Commentaire interne visible uniquement par le support",
    )
    attachments = models.JSONField(default=list, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Commentaire de ticket"
        verbose_name_plural = "Commentaires de tickets"
        ordering = ["created_at"]
        indexes = [
            models.Index(fields=["ticket", "-created_at"]),
        ]

    def __str__(self):
        return f"Commentaire #{self.id} sur ticket #{self.ticket.id}"


class TicketAttachment(models.Model):
    """
    Pièces jointes pour les tickets et commentaires.
    
    Séparé du modèle principal pour une meilleure gestion des fichiers.
    """

    ticket = models.ForeignKey(
        SupportTicket,
        on_delete=models.CASCADE,
        related_name="ticket_attachments",
        null=True,
        blank=True,
    )
    comment = models.ForeignKey(
        TicketComment,
        on_delete=models.CASCADE,
        related_name="comment_attachments",
        null=True,
        blank=True,
    )
    file = models.FileField(upload_to="support/tickets/")
    filename = models.CharField(max_length=255)
    file_size = models.IntegerField(help_text="Taille du fichier en octets")
    file_type = models.CharField(max_length=50, blank=True)
    
    uploaded_by = models.ForeignKey(
        CustomUser,
        on_delete=models.SET_NULL,
        null=True,
        related_name="uploaded_attachments",
    )
    
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Pièce jointe de ticket"
        verbose_name_plural = "Pièces jointes de tickets"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.filename} ({self.ticket or self.comment})"
