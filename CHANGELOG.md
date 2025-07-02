# Changelog

All notable changes to theClaif (Command-Line Artificial Intelligence Framework) project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.6] - 2025-07-01

### Added
- Added new exports to common module: ClaifOptions, ClaifResponse, ClaifTimeoutError, MessageRole, ResponseMetrics, SessionError, TransportError, ValidationError
- Added save_config function export from config module
- Added format_metrics utility function
- Added find_executable and InstallError imports to common utils

### Changed
- Enhanced error hierarchy with more specific error types
- Improved imports organization in all provider modules (claude.py, codex.py, gemini.py)
- Updated client.py to use enhanced imports
- Fixed import paths for better module organization
- Enhanced server.py imports and error handling

### Fixed
- Removed empty src/__init__.py file
- Fixed import inconsistencies across modules
- Improved type exports for better API consistency

### Removed
- Removed duplicate imports and unnecessary code

## [1.0.5] - 2025-07-01

[Previous version - no changelog entry]

## [1.0.4] - 2025-07-01

[Previous version - no changelog entry]

## [1.0.3] - 2025-07-01

[Previous version - no changelog entry]

## [1.0.2] - 2025-07-01

### Changed
- Reduced log noise by changing provider selection logs from INFO to DEBUG level
- "Using provider: {provider}" messages now only appear in debug mode
- "Randomly selected provider: {provider}" messages now only appear in debug mode

### Improved
- Cleaner command output with minimal logging unless verbose mode is enabled
- Better user experience with less noisy console output

## [1.0.1] - 2025-01-01

### Changed
- Updated all logging implementation to use loguru instead of custom logger wrapper
- Simplified logging configuration in CLI with automatic level adjustment based on verbose flag
- Added debug logging for configuration display and updates
- Added info logging for configuration saves
- Added warning logging for unavailable interactive mode

### Fixed
- Removed unnecessary imports and simplified logger initialization
- Fixed import ordering to follow Python conventions

## [1.0.0] - 2025-01-01

### Added
- Initial release ofClaif core framework
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