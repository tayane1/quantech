from users.models.customerUser_model import CustomUser
from django.db import models

class UserNotification(models.Model):
    """Notifications pour les utilisateurs"""
    NOTIFICATION_TYPES = [
        ('info', 'Information'),
        ('warning', 'Avertissement'),
        ('success', 'Succès'),
        ('error', 'Erreur'),
    ]
    
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='notifications')
    title = models.CharField(max_length=255)
    message = models.TextField()
    notification_type = models.CharField(max_length=20, choices=NOTIFICATION_TYPES, default='info')
    
    is_read = models.BooleanField(default=False)
    read_at = models.DateTimeField(null=True, blank=True)
    
    related_link = models.CharField(max_length=500, blank=True)  # URL de redirection
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Notification"
        verbose_name_plural = "Notifications"
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user} - {self.title}"
