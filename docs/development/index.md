---
layout: default
title: Development
nav_order: 7
has_children: true
---

# Developer Documentation

Resources for contributing to Claif and developing custom providers.

## Development Environment

### Setup Requirements
- Python 3.8+ (3.12+ recommended)
- uv package manager
- Git for version control
- Pre-commit hooks for code quality

### Local Development Setup
```bash
# Clone the repository
git clone https://github.com/twardoch/claif.git
cd claif

# Install development dependencies
uv pip install -e ".[dev]"

# Set up pre-commit hooks
pre-commit install

# Run tests
uvx hatch test
```

## Contributing Guidelines

### Code Standards
- **PEP 8** compliance with 120-character line limit
- **Type hints** for all public APIs
- **Docstrings** in imperative mood (PEP 257)
- **Modern Python** features (f-strings, pattern matching)
- **Loguru** for all logging needs

### Testing Requirements
- **80%+ test coverage** for all new code
- **Unit tests** for individual components
- **Integration tests** for provider interactions
- **Mocked dependencies** for reliable testing
- **Cross-platform** compatibility verified

### Code Quality Tools
```bash
# Format code
fd -e py -x ruff format {}

# Lint code
fd -e py -x ruff check --fix {}

# Type checking
mypy src/

# Run all checks
pre-commit run --all-files
```

## Architecture Principles

### Core Design Patterns
- **Plugin Architecture** - Modular provider system
- **Abstract Base Classes** - Consistent provider interface
- **Async-First** - Non-blocking operations by default
- **Configuration-Driven** - TOML-based settings
- **Error Hierarchy** - Structured exception handling

### Provider Development
- **Minimal Interface** - Implement only required methods
- **Error Handling** - Map provider errors to Claif types
- **Testing Strategy** - Mock external dependencies
- **Documentation** - Comprehensive usage examples

## Release Process

### Versioning Strategy
- **Semantic Versioning** (MAJOR.MINOR.PATCH)
- **Coordinated Releases** across all packages
- **Dependency Management** between core and providers
- **Migration Guides** for breaking changes

### Release Workflow
1. **Test all providers** in clean environments
2. **Update version numbers** in all packages
3. **Generate changelogs** from commit history
4. **Create release tags** with v{version} format
5. **Publish to PyPI** in dependency order

## Navigation

- [Setup Guide](setup.md) - Development environment
- [Contributing](contributing.md) - Contribution guidelines
- [Architecture](architecture.md) - Design decisions
- [Provider Development](providers.md) - Creating providers
- [Release Process](releases.md) - Version management
- [Testing Guide](testing.md) - Testing strategies