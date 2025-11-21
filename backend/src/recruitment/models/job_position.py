"""Modèle représentant une offre d'emploi."""

from django.db import models


class JobPosition(models.Model):
    """Offre d'emploi publiée par l'organisation."""

    STATUS_OPEN = "open"
    STATUS_CLOSED = "closed"
    STATUS_ON_HOLD = "on_hold"

    STATUS_CHOICES = [
        (STATUS_OPEN, "Ouvert"),
        (STATUS_CLOSED, "Fermé"),
        (STATUS_ON_HOLD, "En attente"),
    ]

    title = models.CharField(max_length=255)
    description = models.TextField()
    department = models.ForeignKey(
        "department.Department",
        on_delete=models.SET_NULL,
        null=True,
        related_name="job_positions",
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default=STATUS_OPEN,
    )
    urgency = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Offre d'emploi"
        verbose_name_plural = "Offres d'emploi"
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return self.title

