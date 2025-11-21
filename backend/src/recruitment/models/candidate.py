"""Modèle représentant un candidat."""

from django.db import models

from .job_position import JobPosition


class Candidate(models.Model):
    """Candidat postulant à une offre d'emploi."""

    STATUS_APPLIED = "applied"
    STATUS_REVIEWING = "reviewing"
    STATUS_INTERVIEW = "interview"
    STATUS_OFFERED = "offered"
    STATUS_REJECTED = "rejected"
    STATUS_HIRED = "hired"

    STATUS_CHOICES = [
        (STATUS_APPLIED, "Candidature reçue"),
        (STATUS_REVIEWING, "En examen"),
        (STATUS_INTERVIEW, "Entretien"),
        (STATUS_OFFERED, "Offre faite"),
        (STATUS_REJECTED, "Rejeté"),
        (STATUS_HIRED, "Embauché"),
    ]

    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=20)
    resume = models.FileField(upload_to="resumes/")
    position = models.ForeignKey(
        JobPosition,
        on_delete=models.CASCADE,
        related_name="candidates",
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default=STATUS_APPLIED,
    )
    applied_date = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    notes = models.TextField(blank=True)

    class Meta:
        verbose_name = "Candidat"
        verbose_name_plural = "Candidats"
        ordering = ["-applied_date"]

    def __str__(self) -> str:
        return f"{self.first_name} {self.last_name}"

