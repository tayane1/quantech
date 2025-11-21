"""Serializer pour le modèle TalentRequest (demandes de talents)."""

from rest_framework import serializers
from recruitment.models.talent_request import TalentRequest
from recruitment.models.job_position import JobPosition


class TalentRequestSerializer(serializers.ModelSerializer):
    """Serializer pour les demandes de talents avec informations contextuelles."""

    position_title = serializers.CharField(
        source="position.title", read_only=True
    )
    position_department = serializers.CharField(
        source="position.department.name", read_only=True, allow_null=True
    )
    requested_by_name = serializers.CharField(
        source="requested_by.get_full_name", read_only=True, allow_null=True
    )
    status_display = serializers.CharField(
        source="get_status_display", read_only=True
    )

    class Meta:
        model = TalentRequest
        fields = [
            "id",
            "position",
            "position_title",
            "position_department",
            "requested_by",
            "requested_by_name",
            "number_of_people",
            "status",
            "status_display",
            "description",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["created_at", "updated_at"]

    def validate_number_of_people(self, value):
        """Valide que le nombre de personnes est positif."""
        if value <= 0:
            raise serializers.ValidationError(
                "Le nombre de personnes doit être supérieur à 0."
            )
        return value

    def validate(self, attrs):
        """Valide la cohérence des données."""
        # Si le statut est "fulfilled", vérifier que la position existe
        if attrs.get("status") == TalentRequest.STATUS_FULFILLED:
            position = attrs.get("position") or (
                self.instance.position if self.instance else None
            )
            if position and position.status == JobPosition.STATUS_CLOSED:
                raise serializers.ValidationError(
                    "Impossible de marquer comme satisfait si l'offre est fermée."
                )
        return attrs

