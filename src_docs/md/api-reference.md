# API Reference

This comprehensive reference covers the Claif Python API for programmatic interaction with AI providers. Use these APIs to integrate Claif into your applications, scripts, and services.

## Core Classes

### ClaifClient

The main client class for interacting with AI providers.

```python
from claif import ClaifClient
import asyncio

async def main():
    client = ClaifClient()
    response = await client.send_message("Hello, world!")
    print(response)

asyncio.run(main())
```

#### Constructor

```python
class ClaifClient:
    def __init__(
        self,
        provider: str | None = None,
        config: dict | None = None,
        **kwargs
    ):
        """
        Initialize Claif client.
        
        Args:
            provider: Default provider name ("claude", "gemini", "codex")
            config: Configuration dictionary
            **kwargs: Additional configuration options
        """
```

**Example:**
```python
# Default configuration
client = ClaifClient()

# Specific provider
client = ClaifClient(provider="claude")

# Custom configuration
client = ClaifClient(
    provider="gemini",
    config={
        "gemini": {
            "model": "gemini-pro",
            "temperature": 0.3
        }
    }
)
```

#### Methods

##### send_message()

Send a message and get a complete response.

```python
async def send_message(
    self,
    message: str,
    provider: str | None = None,
    model: str | None = None,
    context: list[Message] | None = None,
    **kwargs
) -> str:
    """
    Send a message to an AI provider.
    
    Args:
        message: The message to send
        provider: Override default provider
        model: Override default model
        context: Previous conversation context
        **kwargs: Provider-specific options
        
    Returns:
        The AI response as a string
        
    Raises:
        ProviderError: Provider-specific errors
        NetworkError: Connection issues
        AuthenticationError: Invalid API keys
    """
```

**Example:**
```python
# Simple message
response = await client.send_message("What is Python?")

# With provider override
response = await client.send_message(
    "Explain quantum computing",
    provider="claude"
)

# With context
from claif.common.types import Message, MessageRole

context = [
    Message(role=MessageRole.USER, content="What is AI?"),
    Message(role=MessageRole.ASSISTANT, content="AI is..."),
]

response = await client.send_message(
    "How does machine learning relate to AI?",
    context=context
)

# With provider-specific options
response = await client.send_message(
    "Generate code",
    provider="codex",
    temperature=0.1,
    max_tokens=2000
)
```

##### stream_message()

Stream response tokens in real-time.

```python
async def stream_message(
    self,
    message: str,
    provider: str | None = None,
    model: str | None = None,
    context: list[Message] | None = None,
    **kwargs
) -> AsyncIterator[str]:
    """
    Stream message response tokens.
    
    Args:
        message: The message to send
        provider: Override default provider
        model: Override default model
        context: Previous conversation context
        **kwargs: Provider-specific options
        
    Yields:
        Response tokens as they're generated
    """
```

**Example:**
```python
async def stream_example():
    client = ClaifClient()
    
    print("Response: ", end="")
    async for token in client.stream_message("Write a short poem"):
        print(token, end="", flush=True)
    print()  # New line at end
```

##### get_providers()

Get information about available providers.

```python
def get_providers(self) -> dict[str, ProviderInfo]:
    """
    Get information about all available providers.
    
    Returns:
        Dictionary mapping provider names to ProviderInfo objects
    """
```

**Example:**
```python
providers = client.get_providers()
for name, info in providers.items():
    print(f"{name}: {info.status}")
    print(f"  Models: {info.models}")
    print(f"  Package: {info.package}")
```

##### validate_provider()

Check if a provider is available and properly configured.

```python
async def validate_provider(self, provider: str) -> bool:
    """
    Validate that a provider is available and configured.
    
    Args:
        provider: Provider name to validate
        
    Returns:
        True if provider is valid and configured
    """
```

## Message Types

### Message

Represents a single message in a conversation.

```python
from dataclasses import dataclass
from enum import Enum
from typing import Optional

class MessageRole(Enum):
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"

@dataclass
class Message:
    role: MessageRole
    content: str
    metadata: Optional[dict] = None
    timestamp: Optional[str] = None
```

**Example:**
```python
from claif.common.types import Message, MessageRole

# User message
user_msg = Message(
    role=MessageRole.USER,
    content="What is the capital of France?"
)

# Assistant response
assistant_msg = Message(
    role=MessageRole.ASSISTANT,
    content="The capital of France is Paris.",
    metadata={"provider": "claude", "model": "claude-3-sonnet"}
)

# System message
system_msg = Message(
    role=MessageRole.SYSTEM,
    content="You are a helpful assistant."
)
```

### ProviderInfo

Information about an AI provider.

```python
@dataclass
class ProviderInfo:
    name: str
    package: str
    version: str
    models: list[str]
    status: str  # "available", "not_configured", "error"
    capabilities: list[str]
    error: Optional[str] = None
```

## Provider Classes

### Base Provider

Abstract base class for all providers.

```python
from abc import ABC, abstractmethod
from typing import AsyncIterator

class Provider(ABC):
    """Base class for all AI providers."""
    
    @abstractmethod
    async def send_message(
        self,
        message: str,
        context: list[Message] | None = None,
        **kwargs
    ) -> str:
        """Send a message and return response."""
        
    @abstractmethod
    async def stream_message(
        self,
        message: str,
        context: list[Message] | None = None,
        **kwargs
    ) -> AsyncIterator[str]:
        """Stream response tokens."""
        
    @abstractmethod
    def validate_config(self) -> bool:
        """Validate provider configuration."""
        
    @abstractmethod
    def get_models(self) -> list[str]:
        """Get available models."""
```

### Custom Provider Implementation

Create a custom provider by inheriting from the base class:

```python
from claif.providers.base import Provider
from claif.common.types import Message

class MyCustomProvider(Provider):
    def __init__(self, config: dict):
        self.config = config
        self.api_key = config.get("api_key")
        
    async def send_message(
        self,
        message: str,
        context: list[Message] | None = None,
        **kwargs
    ) -> str:
        # Implement your API call logic
        response = await self._call_api(message, context, **kwargs)
        return response
        
    async def stream_message(
        self,
        message: str,
        context: list[Message] | None = None,
        **kwargs
    ) -> AsyncIterator[str]:
        # Implement streaming logic
        async for token in self._stream_api(message, context, **kwargs):
            yield token
            
    def validate_config(self) -> bool:
        return self.api_key is not None
        
    def get_models(self) -> list[str]:
        return ["my-model-v1", "my-model-v2"]
        
    async def _call_api(self, message: str, context, **kwargs) -> str:
        # Your API implementation
        pass
        
    async def _stream_api(self, message: str, context, **kwargs):
        # Your streaming implementation
        pass
```

## Configuration API

### get_config()

Get the current configuration.

```python
from claif.common.config import get_config

def get_config(
    config_file: str | None = None,
    reload: bool = False
) -> dict:
    """
    Get the current configuration.
    
    Args:
        config_file: Path to specific config file
        reload: Force reload from disk
        
    Returns:
        Configuration dictionary
    """
```

**Example:**
```python
from claif.common.config import get_config

# Get current configuration
config = get_config()
print(config["general"]["provider"])

# Load specific config file
config = get_config("/path/to/custom.toml")

# Force reload
config = get_config(reload=True)
```

### set_config()

Set configuration values programmatically.

```python
def set_config(key: str, value: any, save: bool = True) -> None:
    """
    Set a configuration value.
    
    Args:
        key: Configuration key (dot notation supported)
        value: Value to set
        save: Save to config file
    """
```

**Example:**
```python
from claif.common.config import set_config

# Set simple value
set_config("general.provider", "claude")

# Set nested value
set_config("claude.temperature", 0.7)

# Set without saving to file
set_config("debug.enabled", True, save=False)
```

## Error Handling

### Exception Hierarchy

```python
# Base exception
class ClaifError(Exception):
    """Base exception for all Claif errors."""
    pass

# Provider errors
class ProviderError(ClaifError):
    """Provider-specific errors."""
    def __init__(self, message: str, provider: str, details: dict = None):
        super().__init__(message)
        self.provider = provider
        self.details = details or {}

# Configuration errors
class ConfigurationError(ClaifError):
    """Configuration-related errors."""
    pass

# Authentication errors
class AuthenticationError(ProviderError):
    """API key or authentication errors."""
    pass

# Network errors
class NetworkError(ClaifError):
    """Network connectivity errors."""
    pass

# Rate limiting errors
class RateLimitError(ProviderError):
    """API rate limiting errors."""
    def __init__(self, message: str, provider: str, retry_after: int = None):
        super().__init__(message, provider)
        self.retry_after = retry_after
```

### Error Handling Examples

```python
from claif import ClaifClient
from claif.common.errors import (
    ProviderError,
    AuthenticationError,
    RateLimitError,
    NetworkError
)
import asyncio

async def robust_client_example():
    client = ClaifClient()
    
    try:
        response = await client.send_message("Hello, world!")
        return response
        
    except AuthenticationError as e:
        print(f"Authentication failed for {e.provider}: {e}")
        # Handle API key issues
        return None
        
    except RateLimitError as e:
        print(f"Rate limited by {e.provider}")
        if e.retry_after:
            print(f"Retry after {e.retry_after} seconds")
            await asyncio.sleep(e.retry_after)
            # Retry the request
            return await client.send_message("Hello, world!")
        return None
        
    except NetworkError as e:
        print(f"Network error: {e}")
        # Implement retry logic or fallback
        return None
        
    except ProviderError as e:
        print(f"Provider {e.provider} error: {e}")
        # Try different provider
        try:
            return await client.send_message("Hello, world!", provider="gemini")
        except ProviderError:
            return None
```

## Async Context Management

### Using async context managers

```python
from claif import ClaifClient

async def context_manager_example():
    async with ClaifClient() as client:
        response = await client.send_message("Hello")
        return response
    # Client automatically cleaned up
```

### Session Management

```python
from claif.session import SessionManager

async def session_example():
    session_manager = SessionManager()
    
    # Create new session
    session = await session_manager.create_session(
        name="my_session",
        provider="claude"
    )
    
    # Add messages to session
    await session.add_message("What is Python?")
    response = await session.send_message("Tell me more about its syntax")
    
    # Save session
    await session_manager.save_session(session)
    
    # Load session later
    loaded_session = await session_manager.load_session("my_session")
```

## Utilities

### Text Processing

```python
from claif.common.utils import (
    format_response,
    truncate_text,
    count_tokens,
    split_text_by_tokens
)

# Format response for display
formatted = format_response(response, format="markdown")

# Truncate long text
short_text = truncate_text(long_text, max_length=1000)

# Token counting
token_count = count_tokens(text, model="gpt-4")

# Split text by token limit
chunks = split_text_by_tokens(text, max_tokens=2000, model="claude-3-sonnet")
```

### File Operations

```python
from claif.common.file_utils import (
    read_file,
    write_file,
    analyze_file,
    get_file_type
)

# Read file with encoding detection
content = await read_file("document.txt")

# Write response to file
await write_file("output.md", response, format="markdown")

# Analyze file content
analysis = await analyze_file("code.py", "Review this code")

# Detect file type
file_type = get_file_type("image.jpg")  # Returns "image"
```

## Advanced Usage

### Parallel Processing

```python
import asyncio
from claif import ClaifClient

async def parallel_processing():
    client = ClaifClient()
    
    # Process multiple queries in parallel
    tasks = [
        client.send_message("What is AI?", provider="claude"),
        client.send_message("What is ML?", provider="gemini"),
        client.send_message("What is DL?", provider="codex")
    ]
    
    responses = await asyncio.gather(*tasks, return_exceptions=True)
    
    for i, response in enumerate(responses):
        if isinstance(response, Exception):
            print(f"Task {i} failed: {response}")
        else:
            print(f"Task {i}: {response[:100]}...")
```

### Provider Fallback Chain

```python
async def fallback_chain(client: ClaifClient, message: str):
    providers = ["claude", "gemini", "codex"]
    
    for provider in providers:
        try:
            response = await client.send_message(message, provider=provider)
            return response, provider
        except Exception as e:
            print(f"Provider {provider} failed: {e}")
            continue
    
    raise Exception("All providers failed")
```

### Custom Tool Integration

```python
from claif.tools import Tool, ToolRegistry

class CalculatorTool(Tool):
    name = "calculator"
    description = "Perform mathematical calculations"
    
    async def execute(self, expression: str) -> str:
        try:
            result = eval(expression)  # Use safely in production
            return str(result)
        except Exception as e:
            return f"Error: {e}"

# Register tool
registry = ToolRegistry()
registry.register(CalculatorTool())

# Use with client
client = ClaifClient(tools=registry)
response = await client.send_message(
    "Calculate 15 * 23 using the calculator tool"
)
```

### Streaming with Custom Processing

```python
async def process_streaming_response():
    client = ClaifClient()
    
    full_response = ""
    word_count = 0
    
    async for token in client.stream_message("Write a long story"):
        full_response += token
        
        # Count words as we stream
        if token.isspace():
            word_count += 1
            
        # Print progress every 50 words
        if word_count % 50 == 0:
            print(f"Progress: {word_count} words...")
            
        # Print token immediately
        print(token, end="", flush=True)
    
    print(f"\nFinal count: {word_count} words")
    return full_response
```

## Testing and Mocking

### Mock Provider for Testing

```python
from claif.providers.base import Provider
from claif.common.types import Message

class MockProvider(Provider):
    def __init__(self, responses: dict):
        self.responses = responses
        
    async def send_message(self, message: str, **kwargs) -> str:
        return self.responses.get(message, "Mock response")
        
    async def stream_message(self, message: str, **kwargs):
        response = self.responses.get(message, "Mock response")
        for char in response:
            yield char
            
    def validate_config(self) -> bool:
        return True
        
    def get_models(self) -> list[str]:
        return ["mock-model"]

# Use in tests
mock_responses = {
    "Hello": "Hi there!",
    "What is AI?": "AI is artificial intelligence."
}

mock_provider = MockProvider(mock_responses)
client = ClaifClient()
client._providers["mock"] = mock_provider

response = await client.send_message("Hello", provider="mock")
assert response == "Hi there!"
```

### Testing with pytest

```python
import pytest
from claif import ClaifClient
from claif.common.errors import ProviderError

@pytest.mark.asyncio
async def test_basic_message():
    client = ClaifClient()
    response = await client.send_message("Hello")
    assert isinstance(response, str)
    assert len(response) > 0

@pytest.mark.asyncio
async def test_provider_fallback():
    client = ClaifClient()
    
    # This should work with any available provider
    response = await client.send_message("What is 2+2?")
    assert "4" in response

@pytest.mark.asyncio
async def test_invalid_provider():
    client = ClaifClient()
    
    with pytest.raises(ProviderError):
        await client.send_message("Hello", provider="nonexistent")
```

## Performance Optimization

### Connection Pooling

```python
from claif import ClaifClient
from claif.common.config import set_config

# Configure connection pooling
set_config("performance.max_connections", 10)
set_config("performance.keep_alive", True)

client = ClaifClient()
# Client will reuse connections
```

### Response Caching

```python
from claif.cache import ResponseCache

# Enable caching
cache = ResponseCache(ttl=3600)  # 1 hour TTL
client = ClaifClient(cache=cache)

# First call - hits API
response1 = await client.send_message("What is Python?")

# Second call - returns cached response
response2 = await client.send_message("What is Python?")
assert response1 == response2
```

## Summary

The Claif Python API provides:

- **Async-first design** for high performance
- **Provider abstraction** for seamless switching
- **Comprehensive error handling** for robust applications
- **Flexible configuration** for different environments
- **Extensible architecture** for custom providers and tools
- **Rich type system** for better development experience

Use these APIs to build powerful AI-integrated applications that can leverage multiple providers and adapt to changing requirements.

Next steps:
- [Development](development.md) - Contribute to Claif
- [Troubleshooting](troubleshooting.md) - Debug common issues