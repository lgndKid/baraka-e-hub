"""Abstraction de la passerelle de paiement.

`SandboxGateway` simule une passerelle (aucun argent reel). Pour la production,
creez une sous-classe de `BaseGateway` pour votre prestataire (CinetPay, PayDunya,
Flutterwave, ...), implementez `initier`, puis pointez `PAYMENT_GATEWAY` dessus.
Le prestataire confirmera ensuite le paiement via `POST /api/paiements/webhook`.
"""
from django.conf import settings
from django.utils.module_loading import import_string


class BaseGateway:
    def initier(self, paiement) -> dict:
        """Retourne {'reference_passerelle': str, 'url_paiement': str|None}."""
        raise NotImplementedError


class SandboxGateway(BaseGateway):
    def initier(self, paiement):
        return {
            "reference_passerelle": f"SBX-{paiement.reference.hex[:12]}",
            "url_paiement": None,
        }


def get_gateway() -> BaseGateway:
    return import_string(settings.PAYMENT_GATEWAY)()
