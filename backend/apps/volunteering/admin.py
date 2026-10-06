from django.contrib import admin

from .models import Candidature


@admin.register(Candidature)
class CandidatureAdmin(admin.ModelAdmin):
    list_display = ("nom", "email", "role_souhaite", "statut", "date")
    list_filter = ("statut", "role_souhaite")
    search_fields = ("nom", "email", "motivation")
    actions = ["marquer_en_revue", "marquer_acceptee", "marquer_refusee"]

    @admin.action(description="Marquer « En revue »")
    def marquer_en_revue(self, request, qs):
        qs.update(statut=Candidature.Statut.EN_REVUE)

    @admin.action(description="Marquer « Acceptée »")
    def marquer_acceptee(self, request, qs):
        qs.update(statut=Candidature.Statut.ACCEPTEE)

    @admin.action(description="Marquer « Refusée »")
    def marquer_refusee(self, request, qs):
        qs.update(statut=Candidature.Statut.REFUSEE)
