# CLAIF - Command Line Artificial Intelligence Framework

## Quickstart

CLAIF is a unified Python framework that lets you query multiple AI providers (Claude, Gemini, OpenAI) through one simple interface.

```bash
pip install claif[all] && claif query "Explain quantum computing in one sentence"
```

CLAIF is a unified Python framework for interacting with multiple AI language model providers through a consistent interface. It provides a plugin-based architecture that enables seamless integration with various AI providers while maintaining a common API.

## What is CLAIF?

CLAIF is a lightweight framework that provides:

- **Unified Interface**: Single API to interact with multiple AI providers (Claude, Gemini, Codex/OpenAI)
- **Plugin Architecture**: Dynamic provider discovery through Python entry points
- **Fire CLI**: Command-line interface with rich terminal output
- **MCP Server**: FastMCP server for tool integration
- **Async Support**: Full async/await support for all operations
- **Type Safety**: Comprehensive type hints throughout the codebase

## Installation

### Basic Installation

```bash
pip install claif
```

### With Provider Packages

CLAIF requires provider packages to be installed separately:

```bash
# Install with all providers
pip install claif[all]

# Or install specific providers
pip install claif claif_cla  # For Claude support
pip install claif claif_gem  # For Gemini support  
pip install claif claif_cod  # For Codex/OpenAI support
```

### Development Installation

```bash
git clone https://github.com/twardoch/claif.git
cd claif
pip install -e ".[dev,test]"
```

## CLI Usage

CLAIF provides a comprehensive command-line interface built with Fire.

### Basic Commands

```bash
# Query default provider
claif query "What is Python?"

# Query specific provider
claif query "Explain recursion" --provider claude

# Query with options
claif query "Write a haiku" --temperature 0.7 --max-tokens 50

# Stream responses in real-time
claif stream "Tell me a story" --provider gemini

# Query random provider
claif random "Tell me a joke"

# Query all providers in parallel
claif parallel "What is AI?" --compare
```

### Provider Management

```bash
# List available providers and their status
claif providers list

# Check provider health
claif providers status
```

### Configuration

```bash
# Show current configuration
claif config show

# Set default provider
claif config set default_provider=gemini

# Save configuration
claif config save
```

### MCP Server

```bash
# Start the MCP (Model Context Protocol) server
claif server --host localhost --port 8000
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
    options = ClaifOptions(provider=Provider.CLAUDE)
    async for message in query("Explain Python", options):
        print(message.content)

asyncio.run(main())
```

### Advanced Options

```python
from claif import ClaifOptions, Provider

options = ClaifOptions(
    provider=Provider.GEMINI,
    model="gemini-pro",
    temperature=0.7,
    max_tokens=1000,
    system_prompt="You are a helpful assistant",
    timeout=30,
    cache=True,
    verbose=True
)

async for message in query("Complex question", options):
    print(message.content)
```

### Parallel Queries

```python
from claif.client import query_all, query_random

# Query all providers in parallel
async for results in query_all("What is machine learning?"):
    for provider, messages in results.items():
        print(f"\n{provider.value}:")
        for msg in messages:
            print(msg.content)

# Query random provider
async for message in query_random("Tell me a joke"):
    print(message.content)
```

### Using the Client Class

```python
from claif.client import ClaifClient
from claif import ClaifOptions, Provider

client = ClaifClient()

# List available providers
providers = client.list_providers()
print(providers)  # [Provider.CLAUDE, Provider.GEMINI, Provider.CODEX]

# Query specific provider
options = ClaifOptions(provider=Provider.CLAUDE)
async for message in client.query("Hello", options):
    print(message.content)
```

## Why CLAIF is Useful

### 1. **Provider Independence**
- Switch between AI providers without changing your code
- Compare responses from multiple providers easily
- Avoid vendor lock-in

### 2. **Simplified Integration**
- Single API for all providers
- Consistent error handling
- Unified configuration management

### 3. **Developer Experience**
- Type hints for better IDE support
- Rich CLI with beautiful output
- Comprehensive logging with loguru
- MCP server for tool integration

### 4. **Extensibility**
- Plugin-based architecture
- Easy to add new providers
- Clean separation of concerns

## How It Works

### Architecture Overview

CLAIF uses a layered architecture:

```
┌─────────────────────────────┐
│      User Application       │
├─────────────────────────────┤
│        CLAIF CLI           │ ← Fire-based CLI with rich output
├─────────────────────────────┤
│      CLAIF Client          │ ← Async client with provider routing
├─────────────────────────────┤
│    Common Types/Utils      │ ← Shared data structures and utilities
├─────────────────────────────┤
│    Provider Wrappers       │ ← Simple adapters for provider packages
├─────┬─────┬─────┬──────────┤
│claif_cla│claif_gem│claif_cod│ ← Actual provider implementations
└─────┴─────┴─────┴──────────┘
```

### Core Components

#### 1. **Common Module** (`src/claif/common/`)

Provides shared functionality across all providers:

- **types.py**: Core data structures
  - `Message`: Base message class with role and content
  - `Provider`: Enum of supported providers (CLAUDE, GEMINI, CODEX)
  - `ClaifOptions`: Configuration for queries
  - `TextBlock`, `ToolUseBlock`, `ToolResultBlock`: Content block types
  - `ResponseMetrics`: Performance tracking

- **config.py**: Configuration management
  - Hierarchical loading: defaults → files → environment → CLI
  - Provider-specific configurations
  - Session and cache settings

- **errors.py**: Exception hierarchy
  - `ClaifError`: Base exception
  - `ProviderError`: Provider-specific errors
  - `ConfigurationError`: Config issues

- **utils.py**: Utilities
  - Response formatting (text, JSON, markdown)
  - Progress indicators
  - Logging configuration

#### 2. **Providers Module** (`src/claif/providers/`)

Simple wrapper classes that delegate to provider packages:

```python
# claude.py
class ClaudeProvider:
    async def query(self, prompt: str, options: ClaifOptions) -> AsyncIterator[Message]:
        async for message in claude_query(prompt, options):
            yield message
```

Each provider wrapper:
- Imports the actual provider package (`claif_cla`, `claif_gem`, `claif_cod`)
- Implements the same `query` interface
- Logs debug information

#### 3. **Client Module** (`src/claif/client.py`)

The main client implementation:

```python
class ClaifClient:
    def __init__(self):
        self.providers = {
            Provider.CLAUDE: ClaudeProvider(),
            Provider.GEMINI: GeminiProvider(),
            Provider.CODEX: CodexProvider(),
        }
```

Features:
- Routes queries to appropriate providers
- Implements `query`, `query_random`, and `query_all`
- Handles provider selection and error recovery

#### 4. **CLI Module** (`src/claif/cli.py`)

Fire-based CLI with rich terminal output:

```python
class ClaifCLI:
    def __init__(self, config_file=None, verbose=False):
        # Configure loguru based on verbose flag
        logger.remove()
        log_level = "DEBUG" if verbose else "INFO"
        logger.add(sys.stderr, level=log_level)
```

Commands:
- `query`: Basic queries with options
- `stream`: Live streaming responses
- `random`: Query random provider
- `parallel`: Query all providers
- `providers`: List and check health
- `config`: Manage configuration
- `server`: Start MCP server

#### 5. **Server Module** (`src/claif/server.py`)

FastMCP server implementation providing tools:
- `claif_query`: Query specific provider
- `claif_query_random`: Query random provider
- `claif_query_all`: Query all providers
- `claif_list_providers`: List available providers
- `claif_health_check`: Check provider health

### Configuration System

Configuration is loaded hierarchically:

1. **Default values** in `Config` dataclass
2. **Config files**:
   - `~/.claif/config.json`
   - `~/.config/claif/config.json`
   - `./claif.json`
3. **Environment variables**: `CLAIF_*`
4. **CLI arguments**

Example configuration:

```json
{
    "default_provider": "claude",
    "providers": {
        "claude": {
            "enabled": true,
            "model": "claude-3-opus-20240229",
            "api_key_env": "ANTHROPIC_API_KEY"
        },
        "gemini": {
            "enabled": true,
            "api_key_env": "GEMINI_API_KEY"
        }
    },
    "cache_enabled": true,
    "cache_ttl": 3600
}
```

### Plugin System

CLAIF uses Python's entry points for dynamic provider discovery:

```python
# In src/__init__.py
class PluginFinder:
    """Enables imports like: from claif import claude"""
    def find_spec(cls, fullname, path, target=None):
        # Looks up plugins via entry points
```

Provider packages register themselves:

```toml
# In provider's pyproject.toml
[project.entry-points."claif.plugins"]
claude = "claif_cla"
```

### Message Flow

1. **User Input**: CLI command or API call
2. **Options Parsing**: Create `ClaifOptions` with configuration
3. **Provider Selection**: Choose provider based on options
4. **Query Routing**: Client routes to appropriate provider wrapper
5. **Provider Execution**: Provider package handles actual API call
6. **Response Streaming**: Yield `Message` objects as they arrive
7. **Output Formatting**: Display with rich or return structured data

### Logging System

CLAIF uses loguru for simple, powerful logging:

- Automatic configuration based on verbose flag
- Debug logs for provider selection and queries
- Info logs for configuration changes
- Warning logs for missing features
- Structured logging with context

## Development

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src/claif --cov-report=term-missing

# Run specific test
pytest -k test_version
```

### Code Quality

```bash
# Format code
ruff format src tests

# Lint code  
ruff check src tests --fix

# Type checking
mypy src/claif
```

### Building

```bash
# Build distribution
python -m build

# Install in development mode
pip install -e ".[dev,test]"
```

## Project Structure

```
claif/
├── src/
│   ├── __init__.py              # Plugin system initialization
│   └── claif/
│       ├── __init__.py          # Public API exports
│       ├── common/              # Shared components
│       │   ├── __init__.py     # Exports logger, types, utils
│       │   ├── types.py        # Core data structures
│       │   ├── config.py       # Configuration management
│       │   ├── errors.py       # Exception hierarchy
│       │   └── utils.py        # Formatting and helpers
│       ├── providers/           # Provider wrappers
│       │   ├── __init__.py     # Provider exports
│       │   ├── claude.py       # Claude wrapper
│       │   ├── gemini.py       # Gemini wrapper
│       │   └── codex.py        # Codex wrapper
│       ├── client.py            # Main client implementation
│       ├── cli.py               # Fire CLI interface
│       └── server.py            # FastMCP server
├── tests/                       # Test suite
├── pyproject.toml               # Package configuration
├── LICENSE                      # MIT license
├── README.md                    # This file
├── CHANGELOG.md                 # Version history
├── PLAN.md                      # Development plan
├── TODO.md                      # Task list
└── PROGRESS.md                  # Implementation status
```

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Run tests and linting
5. Commit your changes (`git commit -m 'Add amazing feature'`)
6. Push to the branch (`git push origin feature/amazing-feature`)
7. Open a Pull Request

## License

MIT License - see [LICENSE](LICENSE) file for details.

## Related Projects

- [claif_cla](https://github.com/twardoch/claif_cla/) - Claude provider implementation
- [claif_gem](https://github.com/twardoch/claif_gem/) - Gemini provider implementation
- [claif_cod](https://github.com/twardoch/claif_cod/) - Codex/OpenAI provider implementation

## Links

- [GitHub Repository](https://github.com/twardoch/claif)
- [PyPI Package](https://pypi.org/project/claif/)
- [Documentation](https://github.com/twardoch/claif#readme)
- [Issue Tracker](https://github.com/twardoch/claif/issues)