"""Modèle pour la configuration 2FA."""

from django.db import models

from users.models.customerUser_model import CustomUser


class TwoFactorAuth(models.Model):
    """Configuration 2FA pour les utilisateurs."""

    TYPE_EMAIL = "email"
    TYPE_SMS = "sms"
    TYPE_TOTP = "totp"

    TYPE_CHOICES = [
        (TYPE_EMAIL, "Email"),
        (TYPE_SMS, "SMS"),
        (TYPE_TOTP, "Authenticator App (TOTP)"),
    ]

    user = models.OneToOneField(
        CustomUser,
        on_delete=models.CASCADE,
        related_name="two_factor_auth",
    )
    is_enabled = models.BooleanField(default=False)
    method = models.CharField(max_length=20, choices=TYPE_CHOICES, default=TYPE_EMAIL)

    secret_key = models.CharField(max_length=32, blank=True)
    backup_codes = models.JSONField(default=list)

    verified = models.BooleanField(default=False)
    verified_at = models.DateTimeField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Authentification 2FA"
        verbose_name_plural = "Authentifications 2FA"

    def __str__(self) -> str:
        return f"2FA for {self.user}"

