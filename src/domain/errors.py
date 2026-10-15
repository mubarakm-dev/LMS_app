class LMSError(Exception):
    """Base class for all application errors shown to the user."""


class ValidationError(LMSError):
    pass


class AuthError(LMSError):
    pass


class PermissionDenied(LMSError):
    pass


class NotFound(LMSError):
    pass


class DuplicateError(LMSError):
    pass


class ServiceUnavailable(LMSError):
    """Database, SMTP, microphone, TTS or translation backend failed."""
