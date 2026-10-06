from django.conf import settings
from django.db import models


class Notification(models.Model):
    class Type(models.TextChoices):
        NOUVEAU_COURS = "nouveau_cours", "Nouveau cours"
        RENOUVELLEMENT = "renouvellement", "Renouvellement de carte"
        PAIEMENT = "paiement", "Paiement"
        INFO = "info", "Information"

    utilisateur = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="notifications"
    )
    type = models.CharField(max_length=20, choices=Type.choices, default=Type.INFO)
    titre = models.CharField(max_length=200)
    message = models.TextField(blank=True)
    lue = models.BooleanField(default=False)
    date = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-date"]

    def __str__(self):
        return f"{self.utilisateur_id} — {self.titre}"


def notifier(utilisateur, type, titre, message=""):
    return Notification.objects.create(
        utilisateur=utilisateur, type=type, titre=titre, message=message
    )
