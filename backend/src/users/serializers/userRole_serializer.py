"""Serializer pour le modèle UserRole (rôles utilisateur)."""

from rest_framework import serializers
from django.contrib.auth.models import Permission
from users.models import UserRole


class UserRoleSerializer(serializers.ModelSerializer):
    """
    Serializer pour les rôles utilisateur.

    Inclut :
    - Informations du rôle
    - Liste des permissions associées
    - Nombre d'utilisateurs ayant ce rôle
    """

    permissions_names = serializers.SerializerMethodField()
    permission_ids = serializers.PrimaryKeyRelatedField(
        many=True,
        read_only=False,
        queryset=Permission.objects.all(),
        source="permissions",
        required=False,
        allow_null=True,
    )
    users_count = serializers.SerializerMethodField()

    class Meta:
        model = UserRole
        fields = [
            "id",
            "name",
            "code",
            "description",
            "permissions",
            "permission_ids",
            "permissions_names",
            "users_count",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["created_at", "updated_at"]

    def get_permissions_names(self, obj):
        """Retourne la liste des noms de permissions."""
        return [perm.name for perm in obj.permissions.all()]

    def get_users_count(self, obj):
        """Retourne le nombre d'utilisateurs ayant ce rôle."""
        from users.models import CustomUser

        # Compte les utilisateurs ayant ce rôle (via le champ role si c'est un CharField)
        # Adaptez selon votre implémentation réelle
        return 0  # À implémenter selon votre logique métier
