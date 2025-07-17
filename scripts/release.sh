#!/bin/bash
# this_file: scripts/release.sh
# Release script for Claif - creates git tags and releases

set -e

echo "=== Claif Release Script ==="
echo "Releasing Claif $(date)"

# Check if we're in the right directory
if [ ! -f "pyproject.toml" ]; then
    echo "Error: pyproject.toml not found. Please run from the project root."
    exit 1
fi

# Check if git is clean
if [ -n "$(git status --porcelain)" ]; then
    echo "Error: Git working directory is not clean. Please commit or stash changes."
    exit 1
fi

# Get current version from git
CURRENT_VERSION=$(git describe --tags --abbrev=0 2>/dev/null || echo "v0.0.0")
echo "Current version: $CURRENT_VERSION"

# Parse version increment type
VERSION_TYPE="${1:-patch}"
case $VERSION_TYPE in
    major|minor|patch)
        ;;
    *)
        echo "Usage: $0 [major|minor|patch]"
        echo "Default: patch"
        exit 1
        ;;
esac

# Calculate next version
IFS='.' read -r major minor patch <<< "${CURRENT_VERSION#v}"
case $VERSION_TYPE in
    major)
        major=$((major + 1))
        minor=0
        patch=0
        ;;
    minor)
        minor=$((minor + 1))
        patch=0
        ;;
    patch)
        patch=$((patch + 1))
        ;;
esac

NEW_VERSION="v$major.$minor.$patch"
echo "New version: $NEW_VERSION"

# Confirm release
read -p "Create release $NEW_VERSION? (y/N): " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Release cancelled."
    exit 0
fi

# Activate virtual environment if it exists
if [ -d ".venv" ]; then
    echo "Activating virtual environment..."
    source .venv/bin/activate
fi

# Run full build and test
echo "Running full build and test..."
./scripts/build.sh

# Update CHANGELOG.md
echo "Updating CHANGELOG.md..."
if [ -f "CHANGELOG.md" ]; then
    # Create a backup
    cp CHANGELOG.md CHANGELOG.md.bak
    
    # Add new version entry
    sed -i "1a\\
\\
## [$NEW_VERSION] - $(date +%Y-%m-%d)\\
\\
### Added\\
- Version $NEW_VERSION release\\
" CHANGELOG.md
    
    echo "Updated CHANGELOG.md with new version"
fi

# Create git tag
echo "Creating git tag $NEW_VERSION..."
git tag -a "$NEW_VERSION" -m "Release $NEW_VERSION"

# Push tag
echo "Pushing tag to origin..."
git push origin "$NEW_VERSION"

echo "Release $NEW_VERSION completed!"
echo "Next steps:"
echo "- GitHub Actions will automatically build and publish the release"
echo "- Monitor the workflow at: https://github.com/twardoch/claif/actions"
echo "- Release artifacts will be available at: https://github.com/twardoch/claif/releases/tag/$NEW_VERSION"