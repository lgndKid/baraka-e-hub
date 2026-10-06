import hashlib
import hmac
import json

from django.conf import settings
from django.contrib.auth import get_user_model
from drf_spectacular.utils import OpenApiParameter, extend_schema, extend_schema_view
from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from apps.accounts.serializers import DetailSerializer
from apps.core.audit import log_action
from apps.core.permissions import IsAdminRole, is_admin
from apps.members.models import Membre

from .gateway import get_gateway
from .models import Paiement
from .serializers import (
    PaiementInitResponseSerializer,
    PaiementInitSerializer,
    PaiementSerializer,
    WebhookSerializer,
)
from .services import confirmer_paiement, echouer_paiement


@extend_schema_view(
    list=extend_schema(summary="Historique des paiements (les miens ; tous pour un admin)"),
    retrieve=extend_schema(summary="Détail d'un paiement"),
)
class PaiementViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = PaiementSerializer
    filterset_fields = ["statut", "methode"]
    ordering_fields = ["date", "montant"]

    def get_permissions(self):
        if self.action == "webhook":
            return [permissions.AllowAny()]
        return [permissions.IsAuthenticated()]

    def get_throttles(self):
        self.throttle_scope = "payment" if self.action == "initier" else None
        return super().get_throttles()

    def get_queryset(self):
        qs = Paiement.objects.select_related("membre__utilisateur")
        if getattr(self, "swagger_fake_view", False):
            return qs.none()
        if is_admin(self.request.user):
            return qs
        return qs.filter(membre__utilisateur=self.request.user)

    @extend_schema(
        summary="Initier un paiement de carte de membre",
        description="Le montant est fixé côté serveur. Le statut passe à `confirme` "
        "via le webhook de la passerelle.",
        request=PaiementInitSerializer,
        responses={201: PaiementInitResponseSerializer},
    )
    def create(self, request, *args, **kwargs):
        return self.initier(request)

    def initier(self, request):
        serializer = PaiementInitSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        membre, _ = Membre.objects.get_or_create(utilisateur=request.user)
        paiement = Paiement.objects.create(
            membre=membre,
            montant=settings.CARTE_MEMBRE_MONTANT,
            devise=settings.CARTE_MEMBRE_DEVISE,
            methode=serializer.validated_data["methode"],
            telephone=serializer.validated_data.get("telephone", ""),
        )
        resultat = get_gateway().initier(paiement)
        paiement.reference_passerelle = resultat.get("reference_passerelle", "")
        paiement.save(update_fields=["reference_passerelle"])
        log_action(
            "paiement.initie",
            request=request,
            paiement=str(paiement.reference),
            montant=paiement.montant,
            methode=paiement.methode,
        )
        return Response(
            {
                "paiement": PaiementSerializer(paiement).data,
                "url_paiement": resultat.get("url_paiement"),
            },
            status=status.HTTP_201_CREATED,
        )

    @extend_schema(
        summary="Webhook de confirmation asynchrone (passerelle)",
        description=(
            "Appelé par la passerelle de paiement. Le corps brut doit être signé : "
            "en-tête `X-Signature` = HMAC-SHA256 hexadécimal du corps avec "
            "`PAYMENT_WEBHOOK_SECRET`. Idempotent."
        ),
        parameters=[
            OpenApiParameter("X-Signature", str, OpenApiParameter.HEADER, required=True)
        ],
        request=WebhookSerializer,
        responses={200: DetailSerializer},
        auth=[],
    )
    @action(
        detail=False,
        methods=["post"],
        url_path="webhook",
        authentication_classes=[],
        permission_classes=[permissions.AllowAny],
    )
    def webhook(self, request):
        signature = request.headers.get("X-Signature", "")
        attendu = hmac.new(
            settings.PAYMENT_WEBHOOK_SECRET.encode(), request.body, hashlib.sha256
        ).hexdigest()
        if not hmac.compare_digest(signature, attendu):
            log_action("paiement.webhook_signature_invalide", request=request)
            return Response({"detail": "Signature invalide."}, status=status.HTTP_403_FORBIDDEN)
        try:
            data = json.loads(request.body)
        except ValueError:
            return Response({"detail": "JSON invalide."}, status=status.HTTP_400_BAD_REQUEST)
        serializer = WebhookSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        v = serializer.validated_data
        try:
            if v["statut"] == "success":
                confirmer_paiement(v["reference"], v.get("reference_passerelle", ""), request)
            else:
                echouer_paiement(v["reference"], request)
        except Paiement.DoesNotExist:
            return Response({"detail": "Paiement inconnu."}, status=status.HTTP_404_NOT_FOUND)
        return Response({"detail": "ok"})
