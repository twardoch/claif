#!/bin/bash
# this_file: scripts/build.sh
# Build script for Claif - performs linting, type checking, testing, and builds

set -e

echo "=== Claif Build Script ==="
echo "Building Claif $(date)"

# Check if we're in the right directory
if [ ! -f "pyproject.toml" ]; then
    echo "Error: pyproject.toml not found. Please run from the project root."
    exit 1
fi

# Activate virtual environment if it exists
if [ -d ".venv" ]; then
    echo "Activating virtual environment..."
    source .venv/bin/activate
fi

# Install dependencies if needed
echo "Installing dependencies..."
pip install -e ".[dev,test]"

# Clean up previous builds
echo "Cleaning up previous builds..."
rm -rf dist/ build/ src/claif.egg-info/

# Code formatting
echo "Formatting code..."
ruff format --respect-gitignore src tests

# Code linting
echo "Linting code..."
ruff check --fix --unsafe-fixes src tests

# Type checking
echo "Type checking..."
mypy src/claif

# Run tests
echo "Running tests..."
python -m pytest tests/ -v --cov=src/claif --cov-report=term-missing

# Build the package
echo "Building package..."
python -m build

echo "Build completed successfully!"
echo "Artifacts in dist/:"
ls -la dist/