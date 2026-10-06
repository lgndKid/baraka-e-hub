from rest_framework import serializers

from .models import Membre


class MembreAnnuaireSerializer(serializers.ModelSerializer):
    nom = serializers.CharField(source="utilisateur.nom", read_only=True)

    class Meta:
        model = Membre
        fields = ("id", "nom", "profession", "entreprise", "ville", "pays", "bio")
        read_only_fields = fields


class MembreDetailSerializer(serializers.ModelSerializer):
    nom = serializers.CharField(source="utilisateur.nom", read_only=True)
    email = serializers.EmailField(source="utilisateur.email", read_only=True)
    carte_active = serializers.BooleanField(source="est_active", read_only=True)

    class Meta:
        model = Membre
        fields = (
            "id",
            "nom",
            "email",
            "statut_carte",
            "carte_active",
            "date_debut",
            "date_fin",
            "profession",
            "entreprise",
            "ville",
            "pays",
            "bio",
            "visible_annuaire",
        )
        read_only_fields = ("id", "statut_carte", "date_debut", "date_fin")


class MembreProfilSerializer(MembreDetailSerializer):
    class Meta(MembreDetailSerializer.Meta):
        read_only_fields = (
            "id",
            "nom",
            "email",
            "statut_carte",
            "carte_active",
            "date_debut",
            "date_fin",
        )
