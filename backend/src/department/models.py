from django.db import models


class Department(models.Model):
    name = models.CharField(max_length=200)
    code = models.CharField(max_length=50, unique=True)
    description = models.TextField(blank=True)
    manager = models.ForeignKey(
        "employee.Employee",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="managed_departments",
    )
    location = models.CharField(max_length=200)
    budget = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Département"
        verbose_name_plural = "Départements"
    
    def __str__(self):
        return self.name
    
    @property
    def employee_count(self):
        return self.employees.filter(status='active').count()
