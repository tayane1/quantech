"""Serializer pour le modèle TicketComment (commentaires de tickets)."""

from rest_framework import serializers
from support.models import TicketComment


class TicketCommentSerializer(serializers.ModelSerializer):
    """
    Serializer pour les commentaires de tickets.
    
    Inclut :
    - Informations du commentaire
    - Informations de l'auteur
    - Informations du ticket associé
    """

    author_name = serializers.SerializerMethodField()
    author_email = serializers.CharField(source="author.email", read_only=True)
    ticket_title = serializers.CharField(source="ticket.title", read_only=True)

    class Meta:
        model = TicketComment
        fields = [
            "id",
            "ticket",
            "ticket_title",
            "author",
            "author_name",
            "author_email",
            "content",
            "is_internal",
            "attachments",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["created_at", "updated_at"]

    def get_author_name(self, obj):
        """Retourne le nom complet de l'auteur."""
        if obj.author:
            return f"{obj.author.first_name} {obj.author.last_name}"
        return None

    def create(self, validated_data):
        """Crée un nouveau commentaire."""
        # Si l'auteur n'est pas fourni, utiliser l'utilisateur connecté
        if "author" not in validated_data:
            request = self.context.get("request")
            if request and hasattr(request, "user"):
                validated_data["author"] = request.user

        return super().create(validated_data)

