"""Tests for claif.common.errors module."""

import pytest

from claif.common.errors import (
    ClaifError,
    ProviderError,
    ConfigurationError,
    SessionError,
    TransportError,
    ClaifTimeoutError,
    ValidationError
)


class TestClaifError:
    """Test base ClaifError class."""
    
    def test_claif_error_basic(self):
        """Test basic ClaifError creation."""
        error = ClaifError("Test error message")
        assert str(error) == "Test error message"
        assert error.message == "Test error message"
        assert error.details == {}
    
    def test_claif_error_with_details(self):
        """Test ClaifError with details."""
        details = {"code": 500, "context": "API call failed"}
        error = ClaifError("Error occurred", details=details)
        assert str(error) == "Error occurred"
        assert error.message == "Error occurred"
        assert error.details["code"] == 500
        assert error.details["context"] == "API call failed"
    
    def test_claif_error_inheritance(self):
        """Test that ClaifError inherits from Exception."""
        error = ClaifError("Test")
        assert isinstance(error, Exception)
    
    def test_claif_error_empty_details(self):
        """Test ClaifError with None details."""
        error = ClaifError("Test", details=None)
        assert error.details == {}


class TestProviderError:
    """Test ProviderError class."""
    
    def test_provider_error_basic(self):
        """Test basic ProviderError."""
        error = ProviderError("claude", "Provider failed")
        assert str(error) == "claude: Provider failed"
        assert error.provider == "claude"
        assert error.message == "claude: Provider failed"
    
    def test_provider_error_with_details(self):
        """Test ProviderError with additional details."""
        details = {"endpoint": "/v1/chat", "status": 503}
        error = ProviderError("gemini", "API call failed", details=details)
        assert str(error) == "gemini: API call failed"
        assert error.provider == "gemini"
        assert error.details["endpoint"] == "/v1/chat"
        assert error.details["status"] == 503
    
    def test_provider_error_inheritance(self):
        """Test ProviderError inheritance chain."""
        error = ProviderError("test", "Test error")
        assert isinstance(error, ClaifError)
        assert isinstance(error, Exception)


class TestConfigurationError:
    """Test ConfigurationError class."""
    
    def test_config_error_basic(self):
        """Test basic ConfigurationError."""
        error = ConfigurationError("Invalid configuration")
        assert str(error) == "Invalid configuration"
        assert error.message == "Invalid configuration"
    
    def test_config_error_with_details(self):
        """Test ConfigurationError with details."""
        details = {"field": "api_key", "reason": "missing"}
        error = ConfigurationError("Missing required field", details=details)
        assert error.details["field"] == "api_key"
        assert error.details["reason"] == "missing"
    
    def test_config_error_inheritance(self):
        """Test ConfigurationError inheritance."""
        error = ConfigurationError("Test")
        assert isinstance(error, ClaifError)
        assert isinstance(error, Exception)


class TestSessionError:
    """Test SessionError class."""
    
    def test_session_error_basic(self):
        """Test basic SessionError."""
        error = SessionError("Session expired")
        assert str(error) == "Session expired"
        assert error.message == "Session expired"
    
    def test_session_error_with_details(self):
        """Test SessionError with session details."""
        details = {"session_id": "abc123", "duration": 3600}
        error = SessionError("Session timeout", details=details)
        assert error.details["session_id"] == "abc123"
        assert error.details["duration"] == 3600
    
    def test_session_error_inheritance(self):
        """Test SessionError inheritance."""
        error = SessionError("Test")
        assert isinstance(error, ClaifError)


class TestTransportError:
    """Test TransportError class."""
    
    def test_transport_error_basic(self):
        """Test basic TransportError."""
        error = TransportError("Connection failed")
        assert str(error) == "Connection failed"
        assert error.message == "Connection failed"
    
    def test_transport_error_with_details(self):
        """Test TransportError with network details."""
        details = {"host": "api.example.com", "port": 443, "protocol": "https"}
        error = TransportError("Network timeout", details=details)
        assert error.details["host"] == "api.example.com"
        assert error.details["port"] == 443
        assert error.details["protocol"] == "https"
    
    def test_transport_error_inheritance(self):
        """Test TransportError inheritance."""
        error = TransportError("Test")
        assert isinstance(error, ClaifError)


class TestClaifTimeoutError:
    """Test ClaifTimeoutError class."""
    
    def test_timeout_error_basic(self):
        """Test basic ClaifTimeoutError."""
        error = ClaifTimeoutError("Operation timed out")
        assert str(error) == "Operation timed out"
        assert error.message == "Operation timed out"
    
    def test_timeout_error_with_details(self):
        """Test ClaifTimeoutError with timeout details."""
        details = {"timeout_seconds": 30, "operation": "query", "provider": "claude"}
        error = ClaifTimeoutError("Query timeout", details=details)
        assert error.details["timeout_seconds"] == 30
        assert error.details["operation"] == "query"
        assert error.details["provider"] == "claude"
    
    def test_timeout_error_inheritance(self):
        """Test ClaifTimeoutError inheritance."""
        error = ClaifTimeoutError("Test")
        assert isinstance(error, ClaifError)


class TestValidationError:
    """Test ValidationError class."""
    
    def test_validation_error_basic(self):
        """Test basic ValidationError."""
        error = ValidationError("Invalid input")
        assert str(error) == "Invalid input"
        assert error.message == "Invalid input"
    
    def test_validation_error_with_field_details(self):
        """Test ValidationError with field validation details."""
        details = {
            "field": "temperature",
            "value": 3.0,
            "constraint": "Must be between 0 and 2"
        }
        error = ValidationError("Invalid temperature value", details=details)
        assert error.details["field"] == "temperature"
        assert error.details["value"] == 3.0
        assert error.details["constraint"] == "Must be between 0 and 2"
    
    def test_validation_error_inheritance(self):
        """Test ValidationError inheritance."""
        error = ValidationError("Test")
        assert isinstance(error, ClaifError)


class TestErrorScenarios:
    """Test common error scenarios."""
    
    def test_provider_initialization_errors(self):
        """Test errors during provider initialization."""
        # Missing API key
        error1 = ConfigurationError(
            "Missing API key",
            details={"provider": "claude", "field": "api_key"}
        )
        assert "Missing API key" in str(error1)
        
        # Invalid provider
        error2 = ValidationError(
            "Invalid provider name",
            details={"provider": "unknown", "valid_providers": ["claude", "gemini", "codex"]}
        )
        assert "Invalid provider name" in str(error2)
    
    def test_runtime_errors(self):
        """Test errors during runtime operations."""
        # Network timeout
        error1 = TransportError(
            "Connection timeout",
            details={"url": "https://api.anthropic.com", "timeout": 30}
        )
        assert "Connection timeout" in str(error1)
        
        # Provider API error
        error2 = ProviderError(
            "claude",
            "API rate limit exceeded",
            details={"retry_after": 60, "limit": 1000}
        )
        assert "claude: API rate limit exceeded" == str(error2)
        
        # Query timeout
        error3 = ClaifTimeoutError(
            "Query timeout after 30s",
            details={"provider": "gemini", "prompt_length": 5000}
        )
        assert "Query timeout after 30s" in str(error3)
    
    def test_error_chaining(self):
        """Test error chaining and context."""
        try:
            try:
                raise TransportError("Network issue")
            except TransportError as e:
                raise ProviderError(
                    "claude",
                    "Request failed due to network error",
                    details={"original_error": str(e)}
                ) from e
        except ProviderError as e:
            assert e.__cause__ is not None
            assert isinstance(e.__cause__, TransportError)
            assert str(e.__cause__) == "Network issue"
            assert e.details["original_error"] == "Network issue"
    
    def test_error_handling_patterns(self):
        """Test common error handling patterns."""
        def handle_provider_error():
            try:
                raise ProviderError("claude", "API error", {"status": 500})
            except ProviderError as e:
                # Can access provider-specific info
                assert e.provider == "claude"
                assert e.details["status"] == 500
                return f"Provider {e.provider} failed with status {e.details['status']}"
        
        result = handle_provider_error()
        assert result == "Provider claude failed with status 500"
    
    def test_error_comparison(self):
        """Test error comparison and type checking."""
        errors = [
            ClaifError("Base error"),
            ProviderError("claude", "Provider error"),
            ConfigurationError("Config error"),
            SessionError("Session error"),
            TransportError("Transport error"),
            ClaifTimeoutError("Timeout error"),
            ValidationError("Validation error")
        ]
        
        # All should be ClaifError instances
        for error in errors:
            assert isinstance(error, ClaifError)
        
        # Specific type checks
        assert isinstance(errors[1], ProviderError)
        assert not isinstance(errors[0], ProviderError)
        assert isinstance(errors[2], ConfigurationError)
        assert isinstance(errors[5], ClaifTimeoutError)