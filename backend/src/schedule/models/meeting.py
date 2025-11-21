"""Modèle représentant une réunion."""

from django.db import models

from employee.models.employee import Employee


class Meeting(models.Model):
    """Réunion planifiée par un employé."""

    title = models.CharField(max_length=255)
    description = models.TextField()
    organizer = models.ForeignKey(
        Employee,
        on_delete=models.SET_NULL,
        null=True,
        related_name="organized_meetings",
    )
    attendees = models.ManyToManyField(
        Employee,
        related_name="meetings",
        blank=True,
    )

    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    location = models.CharField(max_length=255, blank=True)
    video_conference_link = models.URLField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Réunion"
        verbose_name_plural = "Réunions"
        ordering = ["-start_time"]

    def __str__(self) -> str:
        return self.title

