"""
ViewSet pour la gestion des catégories de support (SupportCategory).

Ce ViewSet implémente les opérations CRUD complètes pour les catégories :
- Liste, détail, création, modification, suppression
- Actions personnalisées : activer/désactiver, statistiques
- Permissions : tout utilisateur authentifié peut lire, seuls les admins peuvent créer/modifier/supprimer
"""

from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from django.db.models import Count

from support.models import SupportCategory
from support.serializers.support_category_serializer import SupportCategorySerializer


class IsHRManagerOrAdmin(permissions.BasePermission):
    """
    Permission personnalisée :
    - Les admins et HR managers peuvent tout faire
    - Les autres utilisateurs peuvent uniquement lire
    """

    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return request.user and request.user.is_authenticated
        return (
            request.user
            and request.user.is_authenticated
            and (
                request.user.is_staff
                or getattr(request.user, "role", None) in ["admin", "hr_manager"]
            )
        )


class SupportCategoryViewSet(viewsets.ModelViewSet):
    """
    ViewSet pour les catégories de support.
    
    Endpoints disponibles :
    - GET /api/support/support-categories/ : Liste des catégories
    - POST /api/support/support-categories/ : Créer une catégorie (admin seulement)
    - GET /api/support/support-categories/{id}/ : Détails d'une catégorie
    - PUT/PATCH /api/support/support-categories/{id}/ : Modifier une catégorie (admin seulement)
    - DELETE /api/support/support-categories/{id}/ : Supprimer une catégorie (admin seulement)
    - POST /api/support/support-categories/{id}/activate/ : Activer une catégorie
    - POST /api/support/support-categories/{id}/deactivate/ : Désactiver une catégorie
    - GET /api/support/support-categories/{id}/tickets/ : Tickets d'une catégorie
    - GET /api/support/support-categories/active/ : Catégories actives uniquement
    - GET /api/support/support-categories/statistics/ : Statistiques
    """
    
    queryset = SupportCategory.objects.prefetch_related("tickets").all()
    serializer_class = SupportCategorySerializer
    permission_classes = [permissions.IsAuthenticated, IsHRManagerOrAdmin]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ["is_active"]
    search_fields = ["name", "description"]
    ordering_fields = ["name", "created_at"]
    ordering = ["name"]

    @action(detail=True, methods=["post"], url_path="activate")
    def activate(self, request, pk=None):
        """Active une catégorie."""
        category = self.get_object()
        category.is_active = True
        category.save()
        
        serializer = self.get_serializer(category)
        return Response(serializer.data)

    @action(detail=True, methods=["post"], url_path="deactivate")
    def deactivate(self, request, pk=None):
        """Désactive une catégorie."""
        category = self.get_object()
        category.is_active = False
        category.save()
        
        serializer = self.get_serializer(category)
        return Response(serializer.data)

    @action(detail=True, methods=["get"], url_path="tickets")
    def tickets(self, request, pk=None):
        """Récupère les tickets d'une catégorie."""
        category = self.get_object()
        tickets = category.tickets.all()
        
        from support.serializers.support_ticket_serializer import (
            SupportTicketListSerializer,
        )
        
        page = self.paginate_queryset(tickets)
        if page is not None:
            serializer = SupportTicketListSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = SupportTicketListSerializer(tickets, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=["get"], url_path="active")
    def active(self, request):
        """Récupère uniquement les catégories actives."""
        categories = self.get_queryset().filter(is_active=True)
        
        page = self.paginate_queryset(categories)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(categories, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=["get"], url_path="statistics")
    def statistics(self, request):
        """Statistiques sur les catégories."""
        queryset = self.get_queryset()
        
        stats = {
            "total": queryset.count(),
            "active": queryset.filter(is_active=True).count(),
            "inactive": queryset.filter(is_active=False).count(),
            "by_category": queryset.annotate(
                tickets_count=Count("tickets")
            ).values("id", "name", "tickets_count").order_by("-tickets_count"),
        }
        
        return Response(stats)

