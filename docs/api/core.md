---
layout: default
title: Core Classes
parent: API Reference
nav_order: 1
---

# Core Classes

This section documents the main API classes and methods in the Claif framework.

## ClaifClient

The main client class for interacting with AI providers through the Claif framework.

```python
from claif import ClaifClient

client = ClaifClient()
```

### Constructor

```python
ClaifClient(
    config: Optional[Config] = None,
    default_provider: Optional[str] = None,
    timeout: float = 120.0
)
```

**Parameters:**
- `config` - Configuration object, auto-loaded from `~/.claif/config.toml` if not provided
- `default_provider` - Default provider to use when none specified
- `timeout` - Default timeout for requests in seconds

### Methods

#### `query(message, provider=None, **options)`

Send a query to an AI provider.

```python
response = client.query(
    "Explain quantum computing", 
    provider="claude",
    temperature=0.7
)
```

**Parameters:**
- `message` (str | Message) - The message to send
- `provider` (str, optional) - Provider name ("claude", "gemini", "codex")
- `**options` - Provider-specific options

**Returns:** `Message` - The provider's response

**Raises:**
- `ProviderError` - If provider is unavailable or returns an error
- `ValidationError` - If message format is invalid
- `TimeoutError` - If request exceeds timeout

#### `list_providers()`

Get a list of available providers.

```python
providers = client.list_providers()
# Returns: ["claude", "gemini", "codex"]
```

**Returns:** `List[str]` - Names of available providers

#### `get_provider_info(provider_name)`

Get detailed information about a specific provider.

```python
info = client.get_provider_info("claude")
# Returns: {"name": "claude", "version": "1.0.0", "available": True, ...}
```

**Parameters:**
- `provider_name` (str) - Name of the provider

**Returns:** `Dict[str, Any]` - Provider information

#### `stream_query(message, provider=None, **options)`

Stream a query response for real-time output.

```python
for chunk in client.stream_query("Write a story", provider="claude"):
    print(chunk.content, end="", flush=True)
```

**Parameters:**
- Same as `query()`

**Yields:** `Message` - Response chunks as they arrive

## AsyncClaifClient

Async version of the main client for concurrent operations.

```python
from claif import AsyncClaifClient
import asyncio

async def main():
    async with AsyncClaifClient() as client:
        response = await client.query("Hello, world!")
```

### Methods

All methods are async versions of `ClaifClient` methods:

- `async query(...)` - Async query execution
- `async list_providers()` - Async provider listing
- `async get_provider_info(...)` - Async provider info
- `async stream_query(...)` - Async streaming query

## Message

Represents a message in the Claif system.

```python
from claif.common.types import Message, TextBlock

message = Message(
    content=[TextBlock(text="Hello, world!")],
    metadata={"source": "user"}
)
```

### Constructor

```python
Message(
    content: List[ContentBlock],
    metadata: Optional[Dict[str, Any]] = None
)
```

**Parameters:**
- `content` - List of content blocks (text, images, tool uses, etc.)
- `metadata` - Optional metadata dictionary

### Properties

- `text` (str) - Combined text content from all text blocks
- `blocks` (List[ContentBlock]) - All content blocks
- `metadata` (Dict[str, Any]) - Message metadata

### Methods

#### `to_dict()`

Convert message to dictionary format.

```python
data = message.to_dict()
```

**Returns:** `Dict[str, Any]` - Dictionary representation

#### `from_dict(data)`

Create message from dictionary (class method).

```python
message = Message.from_dict({"content": [{"type": "text", "text": "Hello"}]})
```

**Parameters:**
- `data` (Dict[str, Any]) - Dictionary representation

**Returns:** `Message` - New message instance

## ContentBlock

Base class for all content blocks.

### TextBlock

Text content block.

```python
from claif.common.types import TextBlock

block = TextBlock(text="Hello, world!")
```

**Properties:**
- `text` (str) - The text content
- `type` (str) - Always "text"

### ToolUseBlock

Tool usage content block.

```python
from claif.common.types import ToolUseBlock

block = ToolUseBlock(
    tool_name="calculator",
    parameters={"expression": "2 + 2"}
)
```

**Properties:**
- `tool_name` (str) - Name of the tool to use
- `parameters` (Dict[str, Any]) - Tool parameters
- `type` (str) - Always "tool_use"

## Provider

Abstract base class for all providers.

```python
from claif.providers.base import Provider

class MyProvider(Provider):
    async def query(self, message: Message, **options) -> Message:
        # Implementation here
        pass
```

### Abstract Methods

#### `query(message, **options)`

Send a query to the provider.

**Parameters:**
- `message` (Message) - The message to send
- `**options` - Provider-specific options

**Returns:** `Message` - The provider's response

#### `stream_query(message, **options)`

Stream a query response.

**Parameters:**
- Same as `query()`

**Yields:** `Message` - Response chunks

### Properties

- `name` (str) - Provider name
- `version` (str) - Provider version
- `available` (bool) - Whether provider is available

## Configuration Classes

### Config

Main configuration class.

```python
from claif.common.config import Config

config = Config.load()  # Load from ~/.claif/config.toml
```

### ClaifOptions

Query options and settings.

```python
from claif.common.types import ClaifOptions

options = ClaifOptions(
    temperature=0.7,
    max_tokens=1000,
    timeout=30.0
)
```

**Properties:**
- `temperature` (float) - Sampling temperature (0.0-1.0)
- `max_tokens` (int) - Maximum tokens in response
- `timeout` (float) - Request timeout in seconds
- `stream` (bool) - Whether to stream the response
- `provider_options` (Dict[str, Any]) - Provider-specific options

## Examples

### Basic Usage

```python
from claif import ClaifClient

# Initialize client
client = ClaifClient()

# Send a simple query
response = client.query("What is the capital of France?")
print(response.text)

# Use specific provider with options
response = client.query(
    "Write a haiku about coding",
    provider="claude",
    temperature=0.8,
    max_tokens=100
)
```

### Async Usage

```python
import asyncio
from claif import AsyncClaifClient

async def main():
    async with AsyncClaifClient() as client:
        # Concurrent queries
        tasks = [
            client.query("Translate 'hello' to French"),
            client.query("Translate 'hello' to Spanish"),
            client.query("Translate 'hello' to German")
        ]
        
        responses = await asyncio.gather(*tasks)
        for response in responses:
            print(response.text)

asyncio.run(main())
```

### Streaming Usage

```python
from claif import ClaifClient

client = ClaifClient()

print("AI Response: ", end="", flush=True)
for chunk in client.stream_query("Tell me a short story"):
    print(chunk.text, end="", flush=True)
print()  # New line at end
```

### Provider Information

```python
from claif import ClaifClient

client = ClaifClient()

# List all providers
providers = client.list_providers()
print(f"Available providers: {providers}")

# Get detailed provider info
for provider in providers:
    info = client.get_provider_info(provider)
    print(f"{provider}: {info['version']} (available: {info['available']})")
```