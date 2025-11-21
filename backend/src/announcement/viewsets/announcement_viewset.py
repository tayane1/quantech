"""
ViewSet pour la gestion des annonces (Announcement).

Ce ViewSet implémente les opérations CRUD complètes pour les annonces :
- Liste, détail, création, modification, suppression
- Filtrage par auteur, département, statut de publication
- Actions personnalisées : annonces publiées, annonces par département
- Permissions : tout utilisateur authentifié peut lire, seuls les admins/HR peuvent créer/modifier/supprimer
"""

from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from django.db.models import Q, Count
from django.utils import timezone

from announcement.models import Announcement
from announcement.serializers.announcement_serializer import (
    AnnouncementSerializer,
    AnnouncementListSerializer,
)


class IsHRManagerOrAdmin(permissions.BasePermission):
    """
    Permission personnalisée :
    - Les admins et HR managers peuvent tout faire (CRUD complet)
    - Les autres utilisateurs peuvent uniquement lire (GET)
    - Les auteurs peuvent modifier/supprimer leurs propres annonces
    """

    def has_permission(self, request, view):
        """Vérifie la permission au niveau de la vue."""
        # Les méthodes de lecture sont autorisées pour tous les utilisateurs authentifiés
        if request.method in permissions.SAFE_METHODS:
            return request.user and request.user.is_authenticated
        
        # Les méthodes d'écriture nécessitent d'être admin ou HR manager
        return (
            request.user
            and request.user.is_authenticated
            and (
                request.user.is_staff
                or getattr(request.user, "role", None) in ["admin", "hr_manager"]
            )
        )

    def has_object_permission(self, request, view, obj):
        """Vérifie la permission au niveau de l'objet."""
        # Lecture autorisée pour tous
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # Modification/suppression autorisée pour :
        # 1. Admins et HR managers
        # 2. L'auteur de l'annonce
        if request.user.is_staff or getattr(request.user, "role", None) in ["admin", "hr_manager"]:
            return True
        
        # Vérifier si l'utilisateur est l'auteur
        if obj.author and hasattr(request.user, "employee"):
            return obj.author == request.user.employee
        
        return False


class AnnouncementViewSet(viewsets.ModelViewSet):
    """
    ViewSet pour les annonces.
    
    Endpoints disponibles :
    - GET /api/announcement/announcements/ : Liste des annonces
    - POST /api/announcement/announcements/ : Créer une annonce
    - GET /api/announcement/announcements/{id}/ : Détails d'une annonce
    - PUT/PATCH /api/announcement/announcements/{id}/ : Modifier une annonce
    - DELETE /api/announcement/announcements/{id}/ : Supprimer une annonce
    - GET /api/announcement/announcements/published/ : Annonces publiées uniquement
    - GET /api/announcement/announcements/my-announcements/ : Mes annonces (auteur)
    - GET /api/announcement/announcements/visible-to-me/ : Annonces visibles pour moi
    - GET /api/announcement/announcements/{id}/departments/ : Départements ciblés
    """
    
    queryset = Announcement.objects.select_related("author").prefetch_related(
        "departments"
    ).all()
    serializer_class = AnnouncementSerializer
    permission_classes = [permissions.IsAuthenticated, IsHRManagerOrAdmin]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ["author", "published", "visible_to_all"]
    search_fields = ["title", "content"]
    ordering_fields = ["published_date", "updated_date", "title"]
    ordering = ["-published_date"]  # Plus récentes en premier par défaut

    def get_serializer_class(self):
        """Utilise un serializer simplifié pour les listes."""
        if self.action == "list":
            return AnnouncementListSerializer
        return AnnouncementSerializer

    def get_queryset(self):
        """
        Optimise et filtre le queryset selon l'utilisateur.
        
        Pour les utilisateurs non-admin :
        - Ne montre que les annonces publiées
        - Filtre selon la visibilité (tous ou départements de l'utilisateur)
        """
        queryset = super().get_queryset()
        
        # Les admins/HR voient tout
        if self.request.user.is_staff or getattr(self.request.user, "role", None) in ["admin", "hr_manager"]:
            return queryset
        
        # Pour les autres utilisateurs : seulement les annonces publiées
        queryset = queryset.filter(published=True)
        
        # Filtrer selon la visibilité
        user_employee = getattr(self.request.user, "employee", None)
        if user_employee and user_employee.department:
            # Annonces visibles par tous OU annonces ciblant le département de l'utilisateur
            queryset = queryset.filter(
                Q(visible_to_all=True) | Q(departments=user_employee.department)
            ).distinct()
        else:
            # Si l'utilisateur n'a pas de département, seulement les annonces visibles par tous
            queryset = queryset.filter(visible_to_all=True)
        
        return queryset

    def perform_create(self, serializer):
        """
        Personnalise la création d'une annonce.
        
        Définit automatiquement l'auteur si non fourni.
        """
        # Si l'auteur n'est pas dans les données, utiliser l'utilisateur connecté
        if "author" not in serializer.validated_data:
            if hasattr(self.request.user, "employee"):
                serializer.save(author=self.request.user.employee)
            else:
                serializer.save()
        else:
            serializer.save()

    @action(detail=False, methods=["get"], url_path="published")
    def published(self, request):
        """
        Action personnalisée : Récupérer uniquement les annonces publiées.
        GET /api/announcement/announcements/published/
        """
        announcements = self.get_queryset().filter(published=True)
        
        page = self.paginate_queryset(announcements)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(announcements, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=["get"], url_path="my-announcements")
    def my_announcements(self, request):
        """
        Action personnalisée : Récupérer les annonces créées par l'utilisateur connecté.
        GET /api/announcement/announcements/my-announcements/
        """
        user_employee = getattr(request.user, "employee", None)
        if not user_employee:
            return Response(
                {"detail": "L'utilisateur n'a pas de profil employé associé."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        
        announcements = self.get_queryset().filter(author=user_employee)
        
        page = self.paginate_queryset(announcements)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(announcements, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=["get"], url_path="visible-to-me")
    def visible_to_me(self, request):
        """
        Action personnalisée : Récupérer les annonces visibles pour l'utilisateur connecté.
        GET /api/announcement/announcements/visible-to-me/
        
        Prend en compte :
        - Les annonces visibles par tous
        - Les annonces ciblant le département de l'utilisateur
        """
        user_employee = getattr(request.user, "employee", None)
        
        queryset = self.get_queryset().filter(published=True)
        
        if user_employee and user_employee.department:
            # Annonces visibles par tous OU ciblant le département de l'utilisateur
            queryset = queryset.filter(
                Q(visible_to_all=True) | Q(departments=user_employee.department)
            ).distinct()
        else:
            # Seulement les annonces visibles par tous
            queryset = queryset.filter(visible_to_all=True)
        
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=["get"], url_path="departments")
    def departments(self, request, pk=None):
        """
        Action personnalisée : Récupérer les départements ciblés par une annonce.
        GET /api/announcement/announcements/{id}/departments/
        """
        announcement = self.get_object()
        departments = announcement.departments.all()
        
        from department.serializers.department_serializer import DepartmentListSerializer
        
        serializer = DepartmentListSerializer(departments, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=["post"], url_path="publish")
    def publish(self, request, pk=None):
        """
        Action personnalisée : Publier une annonce.
        POST /api/announcement/announcements/{id}/publish/
        """
        announcement = self.get_object()
        announcement.published = True
        announcement.save()
        
        serializer = self.get_serializer(announcement)
        return Response(serializer.data)

    @action(detail=True, methods=["post"], url_path="unpublish")
    def unpublish(self, request, pk=None):
        """
        Action personnalisée : Dépublier une annonce.
        POST /api/announcement/announcements/{id}/unpublish/
        """
        announcement = self.get_object()
        announcement.published = False
        announcement.save()
        
        serializer = self.get_serializer(announcement)
        return Response(serializer.data)

    @action(detail=False, methods=["get"], url_path="statistics")
    def statistics(self, request):
        """
        Action personnalisée : Statistiques globales sur les annonces.
        GET /api/announcement/announcements/statistics/
        """
        queryset = self.get_queryset()
        
        stats = {
            "total": queryset.count(),
            "published": queryset.filter(published=True).count(),
            "unpublished": queryset.filter(published=False).count(),
            "visible_to_all": queryset.filter(visible_to_all=True).count(),
            "by_department": queryset.filter(visible_to_all=False).count(),
            "this_month": queryset.filter(
                published_date__month=timezone.now().month,
                published_date__year=timezone.now().year,
            ).count(),
            "by_author": queryset.values("author__first_name", "author__last_name")
            .annotate(count=Count("id"))
            .order_by("-count")[:10],
        }
        
        return Response(stats)

