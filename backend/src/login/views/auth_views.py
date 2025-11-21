"""
Vues d'authentification avec rate limiting.

Ces vues gèrent le login avec protection contre les attaques brute force.
"""

from rest_framework import status
from rest_framework.decorators import api_view, permission_classes, throttle_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.throttling import AnonRateThrottle, UserRateThrottle
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from django.utils import timezone
from datetime import timedelta

from users.models import CustomUser
from login.models.login_attempt import LoginAttempt
from login.models.login_history import LoginHistory


class LoginThrottle(AnonRateThrottle):
    """
    Rate limiting personnalisé pour le login.
    
    Limite : 5 tentatives par minute par IP.
    """
    rate = '5/minute'
    scope = 'login'


@api_view(['POST'])
@permission_classes([AllowAny])
@throttle_classes([LoginThrottle])
def login_view(request):
    """
    Vue de login avec rate limiting et tracking des tentatives.
    
    POST /api/login/login/
    
    Body:
    {
        "username": "user",
        "password": "password"
    }
    
    Réponse:
    {
        "access": "token",
        "refresh": "token",
        "user": {...}
    }
    """
    username = request.data.get('username')
    password = request.data.get('password')
    
    if not username or not password:
        return Response(
            {"detail": "Username et password requis."},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Vérifier les tentatives de connexion échouées
    ip_address = get_client_ip(request)
    
    try:
        # Vérifier si l'IP est bloquée
        login_attempt = LoginAttempt.objects.filter(
            email=username,
            ip_address=ip_address,
            locked_until__gt=timezone.now()
        ).first()
        
        if login_attempt:
            remaining_time = (login_attempt.locked_until - timezone.now()).seconds
            return Response(
                {
                    "detail": f"Trop de tentatives échouées. Réessayez dans {remaining_time // 60} minutes.",
                    "locked_until": login_attempt.locked_until.isoformat()
                },
                status=status.HTTP_429_TOO_MANY_REQUESTS
            )
        
        # Authentifier l'utilisateur
        user = authenticate(request=request, username=username, password=password)
        
        if user is None:
            # Enregistrer la tentative échouée
            record_failed_login_attempt(username, ip_address)
            
            return Response(
                {"detail": "Identifiants incorrects."},
                status=status.HTTP_401_UNAUTHORIZED
            )
        
        if not user.is_active:
            return Response(
                {"detail": "Compte désactivé."},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Réussite : générer les tokens
        refresh = RefreshToken.for_user(user)
        access_token = refresh.access_token
        
        # Enregistrer la connexion réussie
        record_successful_login(user, request)
        
        # Réinitialiser les tentatives échouées
        LoginAttempt.objects.filter(email=username, ip_address=ip_address).delete()
        
        # Retourner les tokens et les infos utilisateur
        from users.serializers.customUser_serializer import CustomUserSerializer
        user_serializer = CustomUserSerializer(user, context={'request': request})
        
        # Format de réponse compatible avec le frontend
        # Le frontend attend : { access, refresh, user } ou { access_token, refresh_token, user }
        return Response({
            "access": str(access_token),
            "refresh": str(refresh),
            "user": user_serializer.data
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response(
            {"detail": "Une erreur est survenue lors de la connexion."},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
@permission_classes([AllowAny])
def refresh_token_view(request):
    """
    Rafraîchir un token d'accès.
    
    POST /api/login/refresh/
    
    Body:
    {
        "refresh": "refresh_token"
    }
    
    Réponse:
    {
        "access": "new_access_token"
    }
    """
    refresh_token = request.data.get('refresh')
    
    if not refresh_token:
        return Response(
            {"detail": "Refresh token requis."},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    try:
        refresh = RefreshToken(refresh_token)
        access_token = refresh.access_token
        
        return Response({
            "access": str(access_token)
        })
        
    except Exception:
        return Response(
            {"detail": "Token invalide ou expiré."},
            status=status.HTTP_401_UNAUTHORIZED
        )


@api_view(['POST'])
def logout_view(request):
    """
    Vue de déconnexion.
    
    POST /api/login/logout/
    
    Body: (optionnel)
    {
        "refresh": "refresh_token"
    }
    
    Réponse:
    {
        "detail": "Déconnexion réussie."
    }
    """
    refresh_token_str = request.data.get('refresh')
    
    if refresh_token_str:
        try:
            # Révoquer le token de rafraîchissement dans la base de données
            from login.models.refresh_token import RefreshToken as RefreshTokenModel
            token_obj = RefreshTokenModel.objects.filter(
                token=refresh_token_str,
                revoked=False
            ).first()
            
            if token_obj:
                token_obj.revoked = True
                token_obj.revoked_at = timezone.now()
                token_obj.save()
        except Exception:
            # Si le token est invalide, on continue quand même
            pass
    
    # Si l'utilisateur est authentifié, mettre à jour l'historique
    if request.user.is_authenticated:
        last_login = LoginHistory.objects.filter(
            user=request.user,
            is_successful=True,
            logout_time__isnull=True
        ).order_by('-login_time').first()
        
        if last_login:
            last_login.logout_time = timezone.now()
            last_login.save()
    
    return Response(
        {"detail": "Déconnexion réussie."},
        status=status.HTTP_200_OK
    )


def get_client_ip(request):
    """Récupère l'adresse IP du client."""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


def record_failed_login_attempt(username: str, ip_address: str):
    """
    Enregistre une tentative de connexion échouée.
    
    Si plus de 5 tentatives échouées, bloque l'IP pendant 15 minutes.
    """
    attempt, created = LoginAttempt.objects.get_or_create(
        email=username,
        ip_address=ip_address,
        defaults={'failed_attempts': 1}
    )
    
    if not created:
        attempt.failed_attempts += 1
        attempt.save()
    
    # Bloquer si plus de 5 tentatives
    if attempt.failed_attempts >= 5:
        attempt.locked_until = timezone.now() + timedelta(minutes=15)
        attempt.save()


def record_successful_login(user: CustomUser, request):
    """Enregistre une connexion réussie dans l'historique."""
    ip_address = get_client_ip(request)
    user_agent = request.META.get('HTTP_USER_AGENT', '')
    
    LoginHistory.objects.create(
        user=user,
        ip_address=ip_address,
        user_agent=user_agent,
        is_successful=True
    )


@api_view(['POST'])
@permission_classes([AllowAny])
def register_view(request):
    """
    Vue d'inscription publique.
    
    POST /api/login/register/
    
    Body:
    {
        "username": "user",
        "email": "user@example.com",
        "password": "password",
        "password_confirm": "password",
        "first_name": "John",
        "last_name": "Doe",
        "role": "employee"
    }
    
    Réponse:
    {
        "access": "token",
        "refresh": "token",
        "user": {...}
    }
    """
    from users.serializers.customUser_serializer import CustomUserSerializer
    
    # Créer un serializer avec les données fournies
    serializer = CustomUserSerializer(data=request.data)
    
    if serializer.is_valid():
        # Créer l'utilisateur
        user = serializer.save()
        
        # L'utilisateur créé est automatiquement actif par défaut
        # Générer les tokens JWT
        refresh = RefreshToken.for_user(user)
        access_token = refresh.access_token
        
        # Enregistrer la connexion réussie
        record_successful_login(user, request)
        
        # Retourner les tokens et les infos utilisateur
        user_serializer = CustomUserSerializer(user, context={'request': request})
        
        return Response({
            "access": str(access_token),
            "refresh": str(refresh),
            "user": user_serializer.data
        }, status=status.HTTP_201_CREATED)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
