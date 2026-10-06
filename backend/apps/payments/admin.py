from django.contrib import admin

from .models import Paiement


@admin.register(Paiement)
class PaiementAdmin(admin.ModelAdmin):
    list_display = ("reference", "membre", "montant", "devise", "methode", "statut", "date")
    list_filter = ("statut", "methode")
    search_fields = ("reference", "membre__utilisateur__email", "reference_passerelle")
    readonly_fields = ("reference", "date", "date_confirmation")
