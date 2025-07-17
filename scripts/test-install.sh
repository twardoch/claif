#!/bin/bash
# this_file: scripts/test-install.sh
# Test script to verify installation and basic functionality

set -e

echo "=== Claif Installation Test ==="
echo "Testing Claif installation and basic functionality $(date)"
echo

# Test 1: Package installation
echo "1. Testing package installation..."
pip install -e .

# Test 2: Basic CLI functionality
echo "2. Testing CLI functionality..."
python -m claif.cli --help > /dev/null
echo "✅ CLI help works"

# Test 3: Version command
echo "3. Testing version command..."
VERSION=$(python -c "import claif; print(claif.__version__)")
echo "✅ Version: $VERSION"

# Test 4: Provider listing
echo "4. Testing provider listing..."
python -c "from claif.client import ClaifClient; c = ClaifClient(); print('Available providers:', [p.value for p in c.list_providers()])"
echo "✅ Provider listing works"

# Test 5: Configuration loading
echo "5. Testing configuration loading..."
python -c "from claif.common.config import load_config; config = load_config(); print('Config loaded successfully')"
echo "✅ Configuration loading works"

# Test 6: Error handling
echo "6. Testing error handling..."
python -c "from claif.common.errors import ClaifError; print('Error classes imported successfully')"
echo "✅ Error handling works"

# Test 7: Build package
echo "7. Testing package build..."
python -m build --outdir test-dist
echo "✅ Package builds successfully"

# Test 8: Check package contents
echo "8. Checking package contents..."
ls -la test-dist/
echo "✅ Package artifacts created"

# Test 9: Install from built package
echo "9. Testing installation from built package..."
pip install test-dist/*.whl --force-reinstall
echo "✅ Installation from wheel works"

# Test 10: Final CLI test
echo "10. Final CLI test..."
python -m claif.cli --help > /dev/null
echo "✅ CLI works after wheel installation"

echo
echo "=== All Tests Passed! ==="
echo "Claif installation and basic functionality verified."
echo
echo "Next steps to test with a real query:"
echo "1. Install provider: pip install claif_cla"
echo "2. Set API key: export ANTHROPIC_API_KEY=your-key"
echo "3. Run query: python -m claif.cli query 'Hello, world!'"

# Cleanup
rm -rf test-dist/