---
layout: default
title: Configuration System
parent: Core Framework
nav_order: 3
---

# Configuration System

Claif's configuration system provides flexible, hierarchical configuration management that supports multiple sources and automatic environment variable integration.

## Overview

The configuration system follows a clear precedence order:

1. **CLI arguments** (highest priority)
2. **Environment variables**
3. **Configuration files**
4. **Default values** (lowest priority)

## Configuration Structure

### Main Configuration Class

```python
@dataclass
class Config:
    """Main configuration class for the Claif framework."""
    
    default_provider: Provider = Provider.CLAUDE
    providers: dict[Provider, ProviderConfig] = field(default_factory=dict)
    cache_enabled: bool = True
    cache_ttl: int = 3600  # seconds
    session_dir: str | None = None  # defaults to ~/.claif/sessions
    verbose: bool = False
    output_format: str = "text"
    retry_config: dict[str, Any] = field(default_factory=lambda: {
        "count": 3, 
        "delay": 1.0, 
        "backoff": 2.0
    })
    mcp_servers: dict[str, Any] = field(default_factory=dict)
```

### Provider Configuration

```python
@dataclass
class ProviderConfig:
    """Configuration for individual providers."""
    
    enabled: bool = True
    model: str | None = None
    api_key_env: str | None = None
    timeout: int = 120
    extra: dict[str, Any] = field(default_factory=dict)
```

## Configuration Files

### File Locations

Claif searches for configuration files in the following order:

1. **Specified file**: `--config path/to/config.json`
2. **User config**: `~/.claif/config.json`
3. **XDG config**: `~/.config/claif/config.json`
4. **Local config**: `./claif.json`

### JSON Format

```json
{
  "default_provider": "claude",
  "cache_enabled": true,
  "cache_ttl": 3600,
  "session_dir": "~/.claif/sessions",
  "verbose": false,
  "output_format": "text",
  "retry_config": {
    "count": 3,
    "delay": 1.0,
    "backoff": 2.0
  },
  "providers": {
    "claude": {
      "enabled": true,
      "model": "claude-3-sonnet-20240229",
      "api_key_env": "ANTHROPIC_API_KEY",
      "timeout": 120,
      "extra": {
        "session_dir": "~/.claif/claude_sessions",
        "auto_approve": false
      }
    },
    "gemini": {
      "enabled": true,
      "model": "gemini-pro",
      "api_key_env": "GEMINI_API_KEY",
      "timeout": 90,
      "extra": {
        "auto_approve": true,
        "context_length": 32000
      }
    },
    "codex": {
      "enabled": true,
      "model": "o4-mini",
      "api_key_env": "OPENAI_API_KEY",
      "timeout": 120,
      "extra": {
        "action_mode": "review",
        "working_dir": "."
      }
    }
  },
  "mcp_servers": {
    "example_server": {
      "command": "python",
      "args": ["-m", "example_mcp_server"],
      "env": {
        "API_KEY": "${EXAMPLE_API_KEY}"
      }
    }
  }
}
```

### TOML Format (Alternative)

While JSON is the primary format, you can also use TOML:

```toml
# ~/.claif/config.toml
default_provider = "claude"
cache_enabled = true
cache_ttl = 3600
session_dir = "~/.claif/sessions"
verbose = false
output_format = "text"

[retry_config]
count = 3
delay = 1.0
backoff = 2.0

[providers.claude]
enabled = true
model = "claude-3-sonnet-20240229"
api_key_env = "ANTHROPIC_API_KEY"
timeout = 120

[providers.claude.extra]
session_dir = "~/.claif/claude_sessions"
auto_approve = false

[providers.gemini]
enabled = true
model = "gemini-pro"
api_key_env = "GEMINI_API_KEY"
timeout = 90

[providers.gemini.extra]
auto_approve = true
context_length = 32000

[providers.codex]
enabled = true
model = "o4-mini"
api_key_env = "OPENAI_API_KEY"
timeout = 120

[providers.codex.extra]
action_mode = "review"
working_dir = "."

[mcp_servers.example_server]
command = "python"
args = ["-m", "example_mcp_server"]

[mcp_servers.example_server.env]
API_KEY = "${EXAMPLE_API_KEY}"
```

## Environment Variables

### Global Settings

| Variable | Type | Description | Default |
|----------|------|-------------|---------|
| `CLAIF_DEFAULT_PROVIDER` | string | Default provider to use | `claude` |
| `CLAIF_VERBOSE` | boolean | Enable verbose logging | `false` |
| `CLAIF_OUTPUT_FORMAT` | string | Output format (text/json) | `text` |
| `CLAIF_CACHE_ENABLED` | boolean | Enable response caching | `true` |
| `CLAIF_CACHE_TTL` | integer | Cache TTL in seconds | `3600` |
| `CLAIF_SESSION_DIR` | string | Session storage directory | `~/.claif/sessions` |

### Retry Configuration

| Variable | Type | Description | Default |
|----------|------|-------------|---------|
| `CLAIF_RETRY_COUNT` | integer | Number of retry attempts | `3` |
| `CLAIF_RETRY_DELAY` | float | Initial retry delay (seconds) | `1.0` |
| `CLAIF_RETRY_BACKOFF` | float | Backoff multiplier | `2.0` |

### Provider API Keys

| Variable | Provider | Description |
|----------|----------|-------------|
| `ANTHROPIC_API_KEY` | Claude | Anthropic API key |
| `GEMINI_API_KEY` | Gemini | Google Gemini API key |
| `OPENAI_API_KEY` | Codex | OpenAI API key |

### Examples

```bash
# Basic environment setup
export CLAIF_DEFAULT_PROVIDER=gemini
export CLAIF_VERBOSE=true
export GEMINI_API_KEY=your_api_key_here

# Advanced configuration
export CLAIF_RETRY_COUNT=5
export CLAIF_RETRY_DELAY=2.0
export CLAIF_CACHE_TTL=7200
export CLAIF_SESSION_DIR=/custom/session/path
```

## Configuration Loading

### Load Process

```python
from claif.common.config import load_config

# Load with default behavior
config = load_config()

# Load with specific config file
config = load_config("/path/to/custom/config.json")
```

### Programmatic Access

```python
from claif.common.config import Config, ProviderConfig
from claif.common.types import Provider

# Create configuration programmatically
config = Config(
    default_provider=Provider.GEMINI,
    verbose=True,
    cache_enabled=False,
    providers={
        Provider.GEMINI: ProviderConfig(
            model="gemini-pro",
            timeout=60,
            extra={"auto_approve": True}
        )
    }
)
```

## CLI Configuration Commands

### View Configuration

```bash
# Show current configuration
claif config show

# Show specific provider configuration
claif config show --provider claude

# Validate configuration
claif config validate
```

### Modify Configuration

```bash
# Interactive configuration setup
claif config

# Set specific values
claif config set default_provider gemini
claif config set providers.claude.model claude-3-opus
claif config set verbose true

# Enable/disable providers
claif config enable claude
claif config disable codex

# Reset to defaults
claif config reset
```

### Configuration Management

```bash
# Export current configuration
claif config export > my-config.json

# Import configuration
claif config import my-config.json

# Show configuration file locations
claif config paths
```

## Provider-Specific Configuration

### Claude Provider

```json
{
  "providers": {
    "claude": {
      "model": "claude-3-sonnet-20240229",
      "api_key_env": "ANTHROPIC_API_KEY",
      "timeout": 120,
      "extra": {
        "session_dir": "~/.claif/claude_sessions",
        "auto_approve": false,
        "approval_strategy": "conservative",
        "max_session_size": 100,
        "enable_vision": true,
        "enable_tools": true
      }
    }
  }
}
```

### Gemini Provider

```json
{
  "providers": {
    "gemini": {
      "model": "gemini-pro",
      "api_key_env": "GEMINI_API_KEY",
      "timeout": 90,
      "extra": {
        "auto_approve": true,
        "context_length": 32000,
        "yes_mode": true,
        "cli_path": "gemini",
        "debug": false
      }
    }
  }
}
```

### Codex Provider

```json
{
  "providers": {
    "codex": {
      "model": "o4-mini",
      "api_key_env": "OPENAI_API_KEY",
      "timeout": 120,
      "extra": {
        "action_mode": "review",
        "working_dir": ".",
        "safe_mode": true,
        "auto_format": true,
        "backup_enabled": true
      }
    }
  }
}
```

## Advanced Configuration

### Environment Variable Substitution

Configuration files support environment variable substitution:

```json
{
  "providers": {
    "claude": {
      "api_key_env": "ANTHROPIC_API_KEY",
      "extra": {
        "session_dir": "${HOME}/.claif/sessions",
        "custom_endpoint": "${CLAUDE_ENDPOINT:-https://api.anthropic.com}"
      }
    }
  }
}
```

### Conditional Configuration

Use environment variables to enable conditional configuration:

```json
{
  "providers": {
    "claude": {
      "enabled": "${CLAUDE_ENABLED:-true}",
      "extra": {
        "debug": "${DEBUG_MODE:-false}",
        "timeout": "${CLAUDE_TIMEOUT:-120}"
      }
    }
  }
}
```

### Multi-Environment Setup

#### Development Configuration

```json
{
  "default_provider": "claude",
  "verbose": true,
  "cache_enabled": false,
  "retry_config": {
    "count": 1,
    "delay": 0.5
  },
  "providers": {
    "claude": {
      "extra": {
        "debug": true,
        "auto_approve": true
      }
    }
  }
}
```

#### Production Configuration

```json
{
  "default_provider": "claude",
  "verbose": false,
  "cache_enabled": true,
  "cache_ttl": 7200,
  "retry_config": {
    "count": 5,
    "delay": 2.0,
    "backoff": 2.0
  },
  "providers": {
    "claude": {
      "extra": {
        "auto_approve": false,
        "approval_strategy": "conservative"
      }
    }
  }
}
```

## Configuration Validation

### Built-in Validation

```python
from claif.common.config import load_config, validate_config

try:
    config = load_config()
    validate_config(config)
    print("Configuration is valid!")
except ConfigurationError as e:
    print(f"Configuration error: {e}")
```

### Custom Validation

```python
def validate_custom_config(config: Config) -> None:
    """Custom configuration validation."""
    
    # Ensure at least one provider is enabled
    enabled_providers = [
        p for p, cfg in config.providers.items() 
        if cfg.enabled
    ]
    if not enabled_providers:
        raise ConfigurationError("At least one provider must be enabled")
    
    # Validate cache TTL
    if config.cache_ttl <= 0:
        raise ConfigurationError("Cache TTL must be positive")
    
    # Validate session directory
    session_path = Path(config.session_dir)
    if not session_path.parent.exists():
        raise ConfigurationError(f"Session directory parent does not exist: {session_path.parent}")
```

## Configuration Schema

### JSON Schema

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "properties": {
    "default_provider": {
      "type": "string",
      "enum": ["claude", "gemini", "codex"]
    },
    "cache_enabled": {
      "type": "boolean"
    },
    "cache_ttl": {
      "type": "integer",
      "minimum": 1
    },
    "session_dir": {
      "type": "string"
    },
    "verbose": {
      "type": "boolean"
    },
    "output_format": {
      "type": "string",
      "enum": ["text", "json", "yaml"]
    },
    "retry_config": {
      "type": "object",
      "properties": {
        "count": {
          "type": "integer",
          "minimum": 0
        },
        "delay": {
          "type": "number",
          "minimum": 0
        },
        "backoff": {
          "type": "number",
          "minimum": 1
        }
      }
    },
    "providers": {
      "type": "object",
      "patternProperties": {
        "^(claude|gemini|codex)$": {
          "type": "object",
          "properties": {
            "enabled": {
              "type": "boolean"
            },
            "model": {
              "type": "string"
            },
            "api_key_env": {
              "type": "string"
            },
            "timeout": {
              "type": "integer",
              "minimum": 1
            },
            "extra": {
              "type": "object"
            }
          }
        }
      }
    }
  }
}
```

## Migration and Compatibility

### Version Migration

```python
def migrate_config_v1_to_v2(old_config: dict) -> dict:
    """Migrate configuration from v1 to v2 format."""
    
    new_config = old_config.copy()
    
    # Rename old keys
    if "default_model" in old_config:
        new_config["default_provider"] = old_config.pop("default_model")
    
    # Restructure provider configuration
    if "api_keys" in old_config:
        api_keys = old_config.pop("api_keys")
        new_config.setdefault("providers", {})
        
        for provider, api_key in api_keys.items():
            new_config["providers"].setdefault(provider, {})
            new_config["providers"][provider]["api_key_env"] = api_key
    
    return new_config
```

### Backward Compatibility

The configuration system maintains backward compatibility:

- Old configuration keys are automatically mapped to new ones
- Deprecated settings generate warnings but continue to work
- Migration happens transparently during config loading

## Best Practices

### 1. Security

```bash
# Store API keys in environment variables, not config files
export ANTHROPIC_API_KEY="your-secret-key"

# Use restrictive file permissions for config files
chmod 600 ~/.claif/config.json

# Avoid committing config files with secrets
echo "*.json" >> .gitignore
```

### 2. Organization

```bash
# Use different config files for different environments
claif --config dev-config.json query "test"
claif --config prod-config.json query "production query"

# Keep common settings in main config, specifics in environment
# Base: ~/.claif/config.json
# Dev: ./dev-config.json (extends base)
# Prod: ./prod-config.json (extends base)
```

### 3. Validation

```python
# Always validate configuration in production
try:
    config = load_config()
    validate_config(config)
except ConfigurationError as e:
    logger.error(f"Invalid configuration: {e}")
    sys.exit(1)
```

### 4. Documentation

```json
{
  "_comment": "This configuration is for development",
  "_version": "2.0",
  "_last_updated": "2024-01-15",
  
  "default_provider": "claude",
  "verbose": true
}
```

## Troubleshooting

### Common Issues

#### Configuration Not Found

```bash
# Check configuration file locations
claif config paths

# Verify file exists and is readable
ls -la ~/.claif/config.json
cat ~/.claif/config.json
```

#### Invalid JSON

```bash
# Validate JSON syntax
cat ~/.claif/config.json | python -m json.tool

# Common JSON errors:
# - Trailing commas
# - Unquoted keys
# - Single quotes instead of double quotes
```

#### Environment Variables Not Working

```bash
# Check environment variables
env | grep CLAIF
env | grep API_KEY

# Verify variable names (case sensitive)
echo $CLAIF_DEFAULT_PROVIDER
echo $ANTHROPIC_API_KEY
```

#### Permission Errors

```bash
# Fix config directory permissions
chmod 755 ~/.claif
chmod 644 ~/.claif/config.json

# Create config directory if missing
mkdir -p ~/.claif
```

## API Reference

### Functions

```python
def load_config(config_file: str | None = None) -> Config:
    """Load configuration from files and environment."""

def merge_config(base: Config, overrides: dict[str, Any]) -> Config:
    """Merge configuration overrides into base config."""

def load_env_config(config: Config) -> Config:
    """Load environment variable overrides."""

def save_config(config: Config, path: str | None = None) -> None:
    """Save configuration to file."""

def validate_config(config: Config) -> None:
    """Validate configuration structure and values."""
```

### Classes

```python
@dataclass
class Config:
    """Main configuration class."""

@dataclass  
class ProviderConfig:
    """Provider-specific configuration."""
```

The configuration system provides a robust foundation for managing Claif settings across different environments and use cases while maintaining security and flexibility.