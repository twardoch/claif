"""Common error types for CLAIF framework."""

from typing import Optional, Dict, Any


class ClaifError(Exception):
    """Base exception for CLAIF framework."""
    
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(message)
        self.message = message
        self.details = details or {}


class ProviderError(ClaifError):
    """Error from a specific provider."""
    
    def __init__(self, provider: str, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(f"{provider}: {message}", details)
        self.provider = provider


class ConfigurationError(ClaifError):
    """Configuration-related error."""
    pass


class SessionError(ClaifError):
    """Session management error."""
    pass


class TransportError(ClaifError):
    """Transport layer error."""
    pass


class TimeoutError(ClaifError):
    """Operation timeout error."""
    pass


class ValidationError(ClaifError):
    """Input validation error."""
    pass