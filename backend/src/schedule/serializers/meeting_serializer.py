"""Serializer pour le modèle Meeting (réunions)."""

from rest_framework import serializers
from schedule.models.meeting import Meeting
from employee.models.employee import Employee


class MeetingSerializer(serializers.ModelSerializer):
    """Serializer pour les réunions avec informations des participants."""

    organizer_name = serializers.CharField(
        source="organizer.get_full_name", read_only=True, allow_null=True
    )
    attendees_count = serializers.IntegerField(source="attendees.count", read_only=True)
    attendees_details = serializers.SerializerMethodField()

    class Meta:
        model = Meeting
        fields = [
            "id",
            "title",
            "description",
            "organizer",
            "organizer_name",
            "attendees",
            "attendees_count",
            "attendees_details",
            "start_time",
            "end_time",
            "location",
            "video_conference_link",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["created_at", "updated_at"]

    def get_attendees_details(self, obj):
        """Retourne les détails des participants."""
        return [
            {
                "id": emp.id,
                "full_name": emp.get_full_name(),
                "email": emp.email,
            }
            for emp in obj.attendees.all()
        ]

    def validate(self, attrs):
        """Valide que end_time est après start_time."""
        start_time = attrs.get("start_time") or (
            self.instance.start_time if self.instance else None
        )
        end_time = attrs.get("end_time") or (
            self.instance.end_time if self.instance else None
        )

        if start_time and end_time and end_time <= start_time:
            raise serializers.ValidationError(
                "L'heure de fin doit être après l'heure de début."
            )
        return attrs

