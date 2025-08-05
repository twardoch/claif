# Development

This guide covers everything you need to know to contribute to Claif, extend its functionality, or create custom providers and tools.

## Development Setup

### Prerequisites

- **Python 3.12+** (required)
- **Git** for version control
- **uv** for package management (recommended)
- **IDE/Editor** with Python support (VS Code, PyCharm, etc.)

### Clone and Setup

```bash
# Clone the repository
git clone https://github.com/twardoch/claif.git
cd claif

# Install development dependencies with uv
uv sync --dev

# Or with pip
pip install -e ".[dev]"

# Install pre-commit hooks
pre-commit install
```

### Development Dependencies

The development environment includes:

```toml
[project.optional-dependencies]
dev = [
    "pytest>=7.0.0",
    "pytest-asyncio>=0.21.0",
    "pytest-cov>=4.0.0",
    "black>=23.0.0",
    "ruff>=0.1.0",
    "mypy>=1.5.0",
    "pre-commit>=3.0.0",
    "mkdocs-material>=9.0.0",
    "mkdocs-mermaid2-plugin>=1.0.0",
]
```

## Project Structure

### Repository Layout

```
claif/
├── src/
│   └── claif/
│       ├── __init__.py          # Public API exports
│       ├── cli.py               # Command-line interface
│       ├── client.py            # Main client class
│       ├── server.py            # MCP server
│       ├── common/              # Shared utilities
│       │   ├── types.py        # Type definitions
│       │   ├── errors.py       # Exception hierarchy
│       │   ├── config.py       # Configuration management
│       │   └── utils.py        # Utility functions
│       ├── providers/           # Provider system
│       │   ├── __init__.py     # Provider registry
│       │   ├── base.py         # Abstract base class
│       │   └── discovery.py    # Plugin discovery
│       ├── session/             # Session management
│       │   ├── __init__.py
│       │   ├── manager.py      # Session operations
│       │   └── storage.py      # Session persistence
│       └── tools/               # MCP tools
│           ├── __init__.py
│           ├── registry.py     # Tool registration
│           └── base.py         # Tool base class
├── tests/                       # Test suite
├── docs/                        # Documentation
├── examples/                    # Example code
├── scripts/                     # Development scripts
├── pyproject.toml              # Project configuration
└── README.md
```

### Code Organization Principles

1. **Separation of Concerns**: Each module has a single responsibility
2. **Provider Independence**: Core framework doesn't depend on specific providers
3. **Async First**: All I/O operations are async
4. **Type Safety**: Comprehensive type hints throughout
5. **Error Handling**: Structured exception hierarchy

## Contributing Guidelines

### Code Style

We use modern Python tooling for consistent code style:

```bash
# Format code
ruff format

# Lint code
ruff check --fix

# Type checking
mypy src/

# Run all checks
pre-commit run --all-files
```

### Code Standards

#### 1. Type Hints

Use comprehensive type hints:

```python
from typing import AsyncIterator, Optional
from claif.common.types import Message

async def send_message(
    self,
    message: str,
    context: list[Message] | None = None,
    **kwargs: any
) -> str:
    """Send message with proper type hints."""
    pass
```

#### 2. Docstrings

Use Google-style docstrings:

```python
def validate_config(self, config: dict) -> bool:
    """Validate provider configuration.
    
    Args:
        config: Configuration dictionary to validate
        
    Returns:
        True if configuration is valid
        
    Raises:
        ConfigurationError: If configuration is invalid
        
    Example:
        >>> provider = MyProvider()
        >>> provider.validate_config({"api_key": "key"})
        True
    """
    pass
```

#### 3. Error Handling

Use structured error handling:

```python
from claif.common.errors import ProviderError

class MyProviderError(ProviderError):
    """Specific error for MyProvider."""
    pass

async def my_method(self):
    try:
        result = await self._api_call()
    except httpx.HTTPError as e:
        raise MyProviderError(
            f"API call failed: {e}",
            provider=self.name,
            details={"status_code": e.response.status_code}
        ) from e
```

#### 4. Async Patterns

Follow async best practices:

```python
import asyncio
import aiohttp

class AsyncProvider:
    def __init__(self):
        self._session: aiohttp.ClientSession | None = None
    
    async def __aenter__(self):
        self._session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self._session:
            await self._session.close()
    
    async def _get_session(self) -> aiohttp.ClientSession:
        if not self._session:
            self._session = aiohttp.ClientSession()
        return self._session
```

### Testing

#### Test Structure

```
tests/
├── unit/                    # Unit tests
│   ├── test_client.py
│   ├── test_config.py
│   └── providers/
│       └── test_base.py
├── integration/             # Integration tests
│   ├── test_provider_integration.py
│   └── test_mcp_integration.py
├── functional/              # End-to-end tests
│   └── test_cli.py
├── fixtures/                # Test data
└── conftest.py             # Pytest configuration
```

#### Writing Tests

```python
import pytest
from unittest.mock import AsyncMock, patch
from claif import ClaifClient
from claif.common.errors import ProviderError

@pytest.mark.asyncio
async def test_send_message_success():
    """Test successful message sending."""
    client = ClaifClient()
    
    with patch.object(client, '_get_provider') as mock_get_provider:
        mock_provider = AsyncMock()
        mock_provider.send_message.return_value = "Hello response"
        mock_get_provider.return_value = mock_provider
        
        response = await client.send_message("Hello")
        
        assert response == "Hello response"
        mock_provider.send_message.assert_called_once_with(
            "Hello", context=None
        )

@pytest.mark.asyncio
async def test_send_message_provider_error():
    """Test handling of provider errors."""
    client = ClaifClient()
    
    with patch.object(client, '_get_provider') as mock_get_provider:
        mock_provider = AsyncMock()
        mock_provider.send_message.side_effect = ProviderError(
            "API error", "test_provider"
        )
        mock_get_provider.return_value = mock_provider
        
        with pytest.raises(ProviderError) as exc_info:
            await client.send_message("Hello")
        
        assert exc_info.value.provider == "test_provider"
```

#### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=claif --cov-report=html

# Run specific test file
pytest tests/test_client.py

# Run with verbose output
pytest -v

# Run only fast tests (skip integration)
pytest -m "not integration"
```

## Creating Custom Providers

### Provider Interface

All providers must implement the base Provider interface:

```python
from abc import ABC, abstractmethod
from typing import AsyncIterator
from claif.providers.base import Provider
from claif.common.types import Message

class MyCustomProvider(Provider):
    """Custom provider implementation."""
    
    def __init__(self, config: dict):
        """Initialize provider with configuration."""
        self.config = config
        self.api_key = config.get("api_key")
        self.base_url = config.get("base_url", "https://api.example.com")
        self.model = config.get("model", "default-model")
        
    async def send_message(
        self,
        message: str,
        context: list[Message] | None = None,
        **kwargs
    ) -> str:
        """Send a message and return complete response."""
        # Build request
        request_data = self._build_request(message, context, **kwargs)
        
        # Make API call
        async with self._get_session() as session:
            response = await self._make_request(session, request_data)
            
        # Process response
        return self._extract_content(response)
        
    async def stream_message(
        self,
        message: str,
        context: list[Message] | None = None,
        **kwargs
    ) -> AsyncIterator[str]:
        """Stream response tokens."""
        request_data = self._build_request(message, context, stream=True, **kwargs)
        
        async with self._get_session() as session:
            async for token in self._stream_request(session, request_data):
                yield token
                
    def validate_config(self) -> bool:
        """Validate provider configuration."""
        return (
            self.api_key is not None and
            self.base_url is not None and
            self.model is not None
        )
        
    def get_models(self) -> list[str]:
        """Get list of available models."""
        return ["model-v1", "model-v2", "model-pro"]
        
    # Private helper methods
    def _build_request(
        self, 
        message: str, 
        context: list[Message] | None = None,
        stream: bool = False,
        **kwargs
    ) -> dict:
        """Build API request data."""
        messages = []
        
        # Add context messages
        if context:
            for msg in context:
                messages.append({
                    "role": msg.role.value,
                    "content": msg.content
                })
        
        # Add current message
        messages.append({
            "role": "user",
            "content": message
        })
        
        return {
            "model": kwargs.get("model", self.model),
            "messages": messages,
            "stream": stream,
            "temperature": kwargs.get("temperature", 0.7),
            "max_tokens": kwargs.get("max_tokens", 2000),
        }
    
    async def _get_session(self):
        """Get HTTP session with appropriate headers."""
        import aiohttp
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "User-Agent": "Claif/1.0.0"
        }
        
        return aiohttp.ClientSession(headers=headers)
    
    async def _make_request(self, session, request_data: dict) -> dict:
        """Make non-streaming API request."""
        async with session.post(
            f"{self.base_url}/chat/completions",
            json=request_data
        ) as response:
            response.raise_for_status()
            return await response.json()
    
    async def _stream_request(self, session, request_data: dict):
        """Make streaming API request."""
        async with session.post(
            f"{self.base_url}/chat/completions",
            json=request_data
        ) as response:
            response.raise_for_status()
            
            async for line in response.content:
                if line.startswith(b"data: "):
                    data = line[6:].decode().strip()
                    if data == "[DONE]":
                        break
                        
                    import json
                    try:
                        event = json.loads(data)
                        if "choices" in event:
                            delta = event["choices"][0].get("delta", {})
                            if "content" in delta:
                                yield delta["content"]
                    except json.JSONDecodeError:
                        continue
    
    def _extract_content(self, response: dict) -> str:
        """Extract content from API response."""
        return response["choices"][0]["message"]["content"]
```

### Provider Registration

Register your provider using entry points in `pyproject.toml`:

```toml
[project.entry-points."claif.providers"]
my_provider = "my_package.providers:MyCustomProvider"
```

Or register programmatically:

```python
from claif.providers import ProviderRegistry

# Register provider
registry = ProviderRegistry()
registry.register("my_provider", MyCustomProvider)

# Use with client
from claif import ClaifClient
client = ClaifClient(provider_registry=registry)
```

### Provider Package Structure

Create a separate package for your provider:

```
claif_my_provider/
├── src/
│   └── claif_my_provider/
│       ├── __init__.py
│       ├── provider.py      # Provider implementation
│       ├── config.py        # Configuration handling
│       └── errors.py        # Provider-specific errors
├── tests/
├── pyproject.toml
└── README.md
```

Example `pyproject.toml` for provider package:

```toml
[project]
name = "claif_my_provider"
version = "1.0.0"
description = "My Provider integration for Claif"
dependencies = [
    "claif>=1.0.0",
    "aiohttp>=3.8.0",
]

[project.entry-points."claif.providers"]
my_provider = "claif_my_provider:MyProvider"

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"
```

## Creating Custom Tools

### Tool Interface

Tools extend Claif's capabilities through the MCP protocol:

```python
from abc import ABC, abstractmethod
from typing import Any
from claif.tools.base import Tool

class CalculatorTool(Tool):
    """Mathematical calculator tool."""
    
    name = "calculator"
    description = "Perform mathematical calculations"
    
    def __init__(self):
        super().__init__()
        self.schema = {
            "type": "object",
            "properties": {
                "expression": {
                    "type": "string",
                    "description": "Mathematical expression to evaluate"
                }
            },
            "required": ["expression"]
        }
    
    async def execute(self, **kwargs) -> Any:
        """Execute the tool with given parameters."""
        expression = kwargs.get("expression")
        if not expression:
            raise ValueError("Expression is required")
        
        try:
            # Use a safe evaluator in production
            import ast
            import operator
            
            # Safe math operations
            operations = {
                ast.Add: operator.add,
                ast.Sub: operator.sub,
                ast.Mult: operator.mul,
                ast.Div: operator.truediv,
                ast.Pow: operator.pow,
                ast.USub: operator.neg,
            }
            
            def safe_eval(node):
                if isinstance(node, ast.Constant):
                    return node.value
                elif isinstance(node, ast.BinOp):
                    return operations[type(node.op)](
                        safe_eval(node.left),
                        safe_eval(node.right)
                    )
                elif isinstance(node, ast.UnaryOp):
                    return operations[type(node.op)](safe_eval(node.operand))
                else:
                    raise ValueError(f"Unsupported operation: {type(node)}")
            
            tree = ast.parse(expression, mode='eval')
            result = safe_eval(tree.body)
            
            return {
                "result": result,
                "expression": expression,
                "success": True
            }
            
        except Exception as e:
            return {
                "error": str(e),
                "expression": expression,
                "success": False
            }
    
    def validate_input(self, **kwargs) -> bool:
        """Validate tool input parameters."""
        return "expression" in kwargs and isinstance(kwargs["expression"], str)
```

### Tool Registration

Register tools with the tool registry:

```python
from claif.tools import ToolRegistry

# Create registry
registry = ToolRegistry()

# Register tool
registry.register(CalculatorTool())

# Use with MCP server
from claif.server import MCPServer

server = MCPServer(tool_registry=registry)
await server.start()
```

### Complex Tool Example

```python
import aiohttp
from claif.tools.base import Tool

class WebSearchTool(Tool):
    """Web search tool using external API."""
    
    name = "web_search"
    description = "Search the web for information"
    
    def __init__(self, api_key: str):
        super().__init__()
        self.api_key = api_key
        self.schema = {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "Search query"
                },
                "num_results": {
                    "type": "integer",
                    "description": "Number of results to return",
                    "default": 5,
                    "minimum": 1,
                    "maximum": 20
                }
            },
            "required": ["query"]
        }
    
    async def execute(self, **kwargs) -> Any:
        """Execute web search."""
        query = kwargs.get("query")
        num_results = kwargs.get("num_results", 5)
        
        async with aiohttp.ClientSession() as session:
            params = {
                "q": query,
                "num": num_results,
                "key": self.api_key
            }
            
            async with session.get(
                "https://api.example.com/search",
                params=params
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    return {
                        "results": data.get("items", []),
                        "query": query,
                        "success": True
                    }
                else:
                    return {
                        "error": f"Search failed with status {response.status}",
                        "query": query,
                        "success": False
                    }
    
    def validate_input(self, **kwargs) -> bool:
        """Validate search parameters."""
        query = kwargs.get("query")
        num_results = kwargs.get("num_results", 5)
        
        return (
            isinstance(query, str) and
            len(query.strip()) > 0 and
            isinstance(num_results, int) and
            1 <= num_results <= 20
        )
```

## Architecture Extensions

### Custom Configuration Sources

Extend the configuration system:

```python
from claif.common.config import ConfigSource

class DatabaseConfigSource(ConfigSource):
    """Load configuration from database."""
    
    def __init__(self, connection_string: str):
        self.connection_string = connection_string
    
    async def load_config(self) -> dict:
        """Load configuration from database."""
        # Database loading logic
        async with get_db_connection(self.connection_string) as conn:
            config_rows = await conn.fetch("SELECT key, value FROM config")
            
        config = {}
        for row in config_rows:
            # Convert flat keys to nested dict
            keys = row['key'].split('.')
            current = config
            for key in keys[:-1]:
                current = current.setdefault(key, {})
            current[keys[-1]] = row['value']
            
        return config

# Register custom config source
from claif.common.config import ConfigManager

config_manager = ConfigManager()
config_manager.add_source(DatabaseConfigSource("postgresql://..."))
```

### Custom Session Storage

Implement custom session storage:

```python
from claif.session.storage import SessionStorage
from claif.common.types import Message

class RedisSessionStorage(SessionStorage):
    """Store sessions in Redis."""
    
    def __init__(self, redis_url: str):
        import redis.asyncio as redis
        self.redis = redis.from_url(redis_url)
    
    async def save_session(self, session_id: str, messages: list[Message]) -> None:
        """Save session to Redis."""
        import json
        
        data = {
            "messages": [
                {
                    "role": msg.role.value,
                    "content": msg.content,
                    "metadata": msg.metadata,
                    "timestamp": msg.timestamp
                }
                for msg in messages
            ]
        }
        
        await self.redis.set(
            f"session:{session_id}",
            json.dumps(data),
            ex=3600  # 1 hour expiry
        )
    
    async def load_session(self, session_id: str) -> list[Message]:
        """Load session from Redis."""
        import json
        from claif.common.types import MessageRole
        
        data = await self.redis.get(f"session:{session_id}")
        if not data:
            return []
        
        parsed = json.loads(data)
        messages = []
        
        for msg_data in parsed["messages"]:
            message = Message(
                role=MessageRole(msg_data["role"]),
                content=msg_data["content"],
                metadata=msg_data.get("metadata"),
                timestamp=msg_data.get("timestamp")
            )
            messages.append(message)
        
        return messages
    
    async def delete_session(self, session_id: str) -> None:
        """Delete session from Redis."""
        await self.redis.delete(f"session:{session_id}")
    
    async def list_sessions(self) -> list[str]:
        """List all session IDs."""
        keys = await self.redis.keys("session:*")
        return [key.decode().replace("session:", "") for key in keys]
```

## Performance Optimization

### Connection Pooling

Implement efficient connection pooling:

```python
import aiohttp
from claif.providers.base import Provider

class OptimizedProvider(Provider):
    """Provider with connection pooling."""
    
    def __init__(self, config: dict):
        super().__init__(config)
        self._session_pool = None
        self._pool_size = config.get("pool_size", 10)
        self._timeout = aiohttp.ClientTimeout(total=config.get("timeout", 60))
    
    async def _get_session(self) -> aiohttp.ClientSession:
        """Get session with connection pooling."""
        if not self._session_pool:
            connector = aiohttp.TCPConnector(
                limit=self._pool_size,
                keepalive_timeout=300,
                enable_cleanup_closed=True
            )
            
            self._session_pool = aiohttp.ClientSession(
                connector=connector,
                timeout=self._timeout,
                headers=self._get_headers()
            )
        
        return self._session_pool
    
    async def close(self):
        """Clean up resources."""
        if self._session_pool:
            await self._session_pool.close()
```

### Caching Implementation

Add response caching:

```python
from typing import Optional
import hashlib
import json
import time

class CachedProvider(Provider):
    """Provider with response caching."""
    
    def __init__(self, config: dict, cache_ttl: int = 3600):
        super().__init__(config)
        self._cache = {}
        self._cache_ttl = cache_ttl
    
    def _get_cache_key(self, message: str, context, **kwargs) -> str:
        """Generate cache key for request."""
        cache_data = {
            "message": message,
            "context": [msg.content for msg in (context or [])],
            "kwargs": {k: v for k, v in kwargs.items() if k != "stream"}
        }
        
        cache_str = json.dumps(cache_data, sort_keys=True)
        return hashlib.md5(cache_str.encode()).hexdigest()
    
    def _get_cached_response(self, cache_key: str) -> Optional[str]:
        """Get cached response if valid."""
        if cache_key in self._cache:
            response, timestamp = self._cache[cache_key]
            if time.time() - timestamp < self._cache_ttl:
                return response
            else:
                del self._cache[cache_key]
        return None
    
    def _cache_response(self, cache_key: str, response: str):
        """Cache response."""
        self._cache[cache_key] = (response, time.time())
    
    async def send_message(self, message: str, context=None, **kwargs) -> str:
        """Send message with caching."""
        cache_key = self._get_cache_key(message, context, **kwargs)
        
        # Check cache first
        cached = self._get_cached_response(cache_key)
        if cached:
            return cached
        
        # Make actual request
        response = await super().send_message(message, context, **kwargs)
        
        # Cache response
        self._cache_response(cache_key, response)
        
        return response
```

## Documentation

### API Documentation

Use Sphinx or similar tools for API documentation:

```python
"""
Provider module for Claif.

This module contains the base Provider class and provider discovery logic.

Example:
    Create a custom provider::

        from claif.providers.base import Provider

        class MyProvider(Provider):
            async def send_message(self, message: str) -> str:
                return f"Echo: {message}"

Attributes:
    PROVIDER_REGISTRY (ProviderRegistry): Global provider registry
"""

class Provider:
    """Base class for all AI providers.
    
    Providers must implement the abstract methods to integrate with
    different AI services while presenting a unified interface.
    
    Attributes:
        name (str): Provider name
        config (dict): Provider configuration
        
    Example:
        Implement a custom provider::
        
            class MyProvider(Provider):
                async def send_message(self, message: str) -> str:
                    # Implementation here
                    return response
    """
    
    async def send_message(
        self,
        message: str,
        context: Optional[List[Message]] = None,
        **kwargs: Any
    ) -> str:
        """Send a message to the provider.
        
        Args:
            message: The message to send
            context: Previous conversation context
            **kwargs: Provider-specific options
            
        Returns:
            The provider's response
            
        Raises:
            ProviderError: If the provider encounters an error
            NetworkError: If there are network connectivity issues
            
        Example:
            >>> provider = MyProvider(config)
            >>> response = await provider.send_message("Hello")
            >>> print(response)
            "Hello! How can I help you?"
        """
        raise NotImplementedError
```

### Contributing Documentation

Update documentation when making changes:

1. **API Changes**: Update docstrings and type hints
2. **New Features**: Add examples and usage guides
3. **Configuration**: Document new config options
4. **Breaking Changes**: Update migration guides

### Example Documentation

Create comprehensive examples:

```python
"""
Examples for the Claif framework.

This module contains complete examples showing different usage patterns.
"""

import asyncio
from claif import ClaifClient
from claif.common.types import Message, MessageRole

async def basic_example():
    """Basic usage example."""
    client = ClaifClient()
    response = await client.send_message("What is Python?")
    print(f"Response: {response}")

async def provider_comparison_example():
    """Compare responses from different providers."""
    client = ClaifClient()
    
    question = "Explain quantum computing in simple terms"
    
    providers = ["claude", "gemini", "codex"]
    responses = {}
    
    for provider in providers:
        try:
            response = await client.send_message(question, provider=provider)
            responses[provider] = response
        except Exception as e:
            responses[provider] = f"Error: {e}"
    
    # Display results
    for provider, response in responses.items():
        print(f"\n{provider.upper()}:")
        print("-" * 40)
        print(response[:200] + "..." if len(response) > 200 else response)

async def conversation_example():
    """Maintain conversation context."""
    client = ClaifClient()
    
    context = []
    
    while True:
        user_input = input("\nYou: ")
        if user_input.lower() in ["quit", "exit"]:
            break
        
        # Add user message to context
        context.append(Message(
            role=MessageRole.USER,
            content=user_input
        ))
        
        # Get response
        response = await client.send_message(user_input, context=context)
        print(f"AI: {response}")
        
        # Add assistant response to context
        context.append(Message(
            role=MessageRole.ASSISTANT,
            content=response
        ))

if __name__ == "__main__":
    # Run examples
    asyncio.run(basic_example())
    asyncio.run(provider_comparison_example())
    asyncio.run(conversation_example())
```

## Release Process

### Version Management

Use semantic versioning (SemVer):

- **Major** (X.0.0): Breaking changes
- **Minor** (0.X.0): New features, backward compatible
- **Patch** (0.0.X): Bug fixes, backward compatible

### Release Checklist

1. **Update Version**: Bump version in `pyproject.toml`
2. **Update Changelog**: Document changes in `CHANGELOG.md`
3. **Run Tests**: Ensure all tests pass
4. **Build Package**: Create distribution packages
5. **Tag Release**: Create git tag
6. **Publish**: Release to PyPI

```bash
# Update version
hatch version patch  # or minor, major

# Run full test suite
pytest --cov=claif --cov-report=html

# Build package
hatch build

# Tag release
git tag v$(hatch version)
git push origin v$(hatch version)

# Publish to PyPI
hatch publish
```

### Automated Releases

Use GitHub Actions for automated releases:

```yaml
# .github/workflows/release.yml
name: Release

on:
  push:
    tags:
      - 'v*'

jobs:
  release:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.12'
      
      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install hatch
      
      - name: Run tests
        run: hatch run test
      
      - name: Build package
        run: hatch build
      
      - name: Publish to PyPI
        run: hatch publish
        env:
          HATCH_INDEX_USER: __token__
          HATCH_INDEX_AUTH: ${{ secrets.PYPI_TOKEN }}
```

## Summary

Developing with Claif involves:

- **Following coding standards** for consistency and quality
- **Implementing provider interfaces** for new AI services
- **Creating tools** to extend functionality
- **Writing comprehensive tests** for reliability
- **Contributing documentation** for community support
- **Following release processes** for stable distributions

The extensible architecture makes it easy to add new providers, tools, and features while maintaining compatibility and code quality.

For more information:
- [API Reference](api-reference.md) - Detailed API documentation
- [Troubleshooting](troubleshooting.md) - Common development issues