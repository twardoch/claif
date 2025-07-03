# claif TODO List - v1.0 MVP Stability Focus

## CRITICAL (Blocking v1.0 Release)

### Core Framework Stability
- [ ] **Verify 80%+ test coverage** - Run full test suite and confirm accurate coverage reporting
  - **Issue**: Many tests failing, coverage likely impacted.
- [ ] **Auto-install works consistently** - Provider installation succeeds in clean environments
  - **Issue**: `test_auto_install_on_missing_cli`, `test_auto_install_failure`, `test_no_auto_install_for_other_errors` failing.
- [ ] **Fix Message class test impact** - Update all provider tests to handle auto-conversion to List[TextBlock]
  - **Issue**: This was a known issue, and likely contributes to some failures.
- [ ] **Fix CLI command execution issues**
  - **Issue**: `test_query_with_params` (query not called), `test_query_error_handling` (error not detected), `test_provider_status` (is_provider_available not called), `test_config_show`, `test_config_set`, `test_config_save` (`Config` object not callable), `test_install_all` (unexpected keyword argument `all`), `test_server_start` (mock call mismatch), `test_session_claude` (`get_provider` attribute error), `test_status_command` (`Table` not called).
- [ ] **Resolve `AttributeError` in client and server tests**
  - **Issue**: `test_get_provider_install_function_claude`, `test_get_provider_install_function_gemini`, `test_get_provider_install_function_codex` (`install_` functions not found in `claif.client`).
  - **Issue**: `test_server_start`, `test_server_main` (`uvicorn`, `fire` attributes not found in `claif.server`).
- [ ] **Address `async def functions are not natively supported` errors**
  - **Issue**: Many client and server tests are failing because `pytest-asyncio` or a similar plugin is not correctly configured or installed.
- [ ] **Fix `NameError` in config tests**
  - **Issue**: `test_get_config_path_default`, `test_get_config_path_from_env`, `test_get_config_path_creates_directory`, `test_get_default_config`, `test_default_config_immutable` (`get_config_path`, `get_default_config` not defined).
- [ ] **Correct `AssertionError` in config tests**
  - **Issue**: `test_provider_config_none_extra` (`extra` is `None` instead of `{}`), `test_config_defaults` (`session_dir` is not `None`), `test_config_none_values` (`providers` is `None`).
  - **Issue**: `test_load_config_invalid_json` (assertion message mismatch), `test_load_config_invalid_provider` (did not raise expected error).
  - **Issue**: `test_save_config_permission_error` (test expects `PermissionError` but fails, likely due to assertion logic).
- [ ] **Resolve `AssertionError` and `TypeError` in install tests**
  - **Issue**: `test_get_install_dir_windows` (path comparison), `test_ensure_bun_installed_install` (bun not found), `test_find_executable_in_path`, `test_find_executable_in_home`, `test_find_executable_not_found` (path comparison or `InstallError` not caught).
  - **Issue**: `test_install_provider_pip`, `test_install_provider_pipx`, `test_install_provider_bun`, `test_install_provider_invalid_method`, `test_uninstall_provider_pip`, `test_install_flow_success`, `test_install_flow_failure` (unexpected keyword argument `method` for `install_provider`/`uninstall_provider`).
- [ ] **Fix `RuntimeError: Could not determine home directory.`**
  - **Issue**: `test_get_install_location_windows` is failing due to environment setup.
- [ ] **Correct `AssertionError` in `test_inject_claif_bin_to_path`**
  - **Issue**: Path comparison issue.
- [ ] **Address `Failed: DID NOT RAISE <class 'NotImplementedError'>` in `test_open_commands_unsupported`**
  - **Issue**: Test expects `NotImplementedError` but doesn't receive it.
- [ ] **Fix provider query tests**
  - **Issue**: `test_query_mock`, `test_query_error`, `test_query_with_options` for Claude, Gemini, Codex providers are failing due to async issues.
- [ ] **Fix server query tests**
  - **Issue**: `test_query_basic`, `test_query_invalid_provider`, `test_query_error_handling`, `test_query_random`, `test_query_random_error`, `test_query_all`, `test_query_all_error`, `test_list_providers`, `test_health_check_single`, `test_health_check_all` are failing due to async issues.
- [ ] **Fix `test_provider_responses_format`**
  - **Issue**: Failing due to async issues.


## HIGH PRIORITY (Required for Stable Release)

### Cross-Platform Reliability
- [ ] **Test on Windows, macOS, Linux** - Verify all core functionality works across platforms
- [ ] **Path handling robustness** - Support spaces, Unicode characters, special paths
- [ ] **Python version compatibility** - Verify Python 3.8+ support
- [ ] **Subprocess execution** - Handle platform-specific differences

### Build & Installation Verification
- [ ] **Local build testing** - Verify `python -m build` works correctly
- [ ] **Installation from packages** - Test wheel and sdist installation
- [ ] **Dependency resolution** - Ensure all dependencies install properly
- [ ] **Package metadata validation** - Correct entry points, classifiers, etc.

### Basic CI/CD
- [ ] **GitHub Actions setup** - Automated testing on push/PR
- [ ] **Cross-platform test matrix** - Windows, macOS, Linux runners
- [ ] **Automated linting** - Ruff, formatting checks
- [ ] **Coverage reporting** - Track and enforce coverage standards

## MEDIUM PRIORITY (Nice to Have for v1.0)

### Documentation Essentials (PRIORITY ELEVATED)
- [ ] **Installation guide** - Clear setup instructions for all platforms
- [ ] **Basic usage examples** - Core functionality demonstrations
- [ ] **Troubleshooting section** - Common issues and solutions
- [ ] **API documentation** - Complete docstrings for public interfaces

### Comprehensive Documentation Overhaul
- [ ] **Analyze current docs gap** - Current docs/ has only 4 basic files vs rich codebase
- [ ] **Create documentation architecture** - Organize docs into logical sections
- [ ] **Set up directory structure** - Create folders for core/, providers/, api/, guides/, etc.

#### Core Framework Documentation (`docs/core/`)
- [ ] **Architecture overview** - Plugin system, provider abstraction, async patterns
- [ ] **Provider interface guide** - Abstract base classes, plugin discovery
- [ ] **Configuration system** - TOML files, environment variables, defaults
- [ ] **Error handling guide** - Error hierarchy, recovery strategies, logging
- [ ] **Type system reference** - Message types, options, responses
- [ ] **Testing framework** - Unit tests, integration tests, mocking

#### Provider Documentation (`docs/providers/`)
- [ ] **Provider architecture** - How providers integrate with core
- [ ] **Anthropic Claude (claif_cla)** - SDK wrapper, session management, tools
- [ ] **OpenAI Codex (claif_cod)** - Code generation, action modes, project awareness
- [ ] **Google Gemini (claif_gem)** - CLI subprocess management, context handling
- [ ] **Custom provider development** - Plugin creation guide, best practices

#### API Reference (`docs/api/`)
- [ ] **Core classes reference** - Client, Config, Provider base classes
- [ ] **Common utilities** - Types, errors, utils, formatters
- [ ] **CLI interface** - Fire-based commands, options, examples
- [ ] **MCP server** - FastMCP implementation, tool integration
- [ ] **Installation system** - Auto-install, dependency management

#### User Guides (`docs/guides/`)
- [ ] **Quick start guide** - Installation, first query, basic config
- [ ] **Configuration guide** - API keys, provider settings, advanced options
- [ ] **CLI usage guide** - All commands, options, examples, workflows
- [ ] **Integration guide** - Using Claif in scripts, programmatic access
- [ ] **Migration guide** - Version changes, breaking changes, upgrading

#### Developer Documentation (`docs/development/`)
- [ ] **Development setup** - Local development, testing, pre-commit hooks
- [ ] **Contributing guide** - Code style, testing requirements, PR process
- [ ] **Architecture decisions** - Design patterns, trade-offs, rationale
- [ ] **Provider development** - Creating new providers, plugin system
- [ ] **Release process** - Versioning, coordination, publishing

#### Examples and Tutorials (`docs/examples/`)
- [ ] **Basic examples** - Simple queries, provider selection, options
- [ ] **Advanced usage** - Complex workflows, error handling, async patterns
- [ ] **Integration examples** - Scripts, automation, CI/CD usage
- [ ] **Provider-specific examples** - Claude sessions, Gemini CLI, Codex modes

#### Troubleshooting (`docs/troubleshooting/`)
- [ ] **Common issues** - Installation problems, configuration errors
- [ ] **Provider-specific issues** - API keys, CLI tools, network errors
- [ ] **Performance troubleshooting** - Slow queries, timeouts, optimization
- [ ] **Debugging guide** - Logging levels, verbose output, error analysis

#### Technical Implementation
- [ ] **Enhance Jekyll setup** - Improve _config.yml, navigation structure
- [ ] **Content integration** - Incorporate existing CLAUDE.md, GEMINI.md, AGENTS.md
- [ ] **Cross-references** - Link between different documentation sections
- [ ] **Code examples testing** - Ensure all examples work and are tested in CI
- [ ] **Search functionality** - Enable easy navigation through docs
- [ ] **Mobile responsiveness** - Optimize for terminal-focused developers

### Release Infrastructure
- [ ] **TestPyPI integration** - Test deployment process
- [ ] **Version coordination** - Manage dependencies between packages
- [ ] **Release automation** - Streamline PyPI publishing

## SUCCESS CRITERIA FOR v1.0

### Reliability (Must Have)
- ✅ **99%+ success rate** for basic provider operations
- ✅ **No resource leaks** in normal operation
- ✅ **Graceful error handling** with clear messages
- ✅ **Consistent behavior** across platforms

### Testing (Must Have)
- ✅ **80%+ test coverage** with verified accuracy
- ✅ **All critical paths tested** including error conditions
- ✅ **Mocked external dependencies** for reliable testing
- ✅ **CI pipeline passing** on all platforms

### User Experience (Should Have)
- ✅ **One-command installation** that works reliably
- ✅ **Clear error messages** for common problems
- ✅ **Basic documentation** for setup and usage
- ✅ **Fast startup time** (<2 seconds)

## NON-GOALS FOR v1.0

Explicitly excluding to maintain focus:

- ❌ **Performance optimization** beyond basic functionality
- ❌ **Advanced configuration** options
- ❌ **Complex caching systems**
- ❌ **Multi-user support**
- ❌ **Database backends**
- ❌ **UI enhancements** beyond terminal output
- ❌ **Provider rotation** or failover logic
- ❌ **Session persistence** across runs
- ❌ **Auto-generated API docs** (manual curation preferred for v1.0)
- ❌ **Interactive documentation** (focus on static, comprehensive docs)
- ❌ **Video tutorials** (text-based documentation priority)

## RISK MITIGATION

### High Risk Items
1. **Cross-platform failures** → Use GitHub Actions matrix early
2. **Provider discovery bugs** → Comprehensive edge case testing

### Medium Risk Items
1. **Documentation gaps** → Focus on installation and basic usage
2. **Build/install issues** → Test with fresh environments regularly

## DEFINITION OF DONE

For each task to be considered complete:

- [ ] **Implementation** meets requirements
- [ ] **Tests** cover the functionality (unit + integration)
- [ ] **Documentation** updated if needed
- [ ] **Error handling** includes clear messages
- [ ] **Cross-platform** compatibility verified
- [ ] **Code review** completed (self-review minimum)

For documentation tasks specifically:

- [ ] **Content accuracy** - All information is current and correct
- [ ] **Code examples** - All examples are tested and work
- [ ] **Navigation** - Easy to find relevant information
- [ ] **Completeness** - Covers all major use cases and features
- [ ] **Clarity** - Written for target audience (users vs developers)
- [ ] **Cross-references** - Links to related sections work correctly

## POST-v1.0 ROADMAP

### v1.1 (Performance & Polish)
- Import time optimization
- Enhanced configuration system
- Performance profiling and optimization
- Extended documentation

### v1.2 (Advanced Features)
- Provider rotation and failover
- Response caching
- Session management
- Advanced error recovery

### v2.0 (Major Features)
- Plugin ecosystem
- Advanced UI features
- Multi-user support
- Performance rewrite
