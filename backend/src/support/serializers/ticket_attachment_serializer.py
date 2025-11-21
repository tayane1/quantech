"""Serializer pour le modèle TicketAttachment (pièces jointes de tickets)."""

from rest_framework import serializers
from support.models import TicketAttachment


class TicketAttachmentSerializer(serializers.ModelSerializer):
    """
    Serializer pour les pièces jointes de tickets.
    
    Inclut :
    - Informations du fichier
    - Informations de l'uploader
    - Informations du ticket/commentaire associé
    """

    uploaded_by_name = serializers.SerializerMethodField()
    ticket_title = serializers.SerializerMethodField()

    class Meta:
        model = TicketAttachment
        fields = [
            "id",
            "ticket",
            "comment",
            "file",
            "filename",
            "file_size",
            "file_type",
            "uploaded_by",
            "uploaded_by_name",
            "ticket_title",
            "created_at",
        ]
        read_only_fields = ["created_at", "filename", "file_size", "file_type"]

    def get_uploaded_by_name(self, obj):
        """Retourne le nom complet de celui qui a uploadé le fichier."""
        if obj.uploaded_by:
            return f"{obj.uploaded_by.first_name} {obj.uploaded_by.last_name}"
        return None

    def get_ticket_title(self, obj):
        """Retourne le titre du ticket associé."""
        if obj.ticket:
            return obj.ticket.title
        elif obj.comment and obj.comment.ticket:
            return obj.comment.ticket.title
        return None

    def create(self, validated_data):
        """Crée une nouvelle pièce jointe."""
        # Si l'uploader n'est pas fourni, utiliser l'utilisateur connecté
        if "uploaded_by" not in validated_data:
            request = self.context.get("request")
            if request and hasattr(request, "user"):
                validated_data["uploaded_by"] = request.user

        # Extraire les informations du fichier
        file = validated_data.get("file")
        if file:
            validated_data["filename"] = file.name
            validated_data["file_size"] = file.size
            # Déterminer le type de fichier
            if hasattr(file, "content_type"):
                validated_data["file_type"] = file.content_type
            else:
                validated_data["file_type"] = "application/octet-stream"

        return super().create(validated_data)

