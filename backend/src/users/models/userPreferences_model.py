from users.models.customerUser_model import CustomUser
from django.db import models

class UserPreference(models.Model):
    """Préférences utilisateur"""
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='preferences')
    
    # Langue et localisation
    language = models.CharField(max_length=10, default='fr')
    timezone = models.CharField(max_length=50, default='UTC')
    
    # Notifications
    email_notifications = models.BooleanField(default=True)
    in_app_notifications = models.BooleanField(default=True)
    sms_notifications = models.BooleanField(default=False)
    
    # Dashboard
    dashboard_theme = models.CharField(max_length=20, choices=[('light', 'Clair'), ('dark', 'Sombre')], default='light')
    show_welcome_message = models.BooleanField(default=True)
    
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Préférence utilisateur"
        verbose_name_plural = "Préférences utilisateur"
    
    def __str__(self):
        return f"Préférences de {self.user}"