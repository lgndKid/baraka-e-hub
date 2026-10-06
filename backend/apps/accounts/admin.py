from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin

from apps.core.audit import log_action

from .models import User


@admin.register(User)
class UserAdmin(DjangoUserAdmin):
    ordering = ("-date_inscription",)
    list_display = ("email", "nom", "role", "is_active", "date_inscription")
    list_filter = ("role", "is_active", "is_staff")
    search_fields = ("email", "nom")
    fieldsets = (
        (None, {"fields": ("email", "password")}),
        ("Profil", {"fields": ("nom", "role", "consentement_donnees")}),
        ("Droits", {"fields": ("is_active", "is_staff", "is_superuser", "groups", "user_permissions")}),
        ("Dates", {"fields": ("last_login", "date_inscription")}),
    )
    add_fieldsets = (
        (None, {"classes": ("wide",), "fields": ("email", "nom", "role", "password1", "password2")}),
    )

    def save_model(self, request, obj, form, change):
        if change and "role" in form.changed_data:
            log_action(
                "utilisateur.changement_role",
                request=request,
                cible=obj.pk,
                nouveau=obj.role,
            )
        super().save_model(request, obj, form, change)
