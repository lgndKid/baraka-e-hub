from django.contrib import admin

from .models import Cours, Inscription


@admin.register(Cours)
class CoursAdmin(admin.ModelAdmin):
    list_display = ("titre", "categorie", "niveau", "intervenant", "publie")
    list_filter = ("categorie", "niveau", "publie")
    search_fields = ("titre", "description", "intervenant")


@admin.register(Inscription)
class InscriptionAdmin(admin.ModelAdmin):
    list_display = ("membre", "cours", "progression", "date")
    list_filter = ("cours",)
