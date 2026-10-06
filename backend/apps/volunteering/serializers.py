from rest_framework import serializers

from .models import Candidature


class CandidatureCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Candidature
        fields = ("id", "nom", "email", "role_souhaite", "motivation", "statut", "date")
        read_only_fields = ("id", "statut", "date")


class CandidatureSerializer(serializers.ModelSerializer):
    class Meta:
        model = Candidature
        fields = (
            "id",
            "utilisateur",
            "nom",
            "email",
            "role_souhaite",
            "motivation",
            "statut",
            "date",
            "date_mise_a_jour",
        )
        read_only_fields = fields


class CandidatureStatutSerializer(serializers.ModelSerializer):
    class Meta:
        model = Candidature
        fields = ("statut",)
