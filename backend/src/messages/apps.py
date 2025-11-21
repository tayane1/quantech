from django.apps import AppConfig


class MessagesConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'messages'
    
    def ready(self):
        """Initialisation de l'application."""
        import messages.signals  # noqa