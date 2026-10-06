from django.urls import include, path
from rest_framework.routers import DefaultRouter

from apps.accounts.views import UtilisateurViewSet
from apps.blog.views import ArticleViewSet
from apps.contact.views import MessageContactViewSet
from apps.courses.views import CoursViewSet, InscriptionViewSet
from apps.members.views import MembreViewSet
from apps.notifications.views import NotificationViewSet
from apps.payments.views import PaiementViewSet
from apps.volunteering.views import CandidatureViewSet

router = DefaultRouter(trailing_slash=False)
router.register("utilisateurs", UtilisateurViewSet, basename="utilisateur")
router.register("candidatures", CandidatureViewSet, basename="candidature")
router.register("blog", ArticleViewSet, basename="article")
router.register("contacts", MessageContactViewSet, basename="contact")
router.register("membres", MembreViewSet, basename="membre")
router.register("cours", CoursViewSet, basename="cours")
router.register("inscriptions", InscriptionViewSet, basename="inscription")
router.register("paiements", PaiementViewSet, basename="paiement")
router.register("notifications", NotificationViewSet, basename="notification")

urlpatterns = [
    path("auth/", include("apps.accounts.urls")),
    path("", include(router.urls)),
]
