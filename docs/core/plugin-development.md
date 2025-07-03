---
layout: default
title: Plugin Development Guide
parent: Core Framework
nav_order: 2
---

# Plugin Development Guide

Learn how to create your own provider plugin for the Claif framework.

## Overview

Claif's plugin architecture allows you to integrate any LLM service as a provider. This guide walks through creating a custom provider package that integrates seamlessly with the Claif ecosystem.

## Quick Start

### 1. Project Structure

Create a new provider package with this structure:

```
claif_myprovider/
├── src/
│   └── claif_myprovider/
│       ├── __init__.py      # Main entry point
│       ├── provider.py      # Provider implementation
│       ├── client.py        # Client logic
│       ├── transport.py     # Communication layer
│       ├── types.py         # Type definitions
│       └── cli.py           # CLI interface (optional)
├── tests/
│   └── test_provider.py
├── pyproject.toml           # Package configuration
├── README.md
└── LICENSE
```

### 2. Package Configuration

Configure your `pyproject.toml`:

```toml
[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[project]
name = "claif_myprovider"
version = "1.0.0"
description = "MyProvider integration for Claif"
requires-python = ">=3.10"
dependencies = [
    "claif>=1.0.0",
    "httpx>=0.24.0",  # or your preferred HTTP client
    "anyio>=3.0.0",
]

[project.entry-points."claif.providers"]
myprovider = "claif_myprovider:MyProvider"

[project.optional-dependencies]
dev = [
    "pytest>=7.0.0",
    "pytest-asyncio>=0.21.0",
    "ruff>=0.1.0",
]
```

### 3. Provider Implementation

Implement the provider in `src/claif_myprovider/provider.py`:

```python
from collections.abc import AsyncIterator
from typing import Any

from claif.providers.base import BaseProvider
from claif.common.types import Message, Role, TextBlock
from claif.common import ClaifOptions, ProviderError

from .client import MyProviderClient
from .types import MyProviderOptions


class MyProvider(BaseProvider):
    """MyProvider implementation for Claif."""
    
    def __init__(self):
        self.client = MyProviderClient()
        self._connected = False
    
    @property
    def name(self) -> str:
        return "myprovider"
    
    @property
    def capabilities(self) -> set[str]:
        return {"text", "streaming", "tools"}  # Your capabilities
    
    async def connect(self) -> None:
        """Initialize the provider connection."""
        if not self._connected:
            await self.client.initialize()
            self._connected = True
    
    async def disconnect(self) -> None:
        """Clean up provider resources."""
        if self._connected:
            await self.client.cleanup()
            self._connected = False
    
    async def query(
        self,
        prompt: str,
        options: ClaifOptions | None = None
    ) -> AsyncIterator[Message]:
        """Execute a query and yield response messages."""
        if not self._connected:
            await self.connect()
        
        # Convert Claif options to provider-specific options
        provider_options = self._convert_options(options)
        
        try:
            # Execute query through client
            async for response in self.client.query(prompt, provider_options):
                # Convert provider response to Claif Message
                yield self._convert_response(response)
                
        except Exception as e:
            raise ProviderError(f"MyProvider query failed: {e}") from e
    
    def _convert_options(self, options: ClaifOptions | None) -> MyProviderOptions:
        """Convert Claif options to provider-specific format."""
        if not options:
            return MyProviderOptions()
        
        return MyProviderOptions(
            model=options.model or "default-model",
            temperature=options.temperature,
            max_tokens=options.max_tokens,
            timeout=options.timeout,
        )
    
    def _convert_response(self, response: Any) -> Message:
        """Convert provider response to Claif Message."""
        return Message(
            role=Role.ASSISTANT,
            content=[TextBlock(text=response.text)],
            metadata={
                "model": response.model,
                "tokens": response.usage.total_tokens,
            }
        )
```

### 4. Entry Point

Create the main entry point in `src/claif_myprovider/__init__.py`:

```python
"""MyProvider integration for Claif."""

from collections.abc import AsyncIterator

from claif.common import ClaifOptions, Message
from claif.providers.base import BaseProvider

from .provider import MyProvider

# Module-level instance
_provider = MyProvider()

# Expose the provider class for plugin discovery
__all__ = ["MyProvider", "query"]


async def query(
    prompt: str,
    options: ClaifOptions | None = None
) -> AsyncIterator[Message]:
    """
    Query MyProvider with Claif-compatible interface.
    
    Args:
        prompt: The query prompt
        options: Query options
        
    Yields:
        Response messages from MyProvider
    """
    async for message in _provider.query(prompt, options):
        yield message
```

## Advanced Features

### 1. Streaming Responses

Implement real-time streaming:

```python
async def stream_query(self, prompt: str, options: MyProviderOptions):
    """Stream responses from the API."""
    async with self.session.stream(
        "POST",
        self.api_url,
        json={"prompt": prompt, **options.dict()},
    ) as response:
        async for line in response.aiter_lines():
            if line.startswith("data: "):
                data = json.loads(line[6:])
                yield self._parse_chunk(data)
```

### 2. Tool Support

Add tool/function calling capabilities:

```python
from claif.common.types import ToolUseBlock, ToolResultBlock

async def handle_tool_use(self, tool_request: ToolUseBlock) -> ToolResultBlock:
    """Execute a tool and return results."""
    if tool_request.tool_name == "calculator":
        result = eval(tool_request.parameters["expression"])
        return ToolResultBlock(
            tool_name="calculator",
            result={"answer": result}
        )
```

### 3. Vision Support

Handle image inputs:

```python
from claif.common.types import ImageBlock

def _build_request(self, prompt: str, options: ClaifOptions):
    messages = []
    
    # Handle text and images
    if isinstance(prompt, str):
        messages.append({"type": "text", "text": prompt})
    
    if options and options.images:
        for image_path in options.images:
            with open(image_path, "rb") as f:
                image_data = base64.b64encode(f.read()).decode()
                messages.append({
                    "type": "image",
                    "data": image_data
                })
    
    return {"messages": messages}
```

### 4. Session Management

Implement conversation persistence:

```python
class SessionManager:
    def __init__(self, session_dir: Path):
        self.session_dir = session_dir
        self.sessions = {}
    
    async def get_session(self, session_id: str) -> Session:
        if session_id not in self.sessions:
            session_path = self.session_dir / f"{session_id}.json"
            if session_path.exists():
                self.sessions[session_id] = Session.load(session_path)
            else:
                self.sessions[session_id] = Session(session_id)
        
        return self.sessions[session_id]
    
    async def save_session(self, session: Session):
        session_path = self.session_dir / f"{session.id}.json"
        session.save(session_path)
```

### 5. Error Handling

Implement robust error handling:

```python
from claif.common import (
    ProviderError,
    ConfigurationError,
    TransportError,
    RateLimitError
)

class MyProviderError(ProviderError):
    """Base error for MyProvider."""
    pass

class AuthenticationError(MyProviderError):
    """Authentication failed."""
    pass

async def _make_request(self, endpoint: str, data: dict):
    try:
        response = await self.session.post(endpoint, json=data)
        response.raise_for_status()
        return response.json()
        
    except httpx.HTTPStatusError as e:
        if e.response.status_code == 401:
            raise AuthenticationError("Invalid API key")
        elif e.response.status_code == 429:
            raise RateLimitError("Rate limit exceeded")
        else:
            raise TransportError(f"HTTP {e.response.status_code}")
            
    except httpx.TimeoutException:
        raise TransportError("Request timed out")
```

## Testing Your Provider

### 1. Unit Tests

Test provider functionality:

```python
import pytest
from unittest.mock import AsyncMock, Mock

from claif_myprovider import MyProvider
from claif.common import ClaifOptions, Role

@pytest.mark.asyncio
async def test_query():
    provider = MyProvider()
    provider.client = AsyncMock()
    
    # Mock response
    mock_response = Mock(text="Hello!", model="test-model")
    provider.client.query.return_value = [mock_response]
    
    # Execute query
    messages = []
    async for msg in provider.query("Hi"):
        messages.append(msg)
    
    assert len(messages) == 1
    assert messages[0].role == Role.ASSISTANT
    assert messages[0].content[0].text == "Hello!"
```

### 2. Integration Tests

Test with real API (optional):

```python
@pytest.mark.integration
@pytest.mark.asyncio
async def test_real_query():
    provider = MyProvider()
    
    messages = []
    async for msg in provider.query("2+2"):
        messages.append(msg)
    
    assert len(messages) > 0
    assert "4" in messages[0].content[0].text
```

### 3. Mock Provider

Create a mock for testing:

```python
class MockMyProvider(MyProvider):
    def __init__(self, responses: list[str]):
        super().__init__()
        self.responses = responses
        self.query_count = 0
    
    async def query(self, prompt: str, options=None):
        if self.query_count < len(self.responses):
            response = self.responses[self.query_count]
            self.query_count += 1
            
            yield Message(
                role=Role.ASSISTANT,
                content=[TextBlock(text=response)]
            )
```

## CLI Integration

Add a CLI for direct provider access:

```python
# src/claif_myprovider/cli.py
import asyncio
from typing import Any

import fire
from rich.console import Console

from . import query
from .types import MyProviderOptions

console = Console()


class MyProviderCLI:
    """CLI for MyProvider."""
    
    def query(self, prompt: str, **kwargs: Any) -> None:
        """Execute a query."""
        options = MyProviderOptions(**kwargs)
        
        async def run():
            async for message in query(prompt, options):
                console.print(message.content[0].text)
        
        asyncio.run(run())
    
    def health(self) -> None:
        """Check provider health."""
        # Implementation


def main():
    fire.Fire(MyProviderCLI)


if __name__ == "__main__":
    main()
```

Add CLI entry point to `pyproject.toml`:

```toml
[project.scripts]
claif-myp = "claif_myprovider.cli:main"
```

## Best Practices

### 1. Configuration

Support multiple configuration sources:

```python
def get_api_key() -> str:
    """Get API key from environment or config."""
    # 1. Environment variable
    if key := os.getenv("MYPROVIDER_API_KEY"):
        return key
    
    # 2. Claif config
    config = load_config()
    if key := config.get("providers", {}).get("myprovider", {}).get("api_key"):
        return key
    
    raise ConfigurationError("MyProvider API key not found")
```

### 2. Logging

Use structured logging:

```python
from loguru import logger

logger.debug("Sending query", provider="myprovider", model=options.model)
logger.error("Query failed", error=str(e), duration=elapsed)
```

### 3. Type Safety

Use type hints throughout:

```python
from typing import TypeVar, Generic

T = TypeVar("T")

class Response(Generic[T]):
    def __init__(self, data: T, metadata: dict[str, Any]):
        self.data = data
        self.metadata = metadata
```

### 4. Resource Management

Properly manage resources:

```python
class MyProviderClient:
    def __init__(self):
        self.session: httpx.AsyncClient | None = None
    
    async def __aenter__(self):
        self.session = httpx.AsyncClient()
        return self
    
    async def __aexit__(self, *args):
        if self.session:
            await self.session.aclose()
```

## Publishing Your Provider

### 1. Documentation

Create comprehensive documentation:

- README with installation and usage
- API documentation
- Configuration guide
- Troubleshooting section

### 2. Testing

Ensure thorough testing:

- Unit tests with >80% coverage
- Integration tests (optional)
- Cross-platform testing
- Performance benchmarks

### 3. Release

Publish to PyPI:

```bash
# Build package
python -m build

# Upload to TestPyPI first
twine upload -r testpypi dist/*

# Test installation
pip install -i https://test.pypi.org/simple/ claif_myprovider

# Upload to PyPI
twine upload dist/*
```

### 4. Registration

Register with Claif community:

1. Submit PR to add to provider list
2. Add to documentation
3. Share in discussions

## Example Providers

Study these providers for inspiration:

- **claif_gem**: Subprocess-based provider
- **claif_cla**: SDK-based provider  
- **claif_cod**: Complex async provider

## Troubleshooting

### Common Issues

1. **Provider not discovered**
   - Check entry point name
   - Verify installation
   - Check for import errors

2. **Async errors**
   - Ensure all I/O is async
   - Use `anyio` for compatibility
   - Handle cleanup properly

3. **Type errors**
   - Match Claif types exactly
   - Use proper inheritance
   - Test type conversions

## Summary

Creating a Claif provider involves:

1. Implementing the `BaseProvider` interface
2. Handling message conversion
3. Managing connections properly
4. Providing good error messages
5. Testing thoroughly

Follow this guide and you'll have a fully integrated provider that works seamlessly with the Claif ecosystem!