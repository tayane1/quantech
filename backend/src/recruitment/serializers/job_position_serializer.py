"""Serializer pour le modèle JobPosition (offres d'emploi)."""

from rest_framework import serializers
from recruitment.models.job_position import JobPosition
from recruitment.models.candidate import Candidate


class JobPositionSerializer(serializers.ModelSerializer):
    """Serializer pour les offres d'emploi avec statistiques."""

    department_name = serializers.CharField(
        source="department.name", read_only=True, allow_null=True
    )
    candidates_count = serializers.IntegerField(
        source="candidates.count", read_only=True
    )
    active_candidates_count = serializers.SerializerMethodField()
    status_display = serializers.CharField(
        source="get_status_display", read_only=True
    )

    class Meta:
        model = JobPosition
        fields = [
            "id",
            "title",
            "description",
            "department",
            "department_name",
            "status",
            "status_display",
            "urgency",
            "candidates_count",
            "active_candidates_count",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["created_at", "updated_at"]

    def get_active_candidates_count(self, obj):
        """Retourne le nombre de candidats actifs (non rejetés, non embauchés)."""
        return obj.candidates.exclude(
            status__in=[Candidate.STATUS_REJECTED, Candidate.STATUS_HIRED]
        ).count()

    def validate(self, attrs):
        """Valide la cohérence des données."""
        # Si le statut est "closed", vérifier qu'il n'y a pas de candidatures en cours
        if attrs.get("status") == JobPosition.STATUS_CLOSED:
            if self.instance:
                active_candidates = self.instance.candidates.exclude(
                    status__in=[Candidate.STATUS_REJECTED, Candidate.STATUS_HIRED]
                ).exists()
                if active_candidates:
                    raise serializers.ValidationError(
                        "Impossible de fermer une offre avec des candidatures actives."
                    )
        return attrs

