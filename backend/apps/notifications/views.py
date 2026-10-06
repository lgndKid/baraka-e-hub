from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework import mixins, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import Notification
from .serializers import NotificationSerializer


@extend_schema_view(
    list=extend_schema(summary="Mes notifications"),
)
class NotificationViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    serializer_class = NotificationSerializer
    filterset_fields = ["lue", "type"]
    ordering_fields = ["date"]

    def get_queryset(self):
        if getattr(self, "swagger_fake_view", False):
            return Notification.objects.none()
        return Notification.objects.filter(utilisateur=self.request.user)

    @extend_schema(
        summary="Marquer une notification comme lue",
        request=None,
        responses={200: NotificationSerializer},
    )
    @action(detail=True, methods=["post"], url_path="lire")
    def lire(self, request, pk=None):
        notif = self.get_object()
        notif.lue = True
        notif.save(update_fields=["lue"])
        return Response(NotificationSerializer(notif).data)

    @extend_schema(summary="Tout marquer comme lu", request=None, responses={204: None})
    @action(detail=False, methods=["post"], url_path="lire-tout")
    def lire_tout(self, request):
        self.get_queryset().filter(lue=False).update(lue=True)
        return Response(status=204)
