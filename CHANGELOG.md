# Changelog

All notable changes to the Claif (Command-Line Artificial Intelligence Framework) project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased] - 2025-01-03

### Fixed
- **Import Resolution**: Corrected numerous `ModuleNotFoundError` and `NameError` issues by adjusting import statements from absolute to relative paths across core framework and provider integration modules. This includes `claif/__init__.py`, `claif/common/__init__.py`, `claif/common/config.py`, `claif/common/utils.py`, `claif/cli.py`, `claif/client.py`, `claif/providers/__init__.py`, `claif/providers/gemini.py`, `claif/providers/claude.py`, `claif/providers/codex.py`, and `claif/server.py`.
- **Gemini Provider Hanging Issue**: Resolved the issue where the Gemini provider would hang indefinitely by refactoring the subprocess communication in `claif_gem/src/claif_gem/transport.py` to use `asyncio.subprocess.communicate()` for more reliable output capture.
- **Logging Levels**: Adjusted log levels for clarity and reduced verbosity:
  - Changed "Using provider: {provider}" messages from INFO to DEBUG in `claif/src/claif/client.py`.
  - Changed "Error during disconnect" messages from WARNING to DEBUG in `claif_gem/src/claif_gem/transport.py`.
- **Missing Imports**: Added missing `BaseModel` and `FastMCP` imports to `claif/src/claif/server.py` to resolve `NameError`.
- **Provider Query Imports**: Corrected the import of `query` functions within `claif/src/claif/providers/gemini.py`, `claif/src/claif/providers/claude.py`, and `claif/src/claif/providers/codex.py` to correctly reference the `query` function from their respective provider packages (e.g., `claif_gem.query` to `claif_gem.claif_gem.query`).

### Added
- **Core Framework Support for Retry Logic**: Added `no_retry` field to `ClaifOptions`
  - Enables providers to respect --no_retry flag from CLI
  - Provides unified retry configuration across all providers
- **Test Infrastructure**: Finalized pytest environment setup
  - Fixed xdist/coverage plugin conflicts
  - Achieved 80%+ test coverage target
  - All tests pass reliably without flaky failures

### Changed
- Updated `ClaifOptions` dataclass to include retry configuration support
- All providers now have consistent retry behavior configuration
- **Message Class Behavior**: Auto-converts string content to TextBlock lists
  - `Message` class now automatically wraps string content into `[TextBlock(text=content)]`
  - This ensures consistency across the framework but may break tests expecting string content

### Verified
- Provider discovery and routing handle all edge cases
- Provider integration tests pass with actual provider packages


## [1.0.9] - 2025-01-02

### Added
- **Comprehensive Test Suite**: Added pytest test structure with 80%+ coverage target
  - Created `pytest.ini` with coverage configuration and test markers
  - Created `.coveragerc` for detailed coverage reporting
  - Added test fixtures and mock providers in `conftest.py`
  - Added unit tests for all core modules:
    - `test_types.py` - Tests for data models (Message, ClaifOptions, ClaifResponse)
    - `test_errors.py` - Tests for error handling hierarchy
    - `test_config.py` - Tests for configuration management and environment variables
    - `test_utils.py` - Tests for utility functions and formatters
    - `test_install.py` - Tests for installation functionality
    - `test_client.py` - Tests for client module with auto-install features
    - `test_cli.py` - Tests for CLI functionality and commands
    - `test_server.py` - Tests for MCP server implementation
    - `test_providers.py` - Tests for provider implementations

### Changed
- Updated test imports to match actual implementation (fixed API mismatches)
- Mocked all external dependencies to ensure tests run without real CLI tools
- Implemented comprehensive async test patterns for provider interactions

### Fixed
- Fixed test structure to match actual codebase API (Message vs ClaifMessage, etc.)
- Resolved import errors in test files
- Updated mock implementations to match real provider behavior

### Technical Improvements
- Test coverage includes all major functionality areas
- Proper async/await test patterns for async operations
- Comprehensive mocking of subprocess calls and file operations
- Tests are isolated and can run without external dependencies

## [1.0.8] - 2025-01-02

### Added
- **Auto-Install Functionality (Issue #201)**: Added comprehensive auto-install support for all provider CLI tools
- Added `InstallError` and `find_executable` to common module exports
- Added `install_provider` and `uninstall_provider` functions
- Added terminal opening utilities for post-install configuration prompts
- Added auto-install exception handling in main client for missing CLI tools

### Changed
- **Provider Integration**: All three providers (claude, gemini, codex) now use real CLI tools instead of mock implementations
- Updated codex provider to use real `@openai/codex` npm package instead of mock
- Enhanced provider discovery to include auto-install capabilities
- Improved error handling with automatic retry after successful CLI installation

### Fixed
- Fixed import paths from `claif.common.*` to relative imports (`.config`, `.errors`, etc.)
- Fixed module import issues across all common modules and providers
- Resolved `ImportError` issues preventing package from loading
- Fixed provider initialization after auto-install

### Technical Improvements
- Streamlined import organization across all modules
- Enhanced error hierarchy with more specific error types
- Improved cross-platform compatibility for CLI tool detection
- Added robust subprocess management for CLI tool installation

## [1.0.7] - 2025-01-02

### Added
- Added comprehensive install functionality with bun bundling support
- Added npm package installation utilities
- Added cross-platform CLI tool detection

### Changed
- Enhanced common module with install utilities and error types
- Improved provider package integration architecture

## [1.0.6] - 2025-01-01

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

## [1.0.5] - 2025-01-01

[Previous version - no changelog entry]

## [1.0.4] - 2025-01-01

[Previous version - no changelog entry]

## [1.0.3] - 2025-01-01

[Previous version - no changelog entry]

## [1.0.2] - 2025-01-01

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
- Initial release of Claif core framework
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