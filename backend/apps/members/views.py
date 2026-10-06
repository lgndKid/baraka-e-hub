from django.db.models import Q
from django.http import Http404
from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework import permissions, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from apps.core.permissions import IsActiveMember, is_admin

from .models import Membre
from .serializers import (
    MembreAnnuaireSerializer,
    MembreDetailSerializer,
    MembreProfilSerializer,
)


@extend_schema_view(
    list=extend_schema(summary="Annuaire des membres (membres actifs)"),
    retrieve=extend_schema(
        summary="Profil d'un membre",
        description="Profil public (annuaire). Le détail complet est renvoyé au membre "
        "concerné et aux admins.",
        responses={200: MembreDetailSerializer},
    ),
)
class MembreViewSet(viewsets.ReadOnlyModelViewSet):
    filterset_fields = ["ville", "pays", "profession"]
    search_fields = [
        "utilisateur__nom",
        "profession",
        "entreprise",
        "ville",
        "pays",
        "bio",
    ]
    ordering_fields = ["utilisateur__nom", "ville", "pays"]

    def get_permissions(self):
        if self.action == "moi":
            return [permissions.IsAuthenticated()]
        return [IsActiveMember()]

    def get_queryset(self):
        qs = Membre.objects.select_related("utilisateur")
        if getattr(self, "swagger_fake_view", False):
            return qs.none()
        if is_admin(self.request.user):
            return qs
        return qs.filter(
            Q(visible_annuaire=True, statut_carte=Membre.StatutCarte.ACTIVE)
            | Q(utilisateur=self.request.user)
        )

    def get_serializer_class(self):
        return MembreAnnuaireSerializer

    def retrieve(self, request, *args, **kwargs):
        membre = self.get_object()
        if is_admin(request.user) or membre.utilisateur_id == request.user.id:
            return Response(MembreDetailSerializer(membre).data)
        return Response(MembreAnnuaireSerializer(membre).data)

    @extend_schema(
        methods=["GET"],
        summary="Mon profil membre",
        responses={200: MembreDetailSerializer},
    )
    @extend_schema(
        methods=["PATCH"],
        summary="Modifier mon profil membre (annuaire)",
        request=MembreProfilSerializer,
        responses={200: MembreDetailSerializer},
    )
    @action(detail=False, methods=["get", "patch"], url_path="moi")
    def moi(self, request):
        membre = Membre.objects.filter(utilisateur=request.user).first()
        if membre is None:
            raise Http404("Aucun profil membre : payez la carte de membre pour y acceder.")
        if request.method == "PATCH":
            serializer = MembreProfilSerializer(membre, data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(MembreDetailSerializer(membre).data)
        return Response(MembreDetailSerializer(membre).data)
