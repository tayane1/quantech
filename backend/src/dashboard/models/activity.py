"""Modèle décrivant les activités affichées sur le dashboard."""

from django.db import models

from employee.models.employee import Employee
from recruitment.models.candidate import Candidate
from recruitment.models.job_position import JobPosition


class Activity(models.Model):
    """Événement notable reflété dans la timeline du dashboard."""

    ACTIVITY_JOB_POSTED = "job_posted"
    ACTIVITY_CANDIDATE_APPLIED = "candidate_applied"
    ACTIVITY_EMPLOYEE_ADDED = "employee_added"
    ACTIVITY_ANNOUNCEMENT_POSTED = "announcement_posted"
    ACTIVITY_SCHEDULE_CREATED = "schedule_created"
    ACTIVITY_MEETING_SCHEDULED = "meeting_scheduled"

    ACTIVITY_TYPES = [
        (ACTIVITY_JOB_POSTED, "Offre postée"),
        (ACTIVITY_CANDIDATE_APPLIED, "Candidature reçue"),
        (ACTIVITY_EMPLOYEE_ADDED, "Employé ajouté"),
        (ACTIVITY_ANNOUNCEMENT_POSTED, "Annonce publiée"),
        (ACTIVITY_SCHEDULE_CREATED, "Tâche créée"),
        (ACTIVITY_MEETING_SCHEDULED, "Réunion planifiée"),
    ]

    user = models.ForeignKey(
        Employee,
        on_delete=models.CASCADE,
        related_name="activities",
    )
    activity_type = models.CharField(max_length=50, choices=ACTIVITY_TYPES)
    description = models.TextField()

    related_position = models.ForeignKey(
        JobPosition,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="activities",
    )
    related_candidate = models.ForeignKey(
        Candidate,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="activities",
    )
    related_employee = models.ForeignKey(
        Employee,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="related_activities",
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Activité"
        verbose_name_plural = "Activités"
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"{self.activity_type} - {self.created_at}"
