"""Modèle décrivant les étapes du processus d'embauche."""

from django.db import models

from .candidate import Candidate


class HiringProcess(models.Model):
    """Étape planifiée du parcours d'embauche d'un candidat."""

    candidate = models.ForeignKey(
        Candidate,
        on_delete=models.CASCADE,
        related_name="hiring_process",
    )
    stage = models.CharField(max_length=100)
    scheduled_date = models.DateTimeField()
    interviewer = models.ForeignKey(
        "employee.Employee",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="interviews",
    )
    feedback = models.TextField(blank=True)
    result = models.CharField(max_length=50, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Processus d'embauche"
        verbose_name_plural = "Processus d'embauche"
        ordering = ["-scheduled_date"]

    def __str__(self) -> str:
        return f"{self.candidate} - {self.stage}"

