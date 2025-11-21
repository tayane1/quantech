"""Serializer pour le modèle UserPermission (permissions utilisateur)."""

from rest_framework import serializers
from users.models import UserPermission


class UserPermissionSerializer(serializers.ModelSerializer):
    """
    Serializer pour les permissions granulaires des utilisateurs.

    Inclut :
    - Informations de la permission
    - Informations de l'utilisateur concerné
    - Informations de celui qui a accordé la permission
    """

    user_name = serializers.SerializerMethodField()
    user_email = serializers.CharField(source="user.email", read_only=True)
    module_display = serializers.CharField(source="get_module_display", read_only=True)
    action_display = serializers.CharField(source="get_action_display", read_only=True)
    granted_by_name = serializers.SerializerMethodField()

    class Meta:
        model = UserPermission
        fields = [
            "id",
            "user",
            "user_name",
            "user_email",
            "module",
            "module_display",
            "action",
            "action_display",
            "granted",
            "granted_by",
            "granted_by_name",
            "granted_date",
        ]
        read_only_fields = ["granted_date"]

    def get_user_name(self, obj):
        """Retourne le nom complet de l'utilisateur."""
        if obj.user:
            return f"{obj.user.first_name} {obj.user.last_name}"
        return None

    def get_granted_by_name(self, obj):
        """Retourne le nom complet de celui qui a accordé la permission."""
        if obj.granted_by:
            return f"{obj.granted_by.first_name} {obj.granted_by.last_name}"
        return None

    def validate(self, attrs):
        """Valide l'unicité de la combinaison user-module-action."""
        user = attrs.get("user", self.instance.user if self.instance else None)
        module = attrs.get("module", self.instance.module if self.instance else None)
        action = attrs.get("action", self.instance.action if self.instance else None)

        queryset = UserPermission.objects.filter(
            user=user, module=module, action=action
        )
        if self.instance:
            queryset = queryset.exclude(pk=self.instance.pk)

        if queryset.exists():
            raise serializers.ValidationError(
                "Cette permission existe déjà pour cet utilisateur."
            )

        return attrs
