#!/bin/bash
# this_file: install.sh
# Installation script for Claif - installs the latest release binary or via pip

set -e

REPO="twardoch/claif"
BINARY_NAME="claif"
INSTALL_DIR="/usr/local/bin"
GITHUB_API="https://api.github.com/repos/$REPO/releases/latest"
DOWNLOAD_BASE="https://github.com/$REPO/releases/download"

echo "=== Claif Installation Script ==="
echo "This script will install the latest version of Claif"
echo

# Detect platform
OS=$(uname -s)
ARCH=$(uname -m)

case $OS in
    Linux)
        PLATFORM="linux"
        ;;
    Darwin)
        PLATFORM="darwin"
        ;;
    *)
        echo "Unsupported OS: $OS"
        echo "Please install via pip: pip install claif"
        exit 1
        ;;
esac

case $ARCH in
    x86_64)
        ARCH_NAME="x86_64"
        ;;
    arm64|aarch64)
        ARCH_NAME="arm64"
        ;;
    *)
        echo "Unsupported architecture: $ARCH"
        echo "Please install via pip: pip install claif"
        exit 1
        ;;
esac

BINARY_FILE="$BINARY_NAME-$PLATFORM-$ARCH_NAME"
echo "Target binary: $BINARY_FILE"

# Check if user prefers pip installation
if [ "$1" == "--pip" ]; then
    echo "Installing via pip..."
    pip install claif
    echo "Claif installed successfully via pip!"
    echo "Run 'claif --help' to get started."
    exit 0
fi

# Check if curl is available
if ! command -v curl &> /dev/null; then
    echo "Error: curl is required but not installed."
    echo "Please install curl or use pip installation: pip install claif"
    exit 1
fi

# Get latest release info
echo "Fetching latest release info..."
LATEST_RELEASE=$(curl -s "$GITHUB_API")
if [ $? -ne 0 ]; then
    echo "Error: Failed to fetch release info from GitHub"
    echo "Please install via pip: pip install claif"
    exit 1
fi

# Extract version and download URL
VERSION=$(echo "$LATEST_RELEASE" | grep '"tag_name"' | sed -E 's/.*"([^"]+)".*/\1/')
DOWNLOAD_URL="$DOWNLOAD_BASE/$VERSION/$BINARY_FILE"

echo "Latest version: $VERSION"
echo "Download URL: $DOWNLOAD_URL"

# Create temporary directory
TEMP_DIR=$(mktemp -d)
TEMP_FILE="$TEMP_DIR/$BINARY_FILE"

echo "Downloading binary..."
curl -L -o "$TEMP_FILE" "$DOWNLOAD_URL"
if [ $? -ne 0 ]; then
    echo "Error: Failed to download binary"
    echo "Please install via pip: pip install claif"
    rm -rf "$TEMP_DIR"
    exit 1
fi

# Make binary executable
chmod +x "$TEMP_FILE"

# Check if we need sudo for installation
if [ ! -w "$INSTALL_DIR" ]; then
    echo "Installing to $INSTALL_DIR (requires sudo)..."
    sudo mv "$TEMP_FILE" "$INSTALL_DIR/$BINARY_NAME"
    sudo chown root:root "$INSTALL_DIR/$BINARY_NAME"
else
    echo "Installing to $INSTALL_DIR..."
    mv "$TEMP_FILE" "$INSTALL_DIR/$BINARY_NAME"
fi

# Clean up
rm -rf "$TEMP_DIR"

# Verify installation
if command -v claif &> /dev/null; then
    echo "✅ Claif installed successfully!"
    echo "Version: $(claif --version)"
    echo
    echo "Get started with:"
    echo "  claif --help"
    echo "  claif query 'Hello, world!'"
    echo "  claif install  # Install AI provider CLIs"
else
    echo "❌ Installation failed - claif not found in PATH"
    echo "Please check that $INSTALL_DIR is in your PATH"
    exit 1
fi