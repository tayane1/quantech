"""Modèle représentant une tâche planifiée."""

from django.db import models

from employee.models.employee import Employee


class Schedule(models.Model):
    """Tâche assignée à un employé."""

    PRIORITY_HIGH = "high"
    PRIORITY_MEDIUM = "medium"
    PRIORITY_LOW = "low"

    PRIORITY_CHOICES = [
        (PRIORITY_HIGH, "Élevée"),
        (PRIORITY_MEDIUM, "Moyenne"),
        (PRIORITY_LOW, "Basse"),
    ]

    title = models.CharField(max_length=255)
    description = models.TextField()
    assigned_to = models.ForeignKey(
        Employee,
        on_delete=models.CASCADE,
        related_name="schedules",
    )
    assigned_by = models.ForeignKey(
        Employee,
        on_delete=models.SET_NULL,
        null=True,
        related_name="assigned_tasks",
    )

    priority = models.CharField(
        max_length=20,
        choices=PRIORITY_CHOICES,
        default=PRIORITY_MEDIUM,
    )
    scheduled_date = models.DateTimeField()
    completed = models.BooleanField(default=False)
    completed_date = models.DateTimeField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Tâche planifiée"
        verbose_name_plural = "Tâches planifiées"
        ordering = ["-scheduled_date"]

    def __str__(self) -> str:
        return self.title

