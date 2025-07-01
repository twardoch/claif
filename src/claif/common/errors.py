"""Common error types for CLAIF framework."""

from typing import Any


class ClaifError(Exception):
    """Base exception for CLAIF framework."""

    def __init__(self, message: str, details: dict[str, Any] | None = None):
        super().__init__(message)
        self.message = message
        self.details = details or {}


class ProviderError(ClaifError):
    """Error from a specific provider."""

    def __init__(self, provider: str, message: str, details: dict[str, Any] | None = None):
        super().__init__(f"{provider}: {message}", details)
        self.provider = provider


class ConfigurationError(ClaifError):
    """Configuration-related error."""


class SessionError(ClaifError):
    """Session management error."""


class TransportError(ClaifError):
    """Transport layer error."""


class ClaifTimeoutError(ClaifError):
    """Operation timeout error."""


class ValidationError(ClaifError):
    """Input validation error."""
