from functools import wraps

from src.domain.enums import Role
from src.domain.errors import AuthError, PermissionDenied


_account_lookup = None


def set_account_lookup(lookup):
    global _account_lookup
    _account_lookup = lookup


def check_account(user, row):
    if row is None or not row["is_active"]:
        raise AuthError("This account has been disabled.")
    if Role(row["role"]) != user.role:
        raise AuthError("Your account was changed by an administrator. Please log in again.")


def require_role(*allowed_roles):
    def decorator(func):
        @wraps(func)
        def wrapper(self, user, *args, **kwargs):
            if user is None:
                raise AuthError("You must be logged in.")
            if _account_lookup is not None:
                check_account(user, _account_lookup(user.id))
            if user.role not in allowed_roles:
                raise PermissionDenied("You are not allowed to do that.")
            return func(self, user, *args, **kwargs)
        return wrapper
    return decorator
