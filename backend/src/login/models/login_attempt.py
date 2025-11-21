"""Modèle pour les tentatives de connexion."""

from django.db import models


class LoginAttempt(models.Model):
    """Suivi des tentatives de connexion échouées."""

    email = models.EmailField()
    ip_address = models.GenericIPAddressField()
    failed_attempts = models.IntegerField(default=1)
    last_attempt = models.DateTimeField(auto_now=True)
    locked_until = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name = "Tentative de connexion"
        verbose_name_plural = "Tentatives de connexion"
        unique_together = ("email", "ip_address")

    def __str__(self) -> str:
        return f"{self.email} - {self.ip_address}"

