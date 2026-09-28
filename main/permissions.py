from functools import wraps

from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied


def can_edit_portfolio(user):
    return user.is_authenticated and (
        user.is_superuser or user.groups.filter(name="Editor").exists()
    )


def _role_required(view, *, allow_editor):
    @login_required(login_url="main:login")
    @wraps(view)
    def protected(request, *args, **kwargs):
        allowed = (
            can_edit_portfolio(request.user)
            if allow_editor else request.user.is_superuser
        )
        if not allowed:
            raise PermissionDenied
        return view(request, *args, **kwargs)

    return protected


def owner_required(view):
    return _role_required(view, allow_editor=False)


def editor_required(view):
    return _role_required(view, allow_editor=True)
