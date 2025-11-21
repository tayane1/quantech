from django.db import models


class Announcement(models.Model):
    title = models.CharField(max_length=255)
    content = models.TextField()
    author = models.ForeignKey(
        "employee.Employee",
        on_delete=models.SET_NULL,
        null=True,
        related_name="announcements",
    )

    published = models.BooleanField(default=True)
    published_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)

    # Portée
    visible_to_all = models.BooleanField(default=True)
    departments = models.ManyToManyField(
        "department.Department",
        blank=True,
        related_name="announcements",
    )

    class Meta:
        verbose_name = "Annonce"
        verbose_name_plural = "Annonces"

    def __str__(self):
        return self.title
