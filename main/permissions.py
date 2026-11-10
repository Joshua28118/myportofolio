from functools import wraps

from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from rest_framework.permissions import BasePermission, SAFE_METHODS


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


class IsPortfolioOwnerOrReadOnly(BasePermission):
    message = "Only the portfolio owner can change projects."

    def has_permission(self, request, view):
        return (
            request.method in SAFE_METHODS
            or request.user.is_superuser
        )


class IsPortfolioOwnerOrEditorOrReadOnly(BasePermission):
    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True
        if not request.user.is_authenticated:
            return False
        if request.user.is_superuser:
            return True
        return (
            request.method in ("PUT", "PATCH")
            and request.user.groups.filter(name="Editor").exists()
        )
