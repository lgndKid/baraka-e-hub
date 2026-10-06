from django.contrib import admin

from .models import Article


@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    list_display = ("titre", "auteur", "date_publication", "publie")
    list_filter = ("publie",)
    search_fields = ("titre", "contenu")
    prepopulated_fields = {"slug": ("titre",)}

    def save_model(self, request, obj, form, change):
        if not obj.auteur_id:
            obj.auteur = request.user
        super().save_model(request, obj, form, change)
