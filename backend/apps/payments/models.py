import uuid

from django.conf import settings
from django.db import models


class Paiement(models.Model):
    class Methode(models.TextChoices):
        ORANGE_MONEY = "orange_money", "Orange Money"
        MOOV_MONEY = "moov_money", "Moov Money"
        MTN_MOMO = "mtn_momo", "MTN Mobile Money"
        CARTE = "carte", "Carte bancaire"

    class Statut(models.TextChoices):
        INITIE = "initie", "Initié"
        CONFIRME = "confirme", "Confirmé"
        ECHOUE = "echoue", "Échoué"

    MOBILE_MONEY = {"orange_money", "moov_money", "mtn_momo"}

    membre = models.ForeignKey(
        "members.Membre", on_delete=models.PROTECT, related_name="paiements"
    )
    reference = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    reference_passerelle = models.CharField(max_length=100, blank=True)
    montant = models.DecimalField(max_digits=12, decimal_places=2)
    devise = models.CharField(max_length=3, default="XOF")
    methode = models.CharField(max_length=20, choices=Methode.choices)
    telephone = models.CharField(max_length=30, blank=True)
    statut = models.CharField(max_length=10, choices=Statut.choices, default=Statut.INITIE)
    date = models.DateTimeField(auto_now_add=True)
    date_confirmation = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-date"]

    def __str__(self):
        return f"{self.reference} — {self.montant} {self.devise} ({self.statut})"
