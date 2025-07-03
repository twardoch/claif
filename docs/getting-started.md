# Getting Started

This guide will walk you through the process of installing and configuring Claif.

## Installation

Claif is a Python package and can be installed using pip:

```bash
pip install claif
```

This will install the core `claif` package. To use a specific LLM provider, you will also need to install the corresponding provider package. For example, to use the Gemini provider, you would run:

```bash
pip install claif_gem
```

## Configuration

After installation, you will need to configure Claif with your API keys for the desired providers. The configuration is stored in a `config.toml` file located in your user's home directory (`~/.claif/config.toml`).

You can create this file manually or run the interactive configuration command:

```bash
claif config
```
