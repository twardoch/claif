---
layout: default
title: User Guides
nav_order: 6
has_children: true
---

# User Guides

Comprehensive guides for installing, configuring, and using Claif effectively.

## Getting Started

### Quick Start
Get up and running with Claif in minutes:

1. **Install Claif**
   ```bash
   uv pip install claif
   ```

2. **Install a Provider**
   ```bash
   uv pip install claif_gem  # or claif_cla, claif_cod
   ```

3. **Configure API Keys**
   ```bash
   claif config
   ```

4. **Make Your First Query**
   ```bash
   claif query "What is 2+2?" --provider gemini
   ```

## Essential Guides

### [Installation Guide](installation.md)
Complete installation instructions for all platforms:
- Python environment setup
- Package installation with uv/pip
- Provider package installation
- System requirements and dependencies

### [Configuration Guide](configuration.md)
Comprehensive configuration setup:
- API key management
- Provider-specific settings
- Configuration file formats (TOML)
- Environment variables
- Advanced configuration options

### [CLI Usage Guide](cli.md)
Master the command-line interface:
- All available commands and options
- Query formatting and examples
- Provider selection strategies
- Verbose output and debugging
- Batch operations and scripting

### [Integration Guide](integration.md)
Use Claif programmatically:
- Python API usage
- Async operations
- Error handling patterns
- Custom workflows
- CI/CD integration

### [Migration Guide](migration.md)
Upgrade between versions:
- Breaking changes by version
- Configuration migration
- Provider updates
- Deprecation notices

## Advanced Topics

### Performance Optimization
- Query optimization strategies
- Concurrent provider usage
- Caching and persistence
- Resource management

### Security Best Practices
- API key protection
- Secure configuration
- Network security
- Input validation

### Troubleshooting
- Common error resolution
- Debug mode usage
- Log analysis
- Performance debugging

## Navigation

- [Installation](installation.md) - Setup and installation
- [Configuration](configuration.md) - API keys and settings
- [CLI Usage](cli.md) - Command-line interface
- [Integration](integration.md) - Programmatic usage
- [Migration](migration.md) - Version upgrades