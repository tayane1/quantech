"""Modèle pour les tokens de réinitialisation de mot de passe."""

from django.db import models

from users.models.customerUser_model import CustomUser


class PasswordResetToken(models.Model):
    """Token pour réinitialisation de mot de passe."""

    user = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name="password_reset_tokens",
    )
    token = models.CharField(max_length=255, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    used = models.BooleanField(default=False)
    used_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name = "Token de réinitialisation"
        verbose_name_plural = "Tokens de réinitialisation"
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"Reset token for {self.user}"

