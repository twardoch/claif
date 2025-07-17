#!/bin/bash
# this_file: scripts/dev-setup.sh
# Development setup script for Claif

set -e

echo "=== Claif Development Setup ==="
echo "Setting up development environment $(date)"

# Check if we're in the right directory
if [ ! -f "pyproject.toml" ]; then
    echo "Error: pyproject.toml not found. Please run from the project root."
    exit 1
fi

# Create virtual environment
echo "Creating virtual environment..."
python3 -m venv .venv

# Activate virtual environment
echo "Activating virtual environment..."
source .venv/bin/activate

# Upgrade pip
echo "Upgrading pip..."
pip install --upgrade pip

# Install development dependencies
echo "Installing development dependencies..."
pip install -e ".[dev,test,all]"

# Install pre-commit hooks
echo "Installing pre-commit hooks..."
pre-commit install

# Create directories
echo "Creating development directories..."
mkdir -p .pytest_cache
mkdir -p htmlcov
mkdir -p dist
mkdir -p build

# Make scripts executable
echo "Making scripts executable..."
chmod +x scripts/*.sh

# Run initial tests
echo "Running initial tests..."
python -m pytest tests/ -v --tb=short

echo "Development setup completed!"
echo ""
echo "Next steps:"
echo "1. Activate virtual environment: source .venv/bin/activate"
echo "2. Run tests: ./scripts/test.sh"
echo "3. Run build: ./scripts/build.sh"
echo "4. Run release: ./scripts/release.sh [major|minor|patch]"
echo ""
echo "Available commands:"
echo "- make lint: Run linting"
echo "- make test: Run tests"
echo "- make build: Build package"
echo "- make clean: Clean build artifacts"