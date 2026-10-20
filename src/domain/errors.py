class LMSError(Exception):
    pass


class ValidationError(LMSError):
    pass


class AuthError(LMSError):
    pass


class UnverifiedError(AuthError):
    pass


class PermissionDenied(LMSError):
    pass


class NotFound(LMSError):
    pass


class DuplicateError(LMSError):
    pass


class ServiceUnavailable(LMSError):
    pass
