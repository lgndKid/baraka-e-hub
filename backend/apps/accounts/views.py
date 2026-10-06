from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework import generics, permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from apps.core.audit import log_action
from apps.core.emails import envoyer_email
from apps.core.permissions import IsAdminRole

from .serializers import (
    DetailSerializer,
    PasswordResetConfirmSerializer,
    PasswordResetRequestSerializer,
    RegisterSerializer,
    RoleUpdateSerializer,
    UserSerializer,
)

User = get_user_model()


@extend_schema(tags=["auth"], summary="Créer un compte")
class RegisterView(generics.CreateAPIView):
    serializer_class = RegisterSerializer
    permission_classes = [permissions.AllowAny]
    authentication_classes = []
    throttle_scope = "register"

    def perform_create(self, serializer):
        user = serializer.save()
        envoyer_email(
            "Bienvenue sur E-Baraka",
            f"Bonjour {user.nom},\n\nVotre compte E-Baraka a bien ete cree.",
            [user.email],
        )


@extend_schema(tags=["auth"], summary="Connexion (JWT)")
class LoginView(TokenObtainPairView):
    throttle_scope = "login"


@extend_schema(tags=["auth"], summary="Rafraîchir le jeton d'accès")
class RefreshView(TokenRefreshView):
    throttle_scope = "login"


@extend_schema_view(
    get=extend_schema(tags=["auth"], summary="Mon profil"),
    patch=extend_schema(tags=["auth"], summary="Modifier mon profil"),
    put=extend_schema(tags=["auth"], summary="Modifier mon profil"),
    delete=extend_schema(
        tags=["auth"],
        summary="Supprimer mon compte (droit à la suppression)",
        responses={204: None},
    ),
)
class MeView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = UserSerializer

    def get_object(self):
        return self.request.user

    def perform_destroy(self, instance):
        log_action("compte.suppression", user=instance, request=self.request, user_id=instance.pk)
        instance.anonymiser()


@extend_schema(
    tags=["auth"],
    summary="Demander la réinitialisation du mot de passe",
    request=PasswordResetRequestSerializer,
    responses={200: DetailSerializer},
)
class PasswordResetRequestView(APIView):
    permission_classes = [permissions.AllowAny]
    authentication_classes = []
    throttle_scope = "password_reset"

    def post(self, request):
        serializer = PasswordResetRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = User.objects.filter(
            email__iexact=serializer.validated_data["email"], is_active=True
        ).first()
        if user:
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            token = default_token_generator.make_token(user)
            lien = f"{settings.FRONTEND_URL}/reinitialiser-mot-de-passe?uid={uid}&token={token}"
            envoyer_email(
                "Reinitialisation de votre mot de passe E-Baraka",
                f"Bonjour {user.nom},\n\nPour choisir un nouveau mot de passe : {lien}\n\n"
                "Si vous n'etes pas a l'origine de cette demande, ignorez ce message.",
                [user.email],
            )
        # Meme reponse dans tous les cas : ne revele pas l'existence d'un compte.
        return Response({"detail": "Si un compte existe, un email a ete envoye."})


@extend_schema(
    tags=["auth"],
    summary="Confirmer la réinitialisation du mot de passe",
    request=PasswordResetConfirmSerializer,
    responses={200: DetailSerializer},
)
class PasswordResetConfirmView(APIView):
    permission_classes = [permissions.AllowAny]
    authentication_classes = []
    throttle_scope = "password_reset"

    def post(self, request):
        serializer = PasswordResetConfirmSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data["user"]
        user.set_password(serializer.validated_data["new_password"])
        user.save(update_fields=["password"])
        log_action("auth.reinitialisation_mot_de_passe", user=user, request=request)
        return Response({"detail": "Mot de passe modifie."})


@extend_schema_view(
    list=extend_schema(tags=["utilisateurs"], summary="Lister les utilisateurs (admin)"),
    retrieve=extend_schema(tags=["utilisateurs"], summary="Détail d'un utilisateur (admin)"),
)
class UtilisateurViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAdminRole]
    filterset_fields = ["role", "is_active"]
    search_fields = ["nom", "email"]

    @extend_schema(
        tags=["utilisateurs"],
        summary="Modifier le rôle d'un utilisateur (admin, journalisé)",
        request=RoleUpdateSerializer,
        responses={200: UserSerializer},
    )
    @action(detail=True, methods=["patch"])
    def role(self, request, pk=None):
        user = self.get_object()
        serializer = RoleUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        ancien = user.role
        user.role = serializer.validated_data["role"]
        user.save(update_fields=["role"])
        log_action(
            "utilisateur.changement_role",
            request=request,
            cible=user.pk,
            ancien=ancien,
            nouveau=user.role,
        )
        return Response(UserSerializer(user).data, status=status.HTTP_200_OK)
