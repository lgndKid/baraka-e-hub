from django.utils import timezone
from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework import viewsets
from rest_framework.parsers import FormParser, JSONParser, MultiPartParser

from apps.core.permissions import IsAdminOrReadOnly, is_admin

from .models import Article
from .serializers import ArticleSerializer


@extend_schema_view(
    list=extend_schema(summary="Lister les articles publiés (public)"),
    retrieve=extend_schema(summary="Lire un article (public)"),
    create=extend_schema(summary="Créer un article (admin)"),
    update=extend_schema(summary="Remplacer un article (admin)"),
    partial_update=extend_schema(summary="Modifier un article (admin)"),
    destroy=extend_schema(summary="Supprimer un article (admin)"),
)
class ArticleViewSet(viewsets.ModelViewSet):
    serializer_class = ArticleSerializer
    permission_classes = [IsAdminOrReadOnly]
    parser_classes = [JSONParser, MultiPartParser, FormParser]
    search_fields = ["titre", "contenu"]
    ordering_fields = ["date_publication", "titre"]
    filterset_fields = ["auteur"]

    def get_queryset(self):
        qs = Article.objects.select_related("auteur")
        if is_admin(self.request.user):
            return qs
        return qs.filter(publie=True, date_publication__lte=timezone.now())

    def perform_create(self, serializer):
        serializer.save(auteur=self.request.user)
