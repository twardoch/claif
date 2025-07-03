---
layout: default
title: Getting Started
nav_order: 2
parent: Home
---

# Getting Started

This comprehensive guide will walk you through installing, configuring, and using Claif for the first time.

## Prerequisites

### System Requirements
- **Python 3.8+** (Python 3.12+ recommended for best performance)
- **Operating System**: Windows 10+, macOS 10.14+, or Linux (Ubuntu 18.04+)
- **Internet connection** for API access and package installation

### Recommended Tools
- **[uv](https://github.com/astral-sh/uv)** - Fast Python package manager (recommended)
- **Git** - For accessing examples and contributing
- **Terminal/Command Prompt** - For CLI usage

## Installation

### Option 1: Using uv (Recommended)

```bash
# Install uv if you don't have it
curl -LsSf https://astral.sh/uv/install.sh | sh

# Install Claif core framework
uv pip install claif

# Install one or more provider packages
uv pip install claif_gem    # Google Gemini
uv pip install claif_cla    # Anthropic Claude  
uv pip install claif_cod    # OpenAI Codex
```

### Option 2: Using pip

```bash
# Install Claif core framework
pip install claif

# Install provider packages
pip install claif_gem claif_cla claif_cod
```

### Verify Installation

```bash
# Check Claif version
claif --version

# List available providers
claif list

# Expected output:
# Available providers:
# - gemini (claif_gem v1.0.0)
# - claude (claif_cla v1.0.0) 
# - codex (claif_cod v1.0.0)
```

## Initial Configuration

### Interactive Setup

The easiest way to configure Claif is using the interactive setup:

```bash
claif config
```

This will prompt you for:
- API keys for each installed provider
- Default provider preference
- Basic settings like timeout and logging level

### Manual Configuration

Create the configuration file at `~/.claif/config.toml`:

```toml
# ~/.claif/config.toml
[general]
default_provider = "gemini"
timeout = 120
log_level = "INFO"

[providers.gemini]
api_key = "your_gemini_api_key_here"
model = "gemini-pro"

[providers.claude]
api_key = "your_anthropic_api_key_here"
model = "claude-3-sonnet-20240229"

[providers.codex]
api_key = "your_openai_api_key_here"
model = "gpt-4"
```

### Environment Variables

You can also set API keys using environment variables:

```bash
# Add to your shell profile (.bashrc, .zshrc, etc.)
export GOOGLE_API_KEY="your_gemini_api_key"
export ANTHROPIC_API_KEY="your_claude_api_key"
export OPENAI_API_KEY="your_codex_api_key"
```

## Getting API Keys

### Google Gemini
1. Visit [Google AI Studio](https://makersuite.google.com/)
2. Create an account or sign in
3. Generate an API key
4. Copy the key to your configuration

### Anthropic Claude
1. Visit [Anthropic Console](https://console.anthropic.com/)
2. Create an account and verify your email
3. Navigate to API Keys section
4. Create a new API key
5. Copy the key to your configuration

### OpenAI (for Codex)
1. Visit [OpenAI Platform](https://platform.openai.com/)
2. Create an account and add billing information
3. Go to API Keys section
4. Create a new secret key
5. Copy the key to your configuration

## First Query

Once configured, test your setup with a simple query:

```bash
# Use default provider
claif query "What is 2 + 2?"

# Use specific provider
claif query "Explain Python decorators" --provider claude

# Verbose output for debugging
claif query "Hello world" --provider gemini --verbose
```

Expected output:
```
2 + 2 equals 4.
```

## Basic Usage Patterns

### Simple Queries
```bash
# Quick calculation
claif query "What is 15% of 200?"

# Code explanation
claif query "Explain this Python code: def fibonacci(n): return n if n <= 1 else fibonacci(n-1) + fibonacci(n-2)"

# Creative writing
claif query "Write a haiku about programming"
```

### Provider Selection
```bash
# Let Claif choose the best provider
claif query "Analyze this data"

# Force specific provider
claif query "Generate Python code" --provider codex

# Compare responses from multiple providers
claif query-all "What is machine learning?"
```

### Options and Flags
```bash
# Increase timeout for long requests
claif query "Long analysis task" --timeout 300

# Save output to file
claif query "Generate report" --output report.md

# Enable debug logging
claif query "Test query" --verbose --log-level DEBUG
```

## Configuration Management

### View Current Configuration
```bash
# Show all settings
claif config show

# Show specific provider settings
claif config show --provider gemini

# Validate configuration
claif config validate
```

### Update Configuration
```bash
# Update default provider
claif config set general.default_provider claude

# Update API key
claif config set providers.gemini.api_key "new_key_here"

# Reset to defaults
claif config reset
```

## Common Issues and Solutions

### No Providers Found
```
Error: No providers found. Please install a provider package.
```

**Solution:**
```bash
uv pip install claif_gem  # or claif_cla, claif_cod
claif list  # Verify installation
```

### API Key Errors
```
ConfigurationError: API key not found for provider 'gemini'
```

**Solutions:**
1. Run `claif config` to set up API keys
2. Check environment variables: `echo $GOOGLE_API_KEY`
3. Verify config file: `cat ~/.claif/config.toml`

### Permission Errors
```
PermissionError: Cannot write to ~/.claif/config.toml
```

**Solutions:**
```bash
# Fix permissions
chmod 755 ~/.claif
chmod 644 ~/.claif/config.toml

# Or recreate directory
rm -rf ~/.claif && claif config
```

## Next Steps

### Learn More
- **[User Guides](/guides/)** - Comprehensive usage documentation
- **[Provider Documentation](/providers/)** - Provider-specific features
- **[Examples](/examples/)** - Real-world usage patterns
- **[API Reference](/api/)** - Complete API documentation

### Advanced Usage
- **Configuration**: Learn about advanced configuration options
- **Scripting**: Use Claif in automation and CI/CD
- **Programming**: Use the Python API programmatically
- **Custom Providers**: Create your own provider plugins

### Get Help
- **[Troubleshooting](/troubleshooting/)** - Common issues and solutions
- **GitHub Issues** - Report bugs and request features
- **Documentation** - This comprehensive guide

Ready to dive deeper? Check out the [User Guides](/guides/) for comprehensive usage patterns!
