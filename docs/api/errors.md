---
layout: default
title: Error Types
parent: API Reference
nav_order: 3
---

# Error Types

Comprehensive documentation of Claif's exception hierarchy and error handling.

## Exception Hierarchy

```
ClaifError
├── ConfigurationError
├── ProviderError
│   ├── ProviderNotFoundError
│   ├── ProviderUnavailableError
│   ├── AuthenticationError
│   ├── RateLimitError
│   └── ProviderTimeoutError
├── ValidationError
│   ├── MessageValidationError
│   └── OptionsValidationError
├── NetworkError
│   ├── ConnectionError
│   └── TimeoutError
└── MCPError
    ├── ServerError
    └── ToolError
```

## Base Exception

### ClaifError

Base exception class for all Claif-related errors.

```python
from claif.common.errors import ClaifError

try:
    client.query("Hello")
except ClaifError as e:
    print(f"Claif error: {e}")
    print(f"Error code: {e.code}")
    print(f"Context: {e.context}")
```

**Attributes:**
- `message` (str) - Human-readable error message
- `code` (str) - Error code for programmatic handling
- `context` (Dict[str, Any]) - Additional error context
- `cause` (Optional[Exception]) - Original exception that caused this error

**Methods:**
- `to_dict()` - Convert error to dictionary format
- `__str__()` - Human-readable string representation

## Configuration Errors

### ConfigurationError

Raised when there are configuration-related issues.

```python
from claif.common.errors import ConfigurationError

# Common scenarios:
# - Invalid config file format
# - Missing required configuration
# - Invalid configuration values
```

**Error Codes:**
- `CONFIG_FILE_NOT_FOUND` - Configuration file doesn't exist
- `CONFIG_PARSE_ERROR` - Configuration file is malformed
- `CONFIG_VALIDATION_ERROR` - Configuration values are invalid
- `MISSING_REQUIRED_CONFIG` - Required configuration is missing

**Example:**
```python
try:
    config = Config.load("invalid_config.toml")
except ConfigurationError as e:
    if e.code == "CONFIG_PARSE_ERROR":
        print("Fix your configuration file syntax")
    elif e.code == "MISSING_REQUIRED_CONFIG":
        print(f"Add missing config: {e.context['missing_keys']}")
```

## Provider Errors

### ProviderError

Base class for all provider-related errors.

```python
from claif.common.errors import ProviderError

try:
    response = client.query("Hello", provider="claude")
except ProviderError as e:
    print(f"Provider error: {e}")
    print(f"Provider: {e.context.get('provider_name')}")
```

**Common Attributes:**
- `provider_name` (str) - Name of the provider that failed
- `request_id` (str) - Unique request identifier for debugging

### ProviderNotFoundError

Raised when a requested provider is not found or not installed.

```python
from claif.common.errors import ProviderNotFoundError

try:
    client.query("Hello", provider="nonexistent")
except ProviderNotFoundError as e:
    print(f"Provider '{e.context['provider_name']}' not found")
    print(f"Available providers: {e.context['available_providers']}")
```

**Error Codes:**
- `PROVIDER_NOT_REGISTERED` - Provider not registered with framework
- `PROVIDER_PACKAGE_MISSING` - Provider package not installed

### ProviderUnavailableError

Raised when a provider is found but currently unavailable.

```python
from claif.common.errors import ProviderUnavailableError

try:
    client.query("Hello", provider="claude")
except ProviderUnavailableError as e:
    print(f"Provider unavailable: {e.context['reason']}")
    # Reason might be: "CLI not installed", "API key missing", etc.
```

**Error Codes:**
- `CLI_NOT_INSTALLED` - Provider CLI tool not installed
- `CLI_NOT_FOUND` - Provider CLI executable not found in PATH
- `API_KEY_MISSING` - Required API key not configured
- `HEALTH_CHECK_FAILED` - Provider failed health check

### AuthenticationError

Raised when authentication with a provider fails.

```python
from claif.common.errors import AuthenticationError

try:
    client.query("Hello", provider="claude")
except AuthenticationError as e:
    print("Check your API key configuration")
    print(f"Provider: {e.context['provider_name']}")
```

**Error Codes:**
- `INVALID_API_KEY` - API key is invalid or expired
- `AUTHENTICATION_FAILED` - Authentication request failed
- `INSUFFICIENT_PERMISSIONS` - API key lacks required permissions

### RateLimitError

Raised when API rate limits are exceeded.

```python
from claif.common.errors import RateLimitError
import time

try:
    client.query("Hello")
except RateLimitError as e:
    retry_after = e.context.get('retry_after', 60)
    print(f"Rate limited. Retry after {retry_after} seconds")
    time.sleep(retry_after)
```

**Error Codes:**
- `RATE_LIMIT_EXCEEDED` - API rate limit exceeded
- `QUOTA_EXCEEDED` - API quota exceeded

**Context Fields:**
- `retry_after` (int) - Seconds to wait before retrying
- `limit_type` (str) - Type of limit ("requests", "tokens", "daily")
- `reset_time` (datetime) - When the limit resets

### ProviderTimeoutError

Raised when a provider request times out.

```python
from claif.common.errors import ProviderTimeoutError

try:
    client.query("Complex task", timeout=30)
except ProviderTimeoutError as e:
    print(f"Request timed out after {e.context['timeout']} seconds")
```

**Error Codes:**
- `REQUEST_TIMEOUT` - Request exceeded timeout
- `CONNECTION_TIMEOUT` - Connection to provider timed out

## Validation Errors

### ValidationError

Base class for input validation errors.

```python
from claif.common.errors import ValidationError
```

### MessageValidationError

Raised when message format or content is invalid.

```python
from claif.common.errors import MessageValidationError
from claif.common.types import Message

try:
    # Invalid message format
    message = Message(content=[])  # Empty content
    client.query(message)
except MessageValidationError as e:
    print(f"Invalid message: {e}")
```

**Error Codes:**
- `EMPTY_MESSAGE` - Message has no content
- `INVALID_CONTENT_TYPE` - Content block type is invalid
- `MESSAGE_TOO_LONG` - Message exceeds maximum length
- `UNSUPPORTED_CONTENT` - Content type not supported by provider

### OptionsValidationError

Raised when query options are invalid.

```python
from claif.common.errors import OptionsValidationError

try:
    client.query("Hello", temperature=2.0)  # Invalid range
except OptionsValidationError as e:
    print(f"Invalid option: {e.context['option_name']}")
    print(f"Valid range: {e.context['valid_range']}")
```

**Error Codes:**
- `INVALID_OPTION_VALUE` - Option value is out of valid range
- `UNKNOWN_OPTION` - Option is not recognized
- `CONFLICTING_OPTIONS` - Options conflict with each other

## Network Errors

### NetworkError

Base class for network-related errors.

```python
from claif.common.errors import NetworkError
```

### ConnectionError

Raised when connection to provider fails.

```python
from claif.common.errors import ConnectionError

try:
    client.query("Hello")
except ConnectionError as e:
    print("Check your internet connection")
    print(f"Failed to connect to: {e.context['endpoint']}")
```

**Error Codes:**
- `CONNECTION_FAILED` - Failed to establish connection
- `DNS_RESOLUTION_FAILED` - Failed to resolve hostname
- `SSL_ERROR` - SSL/TLS connection error

### TimeoutError

Raised when network operations time out.

```python
from claif.common.errors import TimeoutError

try:
    client.query("Hello", timeout=5)
except TimeoutError as e:
    print(f"Request timed out after {e.context['timeout']} seconds")
```

## MCP Server Errors

### MCPError

Base class for Model Context Protocol server errors.

```python
from claif.common.errors import MCPError
```

### ServerError

Raised when MCP server encounters an error.

```python
from claif.common.errors import ServerError
```

**Error Codes:**
- `SERVER_STARTUP_FAILED` - Server failed to start
- `SERVER_SHUTDOWN_ERROR` - Error during server shutdown
- `INVALID_REQUEST` - Invalid MCP request format

### ToolError

Raised when MCP tool execution fails.

```python
from claif.common.errors import ToolError
```

**Error Codes:**
- `TOOL_NOT_FOUND` - Requested tool not available
- `TOOL_EXECUTION_FAILED` - Tool execution failed
- `INVALID_TOOL_PARAMETERS` - Tool parameters are invalid

## Error Handling Best Practices

### Exception Handling Patterns

#### Specific Error Handling

```python
from claif import ClaifClient
from claif.common.errors import (
    ProviderNotFoundError,
    AuthenticationError,
    RateLimitError,
    TimeoutError
)

client = ClaifClient()

try:
    response = client.query("Hello", provider="claude")
except ProviderNotFoundError:
    print("Provider not found. Try: claif install claude")
except AuthenticationError:
    print("Check your API key: claif config set providers.claude.api_key sk-...")
except RateLimitError as e:
    retry_after = e.context.get('retry_after', 60)
    print(f"Rate limited. Wait {retry_after} seconds")
except TimeoutError:
    print("Request timed out. Try again or increase timeout")
except Exception as e:
    print(f"Unexpected error: {e}")
```

#### Retry with Exponential Backoff

```python
import asyncio
import random
from claif.common.errors import RateLimitError, TimeoutError

async def query_with_retry(client, message, max_retries=3):
    for attempt in range(max_retries):
        try:
            return await client.query(message)
        except RateLimitError as e:
            if attempt == max_retries - 1:
                raise
            retry_after = e.context.get('retry_after', 60)
            await asyncio.sleep(retry_after)
        except TimeoutError:
            if attempt == max_retries - 1:
                raise
            # Exponential backoff with jitter
            delay = (2 ** attempt) + random.uniform(0, 1)
            await asyncio.sleep(delay)
```

#### Graceful Degradation

```python
from claif import ClaifClient
from claif.common.errors import ProviderError

client = ClaifClient()
preferred_providers = ["claude", "gemini", "codex"]

for provider in preferred_providers:
    try:
        response = client.query("Hello", provider=provider)
        print(f"Success with {provider}: {response.text}")
        break
    except ProviderError as e:
        print(f"Failed with {provider}: {e}")
        continue
else:
    print("All providers failed")
```

### Error Context Usage

```python
def handle_provider_error(error):
    """Extract useful information from provider errors."""
    context = error.context
    
    print(f"Error: {error.message}")
    print(f"Code: {error.code}")
    
    if 'provider_name' in context:
        print(f"Provider: {context['provider_name']}")
        
    if 'request_id' in context:
        print(f"Request ID: {context['request_id']}")
        
    if 'retry_after' in context:
        print(f"Retry after: {context['retry_after']} seconds")
        
    if 'available_providers' in context:
        print(f"Available: {context['available_providers']}")
```

### Logging Errors

```python
import logging
from claif.common.errors import ClaifError

logger = logging.getLogger(__name__)

try:
    response = client.query("Hello")
except ClaifError as e:
    # Log with context for debugging
    logger.error(
        "Claif operation failed",
        extra={
            'error_code': e.code,
            'error_context': e.context,
            'provider': e.context.get('provider_name'),
            'request_id': e.context.get('request_id')
        }
    )
    raise
```

## Troubleshooting Common Errors

### Provider Not Found

```bash
# Check available providers
claif list

# Install missing provider
claif install claude

# Check provider status
claif health --provider claude
```

### Authentication Errors

```bash
# Set API key
claif config set providers.claude.api_key sk-ant-...

# Verify configuration
claif config get providers.claude.api_key

# Test connection
claif query "test" --provider claude
```

### Rate Limiting

```bash
# Check provider limits
claif health --provider claude

# Use different provider
claif query "Hello" --provider gemini

# Wait and retry later
sleep 60 && claif query "Hello"
```

### Timeout Issues

```bash
# Increase timeout
claif query "Complex task" --timeout 300

# Use streaming for long responses
claif query "Long story" --stream

# Check network connectivity
ping api.anthropic.com
```