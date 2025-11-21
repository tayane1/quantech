"""
ViewSet pour la gestion des activités du dashboard (Activity).

Ce ViewSet gère les activités affichées sur le dashboard :
- Consultation des activités
- Création d'activités (automatique via signaux ou manuelle)
- Actions personnalisées : activités récentes, par type, par utilisateur
"""

from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from django.utils import timezone
from datetime import timedelta

from dashboard.models.activity import Activity
from dashboard.serializers.activity_serializer import ActivitySerializer


class IsAdminOrHR(permissions.BasePermission):
    """
    Permission personnalisée :
    - Les admins et HR peuvent tout faire
    - Les autres utilisateurs peuvent créer et voir leurs propres activités
    """

    def has_object_permission(self, request, view, obj):
        if request.user.is_staff or request.user.role in ["admin", "hr_manager"]:
            return True
        # Les utilisateurs peuvent voir leurs propres activités
        if hasattr(request.user, "employee") and obj.user == request.user.employee:
            return request.method in permissions.SAFE_METHODS
        return False

    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated


class ActivityViewSet(viewsets.ModelViewSet):
    """
    ViewSet pour les activités du dashboard.
    
    Endpoints disponibles :
    - GET /api/dashboard/activities/ : Liste des activités
    - POST /api/dashboard/activities/ : Créer une activité
    - GET /api/dashboard/activities/{id}/ : Détails d'une activité
    - DELETE /api/dashboard/activities/{id}/ : Supprimer une activité
    - GET /api/dashboard/activities/recent/ : Activités récentes
    - GET /api/dashboard/activities/today/ : Activités d'aujourd'hui
    - GET /api/dashboard/activities/by-type/{type}/ : Activités par type
    - GET /api/dashboard/activities/my-activities/ : Mes activités
    """
    
    queryset = Activity.objects.select_related(
        "user", "related_position", "related_candidate", "related_employee"
    ).all()
    serializer_class = ActivitySerializer
    permission_classes = [permissions.IsAuthenticated, IsAdminOrHR]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ["activity_type", "user"]
    search_fields = ["description"]
    ordering_fields = ["created_at"]
    ordering = ["-created_at"]

    def get_queryset(self):
        """Filtre le queryset selon les permissions."""
        queryset = super().get_queryset()

        # Si admin/HR, retourner tout
        if self.request.user.is_staff or self.request.user.role in [
            "admin",
            "hr_manager",
        ]:
            return queryset

        # Sinon, filtrer par utilisateur
        if hasattr(self.request.user, "employee") and self.request.user.employee:
            return queryset.filter(user=self.request.user.employee)

        return queryset.none()

    def perform_create(self, serializer):
        """Lors de la création, définir automatiquement l'utilisateur si non spécifié."""
        if not serializer.validated_data.get("user") and hasattr(
            self.request.user, "employee"
        ):
            serializer.save(user=self.request.user.employee)
        else:
            serializer.save()

    @action(detail=False, methods=["get"], url_path="recent")
    def recent(self, request):
        """
        Action personnalisée : Récupérer les activités récentes (7 derniers jours).
        GET /api/dashboard/activities/recent/
        """
        seven_days_ago = timezone.now() - timedelta(days=7)
        queryset = self.get_queryset().filter(created_at__gte=seven_days_ago)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=["get"], url_path="today")
    def today(self, request):
        """
        Action personnalisée : Récupérer les activités d'aujourd'hui.
        GET /api/dashboard/activities/today/
        """
        today_start = timezone.now().replace(hour=0, minute=0, second=0, microsecond=0)
        queryset = self.get_queryset().filter(created_at__gte=today_start)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @action(
        detail=False,
        methods=["get"],
        url_path="by-type/(?P<activity_type>[^/.]+)",
    )
    def by_type(self, request, activity_type=None):
        """
        Action personnalisée : Récupérer les activités d'un type spécifique.
        GET /api/dashboard/activities/by-type/{activity_type}/
        """
        queryset = self.get_queryset().filter(activity_type=activity_type)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=["get"], url_path="my-activities")
    def my_activities(self, request):
        """
        Action personnalisée : Récupérer mes activités.
        GET /api/dashboard/activities/my-activities/
        """
        if not hasattr(request.user, "employee") or not request.user.employee:
            return Response(
                {"detail": "Vous n'êtes pas associé à un employé."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        queryset = self.get_queryset().filter(user=request.user.employee)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

