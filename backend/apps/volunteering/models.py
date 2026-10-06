from django.conf import settings
from django.db import models


class Candidature(models.Model):
    class Statut(models.TextChoices):
        RECUE = "recue", "Reçue"
        EN_REVUE = "en_revue", "En revue"
        ACCEPTEE = "acceptee", "Acceptée"
        REFUSEE = "refusee", "Refusée"

    utilisateur = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="candidatures",
    )
    nom = models.CharField(max_length=150)
    email = models.EmailField()
    role_souhaite = models.CharField(max_length=150)
    motivation = models.TextField()
    statut = models.CharField(max_length=10, choices=Statut.choices, default=Statut.RECUE)
    date = models.DateTimeField(auto_now_add=True)
    date_mise_a_jour = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-date"]

    def __str__(self):
        return f"{self.nom} — {self.role_souhaite}"
