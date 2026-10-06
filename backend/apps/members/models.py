from datetime import date, timedelta

from django.conf import settings
from django.db import models


class Membre(models.Model):
    class StatutCarte(models.TextChoices):
        ACTIVE = "active", "Active"
        EXPIREE = "expiree", "Expirée"

    utilisateur = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="membre"
    )
    statut_carte = models.CharField(
        max_length=10, choices=StatutCarte.choices, default=StatutCarte.EXPIREE
    )
    date_debut = models.DateField(null=True, blank=True)
    date_fin = models.DateField(null=True, blank=True)
    # Profil / annuaire professionnel
    profession = models.CharField(max_length=150, blank=True)
    entreprise = models.CharField(max_length=150, blank=True)
    ville = models.CharField(max_length=100, blank=True)
    pays = models.CharField(max_length=100, blank=True)
    bio = models.TextField(blank=True)
    visible_annuaire = models.BooleanField(default=True)

    class Meta:
        ordering = ["utilisateur__nom"]

    def __str__(self):
        return f"Membre {self.utilisateur.email}"

    @property
    def est_active(self):
        return (
            self.statut_carte == self.StatutCarte.ACTIVE
            and self.date_fin is not None
            and self.date_fin >= date.today()
        )

    def activer(self, jours):
        """Active / prolonge la carte (renouvellement a la suite si encore valide)."""
        aujourdhui = date.today()
        if self.est_active:
            debut = self.date_fin
        else:
            debut = aujourdhui
            self.date_debut = aujourdhui
        self.date_fin = debut + timedelta(days=jours)
        self.statut_carte = self.StatutCarte.ACTIVE
        self.save()
