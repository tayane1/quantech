"""Serializer pour le modèle HiringProcess (processus d'embauche)."""

from rest_framework import serializers
from recruitment.models.hiring_process import HiringProcess
from recruitment.models.candidate import Candidate


class HiringProcessSerializer(serializers.ModelSerializer):
    """Serializer pour les étapes du processus d'embauche."""

    candidate_name = serializers.CharField(
        source="candidate.get_full_name", read_only=True
    )
    candidate_email = serializers.CharField(
        source="candidate.email", read_only=True
    )
    candidate_position = serializers.CharField(
        source="candidate.position.title", read_only=True
    )
    interviewer_name = serializers.CharField(
        source="interviewer.get_full_name", read_only=True, allow_null=True
    )

    class Meta:
        model = HiringProcess
        fields = [
            "id",
            "candidate",
            "candidate_name",
            "candidate_email",
            "candidate_position",
            "stage",
            "scheduled_date",
            "interviewer",
            "interviewer_name",
            "feedback",
            "result",
            "created_at",
        ]
        read_only_fields = ["created_at"]

    def validate_scheduled_date(self, value):
        """Valide que la date planifiée est dans le futur."""
        from django.utils import timezone

        if self.instance is None and value < timezone.now():
            raise serializers.ValidationError(
                "La date planifiée ne peut pas être dans le passé."
            )
        return value

    def validate(self, attrs):
        """Valide la cohérence des données."""
        candidate = attrs.get("candidate") or (
            self.instance.candidate if self.instance else None
        )
        
        # Vérifier que le candidat n'est pas déjà embauché ou rejeté
        if candidate:
            if candidate.status == Candidate.STATUS_HIRED:
                raise serializers.ValidationError(
                    "Impossible d'ajouter une étape pour un candidat déjà embauché."
                )
            if candidate.status == Candidate.STATUS_REJECTED:
                raise serializers.ValidationError(
                    "Impossible d'ajouter une étape pour un candidat rejeté."
                )
        
        return attrs

