"""Modèle principal représentant un employé."""

from django.db import models


class Employee(models.Model):
    """Employé de l'organisation."""

    GENDER_MALE = "M"
    GENDER_FEMALE = "F"
    GENDER_OTHER = "O"

    GENDER_CHOICES = [
        (GENDER_MALE, "Homme"),
        (GENDER_FEMALE, "Femme"),
        (GENDER_OTHER, "Autre"),
    ]

    STATUS_ACTIVE = "active"
    STATUS_ON_LEAVE = "on_leave"
    STATUS_INACTIVE = "inactive"

    STATUS_CHOICES = [
        (STATUS_ACTIVE, "Actif"),
        (STATUS_ON_LEAVE, "En congé"),
        (STATUS_INACTIVE, "Inactif"),
    ]

    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=20)
    date_of_birth = models.DateField()
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES)
    profile_picture = models.ImageField(
        upload_to="employee_pics/",
        blank=True,
        null=True,
    )

    employee_id = models.CharField(max_length=50, unique=True)
    hire_date = models.DateField()
    position = models.ForeignKey(
        "department.Department",
        on_delete=models.SET_NULL,
        null=True,
        related_name="position_employees",
    )
    department = models.ForeignKey(
        "department.Department",
        on_delete=models.SET_NULL,
        null=True,
        related_name="employees",
    )
    manager = models.ForeignKey(
        "self",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="subordinates",
    )
    salary = models.DecimalField(max_digits=12, decimal_places=2)
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default=STATUS_ACTIVE,
    )

    address = models.TextField()
    city = models.CharField(max_length=100)
    country = models.CharField(max_length=100)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Employé"
        verbose_name_plural = "Employés"
        ordering = ["last_name", "first_name"]

    def __str__(self) -> str:
        return f"{self.first_name} {self.last_name}"

