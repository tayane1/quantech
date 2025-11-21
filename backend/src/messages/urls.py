"""
URLs pour l'application messages.

Ce fichier configure les routes REST pour les endpoints de messagerie :
- /api/messages/conversations/ : Gestion des conversations
- /api/messages/conversations/{id}/messages/ : Messages d'une conversation
- /api/messages/messages/ : Gestion directe des messages

Utilise le DefaultRouter de DRF pour générer automatiquement les routes CRUD.
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from messages.viewsets import ConversationViewSet, MessageViewSet

router = DefaultRouter()
router.register(r"conversations", ConversationViewSet, basename="conversation")
router.register(r"messages", MessageViewSet, basename="message")

# Route spéciale pour les messages d'une conversation
# Cette route doit être avant les routes du router pour éviter les conflits
urlpatterns = [
    path(
        "conversations/<int:conversation_id>/messages/",
        MessageViewSet.as_view({"get": "list", "post": "create"}),
        name="conversation-messages",
    ),
] + router.urls

