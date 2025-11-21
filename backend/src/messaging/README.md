# 💬 Module Messaging - Documentation

## 📋 Vue d'ensemble

Le module **messaging** (renommé pour éviter le conflit avec l'app Django intégrée `messages`) implémente un système de messagerie complet et sécurisé pour WeHR.

### 🔒 Sécurité Robuste

Le module a été conçu avec une sécurité maximale en tête :

1. **Permissions strictes** :
   - Un utilisateur ne peut voir que ses propres conversations
   - Un utilisateur ne peut envoyer des messages que dans ses conversations
   - Seul l'expéditeur peut modifier/supprimer ses messages
   - Les admins ont des droits étendus pour la modération

2. **Validation stricte** :
   - Contenu non vide
   - Longueur limitée (5000 caractères max)
   - Protection contre les injections XSS
   - Validation des participants

3. **Protection contre le spam** :
   - Rate limiting (20 messages par minute par utilisateur)
   - Validation des participants
   - Protection contre les conversations vides

4. **Soft Delete** :
   - Les conversations et messages sont marqués comme supprimés, pas réellement supprimés
   - Permet la modération et la récupération

## 📦 Modèles

### Conversation

Représente une conversation entre plusieurs utilisateurs.

**Champs** :
- `participants` : ManyToMany vers CustomUser
- `created_by` : ForeignKey vers CustomUser
- `subject` : Sujet de la conversation (optionnel)
- `conversation_type` : "direct" ou "group"
- `is_archived` : Boolean
- `is_deleted` : Boolean (soft delete)
- `last_message_at` : DateTime du dernier message

**Validations** :
- Minimum 2 participants
- Conversations directes : exactement 2 participants
- L'utilisateur doit être un participant

### Message

Représente un message dans une conversation.

**Champs** :
- `conversation` : ForeignKey vers Conversation
- `sender` : ForeignKey vers CustomUser
- `recipient` : ForeignKey vers CustomUser (pour messages directs)
- `content` : TextField (max 5000 caractères)
- `attachment` : FileField (optionnel)
- `is_read` : Boolean
- `read_at` : DateTime
- `is_deleted` : Boolean (soft delete)

**Validations** :
- Contenu non vide (min 1 caractère)
- Longueur limitée à 5000 caractères
- Protection contre XSS (patterns suspects)
- L'expéditeur doit être un participant de la conversation
- Pour messages directs : destinataire obligatoire

### MessageReadStatus

Statut de lecture d'un message par utilisateur (utile pour groupes).

**Champs** :
- `message` : ForeignKey vers Message
- `user` : ForeignKey vers CustomUser
- `is_read` : Boolean
- `read_at` : DateTime

## 🔐 Permissions

### IsParticipantOrAdmin

**Conversations** :
- L'utilisateur doit être un participant
- Les admins peuvent voir toutes les conversations

### CanSendMessage

**Messages** :
- L'utilisateur doit être un participant de la conversation
- La conversation ne doit pas être supprimée

### CanModifyMessage

**Messages** :
- Seul l'expéditeur peut modifier/supprimer son message
- Les admins peuvent supprimer n'importe quel message (modération)

## 📡 Endpoints API

### Conversations

- `GET /api/messages/conversations/` : Liste des conversations de l'utilisateur
- `POST /api/messages/conversations/` : Créer une conversation
- `GET /api/messages/conversations/{id}/` : Détails d'une conversation
- `PATCH /api/messages/conversations/{id}/` : Modifier une conversation
- `DELETE /api/messages/conversations/{id}/` : Supprimer (soft delete)
- `POST /api/messages/conversations/{id}/mark-read/` : Marquer comme lue
- `POST /api/messages/conversations/{id}/archive/` : Archiver
- `POST /api/messages/conversations/{id}/unarchive/` : Désarchiver
- `GET /api/messages/conversations/unread/` : Conversations non lues
- `GET /api/messages/conversations/with-user/{user_id}/` : Conversation avec un utilisateur

### Messages

- `GET /api/messages/conversations/{conversation_id}/messages/` : Liste des messages
- `POST /api/messages/conversations/{conversation_id}/messages/` : Envoyer un message
- `GET /api/messages/messages/{id}/` : Détails d'un message
- `PATCH /api/messages/messages/{id}/` : Modifier un message
- `DELETE /api/messages/messages/{id}/` : Supprimer (soft delete)
- `POST /api/messages/messages/{id}/mark-read/` : Marquer comme lu

## 🔧 Configuration

### Installation

1. L'app est déjà ajoutée dans `INSTALLED_APPS` :
   ```python
   "messaging.apps.MessagingConfig",
   ```

2. URLs configurées dans `backend/urls.py` :
   ```python
   path("api/messages/", include("messaging.urls")),
   ```

3. Migrations :
   ```bash
   python manage.py makemigrations messaging
   python manage.py migrate messaging
   ```

## 📊 Filtrage et Recherche

### Conversations

- **Filtres** : `conversation_type`, `is_archived`
- **Recherche** : `subject`
- **Tri** : `last_message_at`, `created_at`

### Messages

- **Filtres** : `conversation`, `sender`, `recipient`, `is_read`
- **Recherche** : `content`
- **Tri** : `created_at`

## 🚀 Utilisation

### Créer une conversation directe

```python
POST /api/messages/conversations/
{
    "participants_ids": [1, 2],
    "conversation_type": "direct"
}
```

### Envoyer un message

```python
POST /api/messages/conversations/1/messages/
{
    "content": "Bonjour !",
    "recipient": 2
}
```

### Marquer une conversation comme lue

```python
POST /api/messages/conversations/1/mark-read/
```

## ⚠️ Limitations de Sécurité Actuelles

1. **Rate Limiting** : 20 messages/minute par utilisateur (basique)
   - À améliorer avec `django-ratelimit` en production

2. **Taille des fichiers** : Pas de limite explicite sur les attachments
   - À ajouter dans `settings.py` :
     ```python
     FILE_UPLOAD_MAX_MEMORY_SIZE = 5 * 1024 * 1024  # 5MB
     ```

3. **Nombre de participants** : Maximum 50 par conversation
   - Modifiable dans `ConversationCreateSerializer`

## 🔄 Signaux

- **post_save Message** : Met à jour `conversation.last_message_at`
- **pre_delete Conversation** : Soft delete des messages associés

## 📝 Admin Django

L'admin Django permet de :
- Voir toutes les conversations et messages
- Modérer les contenus
- Voir les statuts de lecture
- Rechercher par utilisateur, contenu, etc.

## 🧪 Tests Recommandés

1. **Permissions** : Vérifier qu'un utilisateur ne voit que ses conversations
2. **Validation** : Tester les limites de longueur et contenu vide
3. **Rate Limiting** : Envoyer plus de 20 messages/minute
4. **Soft Delete** : Vérifier que les messages ne sont pas réellement supprimés
5. **Cross-User** : Tester qu'un utilisateur ne peut pas voir les messages d'autrui

## 🔐 Sécurité en Production

1. **HTTPS obligatoire** : Pour protéger les messages en transit
2. **Rate Limiting avancé** : Utiliser `django-ratelimit` avec Redis
3. **Chiffrement** : Considérer le chiffrement end-to-end pour messages sensibles
4. **Audit Log** : Logger toutes les actions importantes
5. **Backup** : Sauvegarder régulièrement les conversations

## 📚 Références

- [Django REST Framework - ViewSets](https://www.django-rest-framework.org/api-guide/viewsets/)
- [Django Permissions](https://docs.djangoproject.com/en/stable/topics/auth/)
- [Django Signals](https://docs.djangoproject.com/en/stable/topics/signals/)

