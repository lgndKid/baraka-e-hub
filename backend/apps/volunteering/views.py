from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework import permissions, viewsets

from apps.core.emails import envoyer_email
from apps.core.permissions import IsAdminRole

from .models import Candidature
from .serializers import (
    CandidatureCreateSerializer,
    CandidatureSerializer,
    CandidatureStatutSerializer,
)


@extend_schema_view(
    create=extend_schema(
        summary="Soumettre une candidature bénévole (public)",
        request=CandidatureCreateSerializer,
        responses={201: CandidatureCreateSerializer},
    ),
    list=extend_schema(summary="Lister les candidatures (admin)"),
    retrieve=extend_schema(summary="Détail d'une candidature (admin)"),
    partial_update=extend_schema(
        summary="Mettre à jour le statut d'une candidature (admin)",
        request=CandidatureStatutSerializer,
        responses={200: CandidatureSerializer},
    ),
    destroy=extend_schema(summary="Supprimer une candidature (admin)"),
)
class CandidatureViewSet(viewsets.ModelViewSet):
    queryset = Candidature.objects.all()
    http_method_names = ["get", "post", "patch", "delete", "head", "options"]
    filterset_fields = ["statut"]
    search_fields = ["nom", "email", "role_souhaite"]
    ordering_fields = ["date", "statut"]

    def get_permissions(self):
        if self.action == "create":
            return [permissions.AllowAny()]
        return [IsAdminRole()]

    def get_authenticators(self):
        # Le JWT reste lu s'il est present (pour rattacher l'utilisateur connecte).
        return super().get_authenticators()

    def get_throttles(self):
        self.throttle_scope = "candidature" if self.action == "create" else None
        return super().get_throttles()

    def get_serializer_class(self):
        if self.action == "create":
            return CandidatureCreateSerializer
        if self.action == "partial_update":
            return CandidatureStatutSerializer
        return CandidatureSerializer

    def perform_create(self, serializer):
        user = self.request.user if self.request.user.is_authenticated else None
        candidature = serializer.save(utilisateur=user)
        envoyer_email(
            "Votre candidature E-Baraka a bien été reçue",
            f"Bonjour {candidature.nom},\n\nNous avons bien reçu votre candidature "
            f"pour le rôle « {candidature.role_souhaite} ». Notre équipe reviendra "
            "vers vous prochainement.\n\nMerci pour votre engagement !\nL'équipe E-Baraka",
            [candidature.email],
        )

    def update(self, request, *args, **kwargs):
        response = super().update(request, *args, **kwargs)
        # Reponse complete apres modification du statut.
        response.data = CandidatureSerializer(self.get_object()).data
        return response
