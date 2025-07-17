# Development Guide

## Overview

This document describes the development setup and CI/CD implementation for the Claif project.

## What Was Implemented

### 1. Git-tag-based Semversioning

- **Version Source**: Uses `hatch-vcs` to derive version from git tags
- **Configuration**: Set in `pyproject.toml` with `source = "vcs"`
- **Version File**: Automatically generated at `src/claif/__version__.py`
- **Fallback**: Graceful fallback to `0.0.0+unknown` if version can't be determined

### 2. Comprehensive Test Suite

- **Test Structure**: Organized tests in `tests/` directory
- **Coverage**: Tests for all major components (CLI, client, config, errors, types, utils)
- **Markers**: Support for unit, integration, and benchmark tests
- **Configuration**: Pytest configuration in `pyproject.toml`
- **Provider Mocking**: Tests work without requiring actual provider packages

### 3. Local Build/Test/Release Scripts

#### `scripts/build.sh`
- Lints code with ruff
- Runs type checking with mypy
- Executes test suite with coverage
- Builds distribution packages

#### `scripts/test.sh`
- Runs comprehensive test suite
- Generates coverage reports
- Supports different test categories

#### `scripts/release.sh`
- Calculates next version (major/minor/patch)
- Runs full build and test
- Creates git tags
- Updates CHANGELOG.md
- Pushes to trigger CI/CD

#### `scripts/dev-setup.sh`
- Sets up development environment
- Installs dependencies
- Configures pre-commit hooks
- Runs initial tests

#### `Makefile`
- Convenient make targets for common tasks
- Supports `make test`, `make build`, `make release`, etc.

### 4. GitHub Actions CI/CD

#### `.github/workflows/test.yml`
- Runs on push and pull requests
- Tests on multiple OS (Linux, Windows, macOS)
- Tests multiple Python versions (3.10, 3.11, 3.12)
- Includes security scanning
- Integration and benchmark tests

#### `.github/workflows/release.yml`
- Triggers on git tags (`v*`)
- Tests on TestPyPI first
- Publishes to PyPI
- Builds multiplatform binaries
- Creates GitHub releases
- Updates Homebrew formula

#### `.github/workflows/push.yml`
- Existing workflow for regular pushes
- Code quality checks
- Matrix testing
- Build verification

### 5. Multiplatform Binary Compilation

- **Platforms**: Linux x86_64, Windows x86_64, macOS x86_64, macOS ARM64
- **Tool**: PyInstaller for creating standalone executables
- **Distribution**: Binaries attached to GitHub releases
- **Installation**: Direct download or via installation script

### 6. Release Automation

- **Trigger**: Git tags in format `v*` (e.g., `v1.0.32`)
- **Process**: Test → Build → Publish → Release
- **Artifacts**: 
  - Python packages on PyPI
  - Standalone binaries on GitHub
  - Homebrew formula updates
- **Validation**: TestPyPI testing before production release

### 7. Installation Options

#### `install.sh`
- Detects platform and architecture
- Downloads appropriate binary
- Installs to `/usr/local/bin`
- Fallback to pip installation

#### `Formula/claif.rb`
- Homebrew formula for macOS
- Auto-updates on releases
- Includes provider CLI installation

## Usage

### Development Setup

```bash
# Clone repository
git clone https://github.com/twardoch/claif.git
cd claif

# Set up development environment
./scripts/dev-setup.sh

# Or manually:
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev,test,all]"
```

### Testing

```bash
# Run all tests
./scripts/test.sh

# Or use make
make test

# Run specific test categories
python -m pytest tests/ -m "unit"
python -m pytest tests/ -m "integration"
python -m pytest tests/ -m "benchmark"
```

### Building

```bash
# Build package
./scripts/build.sh

# Or use make
make build

# Build wheel only
python -m build --wheel
```

### Releasing

```bash
# Create patch release
./scripts/release.sh patch

# Create minor release
./scripts/release.sh minor

# Create major release
./scripts/release.sh major

# Or use make
make release          # patch
make release-minor    # minor
make release-major    # major
```

### Installation (End Users)

```bash
# Install via pip
pip install claif

# Install via binary (Linux/macOS)
curl -fsSL https://raw.githubusercontent.com/twardoch/claif/main/install.sh | bash

# Install via Homebrew (macOS)
brew install twardoch/claif/claif
```

## Project Structure

```
claif/
├── .github/workflows/          # GitHub Actions CI/CD
│   ├── test.yml               # Test workflow
│   ├── release.yml            # Release workflow
│   └── push.yml               # Push workflow
├── scripts/                   # Build and utility scripts
│   ├── build.sh              # Build script
│   ├── test.sh               # Test script
│   ├── release.sh            # Release script
│   ├── dev-setup.sh          # Development setup
│   └── test-install.sh       # Installation test
├── Formula/                   # Homebrew formula
│   └── claif.rb              # Homebrew formula
├── src/claif/                 # Source code
├── tests/                     # Test suite
├── pyproject.toml            # Project configuration
├── Makefile                  # Convenient make targets
├── install.sh                # Installation script
└── README.md                 # Documentation
```

## Key Configuration Files

### `pyproject.toml`
- Project metadata and dependencies
- Build system configuration (hatch-vcs)
- Tool configuration (pytest, mypy, ruff)
- Version management via git tags

### GitHub Actions
- Automated testing on multiple platforms
- Secure PyPI publishing with TestPyPI validation
- Binary compilation and distribution
- Release automation

## Security Features

- **Secure Publishing**: Uses trusted publishing to PyPI
- **Dependency Scanning**: Security checks in CI
- **Code Analysis**: Static analysis with bandit
- **Isolated Builds**: Uses isolated environments

## Version Management

The project uses semantic versioning with git tags:

- `v1.0.0` - Major release
- `v1.1.0` - Minor release  
- `v1.0.1` - Patch release
- `v1.0.0-alpha.1` - Pre-release

Versions are automatically calculated from git tags using `hatch-vcs`.

## Troubleshooting

### Common Issues

1. **Import Errors**: Provider packages are optional - tests mock them
2. **Build Failures**: Check linting errors with `ruff check`
3. **Test Failures**: Some tests may fail without provider dependencies
4. **Version Issues**: Ensure git tags are properly formatted

### Development Tips

1. Use `make setup` for initial development setup
2. Run `make test` frequently during development
3. Use `make lint` to fix code formatting
4. Create releases with `make release` for proper versioning

## Contributing

1. Set up development environment: `./scripts/dev-setup.sh`
2. Make changes and add tests
3. Run tests: `./scripts/test.sh`
4. Create pull request
5. Release maintainers will handle versioning and releases