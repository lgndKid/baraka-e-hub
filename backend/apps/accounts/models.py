from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models
from django.utils import timezone


class UserManager(BaseUserManager):
    use_in_migrations = True

    def create_user(self, email, password=None, **extra):
        if not email:
            raise ValueError("L'email est obligatoire.")
        user = self.model(email=self.normalize_email(email).lower(), **extra)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra):
        extra.setdefault("is_staff", True)
        extra.setdefault("is_superuser", True)
        extra.setdefault("role", User.Role.ADMIN)
        return self.create_user(email, password, **extra)


class User(AbstractBaseUser, PermissionsMixin):
    class Role(models.TextChoices):
        VISITEUR = "visiteur", "Visiteur"
        MEMBRE = "membre", "Membre"
        ADMIN = "admin", "Admin / Équipe"

    email = models.EmailField(unique=True)
    nom = models.CharField(max_length=150)
    role = models.CharField(max_length=10, choices=Role.choices, default=Role.VISITEUR)
    date_inscription = models.DateTimeField(default=timezone.now)
    consentement_donnees = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    objects = UserManager()
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["nom"]

    class Meta:
        ordering = ["-date_inscription"]

    def __str__(self):
        return self.email

    def anonymiser(self):
        """Droit a la suppression : anonymise le compte (l'historique comptable est conserve)."""
        self.email = f"supprime-{self.pk}@anonyme.invalid"
        self.nom = "Compte supprimé"
        self.is_active = False
        self.is_staff = False
        self.role = self.Role.VISITEUR
        self.set_unusable_password()
        self.save()
        self.notifications.all().delete()
        self.candidatures.update(nom="Supprimé", email="", motivation="")
        membre = getattr(self, "membre", None)
        if membre:
            membre.profession = membre.entreprise = membre.ville = membre.pays = ""
            membre.bio = ""
            membre.visible_annuaire = False
            membre.save()
            membre.inscriptions.all().delete()
