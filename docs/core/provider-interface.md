---
layout: default
title: Provider Interface
parent: Core Framework
nav_order: 2
---

# Provider Interface Guide

This guide explains how to implement custom providers for the Claif framework and understand the provider interface specification.

## Overview

All Claif providers must implement the `BaseProvider` abstract class, which defines a standardized interface for interacting with Large Language Models (LLMs). This ensures consistency across different provider implementations while allowing flexibility for provider-specific features.

## BaseProvider Abstract Class

### Interface Definition

```python
from abc import ABC, abstractmethod
from collections.abc import AsyncIterator
from claif.common import ClaifOptions, Message

class BaseProvider(ABC):
    """Abstract base class for all Claif LLM providers."""
    
    def __init__(self, name: str) -> None:
        """Initialize the provider with a unique name."""
        self.name = name
    
    @abstractmethod
    async def _query_impl(
        self,
        prompt: str,
        options: ClaifOptions,
    ) -> AsyncIterator[Message]:
        """Provider-specific query implementation."""
        ...
    
    async def query(
        self,
        prompt: str, 
        options: ClaifOptions,
    ) -> AsyncIterator[Message]:
        """Public query method with built-in retry logic."""
        # Implemented by BaseProvider - handles retry logic
        ...
```

### Key Requirements

1. **Async Implementation**: All providers must use async/await patterns
2. **Streaming Support**: Yield messages as they're received 
3. **Error Handling**: Properly handle and raise appropriate exceptions
4. **Type Safety**: Use proper type hints throughout

## Implementing a Custom Provider

### 1. Basic Provider Structure

```python
from claif.providers.base import BaseProvider
from claif.common import Message, MessageRole, ClaifOptions
from claif.common.errors import ProviderError, ClaifTimeoutError

class MyCustomProvider(BaseProvider):
    """Custom provider for MyLLM service."""
    
    def __init__(self):
        super().__init__(name="mycustom")
        self.api_client = None
    
    async def _query_impl(
        self,
        prompt: str,
        options: ClaifOptions,
    ) -> AsyncIterator[Message]:
        """Implement the actual LLM interaction."""
        try:
            # Initialize connection if needed
            await self._ensure_connected(options)
            
            # Prepare the request
            request = self._prepare_request(prompt, options)
            
            # Stream the response
            async for chunk in self.api_client.stream(request):
                if chunk.content:
                    yield Message(
                        role=MessageRole.ASSISTANT,
                        content=chunk.content
                    )
                    
        except TimeoutError as e:
            raise ClaifTimeoutError(self.name, str(e))
        except Exception as e:
            raise ProviderError(self.name, f"Query failed: {e}")
    
    async def _ensure_connected(self, options: ClaifOptions):
        """Ensure API client is properly initialized."""
        if self.api_client is None:
            # Initialize your API client here
            pass
    
    def _prepare_request(self, prompt: str, options: ClaifOptions):
        """Convert Claif options to provider-specific request format."""
        return {
            "prompt": prompt,
            "model": options.model or "default-model",
            "temperature": options.temperature or 0.7,
            "max_tokens": options.max_tokens or 1000,
        }
```

### 2. Plugin Registration

Register your provider using Python entry points in `pyproject.toml`:

```toml
[project.entry-points."claif.providers"]
mycustom = "my_provider_package:MyCustomProvider"
```

### 3. Advanced Features

#### Tool Support

```python
from claif.common import ToolUseBlock, ToolResultBlock

class AdvancedProvider(BaseProvider):
    async def _query_impl(self, prompt: str, options: ClaifOptions):
        # Handle tool use in responses
        async for chunk in self.api_client.stream_with_tools(prompt):
            if chunk.tool_use:
                yield Message(
                    role=MessageRole.ASSISTANT,
                    content=[ToolUseBlock(
                        id=chunk.tool_id,
                        name=chunk.tool_name,
                        input=chunk.tool_input
                    )]
                )
            elif chunk.content:
                yield Message(
                    role=MessageRole.ASSISTANT,
                    content=chunk.content
                )
```

#### Session Management

```python
class SessionProvider(BaseProvider):
    def __init__(self):
        super().__init__("session_provider")
        self.sessions = {}
    
    async def _query_impl(self, prompt: str, options: ClaifOptions):
        session_id = options.session_id or "default"
        
        # Maintain conversation history
        if session_id not in self.sessions:
            self.sessions[session_id] = []
        
        # Add user message to history
        self.sessions[session_id].append({
            "role": "user",
            "content": prompt
        })
        
        # Send full conversation to API
        response = await self.api_client.chat(
            messages=self.sessions[session_id]
        )
        
        # Store assistant response
        self.sessions[session_id].append({
            "role": "assistant", 
            "content": response.content
        })
        
        yield Message(
            role=MessageRole.ASSISTANT,
            content=response.content
        )
```

## Message Format Specification

### Message Structure

```python
@dataclass
class Message:
    role: MessageRole  # USER, ASSISTANT, SYSTEM, RESULT
    content: str | list[ContentBlock]
```

### Content Block Types

#### TextBlock
```python
@dataclass
class TextBlock:
    type: str = "text"
    text: str = ""
```

#### ToolUseBlock
```python
@dataclass
class ToolUseBlock:
    type: str = "tool_use"
    id: str = ""
    name: str = ""
    input: dict[str, Any] = field(default_factory=dict)
```

#### ToolResultBlock
```python
@dataclass
class ToolResultBlock:
    type: str = "tool_result"
    tool_use_id: str = ""
    content: list[TextBlock | Any] = field(default_factory=list)
    is_error: bool = False
```

### Content Normalization

The `Message` class automatically normalizes string content:

```python
# String content is automatically converted
message = Message(role=MessageRole.USER, content="Hello")
# Becomes: Message(role=USER, content=[TextBlock(text="Hello")])

# List content is preserved
message = Message(
    role=MessageRole.ASSISTANT,
    content=[
        TextBlock(text="I'll help you with that."),
        ToolUseBlock(id="tool_1", name="search", input={"query": "python"})
    ]
)
```

## Error Handling

### Exception Hierarchy

Providers should raise appropriate exceptions from the Claif error hierarchy:

```python
from claif.common.errors import (
    ProviderError,           # Base provider error
    ClaifTimeoutError,       # Timeout errors
    ConfigurationError,      # Configuration issues
    ValidationError,         # Input validation errors
)

# Example usage
async def _query_impl(self, prompt: str, options: ClaifOptions):
    if not prompt.strip():
        raise ValidationError("Prompt cannot be empty")
    
    if not self.api_key:
        raise ConfigurationError(f"API key not configured for {self.name}")
    
    try:
        response = await self.api_client.query(prompt, timeout=options.timeout)
    except TimeoutError:
        raise ClaifTimeoutError(self.name, f"Query timed out after {options.timeout}s")
    except Exception as e:
        raise ProviderError(self.name, f"Query failed: {e}")
```

### Retry Behavior

The `BaseProvider.query()` method automatically handles retries using the `tenacity` library. Your `_query_impl` should:

1. **Raise retryable exceptions** for transient failures
2. **Use appropriate exception types** (ProviderError, ClaifTimeoutError, ConnectionError)
3. **Let permanent failures propagate** (ValidationError, ConfigurationError)

```python
# Retryable - will be retried automatically
raise ProviderError(self.name, "Rate limit exceeded")
raise ClaifTimeoutError(self.name, "Request timed out")
raise ConnectionError("Network unavailable")

# Non-retryable - permanent failures
raise ValidationError("Invalid prompt format")
raise ConfigurationError("Missing API key")
```

## Configuration Integration

### ClaifOptions Usage

Your provider should respect common `ClaifOptions` parameters:

```python
async def _query_impl(self, prompt: str, options: ClaifOptions):
    # Use standard options
    model = options.model or self.default_model
    temperature = options.temperature or 0.7
    max_tokens = options.max_tokens or 1000
    timeout = options.timeout or 30
    
    # Provider-specific options can be passed via system_prompt or other fields
    if options.system_prompt:
        prompt = f"{options.system_prompt}\n\n{prompt}"
    
    # Implement timeout handling
    try:
        async with asyncio.timeout(timeout):
            # Your API call here
            pass
    except asyncio.TimeoutError:
        raise ClaifTimeoutError(self.name, f"Query timed out after {timeout}s")
```

### Provider-Specific Configuration

For provider-specific options, you can:

1. **Extend ClaifOptions** (not recommended for compatibility)
2. **Use configuration files** (recommended)
3. **Parse from system_prompt** or other fields

```python
# Recommended: Use configuration system
from claif.common.config import get_provider_config

class MyProvider(BaseProvider):
    def __init__(self):
        super().__init__("myprovider")
        self.config = get_provider_config("myprovider")
        self.api_key = self.config.get("api_key")
        self.base_url = self.config.get("base_url", "https://api.example.com")
```

## Testing Your Provider

### Unit Tests

```python
import pytest
from claif.common import Message, MessageRole, ClaifOptions
from my_provider import MyProvider

@pytest.fixture
def provider():
    return MyProvider()

@pytest.fixture  
def options():
    return ClaifOptions(
        model="test-model",
        temperature=0.5,
        timeout=30
    )

@pytest.mark.asyncio
async def test_basic_query(provider, options):
    """Test basic query functionality."""
    messages = []
    async for message in provider.query("Hello", options):
        messages.append(message)
    
    assert len(messages) > 0
    assert messages[0].role == MessageRole.ASSISTANT
    assert isinstance(messages[0].content, list)

@pytest.mark.asyncio
async def test_error_handling(provider, options):
    """Test error handling."""
    with pytest.raises(ValidationError):
        async for _ in provider.query("", options):
            pass
```

### Mock Testing

```python
from unittest.mock import AsyncMock, patch

@pytest.mark.asyncio
async def test_with_mock_api(provider, options):
    """Test with mocked API client."""
    with patch.object(provider, 'api_client') as mock_client:
        mock_client.stream.return_value = AsyncMock()
        mock_client.stream.return_value.__aiter__.return_value = [
            type('Chunk', (), {'content': 'Hello response'})()
        ]
        
        messages = []
        async for message in provider.query("Hello", options):
            messages.append(message)
        
        assert len(messages) == 1
        assert "Hello response" in str(messages[0].content)
```

## Best Practices

### 1. Resource Management

```python
class ResourceAwareProvider(BaseProvider):
    def __init__(self):
        super().__init__("resource_provider")
        self.session = None
    
    async def __aenter__(self):
        """Async context manager entry."""
        self.session = await create_session()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        if self.session:
            await self.session.close()
    
    async def _query_impl(self, prompt: str, options: ClaifOptions):
        if not self.session:
            self.session = await create_session()
        
        # Use session for requests
        async for chunk in self.session.stream(prompt):
            yield Message(role=MessageRole.ASSISTANT, content=chunk.text)
```

### 2. Logging Integration

```python
from claif.common.utils import logger

class LoggingProvider(BaseProvider):
    async def _query_impl(self, prompt: str, options: ClaifOptions):
        logger.info(f"{self.name}: Starting query", 
                   extra={"prompt_length": len(prompt)})
        
        start_time = time.time()
        message_count = 0
        
        try:
            async for message in self._stream_response(prompt, options):
                message_count += 1
                yield message
                
        except Exception as e:
            logger.error(f"{self.name}: Query failed", 
                        extra={"error": str(e), "duration": time.time() - start_time})
            raise
        else:
            logger.info(f"{self.name}: Query completed",
                       extra={"duration": time.time() - start_time, 
                             "messages": message_count})
```

### 3. Performance Optimization

```python
class OptimizedProvider(BaseProvider):
    def __init__(self):
        super().__init__("optimized")
        self.connection_pool = None
        self.response_cache = {}
    
    async def _query_impl(self, prompt: str, options: ClaifOptions):
        # Check cache first
        if options.cache:
            cache_key = self._get_cache_key(prompt, options)
            if cache_key in self.response_cache:
                logger.debug(f"{self.name}: Serving from cache")
                cached_messages = self.response_cache[cache_key]
                for message in cached_messages:
                    yield message
                return
        
        # Use connection pooling
        async with self._get_connection() as conn:
            messages = []
            async for message in conn.stream(prompt):
                messages.append(message)
                yield message
            
            # Cache successful responses
            if options.cache and messages:
                self.response_cache[cache_key] = messages
    
    def _get_cache_key(self, prompt: str, options: ClaifOptions) -> str:
        """Generate cache key from prompt and options."""
        import hashlib
        key_data = f"{prompt}:{options.model}:{options.temperature}"
        return hashlib.sha256(key_data.encode()).hexdigest()[:16]
```

## Provider Examples

### CLI-Based Provider

Many providers wrap existing CLI tools:

```python
import asyncio
import json
from claif.providers.base import BaseProvider

class CLIProvider(BaseProvider):
    def __init__(self):
        super().__init__("cli_provider")
        self.cli_path = "my-llm-cli"
    
    async def _query_impl(self, prompt: str, options: ClaifOptions):
        cmd = [
            self.cli_path,
            "--model", options.model or "default",
            "--temperature", str(options.temperature or 0.7),
            "--stream",
            prompt
        ]
        
        process = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        
        try:
            while True:
                line = await process.stdout.readline()
                if not line:
                    break
                
                try:
                    data = json.loads(line.decode().strip())
                    if data.get("content"):
                        yield Message(
                            role=MessageRole.ASSISTANT,
                            content=data["content"]
                        )
                except json.JSONDecodeError:
                    continue
        
        finally:
            if process.returncode is None:
                process.terminate()
                await process.wait()
```

### HTTP API Provider

For providers that use HTTP APIs:

```python
import aiohttp
from claif.providers.base import BaseProvider

class HTTPProvider(BaseProvider):
    def __init__(self):
        super().__init__("http_provider")
        self.base_url = "https://api.example.com"
        self.session = None
    
    async def _get_session(self):
        if self.session is None:
            self.session = aiohttp.ClientSession()
        return self.session
    
    async def _query_impl(self, prompt: str, options: ClaifOptions):
        session = await self._get_session()
        
        payload = {
            "prompt": prompt,
            "model": options.model or "default",
            "temperature": options.temperature or 0.7,
            "stream": True
        }
        
        async with session.post(
            f"{self.base_url}/chat/completions",
            json=payload,
            timeout=aiohttp.ClientTimeout(total=options.timeout)
        ) as response:
            if response.status != 200:
                raise ProviderError(
                    self.name, 
                    f"API error: {response.status}"
                )
            
            async for line in response.content:
                if line.startswith(b"data: "):
                    try:
                        data = json.loads(line[6:])
                        if content := data.get("content"):
                            yield Message(
                                role=MessageRole.ASSISTANT,
                                content=content
                            )
                    except json.JSONDecodeError:
                        continue
```

## Conclusion

Implementing a Claif provider involves:

1. **Extending BaseProvider** and implementing `_query_impl`
2. **Handling errors appropriately** with the right exception types
3. **Supporting streaming responses** by yielding messages
4. **Following async patterns** throughout
5. **Registering via entry points** for automatic discovery
6. **Testing thoroughly** with unit and integration tests

The provider interface is designed to be flexible while maintaining consistency across different LLM services. Focus on implementing the core `_query_impl` method correctly, and let the base class handle retry logic and other common functionality.

For more examples, see the official providers:
- [claif_cla](https://github.com/twardoch/claif_cla) - Anthropic Claude
- [claif_gem](https://github.com/twardoch/claif_gem) - Google Gemini  
- [claif_cod](https://github.com/twardoch/claif_cod) - OpenAI Codex