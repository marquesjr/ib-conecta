from functools import wraps

from django.contrib.auth.views import redirect_to_login
from django.core.exceptions import PermissionDenied

from apps.accounts.permissions import user_has_permission


def permission_required(*permissions):
    """Require the user to have at least one of the given permissions."""

    def decorator(view_func):
        @wraps(view_func)
        def _wrapped(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return redirect_to_login(request.get_full_path())
            if not any(user_has_permission(request.user, permission) for permission in permissions):
                raise PermissionDenied
            return view_func(request, *args, **kwargs)

        return _wrapped

    return decorator
