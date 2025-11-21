"""Serializer pour le modèle Announcement (annonces)."""

from rest_framework import serializers
from announcement.models import Announcement
from department.models import Department


class AnnouncementSerializer(serializers.ModelSerializer):
    """
    Serializer complet pour les annonces.
    
    Inclut :
    - Tous les champs du modèle
    - Informations de l'auteur (nom, email)
    - Liste des départements ciblés
    - Métadonnées (dates, statut de publication)
    """

    author_name = serializers.SerializerMethodField()
    author_email = serializers.SerializerMethodField()
    departments_names = serializers.SerializerMethodField()
    departments_ids = serializers.PrimaryKeyRelatedField(
        source="departments",
        many=True,
        read_only=False,
        queryset=Department.objects.all(),
        required=False,
        allow_null=True,
    )

    class Meta:
        model = Announcement
        fields = [
            "id",
            "title",
            "content",
            "author",
            "author_name",
            "author_email",
            "published",
            "published_date",
            "updated_date",
            "visible_to_all",
            "departments",
            "departments_ids",
            "departments_names",
        ]
        read_only_fields = ["published_date", "updated_date"]


    def get_author_name(self, obj):
        """Retourne le nom complet de l'auteur."""
        if obj.author:
            return f"{obj.author.first_name} {obj.author.last_name}"
        return None

    def get_author_email(self, obj):
        """Retourne l'email de l'auteur."""
        if obj.author:
            return obj.author.email
        return None

    def get_departments_names(self, obj):
        """Retourne la liste des noms de départements ciblés."""
        if obj.departments.exists():
            return [dept.name for dept in obj.departments.all()]
        return []

    def validate(self, attrs):
        """
        Valide les données de l'annonce.
        
        Règles :
        - Si visible_to_all est True, departments peut être vide
        - Si visible_to_all est False, au moins un département doit être sélectionné
        """
        visible_to_all = attrs.get("visible_to_all", self.instance.visible_to_all if self.instance else True)
        # Vérifier à la fois departments_ids et departments (après le mapping source)
        departments = attrs.get("departments", None)
        if departments is None:
            departments = attrs.get("departments_ids", None)

        # Si departments_ids n'est pas fourni mais qu'on modifie une instance existante
        if departments is None and self.instance:
            departments = list(self.instance.departments.all())

        # Si visible_to_all est False, on doit avoir au moins un département
        if not visible_to_all:
            # Vérifier si departments est vide ou None
            if not departments:
                raise serializers.ValidationError(
                    {
                        "visible_to_all": "Si l'annonce n'est pas visible par tous, "
                        "au moins un département doit être sélectionné."
                    }
                )
            # Si c'est une liste, vérifier qu'elle n'est pas vide
            if isinstance(departments, list) and len(departments) == 0:
                raise serializers.ValidationError(
                    {
                        "visible_to_all": "Si l'annonce n'est pas visible par tous, "
                        "au moins un département doit être sélectionné."
                    }
                )

        return attrs

    def create(self, validated_data):
        """Crée une nouvelle annonce."""
        # Extraire les départements (peuvent être dans departments ou departments_ids)
        departments = validated_data.pop("departments", None)
        if departments is None:
            departments = validated_data.pop("departments_ids", None)
        
        # Retirer departments_ids des validated_data pour éviter une erreur
        validated_data.pop("departments_ids", None)
        
        # Si l'auteur n'est pas fourni, utiliser l'utilisateur connecté
        if "author" not in validated_data:
            request = self.context.get("request")
            if request and hasattr(request, "user") and hasattr(request.user, "employee") and request.user.employee:
                validated_data["author"] = request.user.employee
            # Si l'utilisateur n'a pas d'employee, l'auteur reste None (autorisé par le modèle)
        
        announcement = Announcement.objects.create(**validated_data)
        
        # Associer les départements si fournis
        if departments:
            announcement.departments.set(departments)
        
        return announcement

    def update(self, instance, validated_data):
        """Met à jour une annonce existante."""
        # Extraire les départements (peuvent être dans departments ou departments_ids)
        departments = validated_data.pop("departments", None)
        if departments is None:
            departments = validated_data.pop("departments_ids", None)
        
        # Retirer departments_ids des validated_data pour éviter une erreur
        validated_data.pop("departments_ids", None)
        
        # Mettre à jour les champs
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        
        # Mettre à jour les départements si fournis
        if departments is not None:
            instance.departments.set(departments)
        
        return instance


class AnnouncementListSerializer(serializers.ModelSerializer):
    """
    Serializer simplifié pour les listes d'annonces.
    
    Utilisé pour optimiser les performances lors de l'affichage
    de listes avec moins de données.
    """

    author_name = serializers.SerializerMethodField()
    departments_count = serializers.SerializerMethodField()

    class Meta:
        model = Announcement
        fields = [
            "id",
            "title",
            "author_name",
            "published",
            "published_date",
            "updated_date",
            "visible_to_all",
            "departments_count",
        ]

    def get_author_name(self, obj):
        """Retourne le nom complet de l'auteur."""
        if obj.author:
            return f"{obj.author.first_name} {obj.author.last_name}"
        return None

    def get_departments_count(self, obj):
        """Retourne le nombre de départements ciblés."""
        return obj.departments.count()

