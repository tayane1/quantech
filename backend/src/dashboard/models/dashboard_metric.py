"""Modèle stockant les métriques affichées sur le dashboard."""

from django.db import models


class DashboardMetric(models.Model):
    """Métriques agrégées pour le tableau de bord."""

    metric_type = models.CharField(max_length=100)
    value = models.IntegerField()
    previous_value = models.IntegerField(null=True, blank=True)
    change_percentage = models.FloatField(null=True, blank=True)

    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Métrique"
        verbose_name_plural = "Métriques"
        ordering = ["metric_type"]

    def __str__(self) -> str:
        return f"{self.metric_type}: {self.value}"
