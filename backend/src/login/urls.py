"""
URLs pour l'application login.

Ce fichier configure les routes REST pour les endpoints d'authentification :
- /api/login/login/ : Connexion
- /api/login/logout/ : Déconnexion
- /api/login/refresh/ : Rafraîchissement de token
- /api/login/history/ : Historique de connexion
- /api/login/refresh-tokens/ : Gestion des tokens de rafraîchissement
- /api/login/password-reset/ : Réinitialisation de mot de passe
- /api/login/attempts/ : Tentatives de connexion (admin)
- /api/login/2fa/ : Authentification à deux facteurs
"""

from django.urls import path
from rest_framework.routers import DefaultRouter
from login.viewsets import (
    LoginHistoryViewSet,
    RefreshTokenViewSet,
    PasswordResetViewSet,
    LoginAttemptViewSet,
    TwoFactorAuthViewSet,
)
from login.views.auth_views import login_view, logout_view, refresh_token_view, register_view

router = DefaultRouter()
router.register(r"history", LoginHistoryViewSet, basename="login-history")
router.register(r"refresh-tokens", RefreshTokenViewSet, basename="refresh-token")
router.register(
    r"password-reset", PasswordResetViewSet, basename="password-reset"
)
router.register(r"attempts", LoginAttemptViewSet, basename="login-attempt")
router.register(r"2fa", TwoFactorAuthViewSet, basename="two-factor-auth")

urlpatterns = [
    path("login/", login_view, name="login"),
    path("register/", register_view, name="register"),
    path("logout/", logout_view, name="logout"),
    path("refresh/", refresh_token_view, name="refresh-token"),
] + router.urls

