#!/bin/bash
# this_file: scripts/test.sh
# Test script for Claif - runs comprehensive test suite

set -e

echo "=== Claif Test Script ==="
echo "Testing Claif $(date)"

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
echo "Installing test dependencies..."
pip install -e ".[test]"

# Run different test categories
echo "Running unit tests..."
python -m pytest tests/ -v -m "unit or not integration" --cov=src/claif --cov-report=term-missing

echo "Running integration tests..."
python -m pytest tests/ -v -m "integration" --cov=src/claif --cov-report=term-missing || echo "Integration tests failed (expected if providers not installed)"

echo "Running benchmarks..."
python -m pytest tests/ -v -m "benchmark" --benchmark-only || echo "Benchmarks failed (optional)"

echo "Running all tests with coverage..."
python -m pytest tests/ -v --cov=src/claif --cov-report=html --cov-report=term-missing

echo "Test results:"
echo "- Coverage report: htmlcov/index.html"
echo "- Test artifacts: .pytest_cache/"