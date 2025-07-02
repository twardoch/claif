# Claif - Command Line Artificial Intelligence Framework

## Quickstart

```bash
# Install with all providers and query Claude
pip install claif[all]
claif query "Explain quantum computing in one sentence"

# Or install specific providers
pip install claif claif_cla  # Just Claude
pip install claif claif_gem  # Just Gemini  
pip install claif claif_cod  # Just Codex/OpenAI

# Stream responses in real-time
claif stream "Tell me a story" --provider gemini

# Query all providers in parallel
claif parallel "What is the meaning of life?" --compare
```

## What is Claif?

Claif is a unified Python framework for interacting with multiple AI language model providers through a consistent interface. It lets you seamlessly switch between Claude (Anthropic), Gemini (Google), and Codex (OpenAI) without changing your code.

**Key Features:**
- **Single API** for all AI providers - write once, use any model
- **Plugin-based architecture** - providers are discovered dynamically  
- **Rich CLI** with Fire framework and beautiful terminal output
- **Full async support** for concurrent operations
- **Type-safe** with comprehensive hints throughout
- **MCP server** for tool integration
- **Auto-install** - missing provider CLIs are installed on first use

## Installation

### Basic Installation

```bash
# Core framework only
pip install claif

# With all providers (recommended)
pip install claif[all]
```

### Installing Specific Providers

```bash
# Claude provider (wraps Claude Code SDK)
pip install claif claif_cla

# Gemini provider (wraps Gemini CLI)  
pip install claif claif_gem

# Codex provider (wraps OpenAI Codex CLI)
pip install claif claif_cod
```

### Installing Provider CLIs

Claif can auto-install missing CLIs, or you can install them manually:

```bash
# Auto-install all CLIs
claif install

# Or install specific CLIs
claif install claude
claif install gemini
claif install codex

# Install via npm (if preferred)
npm install -g @anthropic-ai/claude-code
npm install -g @google/gemini-cli
npm install -g @openai/codex
```

### Development Installation

```bash
git clone https://github.com/twardoch/claif.git
cd claif
pip install -e ".[dev,test]"
```

## CLI Usage

Claif provides a comprehensive command-line interface built with Fire that shows clean, focused output by default. Use `--verbose` for detailed logging.

### Basic Commands

```bash
# Query default provider (Claude)
claif query "What is Python?"

# Query specific provider
claif query "Explain recursion" --provider gemini

# Query with options
claif query "Write a haiku about coding" --temperature 0.7 --max-tokens 50

# Stream responses in real-time with live display
claif stream "Tell me a story" --provider claude

# Query a random provider
claif random "Tell me a programming joke"

# Query all providers in parallel
claif parallel "What is AI?" --compare  # Side-by-side comparison
```

### Provider Management

```bash
# List providers with their status
claif providers list

# Check health of all providers
claif providers status

# Install provider CLIs
claif install         # All providers
claif install claude  # Specific provider

# Check installation status
claif status
```

### Configuration

```bash
# Show current configuration
claif config show

# Set configuration values
claif config set default_provider=gemini
claif config set cache_enabled=true
claif config set output_format=markdown

# Save configuration to file
claif config save
```

### MCP Server

```bash
# Start the MCP (Model Context Protocol) server
claif server --host localhost --port 8000 --reload

# The server provides tools:
# - claif_query: Query specific provider
# - claif_query_random: Query random provider  
# - claif_query_all: Query all providers
# - claif_list_providers: List available providers
# - claif_health_check: Check provider health
```

## Python API Usage

### Basic Usage

```python
import asyncio
from claif import query, ClaifOptions, Provider

async def main():
    # Simple query using default provider
    async for message in query("Hello, world!"):
        print(message.content)
    
    # Query specific provider  
    options = ClaifOptions(provider=Provider.GEMINI)
    async for message in query("Explain Python decorators", options):
        print(f"[{message.role}]: {message.content}")

asyncio.run(main())
```

### Advanced Options

```python
from claif import query, ClaifOptions, Provider

options = ClaifOptions(
    provider=Provider.CLAUDE,
    model="claude-3-opus-20240229",
    temperature=0.7,
    max_tokens=1000,
    system_prompt="You are an expert Python developer",
    timeout=60,
    cache=True,
    verbose=False  # Clean output by default
)

async def get_code_review():
    async for message in query("Review this code: def fib(n): return fib(n-1) + fib(n-2)", options):
        print(message.content)

asyncio.run(get_code_review())
```

### Parallel Queries

```python
from claif import query_all, query_random

# Query all providers in parallel
async def compare_providers():
    async for results in query_all("What is machine learning?"):
        for provider, messages in results.items():
            print(f"\n{provider.value.upper()}:")
            for msg in messages:
                print(msg.content)

# Query random provider
async def get_random_response():
    async for message in query_random("Tell me a programming joke"):
        print(message.content)

asyncio.run(compare_providers())
```

### Using the Client Class

```python
from claif.client import ClaifClient
from claif import ClaifOptions, Provider

# Create client instance
client = ClaifClient()

# List available providers
providers = client.list_providers()
print(f"Available: {[p.value for p in providers]}")

# Query with auto-install
# If Claude CLI is missing, it will be installed automatically
options = ClaifOptions(provider=Provider.CLAUDE)

async def query_with_client():
    async for message in client.query("Explain asyncio", options):
        print(message.content)

asyncio.run(query_with_client())
```

## How It Works

### Architecture Overview

Claif uses a layered architecture that separates concerns and enables provider independence:

```
┌─────────────────────────────┐
│      User Application       │
├─────────────────────────────┤
│       Claif CLI           │ ← Fire-based CLI with rich output
├─────────────────────────────┤
│     Claif Client          │ ← Async client with provider routing
├─────────────────────────────┤
│    Common Types/Utils      │ ← Shared data structures and utilities
├─────────────────────────────┤
│    Provider Wrappers       │ ← Simple adapters for provider packages
├─────┬─────┬─────┬──────────┤
│claif_cla│claif_gem│claif_cod│ ← Actual provider implementations
└─────┴─────┴─────┴──────────┘
```

### Core Components

#### Common Module (`src/claif/common/`)

**types.py** - Core data structures:
```python
class Message:
    role: MessageRole  # USER, ASSISTANT, SYSTEM
    content: str | list[TextBlock | ToolUseBlock | ToolResultBlock]

class Provider(Enum):
    CLAUDE = "claude"
    GEMINI = "gemini" 
    CODEX = "codex"

class ClaifOptions:
    provider: Provider | None
    model: str | None
    temperature: float | None
    max_tokens: int | None
    system_prompt: str | None
    timeout: int | None
    cache: bool = True
    verbose: bool = False
```

**config.py** - Hierarchical configuration:
- Default values → Config files → Environment vars → CLI args
- Locations: `~/.claif/config.json`, `~/.config/claif/config.json`, `./claif.json`
- Provider-specific settings with API key management

**errors.py** - Exception hierarchy:
- `ClaifError` → Base exception
- `ProviderError` → Provider-specific failures
- `ConfigurationError` → Configuration issues  
- `TransportError` → Communication errors
- `TimeoutError` → Operation timeouts

**install.py** - Auto-installation support:
```python
def install_provider(provider, package, exec_name):
    # 1. Install npm package using bun
    # 2. Bundle executable
    # 3. Install to ~/.local/bin
```

#### Providers Module (`src/claif/providers/`)

Simple wrapper classes that delegate to provider packages:

```python
# claude.py
from claif_cla import query as claude_query

class ClaudeProvider:
    async def query(self, prompt: str, options: ClaifOptions) -> AsyncIterator[Message]:
        logger.debug(f"Querying Claude with prompt: {prompt[:50]}...")
        async for message in claude_query(prompt, options):
            yield message
```

Each provider:
- Imports the actual provider package (`claif_cla`, `claif_gem`, `claif_cod`)
- Implements the same `query` interface
- Handles provider-specific option conversion

#### Client Module (`src/claif/client.py`)

The main client with auto-install support:

```python
class ClaifClient:
    def __init__(self):
        self.providers = {
            Provider.CLAUDE: ClaudeProvider(),
            Provider.GEMINI: GeminiProvider(),
            Provider.CODEX: CodexProvider(),
        }
    
    async def query(self, prompt: str, options: ClaifOptions) -> AsyncIterator[Message]:
        try:
            # Route to provider
            async for message in provider.query(prompt, options):
                yield message
        except Exception as e:
            if _is_cli_missing_error(e):
                # Auto-install missing CLI
                install_result = install_func()
                if install_result.get("installed"):
                    # Retry query
                    async for message in provider.query(prompt, options):
                        yield message
```

Key features:
- Routes queries to appropriate providers
- Auto-installs missing provider CLIs
- Implements `query`, `query_random`, and `query_all`
- Handles errors with graceful fallbacks

#### CLI Module (`src/claif/cli.py`)

Fire-based CLI with rich terminal output:

```python
class ClaifCLI:
    def __init__(self, config_file=None, verbose=False):
        # Clean output by default
        logger.remove()
        if verbose:
            logger.add(sys.stderr, level="DEBUG")
        else:
            # Only errors go to stderr in non-verbose mode
            logger.add(sys.stderr, level="ERROR")
```

Main commands:
- `query` - Execute queries with options
- `stream` - Live streaming with rich.Live display
- `random` - Query random provider
- `parallel` - Query all providers (with `--compare` for side-by-side)
- `session` - Start provider-specific interactive session
- `install` - Install provider CLIs with bun bundling
- `config` - Manage settings
- `server` - Start MCP server

#### Server Module (`src/claif/server.py`)

FastMCP server implementation:

```python
server = FastMCP("Claif MCP Server")

@server.tool()
async def claif_query(prompt: str, provider: str = None) -> list[dict]:
    """Query specific AI provider."""
    options = ClaifOptions(provider=Provider(provider) if provider else None)
    messages = []
    async for message in query(prompt, options):
        messages.append(message.to_dict())
    return messages

# Additional tools:
# - claif_query_random: Random provider selection
# - claif_query_all: Parallel queries
# - claif_list_providers: Available providers
# - claif_health_check: Provider status
```

#### Install Module (`src/claif/install.py`)

Handles CLI installation and bundling:

```python
def install_claude() -> dict:
    """Install Claude Code CLI."""
    return install_provider(
        provider="claude",
        package="@anthropic-ai/claude-code", 
        exec_name="claude"
    )

# Installation process:
# 1. Install npm package globally using bun
# 2. Bundle with bun compile for fast startup
# 3. Copy to ~/.local/bin
# 4. Handle platform-specific paths
```

Key features:
- Uses bun for fast npm installs
- Creates bundled executables
- Platform-aware installation paths
- Automatic PATH checking

### Configuration System

Hierarchical configuration loading:

1. **Default values** in `Config` dataclass
2. **Config files** (first found wins):
   - `~/.claif/config.json`
   - `~/.config/claif/config.json`
   - `./claif.json`
3. **Environment variables**: 
   - `CLAIF_DEFAULT_PROVIDER`
   - `CLAIF_VERBOSE`
   - `CLAIF_CACHE_ENABLED`
   - `CLAIF_SESSION_DIR`
4. **CLI arguments** (highest priority)

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
            "model": "gemini-2.5-pro",
            "api_key_env": "GEMINI_API_KEY"
        },
        "codex": {
            "enabled": true,
            "model": "o4-mini"
        }
    },
    "cache_enabled": true,
    "cache_ttl": 3600,
    "output_format": "text"
}
```

### Plugin System

Python's entry points for dynamic provider discovery:

```python
# In src/__init__.py
class PluginFinder:
    """Enables imports like: from claif import claude"""
    def find_spec(cls, fullname, path, target=None):
        if fullname.startswith("claif."):
            # Look up via entry points
            eps = metadata.entry_points(group="claif.plugins")
            for ep in eps:
                if ep.name == plugin_name:
                    return ModuleSpec(fullname, Loader())
```

Provider packages register themselves:

```toml
# In provider's pyproject.toml
[project.entry-points."claif.plugins"]
claude = "claif_cla"
gemini = "claif_gem" 
codex = "claif_cod"
```

### Message Flow

1. **User Input** → CLI command or API call
2. **Options Parsing** → Create `ClaifOptions` with configuration
3. **Provider Selection** → Choose provider based on options
4. **Query Routing** → Client routes to appropriate provider wrapper
5. **CLI Check** → Auto-install if CLI missing
6. **Provider Execution** → Provider package handles actual call
7. **Response Streaming** → Yield `Message` objects as they arrive
8. **Output Formatting** → Display with rich or return structured data

### Code Structure

```
claif/
├── src/
│   ├── __init__.py              # Plugin system initialization
│   └── claif/
│       ├── __init__.py          # Public API exports
│       ├── common/              # Shared components
│       │   ├── __init__.py      
│       │   ├── types.py         # Core data structures
│       │   ├── config.py        # Configuration management
│       │   ├── errors.py        # Exception hierarchy
│       │   ├── install.py       # CLI installation utilities
│       │   └── utils.py         # Formatting and helpers
│       ├── providers/           # Provider wrappers
│       │   ├── __init__.py      
│       │   ├── claude.py        # Claude wrapper
│       │   ├── gemini.py        # Gemini wrapper
│       │   └── codex.py         # Codex wrapper
│       ├── client.py            # Main client implementation
│       ├── cli.py               # Fire CLI interface
│       ├── server.py            # FastMCP server
│       └── install.py           # Provider CLI installation
├── tests/                       # Test suite
├── pyproject.toml               # Package configuration
└── README.md                    # This file
```

### Key Implementation Details

**Async Everywhere**: All I/O operations use async/await for efficiency

**Message Types**: Flexible content that can be string or structured blocks:
```python
class Message:
    role: MessageRole
    content: str | list[TextBlock | ToolUseBlock | ToolResultBlock]
```

**Provider Adapters**: Thin wrappers that maintain provider-specific features:
```python
# Each provider wrapper is ~20 lines
# Imports provider package
# Converts options if needed  
# Yields messages unchanged
```

**Auto-Install Logic**: Missing CLIs trigger automatic installation:
```python
if _is_cli_missing_error(e):
    install_func = _get_provider_install_function(provider)
    if install_func():
        # Retry query with fresh provider instance
```

**Clean Output**: Logging configured to minimize noise:
```python
# Verbose OFF: Only errors to stderr
# Verbose ON: Full debug logging
# AI responses always go to stdout
```

## Installation Details: Bun and Node

Claif uses a hybrid approach for installing provider CLIs:

### Why Bun?

[Bun](https://bun.sh) is used for:
1. **Fast npm installs** - 10x faster than npm
2. **Binary bundling** - Creates standalone executables
3. **Cross-platform** - Works on Windows, macOS, Linux
4. **Minimal dependencies** - Single binary, no Node.js required

### Installation Process

```bash
# 1. Bun installs the npm package globally
bun add -g @anthropic-ai/claude-code

# 2. Bundle script creates optimized binary
bun build claude-wrapper.ts --compile --outfile dist/claude

# 3. Binary is copied to ~/.local/bin
cp dist/claude ~/.local/bin/
```

### Manual Installation Options

If you prefer Node.js:
```bash
# Using npm
npm install -g @anthropic-ai/claude-code
npm install -g @google/gemini-cli  
npm install -g @openai/codex

# Using yarn
yarn global add @anthropic-ai/claude-code

# Using pnpm
pnpm add -g @anthropic-ai/claude-code
```

### Bundle Benefits

1. **Faster startup** - No Node.js initialization
2. **Smaller size** - Single file vs node_modules
3. **No conflicts** - Isolated from system Node.js
4. **Portable** - Copy binary anywhere

### Troubleshooting

```bash
# Check if CLIs are found
claif status

# Manually set CLI paths
export CLAUDE_CLI_PATH=/usr/local/bin/claude
export GEMINI_CLI_PATH=/usr/local/bin/gemini
export CODEX_CLI_PATH=/usr/local/bin/codex

# Skip auto-install and use existing CLIs
claif config set auto_install=false
```

## Why Use Claif?

### 1. **Provider Independence**
- Write once, use any AI model
- Switch providers with a single parameter
- Compare responses side-by-side
- No vendor lock-in

### 2. **Zero Friction**
- Auto-installs missing CLIs on first use
- Clean output - only show what matters
- Smart defaults that just work
- Async for speed

### 3. **Developer Experience**  
- Full type hints and IDE support
- Rich CLI with progress indicators
- Comprehensive error messages
- Fast MCP server for tool integration

### 4. **Production Ready**
- Battle-tested error handling
- Timeout protection
- Response caching (coming soon)
- Configurable everything

### 5. **Extensible**
- Plugin architecture for new providers
- Clean API for custom integrations  
- Well-documented codebase
- Active development

## Contributing

Based on the development guide in [CLAUDE.md](CLAUDE.md):

### Development Setup

```bash
# Clone the repository
git clone https://github.com/twardoch/claif.git
cd claif

# Install with dev dependencies
pip install -e ".[dev,test]"

# Install pre-commit hooks
pre-commit install
```

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src/claif --cov-report=html

# Run specific test
pytest tests/test_client.py -v

# Run integration tests (requires provider packages)
pytest tests/integration/ -v
```

### Code Quality

```bash
# Format code
ruff format src tests

# Lint code  
ruff check src tests --fix

# Type checking
mypy src/claif

# Run all checks (as per CLAUDE.md)
fd -e py -x ruff format {}
fd -e py -x ruff check --fix --unsafe-fixes {}
python -m pytest
```

### Making Changes

1. **Check existing utilities** in `claif.common` before implementing
2. **Maintain API compatibility** - this is a plugin framework
3. **Add tests** for new functionality
4. **Update documentation** in docstrings and README
5. **Follow style** - 120 char lines, descriptive names

### Release Process

```bash
# Update version (uses hatch-vcs)
git tag v1.0.7

# Build distribution
python -m build

# Upload to PyPI
twine upload dist/*
```

## License

MIT License - see [LICENSE](LICENSE) file for details.

Copyright (c) 2025 Adam Twardoch

## Links

### Claif Ecosystem

**Core Framework:**
- [GitHub: twardoch/claif](https://github.com/twardoch/claif) - This repository
- [PyPI: claif](https://pypi.org/project/claif/) - Core package
- [Documentation](https://github.com/twardoch/claif#readme) - Full docs
- [Issues](https://github.com/twardoch/claif/issues) - Bug reports & features

**Provider Packages:**
- [claif_cla](https://github.com/twardoch/claif_cla/) - Claude provider (wraps claude-code-sdk)
- [claif_gem](https://github.com/twardoch/claif_gem/) - Gemini provider (wraps Gemini CLI)  
- [claif_cod](https://github.com/twardoch/claif_cod/) - Codex provider (wraps OpenAI Codex CLI)

### Upstream Projects

**Provider CLIs:**
- [Claude Code](https://github.com/anthropics/claude-code) - Anthropic's official CLI
- [claude-code-sdk](https://github.com/anthropics/claude-code-sdk-python) - Python SDK for Claude
- [Gemini CLI](https://github.com/google-gemini/gemini-cli/) - Google's Gemini CLI
- [OpenAI Codex CLI](https://github.com/openai/codex) - OpenAI's code generation CLI

**Related Tools:**
- [Fire](https://github.com/google/python-fire) - Python CLI framework
- [Rich](https://github.com/Textualize/rich) - Terminal formatting
- [FastMCP](https://github.com/fixie-ai/fastmcp) - MCP server framework
- [Bun](https://bun.sh) - Fast JavaScript runtime used for bundling

### Resources

**Documentation:**
- [Anthropic Docs](https://docs.anthropic.com/) - Claude documentation
- [Google AI Studio](https://ai.google.dev/) - Gemini documentation
- [OpenAI Platform](https://platform.openai.com/) - OpenAI documentation

**Community:**
- [Discussions](https://github.com/twardoch/claif/discussions) - Q&A and ideas
- [Twitter: @adamtwar](https://twitter.com/adamtwar) - Author updates

**Articles & Tutorials:**
- [Building a Unified AI CLI](https://example.com) - Design decisions
- [Plugin Architecture in Python](https://example.com) - Technical deep dive
- [Async Patterns for AI APIs](https://example.com) - Performance guide