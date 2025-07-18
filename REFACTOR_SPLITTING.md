# Claif Source File Refactoring Plan

This document provides a detailed analysis and refactoring plan for the largest source files in the claif project to improve maintainability, readability, and separation of concerns.

## 1. ./src/claif/cli.py (27 KB) - CLI Interface

### Current Structure Analysis

**Main Responsibilities:**
- Fire-based CLI interface (`ClaifCLI` class)
- Command handlers for various operations (query, stream, parallel, etc.)
- Provider management commands
- Installation/uninstallation commands
- Configuration management commands
- Server management
- Status reporting

**Key Components:**
- `ClaifCLI` class (lines 32-735): Monolithic class containing all CLI commands
- Main entry point (lines 737-740)

### Proposed Split Structure

```
src/claif/cli/
├── __init__.py              # Export main CLI class and entry point
├── base.py                  # ClaifCLI base class with initialization
├── commands/
│   ├── __init__.py
│   ├── query.py            # Query-related commands (query, stream, random, parallel)
│   ├── providers.py        # Provider management commands (list, status)
│   ├── config.py           # Configuration commands (show, set, save)
│   ├── install.py          # Installation commands (install, uninstall, status)
│   ├── session.py          # Session management command
│   └── server.py           # Server command
└── utils.py                # CLI-specific utilities
```

**Refactoring Details:**

1. **cli/base.py** (~50 lines)
   - `ClaifCLI.__init__` method
   - Base configuration and logger setup

2. **cli/commands/query.py** (~350 lines)
   - `query()` method (lines 46-130)
   - `stream()` method (lines 145-188)
   - `_stream_async()` helper (lines 189-208)
   - `random()` method (lines 209-256)
   - `parallel()` method (lines 258-324)
   - `_parallel_query()` helper (lines 320-324)
   - `_query_async()` helper (lines 131-136)
   - `_query_async_with_rotation()` helper (lines 138-143)

3. **cli/commands/providers.py** (~70 lines)
   - `providers()` method (lines 326-392)
   - Provider health check logic

4. **cli/commands/config.py** (~60 lines)
   - `config()` method (lines 420-475)

5. **cli/commands/install.py** (~180 lines)
   - `install()` method (lines 512-593)
   - `uninstall()` method (lines 594-668)
   - `status()` method (lines 669-735)

6. **cli/commands/session.py** (~30 lines)
   - `session()` method (lines 476-511)

7. **cli/commands/server.py** (~25 lines)
   - `server()` method (lines 393-418)

**Dependencies to Extract:**
- Console instance and formatting utilities can be shared via cli/utils.py

## 2. ./src/claif/common/install.py (19 KB) - Installation Utilities

### Current Structure Analysis

**Main Responsibilities:**
- npm package installation via bun
- Executable bundling
- Installation directory management
- Provider installation/uninstallation
- Wrapper script creation
- Claude-specific bundling with yoga.wasm

**Key Components:**
- Directory management functions (lines 22-89)
- npm installation functions (lines 91-136)
- Bundling functions (lines 138-187, 395-428)
- Installation functions (lines 189-245, 334-374, 461-512)
- Uninstallation functions (lines 247-277, 376-393)
- Provider-specific functions (lines 514-592)
- Executable finding logic (lines 279-332)

### Proposed Split Structure

```
src/claif/common/install/
├── __init__.py              # Export main functions
├── directories.py           # Directory management utilities
├── npm.py                   # npm/bun package management
├── bundling.py              # Executable bundling logic
├── executable.py            # Executable installation/management
├── providers.py             # Provider-specific installation logic
└── wrapper.py               # Wrapper script generation
```

**Refactoring Details:**

1. **install/directories.py** (~70 lines)
   - `get_install_dir()` (lines 22-28)
   - `ensure_install_dir()` (lines 30-35)
   - `get_install_location()` (lines 71-89)

2. **install/npm.py** (~120 lines)
   - `check_bun_available()` (lines 37-40)
   - `ensure_bun_installed()` (lines 42-69)
   - `install_npm_package()` (lines 91-116)
   - `install_npm_package_with_bun()` (lines 118-136)

3. **install/bundling.py** (~100 lines)
   - `bundle_executable()` (lines 138-187)
   - `bundle_claude()` (lines 395-428)

4. **install/executable.py** (~180 lines)
   - `install_bundled_executable()` (lines 189-245)
   - `uninstall_bundled_executable()` (lines 247-277)
   - `find_executable()` (lines 279-332)
   - `install_provider()` (lines 334-374)
   - `uninstall_provider()` (lines 376-393)

5. **install/wrapper.py** (~30 lines)
   - `create_wrapper_script()` (lines 430-459)

6. **install/providers.py** (~140 lines)
   - `install_claude()` (lines 461-496)
   - `install_gemini()` (lines 498-504)
   - `install_codex()` (lines 506-512)
   - `install_providers()` (lines 514-552)
   - `uninstall_providers()` (lines 554-592)

## 3. ./src/claif/common/utils.py (17 KB) - Utility Functions

### Current Structure Analysis

**Main Responsibilities:**
- Console output formatting and theming
- Response and metrics formatting
- Directory and path management
- Progress bar creation
- Text utilities
- Content block parsing
- Platform-specific terminal operations
- Tool configuration prompts
- Image processing

**Key Components:**
- Console theme and print functions (lines 21-57)
- Response formatting (lines 62-104)
- Message/block conversion (lines 106-145)
- Metrics formatting (lines 147-172)
- Directory utilities (lines 191-338)
- Terminal operations (lines 340-402)
- Configuration prompts (lines 403-433)
- Image processing (lines 435-480)

### Proposed Split Structure

```
src/claif/common/utils/
├── __init__.py              # Export commonly used utilities
├── console.py               # Console output and formatting
├── formatting.py            # Response and metrics formatting
├── paths.py                 # Directory and path management
├── terminal.py              # Terminal and platform-specific operations
├── prompts.py               # User interaction and prompts
└── media.py                 # Image and media processing
```

**Refactoring Details:**

1. **utils/console.py** (~80 lines)
   - Theme definition (lines 22-25)
   - Console instance (line 25)
   - Print functions (lines 28-57)
   - Progress bar creation (lines 174-188)

2. **utils/formatting.py** (~140 lines)
   - `format_response()` (lines 62-104)
   - `message_to_dict()` (lines 106-125)
   - `block_to_dict()` (lines 127-145)
   - `format_metrics()` (lines 147-172)
   - `truncate_text()` (lines 213-228)
   - `parse_content_blocks()` (lines 230-263)

3. **utils/paths.py** (~80 lines)
   - `ensure_directory()` (lines 191-201)
   - `timestamp()` (lines 203-210)
   - `get_claif_data_dir()` (lines 266-278)
   - `get_claif_bin_path()` (lines 281-293)
   - `inject_claif_bin_to_path()` (lines 295-319)
   - `get_install_location()` (lines 322-338)

4. **utils/terminal.py** (~65 lines)
   - `open_commands_in_terminals()` (lines 340-402)

5. **utils/prompts.py** (~35 lines)
   - `_confirm()` (lines 48-52)
   - `_prompt()` (lines 54-57)
   - `prompt_tool_configuration()` (lines 403-433)

6. **utils/media.py** (~50 lines)
   - `process_images()` (lines 435-480)

**Constants to Extract:**
- `APP_NAME` constant (line 59) should go to a constants module or __init__.py

## 4. ./src/claif/client.py (16 KB) - Client Implementation

### Current Structure Analysis

**Main Responsibilities:**
- Unified client interface for LLM providers
- Auto-installation of missing CLIs
- Provider rotation on failure
- Query methods (single, random, parallel)
- Provider instance management

**Key Components:**
- Helper functions (lines 18-76)
- `ClaifClient` class (lines 78-366)
- Module-level convenience functions (lines 368-423)

### Proposed Split Structure

```
src/claif/client/
├── __init__.py              # Export ClaifClient and convenience functions
├── base.py                  # ClaifClient base class
├── providers.py             # Provider instance management
├── auto_install.py          # Auto-installation logic
├── rotation.py              # Provider rotation logic
└── helpers.py               # Helper functions
```

**Refactoring Details:**

1. **client/helpers.py** (~60 lines)
   - `_is_cli_missing_error()` (lines 18-46)
   - `_get_provider_install_function()` (lines 48-76)

2. **client/base.py** (~80 lines)
   - `ClaifClient.__init__()` (lines 87-95)
   - `list_providers()` (lines 283-290)
   - Module-level client instance

3. **client/providers.py** (~20 lines)
   - `_recreate_provider_instance()` (lines 97-114)

4. **client/auto_install.py** (~80 lines)
   - Extract auto-installation logic from `query()` method (lines 158-196)
   - Create dedicated method for handling CLI missing errors

5. **client/rotation.py** (~70 lines)
   - `query_with_rotation()` (lines 292-365)

6. **client/__init__.py** (~120 lines)
   - Main `query()` method (simplified)
   - `query_random()` method (lines 198-225)
   - `query_all()` method (lines 227-281)
   - Module-level convenience functions (lines 371-423)

## 5. ./src/claif/common/config.py (13 KB) - Configuration Management

### Current Structure Analysis

**Main Responsibilities:**
- Configuration data structures
- Loading configuration from multiple sources
- Merging configurations
- Environment variable handling
- Saving configuration

**Key Components:**
- `ProviderConfig` dataclass (lines 16-35)
- `Config` dataclass (lines 37-88)
- Configuration loading functions (lines 90-138)
- Configuration merging (lines 140-202)
- Environment loading (lines 204-265)
- Configuration saving (lines 267-294)

### Proposed Split Structure

```
src/claif/common/config/
├── __init__.py              # Export main Config class and functions
├── models.py                # Config and ProviderConfig dataclasses
├── loader.py                # Configuration loading logic
├── merger.py                # Configuration merging utilities
├── env.py                   # Environment variable handling
└── persistence.py           # Configuration saving/loading to disk
```

**Refactoring Details:**

1. **config/models.py** (~55 lines)
   - `ProviderConfig` dataclass (lines 16-35)
   - `Config` dataclass (lines 37-88)

2. **config/loader.py** (~50 lines)
   - `load_config()` function (lines 90-138)
   - Default config paths logic

3. **config/merger.py** (~65 lines)
   - `merge_config()` function (lines 140-202)
   - `deep_merge()` helper function

4. **config/env.py** (~65 lines)
   - `load_env_config()` function (lines 204-265)

5. **config/persistence.py** (~30 lines)
   - `save_config()` function (lines 267-294)

## Implementation Priority

1. **High Priority:**
   - Split `cli.py` - This is the largest file and most user-facing
   - Split `utils.py` - Widely used across the codebase

2. **Medium Priority:**
   - Split `install.py` - Complex logic that would benefit from separation
   - Split `client.py` - Core functionality that could be more modular

3. **Lower Priority:**
   - Split `config.py` - Already well-organized, but could benefit from separation

## Benefits of Refactoring

1. **Improved Maintainability:** Smaller, focused files are easier to understand and modify
2. **Better Testing:** Smaller modules can be tested in isolation
3. **Reduced Coupling:** Clear separation of concerns reduces interdependencies
4. **Easier Navigation:** Developers can quickly find relevant code
5. **Parallel Development:** Multiple developers can work on different modules without conflicts
6. **Better Import Management:** More granular imports reduce circular dependency risks

## Migration Strategy

1. Create new directory structures
2. Move code to new modules while maintaining backward compatibility
3. Update imports throughout the codebase
4. Add `__init__.py` files that re-export for backward compatibility
5. Update tests to use new module structure
6. Deprecate old monolithic imports over time