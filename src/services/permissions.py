from functools import wraps

from src.domain.errors import AuthError, PermissionDenied


def require_role(*allowed_roles):
    def decorator(func):
        @wraps(func)
        def wrapper(self, user, *args, **kwargs):
            if user is None:
                raise AuthError("You must be logged in.")
            if user.role not in allowed_roles:
                raise PermissionDenied("You are not allowed to do that.")
            return func(self, user, *args, **kwargs)
        return wrapper
    return decorator
