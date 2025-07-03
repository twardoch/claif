---
layout: default
title: Provider Installation Guide
parent: Providers
nav_order: 1
---

# Provider Installation Guide

This guide covers installing and configuring all official Claif providers across different platforms.

## Overview

Claif providers require two components:
1. **Python Package**: The Claif provider wrapper (e.g., `claif_gem`)
2. **CLI Tool**: The underlying LLM CLI (e.g., Gemini CLI)

## Quick Installation

### All Providers at Once

```bash
# Install all Python packages
pip install claif[all]

# Or individually
pip install claif claif_cla claif_gem claif_cod

# Install all CLI tools
claif install all
```

### Individual Providers

```bash
# Claude (Anthropic)
pip install claif_cla
claif install claude

# Gemini (Google)
pip install claif_gem
claif install gemini

# Codex (OpenAI)
pip install claif_cod
claif install codex
```

## Detailed Installation by Platform

### Windows Installation

#### Prerequisites

1. **Python 3.10+** from [python.org](https://python.org)
2. **Node.js** (includes npm) from [nodejs.org](https://nodejs.org)
3. **Git** (optional) from [git-scm.com](https://git-scm.com)

#### Step-by-Step Windows Guide

1. **Install Python packages**:
   ```powershell
   # Open PowerShell as Administrator
   pip install claif claif_cla claif_gem claif_cod
   ```

2. **Install Node.js** (if not already installed):
   - Download from [nodejs.org](https://nodejs.org)
   - Run installer (includes npm)
   - Restart terminal

3. **Install CLI tools**:
   ```powershell
   # Using Claif installer
   claif install claude
   claif install gemini
   claif install codex
   
   # Or manually with npm
   npm install -g @anthropic-ai/claude-code
   npm install -g @google/gemini-cli
   npm install -g @openai/codex
   ```

4. **Add to PATH** (if needed):
   ```powershell
   # Add npm global directory to PATH
   $env:PATH += ";$env:APPDATA\npm"
   
   # Add Claif bin directory
   $env:PATH += ";$env:LOCALAPPDATA\Programs\claif\bin"
   ```

5. **Verify installation**:
   ```powershell
   claude --version
   gemini --version
   codex --version
   ```

#### Windows-Specific Issues

**Issue**: "command not found" after installation
```powershell
# Solution 1: Refresh PATH
refreshenv

# Solution 2: Use full path
& "$env:APPDATA\npm\claude.cmd" --version

# Solution 3: Restart terminal
```

**Issue**: PowerShell execution policy
```powershell
# Allow script execution
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### macOS Installation

#### Prerequisites

1. **Homebrew** (recommended):
   ```bash
   /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
   ```

2. **Python 3.10+**:
   ```bash
   brew install python@3.12
   ```

3. **Node.js**:
   ```bash
   brew install node
   ```

#### Step-by-Step macOS Guide

1. **Install Python packages**:
   ```bash
   pip3 install claif claif_cla claif_gem claif_cod
   ```

2. **Install CLI tools**:
   ```bash
   # Using Claif installer
   claif install all
   
   # Or manually
   npm install -g @anthropic-ai/claude-code
   npm install -g @google/gemini-cli
   npm install -g @openai/codex
   ```

3. **Add to PATH** (if needed):
   ```bash
   # Add to ~/.zshrc or ~/.bash_profile
   export PATH="$HOME/.local/bin:$PATH"
   export PATH="/usr/local/bin:$PATH"
   ```

4. **Verify installation**:
   ```bash
   which claude && claude --version
   which gemini && gemini --version
   which codex && codex --version
   ```

### Linux Installation

#### Ubuntu/Debian

```bash
# Update system
sudo apt update && sudo apt upgrade

# Install Python and pip
sudo apt install python3 python3-pip python3-venv

# Install Node.js
curl -fsSL https://deb.nodesource.com/setup_lts.x | sudo -E bash -
sudo apt install nodejs

# Install Claif
pip install --user claif[all]

# Install CLI tools
claif install all
```

#### Fedora/RHEL

```bash
# Install Python
sudo dnf install python3 python3-pip

# Install Node.js
sudo dnf install nodejs npm

# Install Claif
pip install --user claif[all]

# Install CLI tools
export PATH="$HOME/.local/bin:$PATH"
claif install all
```

#### Arch Linux

```bash
# Install dependencies
sudo pacman -S python python-pip nodejs npm

# Install Claif
pip install --user claif[all]

# Install CLI tools
claif install all
```

## Using Bun (Faster Alternative)

Bun is a fast JavaScript runtime that can replace npm:

### Install Bun

```bash
# macOS/Linux
curl -fsSL https://bun.sh/install | bash

# Windows (PowerShell)
powershell -c "irm bun.sh/install.ps1 | iex"
```

### Install CLI Tools with Bun

```bash
# Much faster than npm
bun add -g @anthropic-ai/claude-code
bun add -g @google/gemini-cli
bun add -g @openai/codex
```

## Provider-Specific Setup

### Claude (claif_cla)

1. **Get API Key**:
   - Visit [Anthropic Console](https://console.anthropic.com)
   - Create account and verify email
   - Generate API key

2. **Configure**:
   ```bash
   # Set environment variable
   export ANTHROPIC_API_KEY="your-key-here"
   
   # Or use Claif config
   claif config set providers.claude.api_key "your-key-here"
   ```

3. **Test**:
   ```bash
   claif-cla "Hello Claude"
   ```

### Gemini (claif_gem)

1. **Get API Key**:
   - Visit [Google AI Studio](https://makersuite.google.com)
   - Create project
   - Generate API key

2. **Configure**:
   ```bash
   # Set environment variable
   export GOOGLE_API_KEY="your-key-here"
   
   # Or use Claif config
   claif config set providers.gemini.api_key "your-key-here"
   ```

3. **Test**:
   ```bash
   claif-gem "Hello Gemini"
   ```

4. **Windows-Specific**:
   ```powershell
   # Use provided wrapper scripts
   & "$env:LOCALAPPDATA\Programs\claif\bin\gemini.cmd" --help
   ```

### Codex (claif_cod)

1. **Get API Key**:
   - Visit [OpenAI Platform](https://platform.openai.com)
   - Add payment method
   - Create API key

2. **Configure**:
   ```bash
   # Set environment variable
   export OPENAI_API_KEY="your-key-here"
   
   # Or use Claif config
   claif config set providers.codex.api_key "your-key-here"
   ```

3. **Test**:
   ```bash
   claif-cod "Generate Python function"
   ```

## Configuration Management

### Environment Variables

```bash
# Linux/macOS (.bashrc, .zshrc)
export ANTHROPIC_API_KEY="sk-ant-..."
export GOOGLE_API_KEY="AI..."
export OPENAI_API_KEY="sk-..."

# Windows (PowerShell)
$env:ANTHROPIC_API_KEY = "sk-ant-..."
$env:GOOGLE_API_KEY = "AI..."
$env:OPENAI_API_KEY = "sk-..."

# Windows (Command Prompt)
set ANTHROPIC_API_KEY=sk-ant-...
set GOOGLE_API_KEY=AI...
set OPENAI_API_KEY=sk-...
```

### Configuration File

Create `~/.claif/config.toml`:

```toml
[general]
default_provider = "gemini"
timeout = 120

[providers.claude]
api_key = "sk-ant-..."
model = "claude-3-sonnet"

[providers.gemini]
api_key = "AI..."
model = "gemini-pro"

[providers.codex]
api_key = "sk-..."
model = "gpt-4"
```

## Troubleshooting

### Common Issues

#### "Provider not found"

```bash
# Check installed providers
claif list

# Reinstall provider
pip install --force-reinstall claif_gem
```

#### "CLI tool not found"

```bash
# Check PATH
echo $PATH

# Find CLI location
which gemini || find / -name gemini 2>/dev/null

# Reinstall CLI
claif install gemini --force
```

#### "Permission denied"

```bash
# Fix permissions
chmod +x ~/.local/bin/claif/*

# Use sudo (not recommended)
sudo claif install gemini
```

#### "API key not found"

```bash
# Check environment
env | grep API_KEY

# Verify config
claif config show

# Test with explicit key
GOOGLE_API_KEY="your-key" claif-gem "test"
```

### Platform-Specific Issues

#### Windows Long Path Issues

```powershell
# Enable long paths
New-ItemProperty -Path "HKLM:\SYSTEM\CurrentControlSet\Control\FileSystem" `
  -Name "LongPathsEnabled" -Value 1 -PropertyType DWORD -Force
```

#### macOS Gatekeeper

```bash
# If CLI blocked by Gatekeeper
xattr -d com.apple.quarantine /usr/local/bin/gemini
```

#### Linux Permissions

```bash
# Add user to npm group
sudo usermod -a -G npm $USER

# Fix npm permissions
mkdir ~/.npm-global
npm config set prefix '~/.npm-global'
echo 'export PATH=~/.npm-global/bin:$PATH' >> ~/.bashrc
```

## Verification

### Test All Providers

```bash
# Quick test
claif query "Hello" --provider claude
claif query "Hello" --provider gemini
claif query "Hello" --provider codex

# Or test all at once
claif query-all "What is 2+2?"
```

### Health Check

```bash
# Check individual providers
claif health claude
claif health gemini
claif health codex

# Check all
claif health all
```

## Uninstallation

### Remove Everything

```bash
# Uninstall Python packages
pip uninstall claif claif_cla claif_gem claif_cod

# Uninstall CLI tools
claif uninstall all

# Remove configuration
rm -rf ~/.claif
```

### Remove Individual Provider

```bash
# Python package
pip uninstall claif_gem

# CLI tool
claif uninstall gemini

# Manual removal
npm uninstall -g @google/gemini-cli
```

## Next Steps

- [Configure API Keys](../guides/configuration.html)
- [Provider-Specific Features](../providers/features.html)
- [Troubleshooting Guide](../troubleshooting/index.html)
- [Usage Examples](../examples/index.html)