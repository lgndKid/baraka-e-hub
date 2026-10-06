from rest_framework import serializers

from .models import Article


class ArticleSerializer(serializers.ModelSerializer):
    auteur_nom = serializers.CharField(source="auteur.nom", read_only=True, default=None)

    class Meta:
        model = Article
        fields = (
            "id",
            "titre",
            "slug",
            "contenu",
            "image",
            "date_publication",
            "auteur",
            "auteur_nom",
            "publie",
        )
        read_only_fields = ("id", "slug", "auteur")
