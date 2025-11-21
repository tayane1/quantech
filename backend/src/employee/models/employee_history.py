"""Modèle stockant l'historique des changements d'un employé."""

from django.db import models

from .employee import Employee


class EmployeeHistory(models.Model):
    """Historique des changements d'un employé."""

    employee = models.ForeignKey(
        Employee,
        on_delete=models.CASCADE,
        related_name="history",
    )
    change_type = models.CharField(max_length=50)
    old_value = models.CharField(max_length=255, blank=True)
    new_value = models.CharField(max_length=255)
    changed_by = models.ForeignKey(
        Employee,
        on_delete=models.SET_NULL,
        null=True,
        related_name="+",
    )
    changed_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Historique employé"
        verbose_name_plural = "Historiques employés"
        ordering = ["-changed_at"]

    def __str__(self) -> str:
        return f"{self.employee} - {self.change_type}"

