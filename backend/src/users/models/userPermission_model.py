from django.contrib.auth.models import Permission
from users.models.customerUser_model import CustomUser
from django.db import models

class UserPermission(models.Model):
    """Permissions granulaires pour l'accès aux modules"""
    MODULE_CHOICES = [
        ('dashboard', 'Dashboard'),
        ('recruitment', 'Recrutement'),
        ('employee', 'Employés'),
        ('department', 'Départements'),
        ('schedule', 'Calendrier'),
        ('announcement', 'Annonces'),
        ('settings', 'Paramètres'),
        ('reports', 'Rapports'),
    ]
    
    ACTION_CHOICES = [
        ('view', 'Voir'),
        ('create', 'Créer'),
        ('edit', 'Modifier'),
        ('delete', 'Supprimer'),
        ('export', 'Exporter'),
    ]
    
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='custom_permissions')
    module = models.CharField(max_length=50, choices=MODULE_CHOICES)
    action = models.CharField(max_length=20, choices=ACTION_CHOICES)
    granted = models.BooleanField(default=True)
    
    granted_by = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, related_name='+')
    granted_date = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Permission utilisateur"
        verbose_name_plural = "Permissions utilisateur"
        unique_together = ('user', 'module', 'action')
    
    def __str__(self):
        return f"{self.user} - {self.module} - {self.action}"
