import logging

from django.conf import settings
from django.core.mail import send_mail

logger = logging.getLogger(__name__)


def envoyer_email(sujet, message, destinataires):
    """Envoi d'email transactionnel. N'interrompt jamais la requete en cas d'echec."""
    try:
        send_mail(
            sujet,
            message,
            settings.DEFAULT_FROM_EMAIL,
            list(destinataires),
            fail_silently=False,
        )
    except Exception:  # noqa: BLE001
        logger.exception("Echec d'envoi d'email : %s", sujet)
