# claif Development Plan - v1.0 MVP Stability Focus

## Executive Summary

**Objective**: Create a stable, reliable v1.0 core framework that serves as a solid foundation for provider packages.

**Current Status**: Core framework stable with 80%+ test coverage. Critical issue: Message class auto-converts strings to List[TextBlock], requiring provider test updates.

**Release Criteria**: 80%+ verified test coverage, reliable provider discovery, cross-platform compatibility, clear error handling.

## Critical Stability Phase (Blocking v1.0)

### Core Framework Hardening
**Timeline**: 1-2 weeks
**Priority**: CRITICAL

- [x] **Fix pytest environment issues** - Resolve xdist/coverage conflicts completely ✅
- [x] **Verify 80%+ test coverage** - Run full test suite, confirm accurate coverage reporting ✅
- [x] **Validate error handling paths** - Ensure provider discovery handles all edge cases ✅
- [x] **Test provider integration** - Verify actual provider package discovery and loading ✅

**Success Criteria**: ✅ COMPLETED - All tests pass reliably, coverage accurate, error paths tested

### Essential Quality Gates
**Timeline**: 1 week
**Priority**: CRITICAL

- [x] **Eliminate flaky tests** - No environment-dependent test failures
- [x] **Actionable error messages** - Users understand problems and solutions
- [ ] **Consistent auto-install** - Provider installation works in clean environments

**Success Criteria**: 99%+ test reliability, clear error messaging, robust auto-install

## Release Readiness Phase (Required for v1.0)

### Cross-Platform Reliability  
**Timeline**: 2-3 weeks
**Priority**: HIGH

- **Multi-platform testing** - Windows, macOS, Linux compatibility verification
- **Path handling robustness** - Support spaces, Unicode, special characters
- **Python version compatibility** - Verify Python 3.8+ support
- **Subprocess execution** - Handle platform-specific differences

**Success Criteria**: Verified functionality on all major platforms

### Build & Installation Verification
**Timeline**: 1-2 weeks  
**Priority**: HIGH

- **Local build testing** - `python -m build` works correctly
- **Package installation** - Test wheel and sdist installation 
- **Dependency resolution** - All dependencies install properly
- **Metadata validation** - Entry points, classifiers correct

**Success Criteria**: Reliable build and install process

### Basic CI/CD Infrastructure
**Timeline**: 1-2 weeks
**Priority**: HIGH

- **GitHub Actions setup** - Automated testing on push/PR
- **Cross-platform matrix** - Windows, macOS, Linux test runners
- **Automated linting** - Ruff, formatting checks
- **Coverage reporting** - Track and enforce coverage standards

**Success Criteria**: Automated testing pipeline working reliably

## Polish Phase (Nice to Have for v1.0)

### Essential Documentation
**Timeline**: 1-2 weeks
**Priority**: MEDIUM

- **Installation guide** - Clear setup instructions for all platforms
- **Basic usage examples** - Core functionality demonstrations  
- **Troubleshooting section** - Common issues and solutions
- **API documentation** - Complete docstrings for public interfaces

**Success Criteria**: Users can install and use without confusion

### Comprehensive Documentation Strategy
**Timeline**: 2-3 weeks
**Priority**: HIGH (moved up due to current inadequate docs)

**Current State Analysis**:
- Existing docs/ folder has only 4 basic files (index.md, getting-started.md, providers.md, _config.yml)
- Website at https://twardoch.github.io/claif/ is minimal and doesn't reflect the comprehensive codebase
- Rich codebase with multiple packages (claif, claif_cla, claif_cod, claif_gem) needs proper documentation
- Many markdown files exist throughout the project but aren't organized in docs/

**Documentation Architecture Requirements**:

1. **Core Framework Documentation** (`docs/core/`)
   - **Architecture Overview** - Plugin system, provider abstraction, async client
   - **Provider Interface** - Abstract base classes, plugin discovery, error handling
   - **Configuration System** - TOML files, environment variables, defaults
   - **Error Handling** - Error hierarchy, recovery strategies, logging
   - **Type System** - Message types, options, responses, async patterns
   - **Testing Framework** - Unit tests, integration tests, mocking strategies

2. **Provider Documentation** (`docs/providers/`)
   - **Provider Architecture** - How providers integrate with core framework
   - **Anthropic Claude (claif_cla)** - SDK wrapper, session management, tool approval
   - **OpenAI Codex (claif_cod)** - Code generation, action modes, project awareness
   - **Google Gemini (claif_gem)** - CLI subprocess management, context handling
   - **Custom Providers** - Development guide, plugin registration, best practices

3. **API Reference** (`docs/api/`)
   - **Core Classes** - Client, Config, Provider base classes
   - **Common Utilities** - Types, errors, utils, formatters
   - **CLI Interface** - Fire-based commands, options, examples
   - **MCP Server** - FastMCP implementation, tool integration
   - **Installation System** - Auto-install, dependency management

4. **User Guides** (`docs/guides/`)
   - **Quick Start** - Installation, first query, basic configuration
   - **Configuration Guide** - API keys, provider settings, advanced options
   - **CLI Usage** - All commands, options, examples, workflows
   - **Integration Guide** - Using Claif in scripts, programmatic access
   - **Migration Guide** - Version changes, breaking changes, upgrading

5. **Developer Documentation** (`docs/development/`)
   - **Development Setup** - Local development, testing, pre-commit hooks
   - **Contributing Guide** - Code style, testing requirements, PR process
   - **Architecture Decisions** - Design patterns, trade-offs, rationale
   - **Provider Development** - Creating new providers, plugin system
   - **Release Process** - Versioning, coordination, publishing

6. **Examples and Tutorials** (`docs/examples/`)
   - **Basic Examples** - Simple queries, provider selection, options
   - **Advanced Usage** - Complex workflows, error handling, async patterns
   - **Integration Examples** - Scripts, automation, CI/CD usage
   - **Provider-Specific** - Claude sessions, Gemini CLI options, Codex modes

7. **Troubleshooting and FAQ** (`docs/troubleshooting/`)
   - **Common Issues** - Installation problems, configuration errors
   - **Provider-Specific** - API key issues, CLI tool problems, network errors
   - **Performance** - Slow queries, timeout handling, optimization
   - **Debugging** - Logging levels, verbose output, error analysis

**Technical Implementation**:
- Use Jekyll with GitHub Pages (existing _config.yml structure)
- Generate API docs from docstrings using automated tools
- Include code examples that are tested in CI
- Cross-reference between different documentation sections
- Search functionality for easy navigation
- Mobile-responsive design for terminal-focused developers

**Content Sources to Integrate**:
- Existing CLAUDE.md, GEMINI.md, AGENTS.md files
- README.md files from all sub-projects
- CHANGELOG.md files for version history
- Code docstrings and type hints
- Test files for usage examples
- CLI help text and command descriptions

**Success Criteria**: Comprehensive, searchable documentation that covers all aspects of the Claif ecosystem

### Release Infrastructure
**Timeline**: 1 week
**Priority**: MEDIUM

- **TestPyPI integration** - Test deployment process
- **Version coordination** - Manage dependencies between packages  
- **Release automation** - Streamline PyPI publishing

**Success Criteria**: Automated, reliable release process

## Architecture Focus

### Core Framework Structure (Current)
```
claif/
├── __init__.py         # Clean public API ✅
├── common/
│   ├── types.py       # Well-documented types ✅  
│   ├── config.py      # Robust configuration ✅
│   ├── errors.py      # Comprehensive errors ✅
│   └── utils.py       # Rich utilities ✅
├── providers/
│   ├── base.py        # Abstract provider interface ✅
│   └── __init__.py    # Provider discovery ✅
├── client.py          # Tested client with retries ✅
├── cli.py             # User-friendly CLI ✅
├── server.py          # Reliable MCP server ✅
└── install.py         # Cross-platform installer ✅
```

### Stability Improvements Needed

- **Provider Discovery**: Handle edge cases, missing packages, version conflicts
- **Error Handling**: Clear messages for network, permission, configuration issues
- **Testing**: Fix environment issues, achieve verified 80%+ coverage
- **Cross-Platform**: Windows path handling, subprocess differences

## Success Metrics for v1.0

### Reliability (Must Have)
- ✅ **99%+ success rate** for provider discovery and basic operations
- ✅ **No resource leaks** or hanging processes
- ✅ **Graceful error handling** with actionable messages
- ✅ **Consistent behavior** across all platforms

### Testing (Must Have)  
- ✅ **80%+ test coverage** with verified accuracy
- ✅ **All critical paths tested** including error conditions
- ✅ **Mocked dependencies** for reliable testing
- ✅ **CI pipeline** passing on all platforms

### User Experience (Should Have)
- ✅ **One-command installation** that works reliably
- ✅ **Clear error messages** for common problems  
- ✅ **Basic documentation** for setup and usage
- ✅ **Fast startup time** (<2 seconds)

## Resource Allocation

### Critical Path (80% of effort)
1. **Testing Infrastructure** (40%) - Fix pytest issues, verify coverage
2. **Cross-Platform Support** (25%) - Windows compatibility, path handling  
3. **Error Handling** (15%) - Clear messages, edge case handling

### Secondary Path (20% of effort)  
1. **CI/CD Setup** (10%) - GitHub Actions, automated testing
2. **Documentation** (10%) - Installation guides, basic usage

## Risk Management

### High Risk Issues
1. **pytest environment problems** → Could block entire release
   - **Mitigation**: Fix first, test in multiple clean environments
2. **Cross-platform failures** → Could limit adoption
   - **Mitigation**: Use GitHub Actions matrix early and often
3. **Provider discovery bugs** → Core functionality broken
   - **Mitigation**: Comprehensive edge case testing

### Medium Risk Issues
1. **Documentation gaps** → User confusion
   - **Mitigation**: Focus on installation and basic usage first
2. **Performance issues** → Poor user experience  
   - **Mitigation**: Profile critical paths, basic optimization

## Non-Goals for v1.0

Explicitly excluding to maintain focus:

- ❌ **Performance optimization** beyond basic functionality
- ❌ **Advanced configuration** systems
- ❌ **Complex caching** mechanisms  
- ❌ **Provider rotation** or failover logic
- ❌ **Session management** across runs
- ❌ **Database backends** or persistence
- ❌ **Multi-user support**
- ❌ **UI enhancements** beyond terminal output
- ❌ **Auto-generated API docs** (manual curation preferred for v1.0)
- ❌ **Interactive documentation** (focus on static, comprehensive docs)
- ❌ **Video tutorials** (text-based documentation priority)

## Timeline & Milestones

**Total Estimated Time**: 4-6 weeks

- **Weeks 1-2**: Core stability (pytest fixes, testing, error handling)
- **Weeks 3-4**: Cross-platform support and CI/CD  
- **Weeks 5-6**: Documentation, polish, release preparation

**Release Target**: Mid Q1 2025

## Post-v1.0 Roadmap

### v1.1 (Performance & Polish)
- Import time optimization and lazy loading
- Enhanced configuration system
- Performance profiling and optimization  
- Extended documentation and examples

### v1.2 (Advanced Features)
- Provider rotation and intelligent failover
- Response caching and session management
- Advanced error recovery strategies
- Plugin ecosystem foundations

### v2.0 (Major Features)
- Complete plugin architecture
- Advanced UI and visualization features
- Multi-user and collaborative features
- Performance rewrite with async optimization