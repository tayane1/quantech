"""Modèle pour les demandes de talents."""

from django.db import models

from .job_position import JobPosition


class TalentRequest(models.Model):
    """Demande d'ouverture ou de renfort sur un poste."""

    STATUS_PENDING = "pending"
    STATUS_APPROVED = "approved"
    STATUS_REJECTED = "rejected"
    STATUS_FULFILLED = "fulfilled"

    STATUS_CHOICES = [
        (STATUS_PENDING, "En attente"),
        (STATUS_APPROVED, "Approuvé"),
        (STATUS_REJECTED, "Rejeté"),
        (STATUS_FULFILLED, "Satisfait"),
    ]

    position = models.ForeignKey(JobPosition, on_delete=models.CASCADE)
    requested_by = models.ForeignKey(
        "employee.Employee",
        on_delete=models.SET_NULL,
        null=True,
        related_name="talent_requests",
    )
    number_of_people = models.IntegerField(default=1)
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default=STATUS_PENDING,
    )
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Demande de talent"
        verbose_name_plural = "Demandes de talent"
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"Demande pour {self.position.title}"

