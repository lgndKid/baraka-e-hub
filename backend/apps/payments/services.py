from django.conf import settings
from django.db import transaction
from django.utils import timezone

from apps.core.audit import log_action
from apps.core.emails import envoyer_email
from apps.notifications.models import Notification, notifier

from .models import Paiement


@transaction.atomic
def confirmer_paiement(reference, reference_passerelle="", request=None):
    """Confirme un paiement (idempotent) et active/prolonge la carte de membre."""
    paiement = Paiement.objects.select_for_update().select_related(
        "membre__utilisateur"
    ).get(reference=reference)
    if paiement.statut == Paiement.Statut.CONFIRME:
        return paiement, False
    paiement.statut = Paiement.Statut.CONFIRME
    paiement.date_confirmation = timezone.now()
    if reference_passerelle:
        paiement.reference_passerelle = reference_passerelle
    paiement.save()

    membre = paiement.membre
    membre.activer(settings.CARTE_MEMBRE_DUREE_JOURS)
    user = membre.utilisateur
    if user.role == user.Role.VISITEUR:
        user.role = user.Role.MEMBRE
        user.save(update_fields=["role"])

    log_action(
        "paiement.confirme",
        user=user,
        request=request,
        paiement=str(paiement.reference),
        montant=paiement.montant,
        devise=paiement.devise,
    )
    notifier(
        user,
        Notification.Type.PAIEMENT,
        "Paiement confirmé",
        f"Votre carte de membre est active jusqu'au {membre.date_fin:%d/%m/%Y}.",
    )
    envoyer_email(
        "Reçu de paiement — carte de membre E-Baraka",
        f"Bonjour {user.nom},\n\nNous avons bien reçu votre paiement de "
        f"{paiement.montant} {paiement.devise} (réf. {paiement.reference}).\n"
        f"Votre carte est valable jusqu'au {membre.date_fin:%d/%m/%Y}.\n\nMerci !",
        [user.email],
    )
    return paiement, True


@transaction.atomic
def echouer_paiement(reference, request=None):
    paiement = Paiement.objects.select_for_update().get(reference=reference)
    if paiement.statut == Paiement.Statut.INITIE:
        paiement.statut = Paiement.Statut.ECHOUE
        paiement.save(update_fields=["statut"])
        log_action(
            "paiement.echoue",
            user=paiement.membre.utilisateur,
            request=request,
            paiement=str(paiement.reference),
        )
    return paiement
