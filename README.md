# CLAIF - Command Line Artificial Intelligence Framework

CLAIF is a unified Python framework for interacting with multiple AI language model providers through a consistent interface. It serves as the core framework that provides common types, error handling, configuration management, and the plugin architecture for various AI provider implementations.

## What is CLAIF?

CLAIF is the foundational package in the CLAIF ecosystem that:

- Defines the common data structures and types used across all provider implementations
- Provides a unified client interface for querying different AI providers
- Implements a Fire-based CLI with rich terminal output
- Offers an MCP (Model Context Protocol) server for integration with other tools
- Handles configuration management, error handling, and logging
- Enables plugin-based provider discovery and loading

The actual provider implementations (Claude, Gemini, Codex) are provided by separate packages:
- [`claif_cla`](https://github.com/twardoch/claif_cla/) - Claude provider via claude_code_sdk
- [`claif_gem`](https://github.com/twardoch/claif_gem/) - Gemini provider via gemini-cli
- [`claif_cod`](https://github.com/twardoch/claif_cod/) - Codex/OpenAI provider

## Installation

### Basic Installation
```bash
pip install claif
```

### With Provider Packages
```bash
# Install with all providers
pip install claif[all]

# Install with specific providers
pip install claif claif_cla  # For Claude support
pip install claif claif_gem  # For Gemini support
pip install claif claif_cod  # For Codex support
```

### Development Installation
```bash
git clone https://github.com/twardoch/claif.git
cd claif
pip install -e ".[dev,test]"
```

## Command Line Usage

CLAIF provides a comprehensive CLI built with Fire and rich for beautiful terminal output.

### Basic Queries
```bash
# Query using default provider
python -m claif.cli query "What is Python?"

# Query specific provider
python -m claif.cli query "Explain recursion" --provider gemini

# Query with options
python -m claif.cli query "Write a haiku" --provider claude --temperature 0.7 --max-tokens 50
```

### Streaming Responses
```bash
# Stream responses in real-time
python -m claif.cli stream "Tell me a story" --provider gemini
```

### Multiple Provider Queries
```bash
# Query a random provider
python -m claif.cli random "Tell me a joke"

# Query all providers in parallel
python -m claif.cli parallel "What is AI?" --compare
```

### Provider Management
```bash
# List available providers
python -m claif.cli providers list
```

### Configuration
```bash
# Show current configuration
python -m claif.cli config show

# Set default provider
python -m claif.cli config set default_provider gemini
```

### MCP Server
```bash
# Start the MCP server
python -m claif.cli server --host localhost --port 8000
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
    cache=True,
    verbose=True
)

async for message in query("Complex question", options):
    print(message.content)
```

### Query Multiple Providers
```python
from claif.client import query_all, query_random

# Query all providers
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
print(providers)

# Query specific provider
options = ClaifOptions(provider=Provider.CLAUDE)
async for message in client.query("Hello", options):
    print(message.content)
```

### MCP Server Integration
```python
from claif.server import start_mcp_server
from claif import Config

config = Config()
start_mcp_server(host="localhost", port=8000, config=config)
```

## Why CLAIF is Useful

### 1. **Unified Interface**
- Single API for multiple AI providers
- Consistent data structures across all providers
- Easy provider switching without code changes

### 2. **Plugin Architecture**
- Modular design with separate provider packages
- Easy to add new providers
- Automatic provider discovery via entry points

### 3. **Rich Feature Set**
- Comprehensive CLI with Fire
- Beautiful terminal output with rich
- MCP server for tool integration
- Flexible configuration system
- Robust error handling

### 4. **Developer Experience**
- Type hints throughout the codebase
- Async/await support
- Comprehensive logging
- Well-structured error hierarchy

## How It Works

### Architecture

```
┌──────────────────────┐
│    User/Application  │
├──────────────────────┤
│   CLAIF CLI (Fire)   │
├──────────────────────┤
│   CLAIF Client API   │
├──────────────────────┤
│  Provider Router     │
├──────────────────────┤
│  Common Types/Utils  │
├────┬────┬────┬──────┤
│claif_cla │claif_gem │claif_cod │ ... │
└────┴────┴────┴──────┘
```

### Core Components

#### 1. **Common Module** (`claif/common/`)
- **types.py**: Core data structures
  - `Message`: Base message class with role and content
  - `TextBlock`, `ToolUseBlock`, `ToolResultBlock`: Content blocks
  - `Provider`: Enum of supported providers
  - `ClaifOptions`: Query configuration
  - `ResponseMetrics`: Performance metrics
- **config.py**: Configuration management
  - Load from files, environment, and CLI args
  - Provider-specific configurations
  - Caching and retry settings
- **errors.py**: Exception hierarchy
  - `ClaifError`: Base exception
  - `ProviderError`, `ConfigurationError`, etc.
- **utils.py**: Utilities
  - Logging setup
  - Response formatting
  - Progress indicators

#### 2. **Providers Module** (`claif/providers/`)
Simple wrapper classes that delegate to the actual provider packages:
- **claude.py**: Imports from `claif_cla`
- **gemini.py**: Imports from `claif_gem`
- **codex.py**: Imports from `claif_cod`

#### 3. **Client Module** (`claif/client.py`)
- `ClaifClient`: Main client class
  - Routes queries to providers
  - Handles provider selection
  - Implements parallel queries
- Module-level convenience functions

#### 4. **CLI Module** (`claif/cli.py`)
- `ClaifCLI`: Fire-based CLI class
  - Query commands with rich output
  - Streaming support
  - Provider management
  - Configuration commands

#### 5. **Server Module** (`claif/server.py`)
- FastMCP server implementation
- MCP tools for querying providers
- Health checks and provider listing

### Plugin System

CLAIF uses Python's entry points for plugin discovery:

```python
# In src/__init__.py
class PluginFinder:
    """Finder for claif plugins to enable package-style imports."""
    # Enables: from claif import claude
```

Provider packages register themselves:
```toml
[project.entry-points."claif.plugins"]
claude = "claif_cla"
```

### Configuration Loading

Configuration is loaded hierarchically:
1. Default values in code
2. Config files: `~/.claif/config.json`, `.claif/config.json`
3. Environment variables: `CLAIF_*`
4. Command line arguments

### Message Flow

1. **User Request**: CLI command or API call
2. **Option Parsing**: ClaifOptions created with provider, model, etc.
3. **Provider Selection**: Based on options or random/all
4. **Query Delegation**: Client routes to provider package
5. **Provider Execution**: Provider package handles API communication
6. **Response Normalization**: Convert to CLAIF Message format
7. **Streaming**: Yield messages as they arrive
8. **Output Formatting**: Rich terminal output or structured data

## Development

### Project Structure
```
claif/
├── src/
│   ├── claif/
│   │   ├── __init__.py         # Plugin system
│   │   ├── common/             # Shared components
│   │   ├── providers/          # Provider wrappers
│   │   ├── client.py           # Client implementation
│   │   ├── cli.py              # CLI interface
│   │   └── server.py           # MCP server
│   └── __init__.py
├── tests/                      # Test suite
├── pyproject.toml              # Project configuration
└── README.md                   # This file
```

### Running Tests
```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src/claif --cov-report=term-missing

# Run specific test
pytest tests/test_package.py::test_version
```

### Code Quality
```bash
# Format code
ruff format src tests

# Lint code
ruff check src tests

# Type checking
mypy src/claif tests
```

### Building
```bash
# Build package
python -m build

# Build with hatch
hatch build
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests and linting
5. Submit a pull request

## License

MIT License - see LICENSE file for details.

## Links

- [GitHub Repository](https://github.com/twardoch/claif)
- [PyPI Package](https://pypi.org/project/claif/)
- Related packages:
  - [claif_cla](https://github.com/twardoch/claif_cla/) - Claude provider
  - [claif_gem](https://github.com/twardoch/claif_gem/) - Gemini provider
  - [claif_cod](https://github.com/twardoch/claif_cod/) - Codex provider