from django.contrib import admin

from .models import Membre


@admin.register(Membre)
class MembreAdmin(admin.ModelAdmin):
    list_display = ("utilisateur", "statut_carte", "date_debut", "date_fin", "ville", "pays")
    list_filter = ("statut_carte", "pays")
    search_fields = ("utilisateur__email", "utilisateur__nom", "profession", "entreprise")
