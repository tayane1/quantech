# Module Login - Documentation Technique

## 📋 Vue d'ensemble

Le module `login` gère l'authentification complète et la sécurité de l'application WeHR. Il inclut la gestion des connexions, tokens, réinitialisation de mot de passe, protection contre les attaques brute force et authentification à deux facteurs (2FA).

## 🏗️ Architecture

### Structure des fichiers

```
login/
├── models/
│   ├── login_history.py          # Historique des connexions
│   ├── refresh_token.py           # Tokens de rafraîchissement
│   ├── password_reset_token.py   # Tokens de réinitialisation
│   ├── login_attempt.py           # Tentatives de connexion (brute force)
│   └── two_factor_auth.py         # Configuration 2FA
├── serializers/
│   ├── login_history_serializer.py
│   ├── refresh_token_serializer.py
│   ├── password_reset_token_serializer.py
│   ├── login_attempt_serializer.py
│   ├── two_factor_auth_serializer.py
│   └── __init__.py
├── viewsets/
│   ├── login_history_viewset.py
│   ├── refresh_token_viewset.py
│   ├── password_reset_viewset.py
│   ├── login_attempt_viewset.py
│   ├── two_factor_auth_viewset.py
│   └── __init__.py
├── views/
│   └── auth_views.py              # Vues d'authentification (login, logout, refresh)
├── urls.py                         # Configuration des routes
└── README_LOGIN.md                 # Cette documentation
```

## 🔧 Composants

### 1. Vues d'authentification (`views/auth_views.py`)

#### `login_view`
- **Endpoint** : `POST /api/login/login/`
- **Fonctionnalités** :
  - Authentification par email/password
  - Protection contre les attaques brute force (verrouillage après 5 tentatives)
  - Génération de tokens JWT (access + refresh)
  - Enregistrement de l'historique de connexion
  - Détection automatique du device et navigateur

#### `logout_view`
- **Endpoint** : `POST /api/login/logout/`
- **Fonctionnalités** :
  - Révoque le refresh token
  - Enregistre l'heure de déconnexion dans l'historique

#### `refresh_token_view`
- **Endpoint** : `POST /api/login/refresh/`
- **Fonctionnalités** :
  - Rafraîchit le token d'accès
  - Vérifie que le token n'est pas révoqué ou expiré

### 2. ViewSets

#### `LoginHistoryViewSet`
- **Permissions** : Utilisateurs voient leur historique, admins voient tout
- **Endpoints** :
  - `GET /api/login/history/` : Liste de l'historique
  - `GET /api/login/history/my-history/` : Mon historique
  - `GET /api/login/history/recent/` : Connexions récentes (7 jours)

#### `RefreshTokenViewSet`
- **Permissions** : Utilisateurs gèrent leurs tokens, admins voient tout
- **Endpoints** :
  - `GET /api/login/refresh-tokens/my-tokens/` : Mes tokens
  - `POST /api/login/refresh-tokens/{id}/revoke/` : Révoquer un token
  - `POST /api/login/refresh-tokens/revoke-all/` : Révoquer tous mes tokens

#### `PasswordResetViewSet`
- **Permissions** : Public pour la demande, admin pour la consultation
- **Endpoints** :
  - `POST /api/login/password-reset/request/` : Demander une réinitialisation
  - `POST /api/login/password-reset/verify/` : Vérifier un token
  - `POST /api/login/password-reset/reset/` : Réinitialiser le mot de passe

#### `LoginAttemptViewSet`
- **Permissions** : Admins uniquement (lecture seule)
- **Endpoints** :
  - `GET /api/login/attempts/` : Liste des tentatives

#### `TwoFactorAuthViewSet`
- **Permissions** : Utilisateurs gèrent leur 2FA, admins voient tout
- **Endpoints** :
  - `GET /api/login/2fa/my-2fa/` : Ma configuration 2FA
  - `POST /api/login/2fa/setup/` : Configurer la 2FA
  - `POST /api/login/2fa/verify/` : Vérifier un code 2FA
  - `POST /api/login/2fa/enable/` : Activer la 2FA
  - `POST /api/login/2fa/disable/` : Désactiver la 2FA
  - `POST /api/login/2fa/generate-backup-codes/` : Générer des codes de secours

### 3. Sécurité implémentée

#### Protection contre les attaques brute force
- Verrouillage automatique après 5 tentatives échouées
- Durée de verrouillage : 15 minutes
- Suivi par email + IP address
- Réinitialisation automatique après verrouillage

#### Gestion des tokens
- Tokens JWT avec expiration (5 min pour access, 1 jour pour refresh)
- Révocation des tokens possible
- Stockage des refresh tokens en base de données
- Vérification de l'expiration et de la révocation

#### Authentification à deux facteurs
- Support de 3 méthodes : Email, SMS, TOTP (Authenticator App)
- Génération de codes de secours
- Vérification avant activation
- QR code pour configuration TOTP

## 📡 Endpoints API

### Authentification

```bash
# Connexion
POST /api/login/login/
{
  "email": "user@example.com",
  "password": "password123"
}
# Retourne : access_token, refresh_token, user

# Déconnexion
POST /api/login/logout/
{
  "refresh_token": "abc123..."
}

# Rafraîchir le token
POST /api/login/refresh/
{
  "refresh_token": "abc123..."
}
```

### Réinitialisation de mot de passe

```bash
# Demander une réinitialisation
POST /api/login/password-reset/request/
{
  "email": "user@example.com"
}

# Vérifier un token
POST /api/login/password-reset/verify/
{
  "token": "abc123..."
}

# Réinitialiser le mot de passe
POST /api/login/password-reset/reset/
{
  "token": "abc123...",
  "new_password": "newpass123"
}
```

### Authentification à deux facteurs

```bash
# Configurer la 2FA
POST /api/login/2fa/setup/
{
  "method": "totp"
}
# Retourne : secret, provisioning_uri (QR code)

# Vérifier le code
POST /api/login/2fa/verify/
{
  "code": "123456"
}
# Retourne : backup_codes

# Activer la 2FA
POST /api/login/2fa/enable/

# Désactiver la 2FA
POST /api/login/2fa/disable/
```

### Historique et tokens

```bash
# Mon historique
GET /api/login/history/my-history/

# Mes tokens
GET /api/login/refresh-tokens/my-tokens/

# Révoquer tous mes tokens
POST /api/login/refresh-tokens/revoke-all/
```

## 🔐 Sécurité

### Validations implémentées

1. **Connexion** :
   - Vérification du verrouillage (brute force)
   - Authentification sécurisée
   - Enregistrement de toutes les tentatives

2. **Réinitialisation de mot de passe** :
   - Tokens uniques et sécurisés
   - Expiration après 1 heure
   - Validation du mot de passe (min 8 caractères)
   - Tokens à usage unique

3. **2FA** :
   - Vérification avant activation
   - Codes de secours générés automatiquement
   - Support de plusieurs méthodes

4. **Tokens** :
   - Vérification de l'expiration
   - Vérification de la révocation
   - Stockage sécurisé en base

### Bonnes pratiques de sécurité

- **Ne pas révéler si un email existe** : Messages génériques pour la réinitialisation
- **Verrouillage progressif** : Protection contre les attaques brute force
- **Tokens sécurisés** : Génération avec `secrets.token_urlsafe()`
- **Expiration automatique** : Tokens avec durée de vie limitée
- **Révocation possible** : Contrôle total sur les tokens actifs

## 🎯 Bonnes pratiques appliquées

1. **Séparation des responsabilités** :
   - Vues pour l'authentification principale
   - ViewSets pour la gestion des ressources
   - Serializers pour la validation

2. **Sécurité renforcée** :
   - Protection brute force
   - Gestion des tokens
   - 2FA optionnelle

3. **Traçabilité** :
   - Historique complet des connexions
   - Suivi des tentatives échouées
   - Enregistrement des déconnexions

4. **Expérience utilisateur** :
   - Messages d'erreur clairs
   - Codes de secours pour 2FA
   - Gestion simple des tokens

## 🚀 Intégration

### Dans `backend/urls.py`

```python
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path("api/users/", include("users.urls")),
    path("api/schedule/", include("schedule.urls")),
    path("api/recruitment/", include("recruitment.urls")),
    path("api/login/", include("login.urls")),  # Ajouter cette ligne
]
```

### Dépendances requises

- `djangorestframework` : Framework REST
- `rest_framework_simplejwt` : Authentification JWT
- `pyotp` : Pour la génération de codes TOTP (2FA)
  ```bash
  pip install pyotp
  ```

### Configuration JWT dans `settings.py`

```python
SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(minutes=5),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=1),
    # ... autres configurations
}
```

## 📝 Exemples d'utilisation

### Workflow complet d'authentification

```python
# 1. Connexion
POST /api/login/login/
{
  "email": "user@example.com",
  "password": "password123"
}
# → access_token, refresh_token

# 2. Utiliser le token pour les requêtes authentifiées
GET /api/users/me/
Headers: Authorization: Bearer <access_token>

# 3. Rafraîchir le token avant expiration
POST /api/login/refresh/
{
  "refresh_token": "<refresh_token>"
}
# → nouveau access_token

# 4. Déconnexion
POST /api/login/logout/
{
  "refresh_token": "<refresh_token>"
}
```

### Workflow de réinitialisation de mot de passe

```python
# 1. Demander une réinitialisation
POST /api/login/password-reset/request/
{
  "email": "user@example.com"
}

# 2. Vérifier le token (optionnel)
POST /api/login/password-reset/verify/
{
  "token": "<token_reçu_par_email>"
}

# 3. Réinitialiser le mot de passe
POST /api/login/password-reset/reset/
{
  "token": "<token>",
  "new_password": "newSecurePassword123"
}
```

### Workflow 2FA

```python
# 1. Configurer la 2FA
POST /api/login/2fa/setup/
{
  "method": "totp"
}
# → secret, provisioning_uri (pour QR code)

# 2. Scanner le QR code avec l'app d'authentification
# 3. Vérifier avec un code
POST /api/login/2fa/verify/
{
  "code": "123456"
}
# → backup_codes

# 4. Activer la 2FA
POST /api/login/2fa/enable/
```

## 🔍 Tests recommandés

1. **Tests unitaires** :
   - Authentification réussie/échouée
   - Protection brute force
   - Validation des tokens
   - Génération de codes 2FA

2. **Tests d'intégration** :
   - Workflow complet de connexion
   - Workflow de réinitialisation
   - Workflow 2FA
   - Révocation de tokens

3. **Tests de sécurité** :
   - Tentatives de brute force
   - Tokens expirés/révoqués
   - Accès non autorisé

## 📚 Références

- [Django REST Framework - Authentication](https://www.django-rest-framework.org/api-guide/authentication/)
- [Simple JWT](https://django-rest-framework-simplejwt.readthedocs.io/)
- [PyOTP - TOTP](https://github.com/pyotp/pyotp)
- [OWASP - Authentication Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Authentication_Cheat_Sheet.html)

