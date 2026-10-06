from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from apps.core.permissions import IsActiveMember, IsAdminOrReadOnly, IsAdminRole, is_admin
from apps.members.models import Membre
from apps.notifications.models import Notification

from .models import Cours, Inscription
from .serializers import CoursSerializer, InscriptionSerializer, ProgressionSerializer


@extend_schema_view(
    list=extend_schema(summary="Lister les cours (catalogue public, sans contenu)"),
    retrieve=extend_schema(
        summary="Détail d'un cours",
        description="Le champ `contenu` n'est présent que pour un membre actif ou un admin.",
    ),
    create=extend_schema(summary="Créer un cours (admin)"),
    update=extend_schema(summary="Remplacer un cours (admin)"),
    partial_update=extend_schema(summary="Modifier un cours (admin)"),
    destroy=extend_schema(summary="Supprimer un cours (admin)"),
)
class CoursViewSet(viewsets.ModelViewSet):
    serializer_class = CoursSerializer
    filterset_fields = ["categorie", "niveau", "intervenant"]
    search_fields = ["titre", "description", "categorie", "intervenant"]
    ordering_fields = ["date_creation", "titre"]

    def get_permissions(self):
        if self.action in ("list", "retrieve"):
            return [permissions.AllowAny()]
        if self.action == "inscription":
            return [IsActiveMember()]
        return [IsAdminRole()]

    def get_queryset(self):
        if is_admin(self.request.user):
            return Cours.objects.all()
        return Cours.objects.filter(publie=True)

    def perform_create(self, serializer):
        cours = serializer.save()
        if cours.publie:
            membres = Membre.objects.filter(
                statut_carte=Membre.StatutCarte.ACTIVE
            ).select_related("utilisateur")
            Notification.objects.bulk_create(
                [
                    Notification(
                        utilisateur=m.utilisateur,
                        type=Notification.Type.NOUVEAU_COURS,
                        titre=f"Nouveau cours : {cours.titre}",
                        message=cours.description[:200],
                    )
                    for m in membres
                ]
            )

    @extend_schema(
        summary="S'inscrire à un cours (membre actif)",
        request=None,
        responses={201: InscriptionSerializer, 200: InscriptionSerializer},
    )
    @action(detail=True, methods=["post"])
    def inscription(self, request, pk=None):
        cours = self.get_object()
        membre = Membre.objects.filter(utilisateur=request.user).first()
        if membre is None:
            return Response(
                {"detail": "Les admins doivent disposer d'un profil membre pour s'inscrire."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        insc, created = Inscription.objects.get_or_create(membre=membre, cours=cours)
        return Response(
            InscriptionSerializer(insc).data,
            status=status.HTTP_201_CREATED if created else status.HTTP_200_OK,
        )


@extend_schema_view(
    list=extend_schema(summary="Mes inscriptions et ma progression"),
    retrieve=extend_schema(summary="Détail d'une inscription"),
)
class InscriptionViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = InscriptionSerializer
    permission_classes = [IsActiveMember]
    filterset_fields = ["cours"]

    def get_queryset(self):
        qs = Inscription.objects.select_related("cours", "membre")
        if getattr(self, "swagger_fake_view", False):
            return qs.none()
        if is_admin(self.request.user):
            return qs
        return qs.filter(membre__utilisateur=self.request.user)

    @extend_schema(
        summary="Mettre à jour ma progression (%)",
        request=ProgressionSerializer,
        responses={200: InscriptionSerializer},
    )
    @action(detail=True, methods=["patch"])
    def progression(self, request, pk=None):
        insc = self.get_object()
        if insc.membre.utilisateur_id != request.user.id:
            return Response(status=status.HTTP_403_FORBIDDEN)
        serializer = ProgressionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        insc.progression = serializer.validated_data["progression"]
        insc.save(update_fields=["progression"])
        return Response(InscriptionSerializer(insc).data)
