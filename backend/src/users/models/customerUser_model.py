from django.contrib.auth.models import AbstractUser, Group, Permission
from django.db import models

class CustomUser(AbstractUser):
    """Modèle utilisateur personnalisé pour WeHR"""
    ROLE_CHOICES = [
        ('admin', 'Administrateur'),
        ('hr_manager', 'Responsable RH'),
        ('recruiter', 'Recruteur'),
        ('manager', 'Manager'),
        ('employee', 'Employé'),
    ]
    
    # Champs de base
    username = models.CharField(max_length=150, unique=True)
    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    
    # Rôle
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='employee')
    
    # Profil
    profile_picture = models.ImageField(upload_to='profile_pics/', blank=True, null=True)
    bio = models.TextField(blank=True)
    phone = models.CharField(max_length=20, blank=True)
    
    # Lien vers Employee
    employee = models.OneToOneField('employee.Employee', on_delete=models.SET_NULL, null=True, blank=True, related_name='user')
    
    # Permissions personnalisées
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    
    # Audit
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    last_login = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        verbose_name = "Utilisateur"
        verbose_name_plural = "Utilisateurs"
    
    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.username})"
