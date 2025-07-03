---
layout: default
title: CLI Reference
parent: API Reference
nav_order: 2
---

# CLI Reference

Complete reference for the Claif command-line interface.

## Installation

Install Claif using pip or uv:

```bash
# Using pip
pip install claif

# Using uv (recommended)
uv pip install claif
```

## Basic Usage

```bash
claif [COMMAND] [OPTIONS] [ARGUMENTS]
```

## Global Options

These options work with all commands:

| Option | Short | Description | Default |
|--------|-------|-------------|---------|
| `--help` | `-h` | Show help message | |
| `--verbose` | `-v` | Enable verbose output | `false` |
| `--debug` | | Enable debug logging | `false` |
| `--config` | `-c` | Path to config file | `~/.claif/config.toml` |
| `--provider` | `-p` | Default provider to use | From config |

## Commands

### `query`

Send a query to an AI provider.

```bash
claif query "What is machine learning?" --provider claude
```

#### Syntax

```bash
claif query MESSAGE [OPTIONS]
```

#### Arguments

- `MESSAGE` - The message to send to the AI provider

#### Options

| Option | Short | Type | Description | Default |
|--------|-------|------|-------------|---------|
| `--provider` | `-p` | str | Provider to use (claude, gemini, codex) | From config |
| `--temperature` | `-t` | float | Sampling temperature (0.0-1.0) | `0.7` |
| `--max-tokens` | `-m` | int | Maximum tokens in response | `1000` |
| `--timeout` | | float | Request timeout in seconds | `120.0` |
| `--stream` | `-s` | bool | Stream response in real-time | `false` |
| `--format` | `-f` | str | Output format (text, json, markdown) | `text` |
| `--no-color` | | bool | Disable colored output | `false` |
| `--save` | | str | Save response to file | |

#### Examples

```bash
# Basic query
claif query "Explain quantum computing"

# Use specific provider with options
claif query "Write a Python function" --provider claude --temperature 0.5

# Stream response
claif query "Tell me a story" --stream

# Save response to file
claif query "Code review best practices" --save response.md

# Output as JSON
claif query "List 5 programming languages" --format json
```

### `config`

Manage Claif configuration.

```bash
claif config show
claif config set providers.claude.api_key sk-...
```

#### Subcommands

##### `show`

Display current configuration.

```bash
claif config show [--format FORMAT]
```

**Options:**
- `--format` - Output format (yaml, json, toml) [default: yaml]

**Example:**
```bash
claif config show --format json
```

##### `set`

Set a configuration value.

```bash
claif config set KEY VALUE
```

**Arguments:**
- `KEY` - Configuration key (dot notation supported)
- `VALUE` - Configuration value

**Examples:**
```bash
# Set default provider
claif config set default_provider claude

# Set API key
claif config set providers.claude.api_key sk-ant-...

# Set timeout
claif config set timeout 60.0

# Set provider-specific option
claif config set providers.gemini.model_name gemini-pro
```

##### `get`

Get a configuration value.

```bash
claif config get KEY
```

**Arguments:**
- `KEY` - Configuration key

**Examples:**
```bash
claif config get default_provider
claif config get providers.claude.api_key
```

##### `unset`

Remove a configuration value.

```bash
claif config unset KEY
```

**Arguments:**
- `KEY` - Configuration key to remove

##### `edit`

Open configuration file in default editor.

```bash
claif config edit
```

##### `reset`

Reset configuration to defaults.

```bash
claif config reset [--confirm]
```

**Options:**
- `--confirm` - Skip confirmation prompt

### `list`

List available providers and their status.

```bash
claif list [OPTIONS]
```

#### Options

| Option | Type | Description | Default |
|--------|------|-------------|---------|
| `--format` | str | Output format (table, json, yaml) | `table` |
| `--available-only` | bool | Show only available providers | `false` |
| `--detailed` | bool | Show detailed provider information | `false` |

#### Examples

```bash
# List all providers
claif list

# Show only available providers
claif list --available-only

# Detailed information as JSON
claif list --detailed --format json
```

### `server`

Start the MCP (Model Context Protocol) server.

```bash
claif server --port 8000
```

#### Options

| Option | Type | Description | Default |
|--------|------|-------------|---------|
| `--host` | str | Host to bind to | `localhost` |
| `--port` | int | Port to bind to | `8080` |
| `--workers` | int | Number of worker processes | `1` |
| `--reload` | bool | Enable auto-reload for development | `false` |

#### Examples

```bash
# Start server on default port
claif server

# Start on specific host and port
claif server --host 0.0.0.0 --port 8000

# Development mode with auto-reload
claif server --reload
```

### `install`

Install provider CLI tools.

```bash
claif install claude
```

#### Syntax

```bash
claif install [PROVIDER] [OPTIONS]
```

#### Arguments

- `PROVIDER` - Provider to install (claude, gemini, codex, or 'all')

#### Options

| Option | Type | Description | Default |
|--------|------|-------------|---------|
| `--force` | bool | Force reinstallation | `false` |
| `--version` | str | Specific version to install | `latest` |
| `--dry-run` | bool | Show what would be installed | `false` |

#### Examples

```bash
# Install Claude CLI
claif install claude

# Install all providers
claif install all

# Force reinstall with specific version
claif install gemini --force --version 1.2.0

# Dry run to see what would be installed
claif install codex --dry-run
```

### `health`

Check health status of providers and system.

```bash
claif health [OPTIONS]
```

#### Options

| Option | Type | Description | Default |
|--------|------|-------------|---------|
| `--provider` | str | Check specific provider only | |
| `--format` | str | Output format (table, json) | `table` |
| `--timeout` | float | Health check timeout | `10.0` |

#### Examples

```bash
# Check all providers
claif health

# Check specific provider
claif health --provider claude

# Output as JSON
claif health --format json
```

### `version`

Show version information.

```bash
claif version [OPTIONS]
```

#### Options

| Option | Type | Description | Default |
|--------|------|-------------|---------|
| `--format` | str | Output format (text, json) | `text` |

## Configuration File

Claif uses a TOML configuration file located at `~/.claif/config.toml`.

### Example Configuration

```toml
# Default provider
default_provider = "claude"

# Global timeout
timeout = 120.0

# Default query options
[query_defaults]
temperature = 0.7
max_tokens = 1000
stream = false

# Provider configurations
[providers.claude]
api_key = "sk-ant-..."
model_name = "claude-3-sonnet-20240229"
timeout = 60.0

[providers.gemini]
api_key = "..."
model_name = "gemini-pro"
temperature = 0.8

[providers.codex]
api_key = "sk-..."
model_name = "gpt-4"
organization = "org-..."

# Logging configuration
[logging]
level = "INFO"
file = "~/.claif/logs/claif.log"
max_size = "10MB"
backup_count = 5
```

### Configuration Keys

#### Global Settings

- `default_provider` (str) - Default provider to use
- `timeout` (float) - Default timeout in seconds
- `log_level` (str) - Logging level (DEBUG, INFO, WARNING, ERROR)

#### Query Defaults

- `query_defaults.temperature` (float) - Default temperature
- `query_defaults.max_tokens` (int) - Default max tokens
- `query_defaults.stream` (bool) - Default streaming behavior

#### Provider Settings

Each provider can have:

- `api_key` (str) - API key for the provider
- `model_name` (str) - Default model to use
- `timeout` (float) - Provider-specific timeout
- `base_url` (str) - Custom API base URL
- Custom provider-specific options

## Environment Variables

Claif respects these environment variables:

| Variable | Description | Default |
|----------|-------------|---------|
| `CLAIF_CONFIG` | Path to config file | `~/.claif/config.toml` |
| `CLAIF_LOG_LEVEL` | Logging level | `INFO` |
| `CLAIF_DEFAULT_PROVIDER` | Default provider | From config |
| `CLAIF_TIMEOUT` | Default timeout | `120.0` |

### Provider-Specific Variables

#### Claude
- `ANTHROPIC_API_KEY` - Claude API key
- `CLAUDE_CLI_PATH` - Path to Claude CLI executable

#### Gemini
- `GOOGLE_API_KEY` - Gemini API key
- `GEMINI_CLI_PATH` - Path to Gemini CLI executable

#### Codex
- `OPENAI_API_KEY` - OpenAI API key
- `OPENAI_ORGANIZATION` - OpenAI organization
- `CODEX_CLI_PATH` - Path to Codex CLI executable

## Exit Codes

| Code | Meaning |
|------|---------|
| 0 | Success |
| 1 | General error |
| 2 | Configuration error |
| 3 | Provider error |
| 4 | Network/timeout error |
| 5 | Authentication error |
| 130 | Interrupted by user (Ctrl+C) |

## Shell Completion

Enable shell completion for better CLI experience:

### Bash

```bash
# Add to ~/.bashrc
eval "$(claif --completion bash)"
```

### Zsh

```bash
# Add to ~/.zshrc
eval "$(claif --completion zsh)"
```

### Fish

```bash
# Add to ~/.config/fish/config.fish
claif --completion fish | source
```

## Tips and Tricks

### Aliases

Create useful aliases in your shell:

```bash
# Quick queries
alias ask="claif query"
alias claude="claif query --provider claude"
alias gemini="claif query --provider gemini"

# Streaming responses
alias stream="claif query --stream"
```

### Piping and Redirection

```bash
# Pipe input
echo "Explain this code:" | cat - script.py | claif query

# Save to file
claif query "Write documentation" > docs.md

# Append to file
claif query "Add conclusion" >> docs.md
```

### JSON Processing

Use `jq` for JSON output processing:

```bash
# Extract just the text response
claif query "Hello" --format json | jq -r '.content[0].text'

# Get multiple responses and format
claif query "List 3 colors" --format json | jq '.content[].text'
```

### Configuration Management

```bash
# Backup current config
cp ~/.claif/config.toml ~/.claif/config.toml.backup

# Quick provider switching
claif config set default_provider claude
claif config set default_provider gemini

# Temporary config override
CLAIF_DEFAULT_PROVIDER=codex claif query "Code example"
```