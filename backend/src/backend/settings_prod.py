"""
Settings de production pour WeHR.

À utiliser en production avec variables d'environnement.
Ne JAMAIS commiter les valeurs réelles de production.
"""

import os
from pathlib import Path
from datetime import timedelta
from .settings import *  # noqa

# Build paths
BASE_DIR = Path(__file__).resolve().parent.parent

# ========================================
# SÉCURITÉ - CRITIQUE
# ========================================

# SECRET_KEY : OBLIGATOIRE via variable d'environnement
SECRET_KEY = os.environ.get('SECRET_KEY')
if not SECRET_KEY:
    raise ValueError(
        "SECRET_KEY environment variable is required in production. "
        "Please set it: export SECRET_KEY='your-secret-key-here'"
    )

# DEBUG : JAMAIS True en production
DEBUG = os.environ.get('DEBUG', 'False') == 'True'
if DEBUG:
    import warnings
    warnings.warn("DEBUG is True in production! This is a security risk.")

# ALLOWED_HOSTS : Domaines autorisés
ALLOWED_HOSTS = os.environ.get('ALLOWED_HOSTS', '').split(',')
ALLOWED_HOSTS = [host.strip() for host in ALLOWED_HOSTS if host.strip()]
if not ALLOWED_HOSTS:
    # Valeurs par défaut pour développement
    ALLOWED_HOSTS = ['localhost', '127.0.0.1', '[::1]']

# ========================================
# HTTPS et HEADERS DE SÉCURITÉ
# ========================================

# Force HTTPS en production
SECURE_SSL_REDIRECT = os.environ.get('SECURE_SSL_REDIRECT', 'True') == 'True'

# HTTP Strict Transport Security (HSTS)
SECURE_HSTS_SECONDS = int(os.environ.get('SECURE_HSTS_SECONDS', '31536000'))  # 1 an
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True

# Content Security
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_BROWSER_XSS_FILTER = True
X_FRAME_OPTIONS = 'DENY'  # Protection clickjacking

# Proxy SSL Header (si derrière un reverse proxy)
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

# ========================================
# CORS - Restrictif en production
# ========================================

CORS_ALLOWED_ORIGINS = os.environ.get('CORS_ALLOWED_ORIGINS', '').split(',')
CORS_ALLOWED_ORIGINS = [origin.strip() for origin in CORS_ALLOWED_ORIGINS if origin.strip()]

if not CORS_ALLOWED_ORIGINS:
    # Valeurs par défaut si non configurées
    CORS_ALLOWED_ORIGINS = ['http://localhost:4200', 'http://localhost:3000']

CORS_ALLOW_CREDENTIALS = True

# CORS headers autorisés
CORS_ALLOW_HEADERS = [
    "accept",
    "accept-encoding",
    "authorization",
    "content-type",
    "dnt",
    "origin",
    "user-agent",
    "x-csrftoken",
    "x-requested-with",
]

# ========================================
# RATE LIMITING
# ========================================

# Configuration DRF avec rate limiting
REST_FRAMEWORK = {
    **REST_FRAMEWORK,  # Conserver la config existante
    'DEFAULT_THROTTLE_CLASSES': [
        'rest_framework.throttling.AnonRateThrottle',
        'rest_framework.throttling.UserRateThrottle'
    ],
    'DEFAULT_THROTTLE_RATES': {
        'anon': '100/hour',      # Utilisateurs anonymes
        'user': '1000/hour',     # Utilisateurs authentifiés
        'login': '5/minute',     # Tentatives de login (scope custom)
        'register': '3/hour',    # Inscriptions (scope custom)
    }
}

# ========================================
# DATABASE - Configuration sécurisée
# ========================================

# Pour PostgreSQL en production (exemple)
# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.postgresql',
#         'NAME': os.environ.get('DB_NAME'),
#         'USER': os.environ.get('DB_USER'),
#         'PASSWORD': os.environ.get('DB_PASSWORD'),
#         'HOST': os.environ.get('DB_HOST', 'localhost'),
#         'PORT': os.environ.get('DB_PORT', '5432'),
#         'OPTIONS': {
#             'sslmode': 'require',
#         },
#     }
# }

# ========================================
# LOGGING - Configuration avancée
# ========================================

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'file': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': BASE_DIR / 'logs' / 'django.log',
            'formatter': 'verbose',
        },
        'security_file': {
            'level': 'WARNING',
            'class': 'logging.FileHandler',
            'filename': BASE_DIR / 'logs' / 'security.log',
            'formatter': 'verbose',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['file'],
            'level': 'INFO',
            'propagate': True,
        },
        'django.security': {
            'handlers': ['security_file'],
            'level': 'WARNING',
            'propagate': False,
        },
    },
}

# Créer le dossier logs s'il n'existe pas
logs_dir = BASE_DIR / 'logs'
logs_dir.mkdir(exist_ok=True)

# ========================================
# SESSION - Configuration sécurisée
# ========================================

# Cookies de session sécurisés
SESSION_COOKIE_SECURE = True  # HTTPS seulement
SESSION_COOKIE_HTTPONLY = True  # Non accessible par JavaScript
SESSION_COOKIE_SAMESITE = 'Lax'  # Protection CSRF
SESSION_COOKIE_AGE = 3600  # 1 heure

# ========================================
# CSRF - Configuration sécurisée
# ========================================

CSRF_COOKIE_SECURE = True  # HTTPS seulement
CSRF_COOKIE_HTTPONLY = True
CSRF_COOKIE_SAMESITE = 'Lax'
CSRF_TRUSTED_ORIGINS = CORS_ALLOWED_ORIGINS.copy()

# ========================================
# EMAIL - Configuration production
# ========================================

# Configuration email (exemple)
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = os.environ.get('EMAIL_HOST', 'smtp.gmail.com')
EMAIL_PORT = int(os.environ.get('EMAIL_PORT', '587'))
EMAIL_USE_TLS = True
EMAIL_HOST_USER = os.environ.get('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD')
DEFAULT_FROM_EMAIL = os.environ.get('DEFAULT_FROM_EMAIL', 'noreply@wehr.com')

# ========================================
# FICHIERS STATIQUES
# ========================================

STATIC_ROOT = os.environ.get('STATIC_ROOT', BASE_DIR / 'staticfiles')
MEDIA_ROOT = os.environ.get('MEDIA_ROOT', BASE_DIR / 'media')

# ========================================
# NOTES
# ========================================

# Variables d'environnement requises en production :
# - SECRET_KEY (obligatoire)
# - ALLOWED_HOSTS (recommandé)
# - CORS_ALLOWED_ORIGINS (recommandé)
# - DB_NAME, DB_USER, DB_PASSWORD, DB_HOST (si PostgreSQL)
# - EMAIL_HOST_USER, EMAIL_HOST_PASSWORD (si email activé)

# Pour utiliser ces settings :
# export DJANGO_SETTINGS_MODULE=backend.settings_prod
# ou
# python manage.py runserver --settings=backend.settings_prod

