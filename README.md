# CLAIF - Command Line Artificial Intelligence Framework

CLAIF is a unified Python framework for interacting with multiple AI language model providers (Claude, Gemini, Codex) through a consistent interface. It provides a powerful abstraction layer that allows seamless switching between different AI providers while maintaining the same API.

## What is CLAIF?

CLAIF serves as a top-level wrapper that:
- Provides a unified interface for multiple AI providers
- Handles provider-specific implementations transparently
- Offers advanced features like caching, retry logic, and session management
- Enables parallel querying of multiple providers
- Includes both Python API and CLI interfaces

## Installation

### From PyPI
```bash
pip install claif
```

### From Source
```bash
git clone https://github.com/twardoch/claif.git
cd claif
pip install -e .
```

### With Optional Dependencies
```bash
# Install with all provider packages
pip install claif[all]

# Install with specific providers
pip install claif claif_cla  # For Claude support
pip install claif claif_gem  # For Gemini support
pip install claif claif_cod  # For Codex support
```

## Command Line Usage

### Basic Query
```bash
# Query default provider (Claude)
claif query "What is the meaning of life?"

# Query specific provider
claif query "Explain quantum computing" --provider gemini

# Query with custom parameters
claif query "Write a haiku" --provider claude --temperature 0.7 --max-tokens 50
```

### Streaming Responses
```bash
# Stream responses in real-time
claif stream "Tell me a story" --provider gemini
```

### Query Multiple Providers
```bash
# Query all providers in parallel
claif query-all "What is Python?"

# Query random provider
claif query-random "Explain recursion"
```

### Session Management
```bash
# Create and use sessions
claif session create
claif query "Hello" --session SESSION_ID
claif session show SESSION_ID
claif session export SESSION_ID --format markdown
```

### Provider Comparison
```bash
# Compare responses from different providers
claif compare "What is AI?" --show-metrics
```

### Health Check
```bash
# Check if providers are available
claif health
claif health --provider gemini
```

## Python API Usage

### Basic Usage
```python
import asyncio
from claif import ClaifOptions, Provider
from claif.client import query

async def main():
    # Query default provider
    async for message in query("Hello, world!"):
        print(message.content)
    
    # Query specific provider
    options = ClaifOptions(provider=Provider.GEMINI)
    async for message in query("Explain Python", options):
        print(message.content)

asyncio.run(main())
```

### Advanced Options
```python
from claif import ClaifOptions, Provider

options = ClaifOptions(
    provider=Provider.CLAUDE,
    model="claude-3-opus-20240229",
    temperature=0.7,
    max_tokens=1000,
    system_prompt="You are a helpful assistant",
    timeout=30,
    cache=True
)

async for message in query("Complex question", options):
    print(message.content)
```

### Query All Providers
```python
from claif.client import query_all

async def compare_providers():
    prompt = "What is machine learning?"
    
    async for results in query_all(prompt):
        for provider, messages in results.items():
            print(f"\n{provider.value}:")
            for msg in messages:
                print(msg.content)

asyncio.run(compare_providers())
```

### Using the Client Class
```python
from claif.client import ClaifClient

client = ClaifClient()

# Query specific provider
async for message in client.query("Hello", options):
    print(message.content)

# Query random provider
async for message in client.query_random("Tell me a joke"):
    print(message.content)
```

## Why CLAIF is Useful

### 1. **Provider Abstraction**
- Write code once, use with any AI provider
- Easy switching between providers without code changes
- Consistent response format across all providers

### 2. **Advanced Features**
- **Caching**: Automatic response caching to reduce API calls and costs
- **Retry Logic**: Built-in retry with exponential backoff
- **Session Management**: Maintain conversation context across queries
- **Error Handling**: Unified error handling across providers

### 3. **Flexibility**
- Use as a library in your Python projects
- Use as a CLI tool for quick queries
- Run as an MCP server for integration with other tools

### 4. **Comparison Tools**
- Query multiple providers simultaneously
- Compare response quality and performance
- Benchmark different models

## How It Works

### Architecture Overview

```
┌─────────────────┐
│   User Code     │
├─────────────────┤
│   CLAIF API     │
├─────────────────┤
│ Provider Router │
├─────┬─────┬─────┤
│Claude│Gemini│Codex│
├─────┼─────┼─────┤
│claif│claif│claif│
│_cla │_gem │_cod │
└─────┴─────┴─────┘
```

### Core Components

#### 1. **Common Module** (`claif/common/`)
- **types.py**: Defines unified data structures (Message, TextBlock, etc.)
- **config.py**: Configuration management and loading
- **errors.py**: Unified error hierarchy
- **utils.py**: Shared utilities and formatters

#### 2. **Providers Module** (`claif/providers/`)
- **claude.py**: Claude provider implementation
- **gemini.py**: Gemini provider implementation  
- **codex.py**: Codex provider implementation

Each provider implements the base interface:
```python
class BaseProvider:
    async def query(prompt: str, options: ClaifOptions) -> AsyncIterator[Message]:
        pass
```

#### 3. **Client Module** (`claif/client.py`)
- Routes queries to appropriate providers
- Handles provider selection logic
- Implements parallel querying

#### 4. **CLI Module** (`claif/cli.py`)
- Fire-based command line interface
- Rich terminal output formatting
- Interactive features

#### 5. **Server Module** (`claif/server.py`)
- MCP (Model Context Protocol) server implementation
- Enables integration with MCP-compatible tools

### Provider Packages

CLAIF uses a plugin architecture where each AI provider is implemented as a separate package:

- **claif_cla**: Claude provider implementation
- **claif_gem**: Gemini provider implementation
- **claif_cod**: Codex provider implementation

These packages are automatically discovered and loaded when installed.

### Configuration

CLAIF uses a hierarchical configuration system:

1. Default configuration
2. User configuration file (`~/.claif/config.toml`)
3. Environment variables
4. Command line arguments

Example configuration:
```toml
[general]
default_provider = "claude"
verbose = false

[cache]
enabled = true
ttl = 3600

[retry]
count = 3
delay = 1.0
backoff = 2.0

[providers.claude]
model = "claude-3-opus-20240229"
api_key_env = "CLAUDE_API_KEY"

[providers.gemini]
model = "gemini-pro"
api_key_env = "GEMINI_API_KEY"
```

### Message Flow

1. User sends a query through CLI or API
2. CLAIF validates options and selects provider(s)
3. Query is forwarded to provider package (claif_cla, claif_gem, etc.)
4. Provider package handles API communication
5. Responses are normalized to CLAIF Message format
6. Messages are yielded back to user
7. Optional caching and session storage

### Error Handling

CLAIF provides a unified error hierarchy:

```python
ClaifError
├── ConfigurationError  # Configuration issues
├── ProviderError      # Provider-specific errors
├── TimeoutError       # Request timeouts
└── ValidationError    # Input validation errors
```

## Contributing

CLAIF is designed to be extensible. To add a new provider:

1. Create a new provider package (e.g., `claif_newprovider`)
2. Implement the provider interface
3. Register the provider in CLAIF
4. Submit a pull request

## License

MIT License - see LICENSE file for details.

## Links

- [GitHub Repository](https://github.com/twardoch/claif)
- [PyPI Package](https://pypi.org/project/claif/)
- [Documentation](https://github.com/twardoch/claif#readme)
- [Issue Tracker](https://github.com/twardoch/claif/issues)