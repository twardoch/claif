---
layout: default
title: Home
nav_order: 1
has_children: true
---

# Claif - Command-Line Artificial Intelligence Framework

Welcome to the comprehensive documentation for Claif, the Command-Line Artificial Intelligence Framework. Claif provides a unified, plugin-based interface for interacting with various large language models (LLMs) directly from your terminal.

## What is Claif?

Claif is a modern, async-first framework that abstracts the complexity of different LLM providers behind a consistent interface. Whether you're using Anthropic's Claude, Google's Gemini, or OpenAI's models, Claif provides the same intuitive command-line and programmatic interface.

### Key Features

- **Unified Interface** - Same commands and API across all providers
- **Plugin Architecture** - Automatic provider discovery and loading
- **Async Operations** - Non-blocking, concurrent requests
- **Type Safety** - Full type hints and validation
- **Rich Configuration** - TOML-based configuration with environment variable support
- **Comprehensive Logging** - Structured logging with Loguru
- **MCP Server** - Model Context Protocol server integration
- **Cross-Platform** - Windows, macOS, and Linux support

## Quick Start

```bash
# Install Claif and a provider
uv pip install claif claif_gem

# Configure your API keys
claif config

# Make your first query
claif query "What is the meaning of life?" --provider gemini
```

## Documentation Sections

### [Getting Started](/getting-started/)
Essential setup and first steps:
- Installation instructions for all platforms
- Configuration and API key setup
- Basic usage examples
- Provider selection

### [Core Framework](/core/)
Deep dive into Claif's architecture:
- Plugin system and provider discovery
- Configuration management
- Error handling and logging
- Type system and async patterns

### [Provider Packages](/providers/)
Official provider integrations:
- **[`claif_cla`](/providers/claude/)** - Anthropic Claude with session management
- **[`claif_cod`](/providers/codex/)** - OpenAI Codex for code generation
- **[`claif_gem`](/providers/gemini/)** - Google Gemini CLI integration

### [API Reference](/api/)
Complete API documentation:
- Core classes and methods
- CLI command reference
- Error types and utilities
- MCP server interface

### [User Guides](/guides/)
Comprehensive usage guides:
- Installation and configuration
- CLI usage patterns
- Programmatic integration
- Migration between versions

### [Development](/development/)
Contributing and extending Claif:
- Development environment setup
- Contributing guidelines
- Architecture principles
- Custom provider development

### [Examples & Tutorials](/examples/)
Practical examples and tutorials:
- Basic usage patterns
- Advanced workflows
- Integration examples
- Provider-specific features

### [Troubleshooting](/troubleshooting/)
Common issues and solutions:
- Installation problems
- Configuration errors
- Provider-specific issues
- Performance optimization

## Project Structure

Claif consists of four main repositories:

- **[`claif`](https://github.com/twardoch/claif/)** - Core framework and provider abstraction
- **[`claif_cla`](https://github.com/twardoch/claif_cla/)** - Anthropic Claude provider 
- **[`claif_cod`](https://github.com/twardoch/claif_cod/)** - OpenAI Codex provider
- **[`claif_gem`](https://github.com/twardoch/claif_gem/)** - Google Gemini provider

## Community and Support

- **GitHub Issues** - Report bugs and request features
- **Documentation** - This comprehensive guide
- **Examples** - Real-world usage patterns
- **Contributing** - Help improve Claif

Ready to get started? Head to the [Getting Started](/getting-started/) guide!
