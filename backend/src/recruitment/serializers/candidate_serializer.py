"""Serializer pour le modèle Candidate (candidats)."""

from rest_framework import serializers
from recruitment.models.candidate import Candidate
from recruitment.models.job_position import JobPosition


class CandidateSerializer(serializers.ModelSerializer):
    """Serializer pour les candidats avec informations de l'offre."""

    position_title = serializers.CharField(
        source="position.title", read_only=True
    )
    position_department = serializers.CharField(
        source="position.department.name", read_only=True, allow_null=True
    )
    full_name = serializers.SerializerMethodField()
    status_display = serializers.CharField(
        source="get_status_display", read_only=True
    )
    hiring_process_count = serializers.IntegerField(
        source="hiring_process.count", read_only=True
    )

    class Meta:
        model = Candidate
        fields = [
            "id",
            "first_name",
            "last_name",
            "full_name",
            "email",
            "phone",
            "resume",
            "position",
            "position_title",
            "position_department",
            "status",
            "status_display",
            "applied_date",
            "updated_at",
            "notes",
            "hiring_process_count",
        ]
        read_only_fields = ["applied_date", "updated_at"]

    def get_full_name(self, obj):
        """Retourne le nom complet du candidat."""
        return f"{obj.first_name} {obj.last_name}"

    def validate_email(self, value):
        """Valide l'unicité de l'email."""
        queryset = Candidate.objects.filter(email=value)
        if self.instance:
            queryset = queryset.exclude(pk=self.instance.pk)
        if queryset.exists():
            raise serializers.ValidationError(
                "Un candidat avec cet email existe déjà."
            )
        return value

    def validate_resume(self, value):
        """Valide le fichier CV (taille et type)."""
        if value:
            # Limiter la taille à 5MB
            if value.size > 5 * 1024 * 1024:
                raise serializers.ValidationError(
                    "Le fichier CV ne doit pas dépasser 5MB."
                )
            # Vérifier l'extension
            allowed_extensions = [".pdf", ".doc", ".docx"]
            if not any(value.name.lower().endswith(ext) for ext in allowed_extensions):
                raise serializers.ValidationError(
                    "Le fichier doit être au format PDF, DOC ou DOCX."
                )
        return value

