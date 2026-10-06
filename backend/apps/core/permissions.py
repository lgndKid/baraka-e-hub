from datetime import date

from rest_framework.permissions import SAFE_METHODS, BasePermission


def is_admin(user):
    return bool(
        user and user.is_authenticated and (user.role == "admin" or user.is_superuser)
    )


def is_active_member(user):
    if not (user and user.is_authenticated):
        return False
    if is_admin(user):
        return True
    membre = getattr(user, "membre", None)
    return bool(membre and membre.est_active)


class IsAdminRole(BasePermission):
    """Admin / Equipe."""

    message = "Reserve a l'equipe E-Baraka."

    def has_permission(self, request, view):
        return is_admin(request.user)


class IsAdminOrReadOnly(BasePermission):
    def has_permission(self, request, view):
        return request.method in SAFE_METHODS or is_admin(request.user)


class IsActiveMember(BasePermission):
    """Membre avec carte active (ou admin)."""

    message = "Une carte de membre active est requise."

    def has_permission(self, request, view):
        return is_active_member(request.user)
