"""Application-specific exceptions for core."""


class AuthorizationError(Exception):
    """Raised when a user tries to access a resource they don't own."""

class NotFoundError(Exception):
    """Raised when a requested resource doesn't exist."""