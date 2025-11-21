from users.models.customerUser_model import CustomUser
from django.db import models


class UserActivity(models.Model):
    """Log des activités utilisateur (audit trail)"""
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='user_activities')
    action = models.CharField(max_length=255)  # ex: "Created job posting", "Updated employee profile"
    module = models.CharField(max_length=50)  # recruitment, employee, etc.
    ip_address = models.GenericIPAddressField(blank=True, null=True)
    user_agent = models.TextField(blank=True)
    
    timestamp = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Activité utilisateur"
        verbose_name_plural = "Activités utilisateur"
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['-timestamp']),
            models.Index(fields=['user', '-timestamp']),
        ]
    
    def __str__(self):
        return f"{self.user} - {self.action} - {self.timestamp}"
