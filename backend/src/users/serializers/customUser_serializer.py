"""Serializer pour le modèle CustomUser (utilisateurs personnalisés)."""

from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password
from users.models import CustomUser


class CustomUserSerializer(serializers.ModelSerializer):
    """
    Serializer complet pour les utilisateurs.

    Inclut :
    - Tous les champs du modèle
    - Informations de l'employé associé
    - Préférences utilisateur
    - Statistiques (nombre de notifications non lues, etc.)
    """

    full_name = serializers.SerializerMethodField()
    role_display = serializers.CharField(source="get_role_display", read_only=True)
    employee_name = serializers.SerializerMethodField()
    preferences = serializers.SerializerMethodField()
    unread_notifications_count = serializers.SerializerMethodField()
    password = serializers.CharField(
        write_only=True, required=False, validators=[validate_password]
    )
    password_confirm = serializers.CharField(write_only=True, required=False)

    class Meta:
        model = CustomUser
        fields = [
            "id",
            "username",
            "email",
            "first_name",
            "last_name",
            "full_name",
            "role",
            "role_display",
            "profile_picture",
            "bio",
            "phone",
            "employee",
            "employee_name",
            "is_active",
            "is_staff",
            "is_superuser",
            "preferences",
            "unread_notifications_count",
            "password",
            "password_confirm",
            "last_login",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "is_staff",
            "is_superuser",
            "last_login",
            "created_at",
            "updated_at",
        ]
        extra_kwargs = {
            "password": {"write_only": True},
        }

    def get_full_name(self, obj):
        """Retourne le nom complet de l'utilisateur."""
        return f"{obj.first_name} {obj.last_name}".strip()

    def get_employee_name(self, obj):
        """Retourne le nom complet de l'employé associé."""
        if obj.employee:
            return f"{obj.employee.first_name} {obj.employee.last_name}"
        return None

    def get_preferences(self, obj):
        """Retourne les préférences de l'utilisateur."""
        if hasattr(obj, "preferences"):
            from users.serializers.userPreference_serializer import (
                UserPreferenceSerializer,
            )

            return UserPreferenceSerializer(obj.preferences).data
        return None

    def get_unread_notifications_count(self, obj):
        """Retourne le nombre de notifications non lues."""
        return obj.notifications.filter(is_read=False).count()

    def validate(self, attrs):
        """Valide les données de l'utilisateur."""
        # Vérifier que password et password_confirm correspondent
        password = attrs.get("password")
        password_confirm = attrs.get("password_confirm")

        if password and password_confirm:
            if password != password_confirm:
                raise serializers.ValidationError(
                    {"password_confirm": "Les mots de passe ne correspondent pas."}
                )
        elif password and not password_confirm:
            raise serializers.ValidationError(
                {
                    "password_confirm": "Ce champ est requis lors de la modification du mot de passe."
                }
            )

        return attrs

    def create(self, validated_data):
        """Crée un nouvel utilisateur avec mot de passe hashé."""
        validated_data.pop("password_confirm", None)
        password = validated_data.pop("password", None)

        user = CustomUser.objects.create(**validated_data)

        if password:
            user.set_password(password)
            user.save()

        return user

    def update(self, instance, validated_data):
        """Met à jour un utilisateur existant."""
        validated_data.pop("password_confirm", None)
        password = validated_data.pop("password", None)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        if password:
            instance.set_password(password)

        instance.save()
        return instance

    def to_representation(self, instance):
        """Convertir l'URL de l'image en URL absolue."""
        representation = super().to_representation(instance)
        if representation.get('profile_picture') and instance.profile_picture:
            request = self.context.get('request')
            if request:
                representation['profile_picture'] = request.build_absolute_uri(instance.profile_picture.url)
            else:
                # En cas d'absence de request, retourner l'URL relative
                # Le frontend devra construire l'URL complète avec l'URL de base de l'API
                representation['profile_picture'] = instance.profile_picture.url if hasattr(instance.profile_picture, 'url') else str(instance.profile_picture)
        return representation


class CustomUserListSerializer(serializers.ModelSerializer):
    """
    Serializer simplifié pour les listes d'utilisateurs.

    Utilisé pour optimiser les performances lors de l'affichage
    de listes avec moins de données.
    """

    full_name = serializers.SerializerMethodField()
    role_display = serializers.CharField(source="get_role_display", read_only=True)

    class Meta:
        model = CustomUser
        fields = [
            "id",
            "username",
            "email",
            "first_name",
            "last_name",
            "full_name",
            "role",
            "role_display",
            "profile_picture",
            "is_active",
            "is_staff",
            "created_at",
        ]

    def get_full_name(self, obj):
        """Retourne le nom complet de l'utilisateur."""
        return f"{obj.first_name} {obj.last_name}".strip()


class CustomUserPasswordSerializer(serializers.Serializer):
    """Serializer pour le changement de mot de passe."""

    old_password = serializers.CharField(required=True, write_only=True)
    new_password = serializers.CharField(
        required=True, write_only=True, validators=[validate_password]
    )
    new_password_confirm = serializers.CharField(required=True, write_only=True)

    def validate(self, attrs):
        """Valide les données de changement de mot de passe."""
        if attrs["new_password"] != attrs["new_password_confirm"]:
            raise serializers.ValidationError(
                {
                    "new_password_confirm": "Les nouveaux mots de passe ne correspondent pas."
                }
            )
        return attrs
