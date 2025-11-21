"""Modèles pour l'application settings (paramètres système)."""

from django.db import models
from users.models import CustomUser


class SystemSettings(models.Model):
    """
    Paramètres système globaux de l'application.
    
    Stocke les configurations générales de l'entreprise/application.
    """

    # Informations de l'entreprise
    company_name = models.CharField(max_length=255, default="Mon Entreprise")
    company_email = models.EmailField(default="contact@entreprise.com")
    company_phone = models.CharField(max_length=20, blank=True)
    company_address = models.TextField(blank=True)
    company_logo = models.ImageField(upload_to="company/", blank=True, null=True)

    # Paramètres généraux
    site_name = models.CharField(max_length=255, default="WeHR")
    site_url = models.URLField(blank=True, default="http://localhost:8000")
    maintenance_mode = models.BooleanField(default=False)
    maintenance_message = models.TextField(blank=True)

    # Paramètres de sécurité
    password_min_length = models.IntegerField(default=8)
    password_require_uppercase = models.BooleanField(default=True)
    password_require_lowercase = models.BooleanField(default=True)
    password_require_numbers = models.BooleanField(default=True)
    password_require_special = models.BooleanField(default=True)
    session_timeout_minutes = models.IntegerField(default=30)
    max_login_attempts = models.IntegerField(default=5)
    lockout_duration_minutes = models.IntegerField(default=15)

    # Paramètres d'email
    email_enabled = models.BooleanField(default=True)
    email_host = models.CharField(max_length=255, blank=True)
    email_port = models.IntegerField(default=587)
    email_use_tls = models.BooleanField(default=True)
    email_from = models.EmailField(blank=True)

    # Paramètres de notification
    enable_email_notifications = models.BooleanField(default=True)
    enable_sms_notifications = models.BooleanField(default=False)
    enable_push_notifications = models.BooleanField(default=True)

    # Paramètres de fichiers
    max_upload_size_mb = models.IntegerField(default=10)
    allowed_file_types = models.JSONField(default=list, blank=True)

    # Paramètres de localisation
    currency = models.CharField(max_length=3, default="XOF", help_text="Code devise ISO 4217 (ex: XOF, EUR, USD)")

    # Dates d'audit
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    updated_by = models.ForeignKey(
        CustomUser,
        on_delete=models.SET_NULL,
        null=True,
        related_name="settings_updates",
    )

    class Meta:
        verbose_name = "Paramètre système"
        verbose_name_plural = "Paramètres système"

    def __str__(self):
        return f"Paramètres système - {self.company_name}"

    def save(self, *args, **kwargs):
        """Assure qu'il n'y a qu'une seule instance de paramètres système."""
        # S'assurer qu'il n'y a qu'une seule instance
        if not self.pk and SystemSettings.objects.exists():
            # Si une instance existe déjà, utiliser celle-ci
            return SystemSettings.objects.first()
        super().save(*args, **kwargs)

    @classmethod
    def get_settings(cls):
        """Retourne les paramètres système (crée une instance par défaut si nécessaire)."""
        settings, created = cls.objects.get_or_create(pk=1)
        return settings


class EmailTemplate(models.Model):
    """
    Modèles d'emails pour les notifications.
    
    Permet de personnaliser les emails envoyés par l'application.
    """

    TEMPLATE_TYPES = [
        ("welcome", "Email de bienvenue"),
        ("password_reset", "Réinitialisation de mot de passe"),
        ("password_changed", "Mot de passe modifié"),
        ("account_activated", "Compte activé"),
        ("account_deactivated", "Compte désactivé"),
        ("notification", "Notification générale"),
        ("announcement", "Annonce"),
        ("ticket_created", "Ticket créé"),
        ("ticket_updated", "Ticket mis à jour"),
        ("ticket_closed", "Ticket fermé"),
    ]

    name = models.CharField(max_length=100, unique=True)
    template_type = models.CharField(max_length=50, choices=TEMPLATE_TYPES)
    subject = models.CharField(max_length=255)
    body_html = models.TextField(help_text="Corps de l'email en HTML")
    body_text = models.TextField(help_text="Corps de l'email en texte brut (fallback)")
    
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Modèle d'email"
        verbose_name_plural = "Modèles d'email"
        ordering = ["name"]

    def __str__(self):
        return f"{self.name} ({self.get_template_type_display()})"


class NotificationSettings(models.Model):
    """
    Paramètres de notifications par type.
    
    Configure quels types de notifications sont activés.
    """

    NOTIFICATION_TYPES = [
        ("user_registration", "Inscription d'utilisateur"),
        ("password_reset", "Réinitialisation de mot de passe"),
        ("employee_created", "Employé créé"),
        ("employee_updated", "Employé modifié"),
        ("announcement_published", "Annonce publiée"),
        ("ticket_created", "Ticket de support créé"),
        ("ticket_updated", "Ticket de support mis à jour"),
        ("system_maintenance", "Maintenance système"),
    ]

    notification_type = models.CharField(max_length=50, choices=NOTIFICATION_TYPES, unique=True)
    enabled = models.BooleanField(default=True)
    send_email = models.BooleanField(default=True)
    send_sms = models.BooleanField(default=False)
    send_push = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Paramètre de notification"
        verbose_name_plural = "Paramètres de notifications"
        ordering = ["notification_type"]

    def __str__(self):
        return f"{self.get_notification_type_display()} - {'Actif' if self.enabled else 'Inactif'}"
