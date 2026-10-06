from datetime import date, timedelta

from django.core.management.base import BaseCommand

from apps.core.emails import envoyer_email
from apps.members.models import Membre
from apps.notifications.models import Notification, notifier


class Command(BaseCommand):
    help = (
        "Expire les cartes echues et envoie les rappels de renouvellement "
        "(J-30 et J-7). A planifier chaque jour (cron)."
    )

    def handle(self, *args, **options):
        today = date.today()
        expirees = Membre.objects.filter(
            statut_carte=Membre.StatutCarte.ACTIVE, date_fin__lt=today
        ).update(statut_carte=Membre.StatutCarte.EXPIREE)
        rappels = 0
        for jours in (30, 7):
            cible = today + timedelta(days=jours)
            for m in Membre.objects.filter(
                statut_carte=Membre.StatutCarte.ACTIVE, date_fin=cible
            ).select_related("utilisateur"):
                msg = f"Votre carte de membre expire le {m.date_fin:%d/%m/%Y} (dans {jours} jours)."
                notifier(m.utilisateur, Notification.Type.RENOUVELLEMENT, "Renouvelez votre carte", msg)
                envoyer_email("Renouvellement de votre carte E-Baraka", msg, [m.utilisateur.email])
                rappels += 1
        self.stdout.write(self.style.SUCCESS(f"{expirees} carte(s) expiree(s), {rappels} rappel(s)."))
