from django.conf import settings
from rest_framework import serializers

from .models import Paiement


class PaiementSerializer(serializers.ModelSerializer):
    class Meta:
        model = Paiement
        fields = (
            "id",
            "reference",
            "membre",
            "montant",
            "devise",
            "methode",
            "telephone",
            "statut",
            "date",
            "date_confirmation",
        )
        read_only_fields = fields


class PaiementInitSerializer(serializers.Serializer):
    methode = serializers.ChoiceField(choices=Paiement.Methode.choices)
    telephone = serializers.CharField(
        required=False,
        allow_blank=True,
        max_length=30,
        help_text="Obligatoire pour le mobile money (Orange / Moov / MTN).",
    )

    def validate(self, attrs):
        if attrs["methode"] in Paiement.MOBILE_MONEY and not attrs.get("telephone"):
            raise serializers.ValidationError(
                {"telephone": "Le numero de telephone est obligatoire pour le mobile money."}
            )
        return attrs


class PaiementInitResponseSerializer(serializers.Serializer):
    paiement = PaiementSerializer()
    url_paiement = serializers.URLField(
        allow_null=True, help_text="URL de la passerelle (redirection) si applicable."
    )


class WebhookSerializer(serializers.Serializer):
    reference = serializers.UUIDField(help_text="Reference E-Baraka du paiement.")
    statut = serializers.ChoiceField(choices=["success", "failed"])
    reference_passerelle = serializers.CharField(required=False, allow_blank=True)
