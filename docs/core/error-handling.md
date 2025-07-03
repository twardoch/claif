---
layout: default
title: Error Handling
parent: Core Framework
nav_order: 4
---

# Error Handling

Claif provides a comprehensive error handling system with structured exceptions, detailed error information, and recovery strategies.

## Exception Hierarchy

### Base Exception

```python
class ClaifError(Exception):
    """Base exception for Claif framework."""
    
    def __init__(self, message: str, details: dict[str, Any] | None = None):
        super().__init__(message)
        self.message = message
        self.details = details or {}
```

All Claif exceptions inherit from `ClaifError` and include:
- **Structured messages**: Clear, actionable error descriptions
- **Details dictionary**: Additional context and debugging information
- **Type hierarchy**: Specific exception types for different error categories

### Exception Types

```
ClaifError (base)
├── ProviderError              # Provider-specific errors
├── ConfigurationError         # Configuration issues
├── SessionError              # Session management errors
├── TransportError            # Network/transport errors
├── ClaifTimeoutError         # Timeout errors
└── ValidationError           # Input validation errors
```

## Provider Errors

### ProviderError

Used for provider-specific failures:

```python
class ProviderError(ClaifError):
    """Error from a specific provider."""
    
    def __init__(self, provider: str, message: str, details: dict[str, Any] | None = None):
        super().__init__(f"{provider}: {message}", details)
        self.provider = provider
```

**Common scenarios:**
- API rate limiting
- Invalid API responses
- CLI tool failures
- Authentication errors

**Example usage:**

```python
try:
    async for message in provider.query("Hello", options):
        yield message
except Exception as e:
    raise ProviderError(
        provider="claude",
        message="API request failed",
        details={
            "status_code": 429,
            "error_type": "rate_limit",
            "retry_after": 60
        }
    ) from e
```

## Configuration Errors

### ConfigurationError

Used for configuration-related issues:

```python
class ConfigurationError(ClaifError):
    """Configuration-related error."""
```

**Common scenarios:**
- Missing API keys
- Invalid configuration files
- Malformed settings
- Missing required dependencies

**Examples:**

```python
# Missing API key
raise ConfigurationError(
    "API key not found for provider 'claude'",
    details={
        "provider": "claude",
        "env_var": "ANTHROPIC_API_KEY",
        "config_file": "~/.claif/config.json"
    }
)

# Invalid configuration
raise ConfigurationError(
    "Invalid timeout value in configuration",
    details={
        "value": -1,
        "expected": "positive integer",
        "location": "providers.claude.timeout"
    }
)
```

## Timeout Errors

### ClaifTimeoutError

Used for operation timeouts:

```python
class ClaifTimeoutError(ClaifError):
    """Operation timeout error."""
```

**Common scenarios:**
- Network request timeouts
- CLI process timeouts
- Session timeouts
- Response streaming timeouts

**Example:**

```python
import asyncio

async def query_with_timeout(self, prompt: str, timeout: int):
    try:
        async with asyncio.timeout(timeout):
            return await self._execute_query(prompt)
    except asyncio.TimeoutError:
        raise ClaifTimeoutError(
            f"Query timed out after {timeout} seconds",
            details={
                "timeout": timeout,
                "provider": self.name,
                "prompt_length": len(prompt)
            }
        )
```

## Transport Errors

### TransportError

Used for network and communication failures:

```python
class TransportError(ClaifError):
    """Transport layer error."""
```

**Common scenarios:**
- Network connectivity issues
- HTTP errors
- SSL/TLS failures
- DNS resolution failures

**Example:**

```python
import aiohttp

try:
    async with session.post(url, json=payload) as response:
        return await response.json()
except aiohttp.ClientConnectorError as e:
    raise TransportError(
        "Failed to connect to provider API",
        details={
            "url": url,
            "error": str(e),
            "provider": self.name
        }
    ) from e
```

## Validation Errors

### ValidationError

Used for input validation failures:

```python
class ValidationError(ClaifError):
    """Input validation error."""
```

**Common scenarios:**
- Empty or invalid prompts
- Invalid option values
- Malformed input data
- Type validation failures

**Example:**

```python
def validate_prompt(prompt: str) -> None:
    if not prompt or not prompt.strip():
        raise ValidationError(
            "Prompt cannot be empty",
            details={
                "prompt_length": len(prompt),
                "prompt_stripped": len(prompt.strip()) if prompt else 0
            }
        )
    
    if len(prompt) > 100000:
        raise ValidationError(
            "Prompt exceeds maximum length",
            details={
                "prompt_length": len(prompt),
                "max_length": 100000
            }
        )
```

## Session Errors

### SessionError

Used for session management failures:

```python
class SessionError(ClaifError):
    """Session management error."""
```

**Common scenarios:**
- Session file corruption
- Concurrent session access
- Session storage issues
- Session expiration

**Example:**

```python
try:
    session = await self.load_session(session_id)
except FileNotFoundError:
    raise SessionError(
        f"Session not found: {session_id}",
        details={
            "session_id": session_id,
            "session_dir": self.session_dir,
            "available_sessions": await self.list_sessions()
        }
    )
```

## Error Handling Patterns

### Try-Catch with Specific Exceptions

```python
from claif.common.errors import (
    ProviderError, 
    ConfigurationError, 
    ClaifTimeoutError,
    ValidationError
)

async def robust_query(client, prompt: str):
    try:
        response = await client.query(prompt)
        return response
        
    except ValidationError as e:
        # Handle user input errors - don't retry
        logger.error(f"Invalid input: {e.message}")
        raise
        
    except ConfigurationError as e:
        # Handle config errors - guide user to fix configuration
        logger.error(f"Configuration error: {e.message}")
        print("Please run 'claif config' to set up your configuration")
        raise
        
    except ClaifTimeoutError as e:
        # Handle timeouts - suggest retry with longer timeout
        logger.warning(f"Request timed out: {e.message}")
        logger.info("Try increasing timeout with --timeout option")
        raise
        
    except ProviderError as e:
        # Handle provider errors - attempt retry or fallback
        logger.warning(f"Provider error: {e.message}")
        if e.details.get("status_code") == 429:
            logger.info("Rate limited, waiting before retry...")
            await asyncio.sleep(e.details.get("retry_after", 60))
            # Retry logic here
        raise
        
    except Exception as e:
        # Handle unexpected errors
        logger.error(f"Unexpected error: {e}")
        raise
```

### Context Manager for Error Handling

```python
from contextlib import asynccontextmanager

@asynccontextmanager
async def error_context(operation: str, provider: str = None):
    """Context manager for consistent error handling."""
    try:
        logger.debug(f"Starting {operation}")
        yield
        logger.debug(f"Completed {operation}")
        
    except ClaifError:
        # Re-raise Claif errors as-is
        raise
        
    except Exception as e:
        # Convert unexpected errors to ClaifError
        error_msg = f"Unexpected error during {operation}: {e}"
        details = {"operation": operation}
        if provider:
            details["provider"] = provider
            
        logger.error(error_msg, extra=details)
        raise ClaifError(error_msg, details) from e

# Usage
async def query_provider(self, prompt: str):
    async with error_context("provider query", self.name):
        return await self._execute_query(prompt)
```

### Retry Logic with Error Types

```python
from tenacity import (
    retry, 
    stop_after_attempt, 
    wait_exponential,
    retry_if_exception_type
)

@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=1, max=10),
    retry=retry_if_exception_type((ProviderError, TransportError, ClaifTimeoutError))
)
async def query_with_retry(provider, prompt: str, options):
    """Query with automatic retry for transient errors."""
    try:
        return await provider.query(prompt, options)
    except (ValidationError, ConfigurationError):
        # Don't retry permanent errors
        raise
    except ProviderError as e:
        # Only retry certain provider errors
        if e.details.get("status_code") in [429, 502, 503, 504]:
            logger.warning(f"Retrying after provider error: {e.message}")
            raise
        else:
            # Don't retry permanent provider errors
            raise
```

## Error Recovery Strategies

### Automatic Fallback

```python
async def query_with_fallback(prompt: str, providers: list[str]):
    """Try multiple providers with automatic fallback."""
    last_error = None
    
    for provider_name in providers:
        try:
            provider = get_provider(provider_name)
            return await provider.query(prompt)
            
        except (ProviderError, ClaifTimeoutError) as e:
            logger.warning(f"Provider {provider_name} failed: {e.message}")
            last_error = e
            continue
            
        except (ConfigurationError, ValidationError):
            # Don't try other providers for these errors
            raise
    
    # All providers failed
    raise ProviderError(
        "all_providers",
        "All providers failed",
        details={
            "tried_providers": providers,
            "last_error": str(last_error)
        }
    ) from last_error
```

### Graceful Degradation

```python
async def query_with_degradation(prompt: str, options):
    """Query with graceful degradation of features."""
    try:
        # Try full-featured query first
        return await provider.query(prompt, options)
        
    except ProviderError as e:
        if "tools_not_supported" in e.details:
            # Retry without tools
            logger.info("Retrying without tool support")
            options_no_tools = dataclasses.replace(options, enable_tools=False)
            return await provider.query(prompt, options_no_tools)
        raise
        
    except ClaifTimeoutError:
        # Retry with shorter prompt
        if len(prompt) > 1000:
            logger.info("Retrying with truncated prompt")
            short_prompt = prompt[:1000] + "..."
            return await provider.query(short_prompt, options)
        raise
```

## Error Reporting

### Structured Error Information

```python
def format_error_report(error: ClaifError) -> dict:
    """Format error for reporting/logging."""
    return {
        "error_type": type(error).__name__,
        "message": error.message,
        "details": error.details,
        "timestamp": datetime.utcnow().isoformat(),
        "provider": getattr(error, 'provider', None),
        "stack_trace": traceback.format_exc() if logger.level <= logging.DEBUG else None
    }
```

### User-Friendly Error Messages

```python
def get_user_message(error: ClaifError) -> str:
    """Convert technical error to user-friendly message."""
    
    if isinstance(error, ConfigurationError):
        if "api_key" in error.message.lower():
            return (
                "API key not configured. "
                "Please run 'claif config' to set up your API keys."
            )
        return f"Configuration error: {error.message}"
    
    elif isinstance(error, ProviderError):
        if error.details.get("status_code") == 429:
            return (
                "Rate limit exceeded. "
                "Please wait a moment before trying again."
            )
        elif error.details.get("status_code") == 401:
            return (
                "Authentication failed. "
                "Please check your API key configuration."
            )
        return f"Provider error: {error.message}"
    
    elif isinstance(error, ClaifTimeoutError):
        return (
            "Request timed out. "
            "Try using a shorter prompt or increasing the timeout."
        )
    
    elif isinstance(error, ValidationError):
        return f"Invalid input: {error.message}"
    
    else:
        return f"An error occurred: {error.message}"
```

## Debugging and Logging

### Error Logging

```python
import logging
from claif.common.utils import logger

def log_error(error: ClaifError, context: dict = None):
    """Log error with appropriate level and context."""
    
    log_data = {
        "error_type": type(error).__name__,
        "message": error.message,
        **error.details,
        **(context or {})
    }
    
    if isinstance(error, (ValidationError, ConfigurationError)):
        # User errors - info level
        logger.info("User error occurred", extra=log_data)
    elif isinstance(error, ProviderError):
        # Provider errors - warning level
        logger.warning("Provider error occurred", extra=log_data)
    else:
        # System errors - error level
        logger.error("System error occurred", extra=log_data)
```

### Debug Information

```python
def add_debug_info(error: ClaifError, **debug_info):
    """Add debug information to error details."""
    error.details.setdefault("debug", {})
    error.details["debug"].update(debug_info)
    return error

# Usage
try:
    result = await api_call()
except Exception as e:
    error = ProviderError(self.name, "API call failed")
    add_debug_info(
        error,
        api_endpoint=url,
        request_id=request_id,
        response_headers=response.headers
    )
    raise error from e
```

## Testing Error Handling

### Unit Tests

```python
import pytest
from claif.common.errors import ProviderError, ConfigurationError

def test_provider_error():
    """Test ProviderError creation and attributes."""
    error = ProviderError(
        provider="test",
        message="Test error",
        details={"code": 500}
    )
    
    assert error.provider == "test"
    assert "test: Test error" in str(error)
    assert error.details["code"] == 500

@pytest.mark.asyncio
async def test_error_handling():
    """Test error handling in provider."""
    provider = TestProvider()
    
    with pytest.raises(ValidationError):
        await provider.query("", options)
    
    with pytest.raises(ConfigurationError):
        provider.api_key = None
        await provider.query("test", options)
```

### Mock Error Scenarios

```python
from unittest.mock import patch, AsyncMock

@pytest.mark.asyncio
async def test_timeout_handling():
    """Test timeout error handling."""
    provider = TestProvider()
    
    with patch.object(provider, '_execute_query') as mock_query:
        mock_query.side_effect = asyncio.TimeoutError()
        
        with pytest.raises(ClaifTimeoutError):
            await provider.query("test", options)

@pytest.mark.asyncio  
async def test_provider_error_handling():
    """Test provider error handling."""
    provider = TestProvider()
    
    with patch.object(provider, '_execute_query') as mock_query:
        mock_query.side_effect = Exception("API Error")
        
        with pytest.raises(ProviderError) as exc_info:
            await provider.query("test", options)
        
        assert "API Error" in str(exc_info.value)
```

## Best Practices

### 1. Use Specific Exception Types

```python
# Good - specific exception
raise ConfigurationError("Missing API key for Claude provider")

# Bad - generic exception  
raise Exception("Configuration error")
```

### 2. Include Helpful Details

```python
# Good - detailed error information
raise ProviderError(
    provider="claude",
    message="Rate limit exceeded",
    details={
        "status_code": 429,
        "retry_after": 60,
        "limit_type": "requests_per_minute",
        "current_usage": 100
    }
)

# Bad - minimal information
raise ProviderError("claude", "Error")
```

### 3. Chain Exceptions

```python
# Good - preserve original exception
try:
    result = api_call()
except HTTPError as e:
    raise ProviderError(
        provider="claude",
        message="API request failed"
    ) from e

# Bad - lose original exception information
try:
    result = api_call()
except HTTPError:
    raise ProviderError("claude", "API request failed")
```

### 4. Handle Errors at Appropriate Level

```python
# Handle specific errors where they can be resolved
try:
    config = load_config()
except ConfigurationError:
    # Can handle here - prompt user to configure
    run_configuration_wizard()
    config = load_config()

# Let generic errors bubble up
try:
    response = await provider.query(prompt)
except ProviderError:
    # Let calling code handle provider errors
    raise
```

The error handling system provides comprehensive coverage of failure scenarios while maintaining clear error types and actionable information for debugging and recovery.