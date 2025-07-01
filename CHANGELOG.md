# Changelog

All notable changes to the CLAIF (Command-Line Artificial Intelligence Framework) project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2025-01-01

### Added
- Initial release of CLAIF core framework
- Unified interface for multiple AI providers (Claude, Gemini, Codex)
- Fire-based CLI with rich terminal output
- Async Python API for programmatic access
- MCP (Model Context Protocol) server for tool integration
- Comprehensive configuration system with hierarchical loading
- Plugin-based provider discovery using Python entry points
- Parallel querying across all providers
- Random provider selection
- Response streaming support
- Provider health checks
- Session management foundation
- Type hints throughout the codebase
- Comprehensive error handling hierarchy
- Logging with Loguru integration
- Response formatting utilities
- Progress indicators for long operations

### Project Structure
- `claif.common`: Shared types, configuration, errors, and utilities
- `claif.providers`: Provider interfaces for Claude, Gemini, and Codex
- `claif.client`: Unified client implementation
- `claif.cli`: Fire-based command-line interface
- `claif.server`: FastMCP server implementation

### Dependencies
- Python 3.10+ support
- fire for CLI framework
- rich for terminal output
- fastmcp for MCP server
- pydantic for data validation
- uvicorn for ASGI server

### Provider Packages
This core framework is designed to work with:
- `claif_cla`: Claude provider implementation
- `claif_gem`: Gemini provider implementation
- `claif_cod`: Codex provider implementation

### Notes
- This is the foundational release focusing on core framework functionality
- Provider packages must be installed separately
- Configuration can be set via files, environment variables, or CLI arguments