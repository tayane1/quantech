"""
ViewSet pour la gestion des tâches planifiées (Schedule).

Ce ViewSet implémente les opérations CRUD complètes pour les tâches planifiées :
- Liste, détail, création, modification, suppression
- Actions personnalisées : marquer comme complétée, filtrer par priorité/statut
- Permissions : les employés ne peuvent voir/modifier que leurs propres tâches (sauf admins)
"""

from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter

from schedule.models.schedule_task import Schedule
from schedule.serializers.schedule_serializer import ScheduleSerializer
from employee.models.employee import Employee


class IsAssignedEmployeeOrAdmin(permissions.BasePermission):
    """
    Permission personnalisée :
    - Les admins peuvent tout faire
    - Les employés peuvent voir/modifier uniquement les tâches qui leur sont assignées
    - Les employés peuvent créer des tâches pour eux-mêmes ou pour d'autres (si assigneur)
    """

    def has_object_permission(self, request, view, obj):
        # Les admins ont tous les droits
        if request.user.is_staff or request.user.is_superuser:
            return True
        
        # Vérifier si l'utilisateur est l'employé assigné
        if hasattr(request.user, 'employee'):
            return obj.assigned_to == request.user.employee
        
        return False

    def has_permission(self, request, view):
        # Tous les utilisateurs authentifiés peuvent accéder
        return request.user and request.user.is_authenticated


class ScheduleViewSet(viewsets.ModelViewSet):
    """
    ViewSet pour les tâches planifiées.
    
    Endpoints disponibles :
    - GET /api/schedule/tasks/ : Liste des tâches (filtrées selon permissions)
    - POST /api/schedule/tasks/ : Créer une nouvelle tâche
    - GET /api/schedule/tasks/{id}/ : Détails d'une tâche
    - PUT/PATCH /api/schedule/tasks/{id}/ : Modifier une tâche
    - DELETE /api/schedule/tasks/{id}/ : Supprimer une tâche
    - POST /api/schedule/tasks/{id}/complete/ : Marquer comme complétée
    - GET /api/schedule/tasks/my-tasks/ : Mes tâches assignées
    - GET /api/schedule/tasks/upcoming/ : Tâches à venir
    """
    
    serializer_class = ScheduleSerializer
    permission_classes = [permissions.IsAuthenticated, IsAssignedEmployeeOrAdmin]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['priority', 'completed', 'assigned_to']
    search_fields = ['title', 'description']
    ordering_fields = ['scheduled_date', 'priority', 'created_at']
    ordering = ['-scheduled_date']  # Par défaut, plus récentes en premier

    def get_queryset(self):
        """
        Filtre le queryset selon les permissions :
        - Admins : voient toutes les tâches
        - Employés : voient uniquement leurs tâches assignées
        """
        queryset = Schedule.objects.select_related(
            'assigned_to', 'assigned_by'
        ).all()
        
        # Si admin, retourner tout
        if self.request.user.is_staff or self.request.user.is_superuser:
            return queryset
        
        # Sinon, filtrer par employé assigné
        if hasattr(self.request.user, 'employee'):
            return queryset.filter(assigned_to=self.request.user.employee)
        
        return queryset.none()

    def perform_create(self, serializer):
        """
        Lors de la création, définir automatiquement l'assigneur si non spécifié.
        """
        # Si assigned_by n'est pas fourni, utiliser l'employé de l'utilisateur connecté
        if not serializer.validated_data.get('assigned_by') and hasattr(self.request.user, 'employee'):
            serializer.save(assigned_by=self.request.user.employee)
        else:
            serializer.save()

    @action(detail=True, methods=['post'], url_path='complete')
    def complete(self, request, pk=None):
        """
        Action personnalisée : Marquer une tâche comme complétée.
        POST /api/schedule/tasks/{id}/complete/
        """
        schedule = self.get_object()
        schedule.completed = True
        from django.utils import timezone
        schedule.completed_date = timezone.now()
        schedule.save()
        
        serializer = self.get_serializer(schedule)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=False, methods=['get'], url_path='my-tasks')
    def my_tasks(self, request):
        """
        Action personnalisée : Récupérer uniquement mes tâches assignées.
        GET /api/schedule/tasks/my-tasks/
        """
        if not hasattr(request.user, 'employee'):
            return Response(
                {"detail": "Vous n'êtes pas associé à un employé."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        tasks = self.get_queryset().filter(assigned_to=request.user.employee)
        serializer = self.get_serializer(tasks, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'], url_path='upcoming')
    def upcoming(self, request):
        """
        Action personnalisée : Récupérer les tâches à venir (non complétées, date future).
        GET /api/schedule/tasks/upcoming/
        """
        from django.utils import timezone
        
        queryset = self.get_queryset().filter(
            completed=False,
            scheduled_date__gte=timezone.now()
        ).order_by('scheduled_date')
        
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

