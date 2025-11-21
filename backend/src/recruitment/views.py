"""
Vues pour l'application recruitment.
"""

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import permissions
from django.db.models import Count, Q, Avg
from django.utils import timezone
from datetime import timedelta

from recruitment.models.job_position import JobPosition
from recruitment.models.candidate import Candidate
from recruitment.models.hiring_process import HiringProcess


class RecruitmentStatisticsView(APIView):
    """
    Vue API pour les statistiques globales du recrutement.
    
    Endpoint : GET /api/recruitment/statistics/
    
    Retourne :
    - Nombre total de postes
    - Nombre de postes ouverts/fermés/urgents
    - Nombre total de candidats
    - Répartition des candidats par statut
    - Nombre de processus actifs
    - Temps moyen de recrutement
    """
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        """Récupère les statistiques globales du recrutement."""
        
        # Statistiques des postes
        total_positions = JobPosition.objects.count()
        open_positions = JobPosition.objects.filter(status=JobPosition.STATUS_OPEN).count()
        closed_positions = JobPosition.objects.filter(status=JobPosition.STATUS_CLOSED).count()
        urgent_positions = JobPosition.objects.filter(urgency=True, status=JobPosition.STATUS_OPEN).count()
        
        # Statistiques des candidats
        total_candidates = Candidate.objects.count()
        
        # Répartition par statut (mapper les statuts backend vers frontend)
        # Le frontend attend : 'applied' | 'screening' | 'interview' | 'offer' | 'hired' | 'rejected'
        # Backend a : 'applied', 'reviewing', 'interview', 'offered', 'rejected', 'hired'
        candidates_by_status = {
            'applied': Candidate.objects.filter(status=Candidate.STATUS_APPLIED).count(),
            'screening': Candidate.objects.filter(status=Candidate.STATUS_REVIEWING).count(),  # 'reviewing' -> 'screening'
            'interview': Candidate.objects.filter(status=Candidate.STATUS_INTERVIEW).count(),
            'offer': Candidate.objects.filter(status=Candidate.STATUS_OFFERED).count(),  # 'offered' -> 'offer'
            'hired': Candidate.objects.filter(status=Candidate.STATUS_HIRED).count(),
            'rejected': Candidate.objects.filter(status=Candidate.STATUS_REJECTED).count(),
        }
        
        # Processus actifs (candidats non rejetés et non embauchés)
        active_processes = Candidate.objects.exclude(
            status__in=[Candidate.STATUS_REJECTED, Candidate.STATUS_HIRED]
        ).count()
        
        # Temps moyen de recrutement (pour les candidats embauchés)
        # Calculer la moyenne des jours entre applied_date et updated_at pour les candidats embauchés
        hired_candidates = Candidate.objects.filter(status=Candidate.STATUS_HIRED).select_related()
        average_time_to_hire = 0
        if hired_candidates.exists():
            time_deltas = []
            for candidate in hired_candidates:
                if hasattr(candidate, 'applied_date') and hasattr(candidate, 'updated_at'):
                    if candidate.applied_date and candidate.updated_at:
                        delta = (candidate.updated_at - candidate.applied_date).total_seconds() / 86400  # Conversion en jours
                        if delta > 0:
                            time_deltas.append(delta)
            if time_deltas:
                average_time_to_hire = sum(time_deltas) / len(time_deltas)
        
        statistics = {
            'total_positions': total_positions,
            'open_positions': open_positions,
            'closed_positions': closed_positions,
            'urgent_positions': urgent_positions,
            'total_candidates': total_candidates,
            'candidates_by_status': candidates_by_status,
            'active_processes': active_processes,
            'average_time_to_hire': round(average_time_to_hire, 2)
        }
        
        return Response(statistics)
