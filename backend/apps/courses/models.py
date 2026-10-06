from django.core.validators import MaxValueValidator
from django.db import models


class Cours(models.Model):
    class Niveau(models.TextChoices):
        DEBUTANT = "debutant", "Débutant"
        INTERMEDIAIRE = "intermediaire", "Intermédiaire"
        AVANCE = "avance", "Avancé"

    titre = models.CharField(max_length=200)
    description = models.TextField()
    categorie = models.CharField(max_length=100, db_index=True)
    niveau = models.CharField(max_length=15, choices=Niveau.choices, default=Niveau.DEBUTANT)
    intervenant = models.CharField(max_length=150)
    contenu = models.TextField(blank=True)
    publie = models.BooleanField(default=True)
    date_creation = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-date_creation"]
        verbose_name_plural = "cours"

    def __str__(self):
        return self.titre


class Inscription(models.Model):
    membre = models.ForeignKey(
        "members.Membre", on_delete=models.CASCADE, related_name="inscriptions"
    )
    cours = models.ForeignKey(Cours, on_delete=models.CASCADE, related_name="inscriptions")
    date = models.DateTimeField(auto_now_add=True)
    progression = models.PositiveSmallIntegerField(default=0, validators=[MaxValueValidator(100)])

    class Meta:
        ordering = ["-date"]
        constraints = [
            models.UniqueConstraint(fields=["membre", "cours"], name="inscription_unique")
        ]

    def __str__(self):
        return f"{self.membre} → {self.cours} ({self.progression}%)"
