"""Modèle de gestion des tokens de rafraîchissement."""

from django.db import models

from users.models.customerUser_model import CustomUser


class RefreshToken(models.Model):
    """Gestion des tokens de rafraîchissement."""

    user = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name="refresh_tokens",
    )
    token = models.TextField(unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    revoked = models.BooleanField(default=False)
    revoked_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name = "Token de rafraîchissement"
        verbose_name_plural = "Tokens de rafraîchissement"
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"{self.user} - Token"

