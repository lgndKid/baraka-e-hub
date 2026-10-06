from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework import permissions, viewsets

from apps.core.emails import envoyer_email
from apps.core.permissions import IsAdminRole

from .models import MessageContact
from .serializers import MessageContactCreateSerializer, MessageContactSerializer


@extend_schema_view(
    create=extend_schema(
        summary="Envoyer un message de contact (public)",
        request=MessageContactCreateSerializer,
        responses={201: MessageContactCreateSerializer},
    ),
    list=extend_schema(summary="Lister les messages (admin)"),
    retrieve=extend_schema(summary="Détail d'un message (admin)"),
    partial_update=extend_schema(summary="Marquer un message comme traité (admin)"),
    destroy=extend_schema(summary="Supprimer un message (admin)"),
)
class MessageContactViewSet(viewsets.ModelViewSet):
    queryset = MessageContact.objects.all()
    http_method_names = ["get", "post", "patch", "delete", "head", "options"]
    filterset_fields = ["traite"]
    search_fields = ["nom", "email", "message"]

    def get_permissions(self):
        if self.action == "create":
            return [permissions.AllowAny()]
        return [IsAdminRole()]

    def get_throttles(self):
        self.throttle_scope = "contact" if self.action == "create" else None
        return super().get_throttles()

    def get_serializer_class(self):
        if self.action == "create":
            return MessageContactCreateSerializer
        return MessageContactSerializer

    def perform_create(self, serializer):
        msg = serializer.save()
        envoyer_email(
            "Nous avons bien reçu votre message — E-Baraka",
            f"Bonjour {msg.nom},\n\nMerci de nous avoir contactés. Nous avons bien reçu "
            "votre message et vous répondrons dans les meilleurs délais.\n\nL'équipe E-Baraka",
            [msg.email],
        )
