---
layout: default
title: API Reference
nav_order: 5
has_children: true
---

# API Reference

Complete reference documentation for the Claif API, including all public classes, methods, and utilities.

## Core API

### Client Classes
- **`ClaifClient`** - Main client for interacting with providers
- **`AsyncClient`** - Async interface for concurrent operations
- **`Provider`** - Abstract base class for all providers

### Configuration
- **`Config`** - Main configuration class
- **`ClaifOptions`** - Query options and settings
- **`ProviderOptions`** - Provider-specific configuration

### Message Types
- **`Message`** - Base message type
- **`TextBlock`** - Text content block
- **`ToolUseBlock`** - Tool usage block
- **`ContentBlock`** - Generic content block

## CLI Interface

### Commands
- **`claif query`** - Send queries to providers
- **`claif config`** - Manage configuration
- **`claif list`** - List available providers
- **`claif server`** - Start MCP server

### Options
- **`--provider`** - Select specific provider
- **`--verbose`** - Enable verbose logging
- **`--config`** - Specify config file
- **`--timeout`** - Set request timeout

## Utility Functions

### Formatting
- **`format_response()`** - Format provider responses
- **`format_metrics()`** - Format performance metrics

### Error Handling
- **`ClaifError`** - Base exception class
- **`ProviderError`** - Provider-specific errors
- **`ConfigurationError`** - Configuration errors
- **`ValidationError`** - Input validation errors

## MCP Server

### FastMCP Integration
- **`start_mcp_server()`** - Start the MCP server
- **`ToolHandler`** - Handle MCP tool requests
- **`ServerConfig`** - MCP server configuration

## Navigation

- [Core Classes](core.md) - Main API classes and methods
- [CLI Reference](cli.md) - Command-line interface
- [Error Types](errors.md) - Exception hierarchy
- [Utilities](utilities.md) - Helper functions and tools
- [MCP Server](mcp.md) - Model Context Protocol server