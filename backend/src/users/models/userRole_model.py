"""Modèle pour les rôles utilisateur."""

from django.contrib.auth.models import Permission
from django.db import models

# Note : Si Permission n'est pas disponible directement, utilisez :
# from django.contrib.auth.models import Permission


class UserRole(models.Model):
    """Gestion détaillée des rôles et permissions."""

    name = models.CharField(max_length=100, unique=True)
    code = models.CharField(max_length=50, unique=True, blank=True, null=True)
    description = models.TextField(blank=True)
    permissions = models.ManyToManyField(
        Permission, related_name="user_roles", blank=True
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Rôle utilisateur"
        verbose_name_plural = "Rôles utilisateur"
        ordering = ["name"]

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        """Génère automatiquement un code si non fourni."""
        if not self.code:
            self.code = self.name.lower().replace(" ", "_")
        super().save(*args, **kwargs)
