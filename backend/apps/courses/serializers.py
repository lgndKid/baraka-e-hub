from rest_framework import serializers

from apps.core.permissions import is_active_member

from .models import Cours, Inscription


class CoursSerializer(serializers.ModelSerializer):
    """Le champ `contenu` n'est renvoye qu'aux membres actifs et aux admins."""

    class Meta:
        model = Cours
        fields = (
            "id",
            "titre",
            "description",
            "categorie",
            "niveau",
            "intervenant",
            "contenu",
            "publie",
            "date_creation",
        )
        read_only_fields = ("id", "date_creation")

    def to_representation(self, instance):
        data = super().to_representation(instance)
        request = self.context.get("request")
        if request is None or not is_active_member(request.user):
            data.pop("contenu", None)
        return data


class InscriptionSerializer(serializers.ModelSerializer):
    cours_titre = serializers.CharField(source="cours.titre", read_only=True)

    class Meta:
        model = Inscription
        fields = ("id", "membre", "cours", "cours_titre", "date", "progression")
        read_only_fields = fields


class ProgressionSerializer(serializers.Serializer):
    progression = serializers.IntegerField(min_value=0, max_value=100)
