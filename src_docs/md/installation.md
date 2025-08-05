# Installation

This comprehensive guide covers all installation methods and deployment scenarios for Claif and its provider packages.

## System Requirements

### Python Version

- **Python 3.12+** (required)
- **Python 3.13** (recommended)

!!! warning "Python Version"
    Claif requires Python 3.12 or higher due to modern syntax and type hints. Check your version:
    ```bash
    python --version
    # or
    python3 --version
    ```

### Operating System Support

Claif is tested and supported on:

- **Linux** (Ubuntu 20.04+, RHEL 8+, Arch, etc.)
- **macOS** (10.15+)
- **Windows** (10, 11) with WSL2 recommended

### Package Managers

Supported installation methods:

- **uv** (recommended) - Modern Python package installer
- **pip** - Standard Python package installer
- **pipx** - For isolated CLI installations
- **conda/mamba** - Via conda-forge (coming soon)

## Installation Methods

### Method 1: Using uv (Recommended)

**uv** is the fastest and most reliable way to install Claif:

```bash
# Install uv if you haven't already
curl -LsSf https://astral.sh/uv/install.sh | sh

# Install core framework
uv pip install claif

# Install provider packages
uv pip install claif_cla claif_gem claif_cod
```

### Method 2: Using pip

Standard pip installation:

```bash
# Install core framework
pip install claif

# Install specific providers
pip install claif_cla  # Claude
pip install claif_gem  # Gemini
pip install claif_cod  # Codex

# Or install all at once
pip install claif[all]  # Includes all providers
```

### Method 3: Using pipx (Isolated Installation)

For isolated CLI-only installation:

```bash
# Install pipx if needed
pip install pipx

# Install claif in isolated environment
pipx install claif

# Install provider packages
pipx inject claif claif_cla claif_gem claif_cod
```

### Method 4: Development Installation

For contributing or development:

```bash
# Clone the repository
git clone https://github.com/twardoch/claif.git
cd claif

# Install in development mode
uv pip install -e ".[dev]"

# Or with pip
pip install -e ".[dev]"
```

## Provider Package Installation

### Core Framework Only

If you only need the framework (for custom providers):

```bash
uv pip install claif
```

### Individual Providers

Install only the providers you need:

=== "Claude (Anthropic)"
    ```bash
    uv pip install claif_cla
    
    # Requires: Anthropic API key
    # Models: Claude 3 family
    # Features: Advanced reasoning, large context
    ```

=== "Gemini (Google)"
    ```bash
    uv pip install claif_gem
    
    # Requires: Google API key
    # Models: Gemini Pro, Gemini Flash
    # Features: Multimodal, fast responses
    ```

=== "Codex (OpenAI)"
    ```bash
    uv pip install claif_cod
    
    # Requires: OpenAI API key
    # Models: GPT-4, GPT-3.5 Turbo
    # Features: Code generation, chat completions
    ```

### All Providers

Install everything:

```bash
# Method 1: Individual packages
uv pip install claif claif_cla claif_gem claif_cod

# Method 2: Bundle (if available)
uv pip install claif[all]
```

## Virtual Environment Setup

### Using uv (Recommended)

```bash
# Create new project
mkdir my-claif-project
cd my-claif-project

# Initialize with uv
uv init
uv add claif claif_cla

# Activate environment
source .venv/bin/activate  # Linux/macOS
# or
.venv\Scripts\activate     # Windows
```

### Using venv

```bash
# Create virtual environment
python -m venv claif-env

# Activate
source claif-env/bin/activate  # Linux/macOS
claif-env\Scripts\activate     # Windows

# Install packages
pip install claif claif_cla claif_gem claif_cod
```

### Using conda

```bash
# Create environment
conda create -n claif python=3.12

# Activate
conda activate claif

# Install via pip (conda packages coming soon)
pip install claif claif_cla claif_gem claif_cod
```

## Container Deployment

### Docker

Create a Dockerfile:

```dockerfile
FROM python:3.12-slim

# Install uv
RUN pip install uv

# Set working directory
WORKDIR /app

# Copy requirements
COPY requirements.txt .

# Install dependencies
RUN uv pip install --system -r requirements.txt

# Copy application
COPY . .

# Set entrypoint
ENTRYPOINT ["claif"]
```

Requirements file:

```txt
claif
claif_cla
claif_gem
claif_cod
```

Build and run:

```bash
# Build image
docker build -t my-claif-app .

# Run with environment variables
docker run --rm \
  -e ANTHROPIC_API_KEY=$ANTHROPIC_API_KEY \
  -e GOOGLE_API_KEY=$GOOGLE_API_KEY \
  my-claif-app ask "Hello world"
```

### Docker Compose

```yaml
version: '3.8'
services:
  claif:
    build: .
    environment:
      - ANTHROPIC_API_KEY=${ANTHROPIC_API_KEY}
      - GOOGLE_API_KEY=${GOOGLE_API_KEY}
      - OPENAI_API_KEY=${OPENAI_API_KEY}
    volumes:
      - ./config:/app/config
    command: server --host 0.0.0.0 --port 8000
```

## Platform-Specific Instructions

### Linux

#### Ubuntu/Debian

```bash
# Update package list
sudo apt update

# Install Python 3.12+ if needed
sudo apt install python3.12 python3.12-pip python3.12-venv

# Install uv
curl -LsSf https://astral.sh/uv/install.sh | sh

# Install claif
uv pip install claif claif_cla
```

#### RHEL/CentOS/Fedora

```bash
# Install Python 3.12+
sudo dnf install python3.12 python3.12-pip

# Install uv
curl -LsSf https://astral.sh/uv/install.sh | sh

# Install claif
uv pip install claif claif_cla
```

#### Arch Linux

```bash
# Install Python (usually latest)
sudo pacman -S python python-pip

# Install uv
curl -LsSf https://astral.sh/uv/install.sh | sh

# Install claif
uv pip install claif claif_cla
```

### macOS

#### Using Homebrew

```bash
# Install Python 3.12+
brew install python@3.12

# Install uv
brew install uv

# Install claif
uv pip install claif claif_cla
```

#### Using pyenv

```bash
# Install pyenv
brew install pyenv

# Install Python 3.12+
pyenv install 3.12.1
pyenv global 3.12.1

# Install uv and claif
pip install uv
uv pip install claif claif_cla
```

### Windows

#### Using Python.org Installer

1. Download Python 3.12+ from [python.org](https://python.org)
2. Install with "Add to PATH" checked
3. Open Command Prompt or PowerShell:

```cmd
# Install uv
pip install uv

# Install claif
uv pip install claif claif_cla
```

#### Using Chocolatey

```powershell
# Install Python
choco install python312

# Install uv
pip install uv

# Install claif
uv pip install claif claif_cla
```

#### Using Windows Subsystem for Linux (WSL2)

Recommended for best experience:

```bash
# In WSL2 terminal
curl -LsSf https://astral.sh/uv/install.sh | sh
uv pip install claif claif_cla claif_gem claif_cod
```

## Verification

### Check Installation

```bash
# Verify claif is installed
claif --version

# Check available providers
claif providers list

# Test basic functionality
claif ask "Hello, world!" --dry-run
```

### Run Diagnostics

```bash
# Comprehensive system check
claif doctor

# Check specific provider
claif doctor --provider claude

# Check configuration
claif config validate
```

## Troubleshooting Installation

### Common Issues

#### Command Not Found

```bash
# Check if claif is in PATH
which claif

# If not found, add to PATH or use full path
export PATH="$HOME/.local/bin:$PATH"

# Or find installation location
pip show claif
```

#### Permission Errors

```bash
# Use user installation
pip install --user claif

# Or fix permissions
sudo chown -R $USER ~/.local/
```

#### Version Conflicts

```bash
# Check for conflicts
pip check

# Upgrade all packages
pip install --upgrade claif claif_cla claif_gem claif_cod

# Or start fresh
pip uninstall claif claif_cla claif_gem claif_cod
pip install claif claif_cla
```

#### Provider Not Found

```bash
# Check if provider package is installed
pip list | grep claif

# Install missing provider
uv pip install claif_cla  # example

# Refresh provider cache
claif providers refresh
```

### Getting Help

If you encounter issues:

1. **Check the logs**: `claif --debug ask "test"`
2. **Run diagnostics**: `claif doctor`
3. **Check GitHub issues**: [Claif Issues](https://github.com/twardoch/claif/issues)
4. **Join discussions**: [GitHub Discussions](https://github.com/twardoch/claif/discussions)

## Upgrading

### Upgrade All Packages

```bash
# Using uv
uv pip install --upgrade claif claif_cla claif_gem claif_cod

# Using pip
pip install --upgrade claif claif_cla claif_gem claif_cod
```

### Version Pinning

For production deployments, pin versions:

```txt
# requirements.txt
claif==1.0.1
claif_cla==1.0.1
claif_gem==1.0.1
claif_cod==1.0.1
```

### Migration Between Versions

Check [CHANGELOG.md](https://github.com/twardoch/claif/blob/main/CHANGELOG.md) for breaking changes and migration guides.

## Next Steps

After installation:

1. **Configure providers**: [Configuration](configuration.md)
2. **Learn basic usage**: [Getting Started](getting-started.md)
3. **Explore CLI commands**: [CLI Usage](cli-usage.md)
4. **Set up development environment**: [Development](development.md)

!!! success "Installation Complete"
    You now have Claif installed and ready to use. The next step is configuring your AI providers and API keys.