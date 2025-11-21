"""
ViewSet pour la gestion des modèles d'emails (EmailTemplate).

Ce ViewSet implémente les opérations CRUD complètes pour les modèles d'emails :
- Liste, détail, création, modification, suppression
- Actions personnalisées : activer/désactiver, dupliquer, prévisualisation
- Permissions : seuls les admins peuvent gérer les modèles d'emails
"""

from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter

from settings.models import EmailTemplate
from settings.serializers.email_template_serializer import (
    EmailTemplateSerializer,
    EmailTemplateListSerializer,
)


class EmailTemplateViewSet(viewsets.ModelViewSet):
    """
    ViewSet pour les modèles d'emails.
    
    Endpoints disponibles :
    - GET /api/settings/email-templates/ : Liste des modèles
    - POST /api/settings/email-templates/ : Créer un modèle (admin seulement)
    - GET /api/settings/email-templates/{id}/ : Détails d'un modèle
    - PUT/PATCH /api/settings/email-templates/{id}/ : Modifier un modèle (admin seulement)
    - DELETE /api/settings/email-templates/{id}/ : Supprimer un modèle (admin seulement)
    - POST /api/settings/email-templates/{id}/activate/ : Activer un modèle
    - POST /api/settings/email-templates/{id}/deactivate/ : Désactiver un modèle
    - POST /api/settings/email-templates/{id}/duplicate/ : Dupliquer un modèle
    - GET /api/settings/email-templates/{id}/preview/ : Prévisualiser un modèle
    - GET /api/settings/email-templates/by-type/{type}/ : Modèles par type
    """
    
    queryset = EmailTemplate.objects.all()
    serializer_class = EmailTemplateSerializer
    permission_classes = [permissions.IsAdminUser]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ["template_type", "is_active"]
    search_fields = ["name", "subject"]
    ordering_fields = ["name", "created_at"]
    ordering = ["name"]

    def get_serializer_class(self):
        """Utilise un serializer simplifié pour les listes."""
        if self.action == "list":
            return EmailTemplateListSerializer
        return EmailTemplateSerializer

    @action(detail=True, methods=["post"], url_path="activate")
    def activate(self, request, pk=None):
        """
        Action personnalisée : Activer un modèle d'email.
        POST /api/settings/email-templates/{id}/activate/
        """
        template = self.get_object()
        template.is_active = True
        template.save()
        
        serializer = self.get_serializer(template)
        return Response(serializer.data)

    @action(detail=True, methods=["post"], url_path="deactivate")
    def deactivate(self, request, pk=None):
        """
        Action personnalisée : Désactiver un modèle d'email.
        POST /api/settings/email-templates/{id}/deactivate/
        """
        template = self.get_object()
        template.is_active = False
        template.save()
        
        serializer = self.get_serializer(template)
        return Response(serializer.data)

    @action(detail=True, methods=["post"], url_path="duplicate")
    def duplicate(self, request, pk=None):
        """
        Action personnalisée : Dupliquer un modèle d'email.
        POST /api/settings/email-templates/{id}/duplicate/
        """
        original = self.get_object()
        new_name = request.data.get("name", f"{original.name} (Copie)")
        
        # Vérifier que le nom n'existe pas déjà
        if EmailTemplate.objects.filter(name=new_name).exists():
            return Response(
                {"name": "Un modèle avec ce nom existe déjà."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        
        # Dupliquer le modèle
        duplicate = EmailTemplate.objects.create(
            name=new_name,
            template_type=original.template_type,
            subject=original.subject,
            body_html=original.body_html,
            body_text=original.body_text,
            is_active=False,  # Désactivé par défaut pour la copie
        )
        
        serializer = self.get_serializer(duplicate)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=["get"], url_path="preview")
    def preview(self, request, pk=None):
        """
        Action personnalisée : Prévisualiser un modèle d'email.
        GET /api/settings/email-templates/{id}/preview/
        """
        template = self.get_object()
        
        # Prévisualisation avec des données de test
        preview_data = {
            "template": {
                "name": template.name,
                "subject": template.subject,
                "body_html": template.body_html,
                "body_text": template.body_text,
            },
            "sample_data": {
                "user_name": "John Doe",
                "company_name": "Mon Entreprise",
                "reset_link": "https://example.com/reset-password?token=abc123",
            },
        }
        
        return Response(preview_data)

    @action(detail=False, methods=["get"], url_path="by-type/(?P<template_type>[^/.]+)")
    def by_type(self, request, template_type=None):
        """
        Action personnalisée : Récupérer les modèles par type.
        GET /api/settings/email-templates/by-type/{type}/
        """
        templates = self.get_queryset().filter(template_type=template_type)
        
        page = self.paginate_queryset(templates)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(templates, many=True)
        return Response(serializer.data)

