---
layout: default
title: Provider Packages
nav_order: 4
has_children: true
---

# Provider Documentation

Claif uses a modular provider system to support different LLM services. Each provider package implements the Claif provider interface while maintaining the unique capabilities of its underlying service.

## Official Provider Packages

### Anthropic Claude (`claif_cla`)
Integrates with Anthropic's Claude models through the Claude Code SDK.

**Key Features:**
- Session management and persistence
- Tool approval strategies  
- Response caching
- MCP (Model Context Protocol) support
- Vision capabilities

**Installation:**
```bash
uv pip install claif_cla
```

### OpenAI Codex (`claif_cod`)  
Provides code generation and manipulation capabilities.

**Key Features:**
- Code generation and editing
- Action mode management (review/interactive/auto)
- Working directory integration
- Project-aware operations
- Safety features and diff preview

**Installation:**
```bash
uv pip install claif_cod
```

### Google Gemini (`claif_gem`)
Wraps the Gemini CLI for Google's Gemini models.

**Key Features:**
- CLI subprocess management
- Auto-approval and yes-mode handling
- Context length management
- System prompt configuration
- Cross-platform compatibility

**Installation:**
```bash
uv pip install claif_gem
```

## Provider Architecture

All providers implement the abstract `Provider` base class and integrate with:

- **Plugin Discovery** - Automatic detection via Python entry points
- **Configuration System** - Provider-specific settings and API keys
- **Error Handling** - Unified error types and recovery strategies
- **Logging** - Structured logging with provider context
- **Testing** - Comprehensive test suites with mocking

## Navigation

- [Provider Architecture](architecture.md) - How providers integrate with core
- [Claude Provider](claude.md) - Anthropic Claude integration details
- [Codex Provider](codex.md) - OpenAI Codex integration details  
- [Gemini Provider](gemini.md) - Google Gemini integration details
- [Custom Providers](custom.md) - Creating your own provider