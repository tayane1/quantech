"""
ViewSet pour la gestion des réunions (Meeting).

Ce ViewSet implémente les opérations CRUD complètes pour les réunions :
- Liste, détail, création, modification, suppression
- Actions personnalisées : réunions à venir, mes réunions, ajouter/retirer participants
- Permissions : tous les utilisateurs authentifiés peuvent créer/voir les réunions
"""

from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from django.db.models import Q

from schedule.models.meeting import Meeting
from schedule.serializers.meeting_serializer import MeetingSerializer
from employee.models.employee import Employee


class MeetingViewSet(viewsets.ModelViewSet):
    """
    ViewSet pour les réunions.
    
    Endpoints disponibles :
    - GET /api/schedule/meetings/ : Liste des réunions
    - POST /api/schedule/meetings/ : Créer une nouvelle réunion
    - GET /api/schedule/meetings/{id}/ : Détails d'une réunion
    - PUT/PATCH /api/schedule/meetings/{id}/ : Modifier une réunion
    - DELETE /api/schedule/meetings/{id}/ : Supprimer une réunion
    - GET /api/schedule/meetings/upcoming/ : Réunions à venir
    - GET /api/schedule/meetings/my-meetings/ : Mes réunions (organisateur ou participant)
    - POST /api/schedule/meetings/{id}/add-attendee/ : Ajouter un participant
    - POST /api/schedule/meetings/{id}/remove-attendee/ : Retirer un participant
    """
    
    serializer_class = MeetingSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['organizer']
    search_fields = ['title', 'description', 'location']
    ordering_fields = ['start_time', 'end_time', 'created_at']
    ordering = ['-start_time']  # Par défaut, plus récentes en premier

    def get_queryset(self):
        """
        Retourne toutes les réunions avec les relations optimisées.
        """
        return Meeting.objects.select_related('organizer').prefetch_related('attendees').all()

    def perform_create(self, serializer):
        """
        Lors de la création, définir automatiquement l'organisateur si non spécifié.
        """
        if not serializer.validated_data.get('organizer') and hasattr(self.request.user, 'employee'):
            serializer.save(organizer=self.request.user.employee)
        else:
            serializer.save()

    @action(detail=False, methods=['get'], url_path='upcoming')
    def upcoming(self, request):
        """
        Action personnalisée : Récupérer les réunions à venir.
        GET /api/schedule/meetings/upcoming/
        """
        from django.utils import timezone
        
        queryset = self.get_queryset().filter(
            start_time__gte=timezone.now()
        ).order_by('start_time')
        
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'], url_path='my-meetings')
    def my_meetings(self, request):
        """
        Action personnalisée : Récupérer mes réunions (en tant qu'organisateur ou participant).
        GET /api/schedule/meetings/my-meetings/
        """
        if not hasattr(request.user, 'employee'):
            return Response(
                {"detail": "Vous n'êtes pas associé à un employé."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        employee = request.user.employee
        meetings = self.get_queryset().filter(
            # Réunions où je suis organisateur OU participant
            Q(organizer=employee) | Q(attendees=employee)
        ).distinct()
        
        serializer = self.get_serializer(meetings, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['post'], url_path='add-attendee')
    def add_attendee(self, request, pk=None):
        """
        Action personnalisée : Ajouter un participant à la réunion.
        POST /api/schedule/meetings/{id}/add-attendee/
        Body: {"employee_id": 1}
        """
        meeting = self.get_object()
        employee_id = request.data.get('employee_id')
        
        if not employee_id:
            return Response(
                {"detail": "employee_id est requis."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            employee = Employee.objects.get(id=employee_id)
            meeting.attendees.add(employee)
            serializer = self.get_serializer(meeting)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Employee.DoesNotExist:
            return Response(
                {"detail": "Employé non trouvé."},
                status=status.HTTP_404_NOT_FOUND
            )

    @action(detail=True, methods=['post'], url_path='remove-attendee')
    def remove_attendee(self, request, pk=None):
        """
        Action personnalisée : Retirer un participant de la réunion.
        POST /api/schedule/meetings/{id}/remove-attendee/
        Body: {"employee_id": 1}
        """
        meeting = self.get_object()
        employee_id = request.data.get('employee_id')
        
        if not employee_id:
            return Response(
                {"detail": "employee_id est requis."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            employee = Employee.objects.get(id=employee_id)
            meeting.attendees.remove(employee)
            serializer = self.get_serializer(meeting)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Employee.DoesNotExist:
            return Response(
                {"detail": "Employé non trouvé."},
                status=status.HTTP_404_NOT_FOUND
            )

