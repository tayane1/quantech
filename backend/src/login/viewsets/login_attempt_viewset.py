"""
ViewSet pour la gestion des tentatives de connexion (LoginAttempt).

Ce ViewSet permet de consulter les tentatives de connexion échouées :
- Protection contre les attaques brute force
- Consultation uniquement pour les admins
- Lecture seule
"""

from rest_framework import viewsets, permissions
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter

from login.models.login_attempt import LoginAttempt
from login.serializers.login_attempt_serializer import LoginAttemptSerializer


class LoginAttemptViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet en lecture seule pour les tentatives de connexion.
    
    Endpoints disponibles :
    - GET /api/login/attempts/ : Liste des tentatives (admin uniquement)
    - GET /api/login/attempts/{id}/ : Détails d'une tentative
    """
    
    serializer_class = LoginAttemptSerializer
    permission_classes = [permissions.IsAdminUser]  # Admins uniquement
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ["email", "ip_address"]
    search_fields = ["email", "ip_address"]
    ordering_fields = ["last_attempt", "failed_attempts"]
    ordering = ["-last_attempt"]

    def get_queryset(self):
        """Retourne toutes les tentatives."""
        return LoginAttempt.objects.all()

