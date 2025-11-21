"""
Améliorations de sécurité pour settings.py (développement et production).

À importer dans settings.py pour ajouter les améliorations de sécurité.
"""

import os

# ========================================
# SÉCURITÉ - Configuration générale
# ========================================

# SECRET_KEY : Préférer variable d'environnement même en développement
SECRET_KEY = os.environ.get(
    'SECRET_KEY',
    "django-insecure-1b_!=2_i9b9ivtck!6ja!96zmh7cwe(p2l2)6=(nq52oqsqso4"  # Dev only
)

# DEBUG : Configuration sécurisée
DEBUG = os.environ.get('DEBUG', 'True') == 'True'

# ALLOWED_HOSTS : Configuration sécurisée
ALLOWED_HOSTS = os.environ.get('ALLOWED_HOSTS', '').split(',')
ALLOWED_HOSTS = [host.strip() for host in ALLOWED_HOSTS if host.strip()]
if not ALLOWED_HOSTS:
    ALLOWED_HOSTS = ['localhost', '127.0.0.1', '[::1]']

# ========================================
# RATE LIMITING - Configuration globale
# ========================================

# Ajouter au REST_FRAMEWORK dans settings.py
REST_FRAMEWORK_THROTTLE_CONFIG = {
    'DEFAULT_THROTTLE_CLASSES': [
        'rest_framework.throttling.AnonRateThrottle',
        'rest_framework.throttling.UserRateThrottle'
    ],
    'DEFAULT_THROTTLE_RATES': {
        'anon': '100/hour',
        'user': '1000/hour',
        'login': '5/minute',
        'register': '3/hour',
    }
}

# ========================================
# HEADERS DE SÉCURITÉ HTTP
# ========================================

# Activer seulement en production (via variable d'environnement)
SECURE_SSL_REDIRECT = os.environ.get('SECURE_SSL_REDIRECT', 'False') == 'True'
SECURE_HSTS_SECONDS = int(os.environ.get('SECURE_HSTS_SECONDS', '0'))  # 0 = désactivé
SECURE_HSTS_INCLUDE_SUBDOMAINS = SECURE_HSTS_SECONDS > 0
SECURE_HSTS_PRELOAD = SECURE_HSTS_SECONDS > 0
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_BROWSER_XSS_FILTER = True
X_FRAME_OPTIONS = 'SAMEORIGIN'  # 'DENY' en production

# ========================================
# SESSIONS et CSRF - Configuration sécurisée
# ========================================

# Activer seulement en production (HTTPS requis)
SESSION_COOKIE_SECURE = os.environ.get('SESSION_COOKIE_SECURE', 'False') == 'True'
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = 'Lax'

CSRF_COOKIE_SECURE = os.environ.get('CSRF_COOKIE_SECURE', 'False') == 'True'
CSRF_COOKIE_HTTPONLY = True
CSRF_COOKIE_SAMESITE = 'Lax'

