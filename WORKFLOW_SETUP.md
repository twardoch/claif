# GitHub Workflows Setup Instructions

## Overview

Due to GitHub App permission restrictions, some workflow files need to be added manually. This document provides complete instructions for setting up the enhanced CI/CD system.

## What Was Successfully Implemented

✅ **Git-tag-based Semversioning**: Uses `hatch-vcs` for automatic version derivation from git tags
✅ **Comprehensive Test Suite**: Enhanced to work without provider dependencies
✅ **Build and Release Scripts**: Complete local development workflow
✅ **Installation Options**: Binary, pip, and Homebrew installation
✅ **Provider Import Fixes**: Graceful handling of missing optional dependencies
✅ **Documentation**: Complete development and setup guides

## Manual Setup Required

### 1. Enhanced Test Workflow

The existing `.github/workflows/test.yml` can be enhanced. Create a new file or replace the existing one:

```yaml
# .github/workflows/test.yml
name: Test

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main, develop ]

jobs:
  test:
    runs-on: ${{ matrix.os }}
    strategy:
      matrix:
        os: [ubuntu-latest, windows-latest, macos-latest]
        python-version: ["3.10", "3.11", "3.12"]
        exclude:
          - os: windows-latest
            python-version: "3.10"
          - os: macos-latest
            python-version: "3.10"

    steps:
    - uses: actions/checkout@v4
      with:
        fetch-depth: 0

    - name: Set up Python ${{ matrix.python-version }}
      uses: actions/setup-python@v5
      with:
        python-version: ${{ matrix.python-version }}

    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -e ".[dev,test]"

    - name: Lint with ruff
      run: |
        ruff check src tests
        ruff format --check src tests

    - name: Type check with mypy
      run: mypy src/claif

    - name: Test with pytest
      run: |
        python -m pytest tests/ -v --cov=src/claif --cov-report=term-missing
```

### 2. Enhanced Release Workflow

The existing `.github/workflows/release.yml` should be enhanced with multiplatform binary compilation:

**Copy the template:**
```bash
# From the repository root
cp .github/workflows/release.yml .github/workflows/release.yml.backup
```

**Then replace with the enhanced version** (see `workflows/release.yml` in the repository).

### 3. Repository Secrets

Add these secrets in Settings → Secrets and variables → Actions:

- `PYPI_TOKEN`: Your PyPI API token
- `TEST_PYPI_TOKEN`: Your TestPyPI API token  
- `GITHUB_TOKEN`: Automatically provided by GitHub

Optional:
- `HOMEBREW_GITHUB_TOKEN`: For Homebrew formula updates

## Quick Setup Commands

```bash
# 1. Copy enhanced workflow (if desired)
cp workflows/release.yml .github/workflows/release.yml

# 2. Test the setup
./scripts/build.sh

# 3. Commit workflow changes
git add .github/workflows/release.yml
git commit -m "feat(ci): add enhanced release workflow with binary compilation"
git push

# 4. Create a test release
git tag v1.0.32-test
git push origin v1.0.32-test
```

## Features of the Enhanced System

### 🏗️ **Build System**
- **Scripts**: `build.sh`, `test.sh`, `release.sh`, `dev-setup.sh`
- **Makefile**: Convenient `make test`, `make build`, `make release`
- **Cross-platform**: Linux, Windows, macOS support

### 🔖 **Versioning**
- **Git-tag-based**: Version derived from git tags (e.g., `v1.0.32`)
- **Semantic versioning**: Major.minor.patch format
- **Development builds**: Automatic dev versions between releases

### 🧪 **Testing**
- **Multi-platform**: Ubuntu, Windows, macOS
- **Multi-version**: Python 3.10, 3.11, 3.12
- **Provider mocking**: Tests work without AI provider packages
- **Coverage reporting**: Comprehensive coverage analysis

### 📦 **Binary Distribution**
- **Multiplatform**: Linux, Windows, macOS (Intel + ARM)
- **Standalone**: No Python installation required
- **GitHub releases**: Automatic attachment to releases
- **Installation script**: Automatic platform detection

### 🍺 **Package Management**
- **PyPI**: Standard `pip install claif`
- **Binary**: `curl -fsSL https://raw.githubusercontent.com/twardoch/claif/main/install.sh | bash`
- **Homebrew**: `brew install twardoch/claif/claif`

## Usage Examples

### Development
```bash
# Setup development environment
./scripts/dev-setup.sh

# Run tests
make test

# Build package
make build

# Create release
make release
```

### User Installation
```bash
# Python package
pip install claif

# Binary installation
curl -fsSL https://raw.githubusercontent.com/twardoch/claif/main/install.sh | bash

# Homebrew (macOS)
brew install twardoch/claif/claif
```

### Release Process
```bash
# Automatic semantic versioning
./scripts/release.sh patch   # 1.0.0 → 1.0.1
./scripts/release.sh minor   # 1.0.0 → 1.1.0
./scripts/release.sh major   # 1.0.0 → 2.0.0

# Manual tagging
git tag v1.0.32
git push origin v1.0.32
```

## Troubleshooting

### Import Errors
Provider packages are optional. The system now gracefully handles missing packages:
```python
# This will work even without claif_cla installed
from claif import query
# Provider error only occurs when actually using the provider
```

### Version Issues
```bash
# Check current version
python -c "import claif; print(claif.__version__)"

# Ensure tags are formatted correctly
git tag v1.0.32  # ✅ Correct format
git tag 1.0.32   # ❌ Missing 'v' prefix
```

### Build Failures
```bash
# Fix linting issues
ruff check --fix src tests

# Run complete build
./scripts/build.sh
```

## What's Next

1. **Merge this PR**: The core system is ready for production
2. **Add workflow enhancements**: Copy the enhanced workflows manually
3. **Set up secrets**: Add PyPI tokens to repository secrets
4. **Test release**: Create a test tag to verify the system works
5. **Update documentation**: Add release notes and user guides

The system provides a robust foundation for automated releases, multiplatform distribution, and developer productivity.