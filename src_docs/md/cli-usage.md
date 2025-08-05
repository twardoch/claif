# CLI Usage

This comprehensive guide covers all Claif command-line interface features, from basic queries to advanced automation workflows.

## Command Overview

Claif provides a hierarchical command structure built with Google Fire:

```bash
claif [GLOBAL_OPTIONS] COMMAND [COMMAND_OPTIONS] [ARGUMENTS]
```

### Global Options

| Option | Description | Example |
|--------|-------------|---------|
| `--provider` | Override default provider | `--provider claude` |
| `--model` | Override default model | `--model gpt-4` |
| `--format` | Output format | `--format json` |
| `--debug` | Enable debug mode | `--debug` |
| `--config` | Use specific config file | `--config ./custom.toml` |
| `--no-color` | Disable colored output | `--no-color` |
| `--timeout` | Request timeout in seconds | `--timeout 60` |

## Basic Commands

### ask - Simple Queries

Send a question or prompt to the AI:

```bash
# Basic question
claif ask "What is the capital of France?"

# Complex reasoning
claif ask "Explain the differences between REST and GraphQL APIs"

# With specific provider
claif ask --provider claude "Analyze the trade-offs of microservices"

# With output formatting
claif ask --format json "List the top 5 programming languages"
```

**Options:**
- `--provider PROVIDER` - Choose AI provider
- `--model MODEL` - Specify model
- `--temperature FLOAT` - Control randomness (0.0-1.0)
- `--max-tokens INT` - Limit response length
- `--system-prompt TEXT` - Set system prompt

### chat - Interactive Conversations

Start an interactive chat session:

```bash
# Basic interactive mode
claif chat

# With specific provider
claif chat --provider gemini

# Load conversation history
claif chat --session research_project

# Interactive with custom settings
claif chat --temperature 0.3 --max-tokens 1000
```

**Interactive Commands:**
- `/help` - Show help
- `/provider claude` - Switch provider
- `/model gpt-4` - Change model
- `/save session_name` - Save current session
- `/load session_name` - Load saved session
- `/clear` - Clear conversation history
- `/exit` - Exit chat mode

**Example Session:**
```
$ claif chat --provider claude
Claif Chat (Claude) - Type /help for commands

You: Explain quantum computing
Claude: Quantum computing is a revolutionary computing paradigm...

You: /provider gemini
Switched to Gemini provider

You: How does this compare to classical computing?
Gemini: Classical computing uses bits that are either 0 or 1...

You: /save quantum_discussion
Session saved as 'quantum_discussion'

You: /exit
```

### code - Code Generation

Generate, analyze, or manipulate code:

```bash
# Generate a function
claif code "Python function to calculate fibonacci numbers"

# Generate a complete class
claif code "REST API class for user management using FastAPI"

# Code with specific language
claif code --language rust "implement a binary search algorithm"

# Code with context from file
claif code "optimize this function for performance" < slow_function.py
```

**Options:**
- `--language LANG` - Target programming language
- `--framework FRAMEWORK` - Specify framework (django, react, etc.)
- `--style STYLE` - Code style (functional, oop, etc.)
- `--output FILE` - Save to file
- `--interactive` - Interactive code generation

### analyze - File and Content Analysis

Analyze files, code, or text content:

```bash
# Analyze a single file
claif analyze README.md "Summarize this documentation"

# Multiple files
claif analyze *.py "Review this codebase for security issues"

# Specific analysis type
claif analyze --type security app.py "Find potential vulnerabilities"

# With custom prompt
claif analyze data.csv "What patterns do you see in this data?"
```

**Analysis Types:**
- `security` - Security vulnerability analysis
- `performance` - Performance optimization suggestions
- `style` - Code style and best practices
- `documentation` - Documentation quality review
- `bugs` - Bug detection and fixing
- `architecture` - Architectural analysis

**Options:**
- `--type TYPE` - Analysis type
- `--recursive` - Analyze directories recursively
- `--exclude PATTERN` - Exclude file patterns
- `--output FILE` - Save analysis report
- `--format FORMAT` - Report format (text, json, html)

## Advanced Commands

### session - Session Management

Manage conversation sessions and context:

```bash
# List all sessions
claif session list

# Start new session
claif session start --name research_project

# Resume existing session
claif session resume research_project

# Show session details
claif session show research_project

# Export session
claif session export research_project > session.json

# Import session
claif session import session.json

# Delete session
claif session delete old_project

# Branch session for experimentation
claif session branch research_project experiment_1

# Merge sessions
claif session merge experiment_1 research_project
```

**Session Options:**
- `--name NAME` - Session name
- `--provider PROVIDER` - Default provider for session
- `--tags TAG1,TAG2` - Session tags
- `--description TEXT` - Session description

### config - Configuration Management

Manage Claif configuration:

```bash
# Show all configuration
claif config show

# Show specific section
claif config show claude

# Set configuration value
claif config set general.provider claude
claif config set claude.model claude-3-opus-20240229

# Get configuration value
claif config get claude.api_key

# Unset value (revert to default)
claif config unset claude.temperature

# Reset configuration
claif config reset
claif config reset claude  # Reset specific section

# Validate configuration
claif config validate

# Test configuration
claif config test --provider claude

# Export configuration
claif config export > backup.toml

# Import configuration
claif config import backup.toml
```

### providers - Provider Management

Manage AI providers:

```bash
# List available providers
claif providers list

# Show provider details
claif providers show claude

# Check provider status
claif providers status
claif providers status claude

# Test provider connection
claif providers test claude

# Refresh provider cache
claif providers refresh

# Install provider package
claif providers install claif_gem

# Update provider packages
claif providers update
```

**Provider Information:**
```bash
$ claif providers list
Available Providers:
  claude (claif_cla)     ✓ Configured
  gemini (claif_gem)     ✓ Configured  
  codex (claif_cod)      ✗ Missing API key

$ claif providers show claude
Provider: Claude (Anthropic)
Package: claif_cla v1.0.1
Models: claude-3-opus, claude-3-sonnet, claude-3-haiku
Status: ✓ Available
API Key: ✓ Configured
Current Model: claude-3-sonnet-20240229
```

### tools - MCP Tool Management

Manage Model Context Protocol tools:

```bash
# List available tools
claif tools list

# Show tool details
claif tools show calculator

# Enable/disable tools
claif tools enable web_search
claif tools disable file_writer

# Test tool functionality
claif tools test calculator "2 + 2"

# Install new tools
claif tools install my_custom_tool

# Tool configuration
claif tools config calculator --timeout 10
```

## Batch Operations

### batch - Process Multiple Inputs

Process multiple files or inputs in batch:

```bash
# Process multiple files
claif batch analyze *.py "Review each file for bugs"

# Batch with custom prompt per file
claif batch process documents/ --prompt "Summarize this document: {filename}"

# Parallel processing
claif batch --parallel 5 analyze logs/*.log "Extract error patterns"

# Save results to directory
claif batch --output results/ analyze src/ "Document each module"
```

**Batch Options:**
- `--parallel N` - Number of parallel operations
- `--output DIR` - Output directory
- `--format FORMAT` - Output format
- `--continue-on-error` - Don't stop on errors
- `--progress` - Show progress bar

### pipeline - Command Pipelines

Chain multiple operations:

```bash
# Analysis pipeline
claif pipeline \
  "analyze *.py --type security" \
  "ask 'Prioritize these security issues by severity'" \
  "code 'Generate fix for the highest priority issue'"

# Data processing pipeline
claif pipeline \
  "analyze data.csv 'Extract key statistics'" \
  "ask 'What insights can we derive?'" \
  "code 'Create a Python script to visualize this data'"
```

## Output and Formatting

### Output Formats

Control output formatting:

```bash
# Text output (default)
claif ask "Hello" --format text

# JSON output
claif ask "List 3 colors" --format json
# Output: {"response": "1. Red\n2. Blue\n3. Green", "provider": "claude"}

# YAML output
claif ask "Describe a dog" --format yaml
# Output:
# response: |
#   A dog is a domesticated mammal...
# provider: claude
# model: claude-3-sonnet

# Markdown output
claif ask "Explain APIs" --format markdown
```

### Streaming Output

Enable real-time streaming:

```bash
# Stream responses as they're generated
claif ask --stream "Write a short story"

# Disable streaming for complete responses
claif ask --no-stream "Generate code"
```

### Custom Templates

Use custom output templates:

```bash
# Custom template file
echo "Provider: {provider}\nModel: {model}\nResponse: {response}" > template.txt

# Use template
claif ask "Hello" --template template.txt
```

## File Operations

### Input from Files

Read input from files:

```bash
# Read prompt from file
claif ask < prompt.txt

# Analyze file content
claif analyze code.py "Review this code"

# Multiple files
claif analyze *.md "Summarize these documents"
```

### Output to Files

Save output to files:

```bash
# Save to file
claif ask "Explain quantum physics" > explanation.md

# Append to file
claif ask "Add more details" >> explanation.md

# Save with metadata
claif ask "Hello" --output result.json --format json
```

## Environment and Context

### Environment Variables

Use environment variables in commands:

```bash
# Use environment variables
export TOPIC="machine learning"
claif ask "Explain $TOPIC basics"

# Provider selection via environment
CLAIF_PROVIDER=gemini claif ask "Quick question"
```

### Working Directory Context

Set context for file operations:

```bash
# Change to project directory
cd /path/to/project

# Analyze with project context
claif analyze . "Review this entire project"

# Use specific working directory
claif --workdir /path/to/project analyze src/ "Code review"
```

## Scripting and Automation

### Shell Integration

Use Claif in shell scripts:

```bash
#!/bin/bash
# analyze_project.sh

# Set up variables
PROJECT_DIR="/path/to/project"
OUTPUT_DIR="./analysis_results"

# Analyze different aspects
claif analyze "$PROJECT_DIR/src" "Security review" > "$OUTPUT_DIR/security.md"
claif analyze "$PROJECT_DIR/tests" "Test coverage analysis" > "$OUTPUT_DIR/tests.md"
claif analyze "$PROJECT_DIR/docs" "Documentation review" > "$OUTPUT_DIR/docs.md"

# Generate summary
claif ask "Summarize these analysis reports" \
  < "$OUTPUT_DIR"/*.md \
  > "$OUTPUT_DIR/summary.md"
```

### JSON Processing

Process JSON output with tools like `jq`:

```bash
# Extract specific fields
claif ask "List 3 programming languages" --format json | jq '.response'

# Process multiple responses
claif batch analyze *.py "Rate code quality 1-10" --format json | \
  jq -r '.[] | "\(.file): \(.response)"'
```

### Error Handling in Scripts

Handle errors gracefully:

```bash
#!/bin/bash
# robust_analysis.sh

if ! claif providers test claude; then
    echo "Claude provider not available, switching to Gemini"
    PROVIDER="gemini"
else
    PROVIDER="claude"
fi

claif ask --provider "$PROVIDER" "Analyze this code" < code.py || {
    echo "Analysis failed, trying with different provider"
    claif ask --provider "codex" "Analyze this code" < code.py
}
```

## Performance and Optimization

### Parallel Processing

Speed up batch operations:

```bash
# Process files in parallel
claif batch --parallel 10 analyze src/**/*.py "Code review"

# Parallel with different providers
claif ask "Question 1" --provider claude &
claif ask "Question 2" --provider gemini &
claif ask "Question 3" --provider codex &
wait
```

### Caching

Enable response caching:

```bash
# Enable caching
claif config set cache.enabled true
claif config set cache.ttl 3600  # 1 hour

# Cache-aware queries
claif ask "What is Python?" --cache-key "python_basics"
```

### Timeouts and Retries

Configure timeouts and retries:

```bash
# Set timeout
claif ask "Complex question" --timeout 300

# Configure retries
claif config set general.max_retries 3
claif config set general.retry_delay 5
```

## Debugging and Troubleshooting

### Debug Mode

Enable detailed debugging:

```bash
# Global debug mode
claif --debug ask "Test question"

# Provider-specific debugging
claif ask "Test" --provider claude --debug

# Save debug info to file
claif --debug ask "Test" 2> debug.log
```

### Verbose Output

Show detailed operation information:

```bash
# Verbose mode
claif --verbose ask "Hello"

# Show request/response details
claif --trace ask "Hello"
```

### Health Checks

Check system health:

```bash
# Overall system check
claif doctor

# Provider-specific checks
claif doctor --provider claude

# Network connectivity test
claif doctor --network

# Configuration validation
claif doctor --config
```

## Keyboard Shortcuts (Interactive Mode)

When in interactive chat mode:

| Shortcut | Action |
|----------|--------|
| `Ctrl+C` | Cancel current input |
| `Ctrl+D` | Exit chat mode |
| `Ctrl+L` | Clear screen |
| `Up/Down` | Navigate command history |
| `Tab` | Auto-complete commands |
| `Ctrl+R` | Search command history |

## Exit Codes

Claif uses standard exit codes:

| Code | Meaning |
|------|---------|
| `0` | Success |
| `1` | General error |
| `2` | Configuration error |
| `3` | Provider error |
| `4` | Network error |
| `5` | Authentication error |
| `130` | Interrupted by user (Ctrl+C) |

## Best Practices

### 1. Use Appropriate Commands

```bash
# Good: Use specific commands
claif code "Python function"      # For code generation
claif analyze file.py "Review"    # For file analysis
claif ask "What is X?"            # For questions

# Avoid: Generic commands for specific tasks
# claif ask "Generate Python code"  # Use 'code' instead
```

### 2. Leverage Sessions

```bash
# For related work, use sessions
claif session start --name "project_review"
claif analyze src/ "Initial review"
claif ask "What are the main issues?"
claif code "Fix the authentication bug"
```

### 3. Choose Right Providers

```bash
# Quick answers
claif ask --provider gemini "What's 2+2?"

# Complex analysis
claif analyze --provider claude large_document.pdf

# Code generation
claif code --provider codex "API endpoint"
```

### 4. Use Batch Operations

```bash
# Instead of individual commands
# claif analyze file1.py "review"
# claif analyze file2.py "review"

# Use batch processing
claif batch analyze *.py "Code review"
```

## Summary

The Claif CLI provides:

- **Flexible command structure** for different AI tasks
- **Multiple output formats** for integration
- **Session management** for complex workflows
- **Batch processing** for efficiency
- **Provider abstraction** for seamless switching
- **Rich debugging** and troubleshooting tools

Master these commands to unlock the full potential of unified AI interactions from your terminal.

Next steps:
- [API Reference](api-reference.md) - Programmatic usage
- [Development](development.md) - Extend Claif functionality
- [Troubleshooting](troubleshooting.md) - Solve common issues