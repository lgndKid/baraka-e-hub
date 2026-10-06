import json

from django.core.serializers.json import DjangoJSONEncoder

from .models import AuditLog


def _ip(request):
    if request is None:
        return None
    xff = request.META.get("HTTP_X_FORWARDED_FOR")
    if xff:
        return xff.split(",")[0].strip()
    return request.META.get("REMOTE_ADDR")


def log_action(action, user=None, request=None, **details):
    if user is None and request is not None and request.user.is_authenticated:
        user = request.user
    safe = json.loads(json.dumps(details, cls=DjangoJSONEncoder))
    return AuditLog.objects.create(
        utilisateur=user, action=action, details=safe, adresse_ip=_ip(request)
    )
