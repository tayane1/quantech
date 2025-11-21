"""Modèles liés à l'historique de connexion."""

from django.db import models

from users.models.customerUser_model import CustomUser


class LoginHistory(models.Model):
    """Historique des connexions utilisateur."""

    user = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name="login_history",
    )
    ip_address = models.GenericIPAddressField()
    user_agent = models.TextField()
    device_type = models.CharField(max_length=50, blank=True)
    browser = models.CharField(max_length=100, blank=True)

    login_time = models.DateTimeField(auto_now_add=True)
    logout_time = models.DateTimeField(null=True, blank=True)

    is_successful = models.BooleanField(default=True)
    failure_reason = models.CharField(max_length=255, blank=True)

    class Meta:
        verbose_name = "Historique de connexion"
        verbose_name_plural = "Historiques de connexion"
        ordering = ["-login_time"]
        indexes = [
            models.Index(fields=["-login_time"]),
            models.Index(fields=["user", "-login_time"]),
        ]

    def __str__(self) -> str:
        return f"{self.user} - {self.login_time}"

