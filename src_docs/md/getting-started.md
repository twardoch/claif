# Getting Started

Welcome to Claif! This guide will help you get up and running with the Command-Line Artificial Intelligence Framework in just a few minutes.

## What You'll Learn

- How to install Claif and provider packages
- Basic configuration setup
- Your first AI interaction
- Essential commands and workflows

## Prerequisites

- **Python 3.12+** - Claif requires modern Python
- **pip** or **uv** - Package manager (uv recommended)
- **API Keys** - For your chosen AI providers

## Quick Installation

### 1. Install the Core Framework

=== "Using uv (Recommended)"
    ```bash
    uv pip install claif
    ```

=== "Using pip"
    ```bash
    pip install claif
    ```

### 2. Install Provider Packages

Choose one or more providers to install:

=== "Claude (Anthropic)"
    ```bash
    uv pip install claif_cla
    ```

=== "Gemini (Google)"
    ```bash
    uv pip install claif_gem
    ```

=== "Codex (OpenAI)"
    ```bash
    uv pip install claif_cod
    ```

=== "All Providers"
    ```bash
    uv pip install claif claif_cla claif_gem claif_cod
    ```

### 3. Verify Installation

```bash
claif --version
claif providers list
```

You should see output showing the installed version and available providers.

## Initial Configuration

### Set Your Default Provider

```bash
# Choose your preferred provider
claif config set provider claude  # or gemini, codex
```

### Configure API Keys

=== "Claude"
    ```bash
    claif config set claude.api_key YOUR_ANTHROPIC_API_KEY
    ```

=== "Gemini"
    ```bash
    claif config set gemini.api_key YOUR_GOOGLE_API_KEY
    ```

=== "Codex"
    ```bash
    claif config set codex.api_key YOUR_OPENAI_API_KEY
    ```

!!! tip "Environment Variables"
    You can also set API keys via environment variables:
    ```bash
    export ANTHROPIC_API_KEY="your-key"
    export GOOGLE_API_KEY="your-key"
    export OPENAI_API_KEY="your-key"
    ```

### View Current Configuration

```bash
claif config show
```

## Your First AI Interaction

Now that everything is set up, let's try your first query:

```bash
claif ask "What is the difference between AI and machine learning?"
```

You should see a detailed response from your configured AI provider!

## Essential Commands

### Basic Queries

```bash
# Simple question
claif ask "How do I sort a list in Python?"

# Code generation
claif code "Write a function to reverse a string"

# File analysis
claif analyze myfile.py "Explain what this code does"
```

### Interactive Mode

For longer conversations:

```bash
claif chat --interactive
```

This starts an interactive session where you can have back-and-forth conversations.

### Provider Management

```bash
# List available providers
claif providers list

# Switch providers temporarily
claif ask --provider gemini "What's the weather like?"

# Check provider status
claif providers status
```

### Configuration Management

```bash
# View all settings
claif config show

# Set specific values
claif config set timeout 120
claif config set output.format json

# Reset to defaults
claif config reset
```

## Common Workflows

### Workflow 1: Code Review

```bash
# Analyze a Python file
claif analyze src/main.py "Review this code for potential issues"

# Get suggestions for improvement
claif code "Optimize this function" < utils.py
```

### Workflow 2: Documentation

```bash
# Generate docstrings
claif code "Add docstrings to this Python class" < myclass.py

# Create README content
claif ask "Write a README for a Python CLI tool that processes CSV files"
```

### Workflow 3: Learning

```bash
# Explain complex topics
claif ask "Explain async/await in Python with examples"

# Get code examples
claif code "Show me how to use context managers in Python"
```

## Next Steps

Now that you have Claif running:

1. **Explore Providers** - Learn about different AI providers in [Providers](providers.md)
2. **Advanced Configuration** - Customize Claif in [Configuration](configuration.md)
3. **CLI Mastery** - Master all commands in [CLI Usage](cli-usage.md)
4. **Python API** - Use Claif programmatically via [API Reference](api-reference.md)

## Troubleshooting

Having issues? Check these common solutions:

### Command Not Found

```bash
# Make sure claif is in your PATH
which claif

# If using virtual environments, ensure it's activated
source venv/bin/activate  # or your venv activation command
```

### Provider Not Available

```bash
# Check if provider package is installed
pip list | grep claif

# Install missing provider
uv pip install claif_cla  # example for Claude
```

### API Key Issues

```bash
# Verify configuration
claif config show

# Test with explicit provider
claif ask --provider claude "test" --debug
```

For more detailed troubleshooting, see [Troubleshooting](troubleshooting.md).

!!! success "You're Ready!"
    Congratulations! You now have Claif configured and ready to use. Start exploring the power of unified AI interactions from your command line.