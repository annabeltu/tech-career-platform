"""Application-specific exceptions for core."""


class AuthorizationError(Exception):
    """Raised when a user lacks permission for the requested operation."""