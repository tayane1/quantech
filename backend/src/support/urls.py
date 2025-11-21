"""
URLs pour l'application support.

Ce fichier configure les routes REST pour les endpoints de support :
- /api/support/support-categories/ : Catégories de support
- /api/support/support-tickets/ : Tickets de support
- /api/support/ticket-comments/ : Commentaires de tickets
- /api/support/ticket-attachments/ : Pièces jointes de tickets

Utilise le DefaultRouter de DRF pour générer automatiquement les routes CRUD.
"""

from rest_framework.routers import DefaultRouter
from support.viewsets import (
    SupportCategoryViewSet,
    SupportTicketViewSet,
    TicketCommentViewSet,
    TicketAttachmentViewSet,
)

router = DefaultRouter()
router.register(
    r"support-categories", SupportCategoryViewSet, basename="support-category"
)
router.register(r"support-tickets", SupportTicketViewSet, basename="support-ticket")
router.register(r"ticket-comments", TicketCommentViewSet, basename="ticket-comment")
router.register(
    r"ticket-attachments", TicketAttachmentViewSet, basename="ticket-attachment"
)

urlpatterns = router.urls

