from django.contrib import admin

from .models import Notification


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ("utilisateur", "type", "titre", "lue", "date")
    list_filter = ("type", "lue")
    search_fields = ("titre", "utilisateur__email")
