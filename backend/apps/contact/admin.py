from django.contrib import admin

from .models import MessageContact


@admin.register(MessageContact)
class MessageContactAdmin(admin.ModelAdmin):
    list_display = ("nom", "email", "date", "traite")
    list_filter = ("traite",)
    search_fields = ("nom", "email", "message")
    actions = ["marquer_traite"]

    @admin.action(description="Marquer comme traité")
    def marquer_traite(self, request, qs):
        qs.update(traite=True)
