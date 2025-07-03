---
layout: default
title: Core Framework
nav_order: 3
has_children: true
---

# Core Framework Documentation

The Claif core framework provides the foundation for all provider integrations and user interactions. This section covers the architectural principles, design patterns, and core components that make Claif work.

## Architecture Overview

Claif follows a plugin-based architecture where:

- **Core Framework** (`claif`) provides the unified interface and common functionality
- **Provider Packages** (`claif_cla`, `claif_cod`, `claif_gem`) implement specific LLM integrations
- **Plugin Discovery** automatically detects and loads available providers
- **Async Client** handles concurrent requests and provider routing

## Key Components

### Provider System
- **Abstract Base Provider** - Defines the interface all providers must implement
- **Plugin Discovery** - Automatically finds and registers installed providers
- **Provider Registry** - Manages available providers and their capabilities

### Configuration System
- **TOML Configuration** - Human-readable configuration files
- **Environment Variables** - Runtime configuration and API keys
- **Default Values** - Sensible defaults for all settings

### Error Handling
- **Error Hierarchy** - Structured error types for different failure modes
- **Recovery Strategies** - Automatic retries and fallback mechanisms
- **Logging Integration** - Comprehensive logging with Loguru

### Type System
- **Message Types** - Unified message format across all providers
- **Options Classes** - Type-safe configuration objects
- **Response Formats** - Consistent response structures

## Navigation

- [Architecture](architecture.md) - Detailed system design and patterns
- [Provider Interface](provider-interface.md) - How to implement providers
- [Configuration](configuration.md) - Configuration system details
- [Error Handling](error-handling.md) - Error types and recovery
- [Types](types.md) - Type system and message formats
- [Testing](testing.md) - Testing framework and patterns