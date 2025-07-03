---
layout: default
title: Examples & Tutorials
nav_order: 8
has_children: true
---

# Examples and Tutorials

Practical examples and step-by-step tutorials for using Claif effectively.

## Basic Examples

### Simple Query
```bash
# Basic query with automatic provider selection
claif query "Explain Python decorators"

# Query with specific provider
claif query "What is machine learning?" --provider claude

# Verbose output for debugging
claif query "Debug this error" --provider gemini --verbose
```

### Configuration Examples
```bash
# Interactive configuration setup
claif config

# List available providers
claif list

# Check current configuration
claif config show
```

## Programming Examples

### Python API Usage
```python
import asyncio
from claif import ClaifClient, ClaifOptions

async def main():
    client = ClaifClient()
    
    # Simple query
    response = await client.query(
        "What is the capital of France?", 
        ClaifOptions(provider="gemini")
    )
    print(response.content)
    
    # Multiple providers
    responses = await client.query_all(
        "Explain quantum computing",
        ClaifOptions(providers=["claude", "gemini"])
    )
    
    for provider, response in responses.items():
        print(f"{provider}: {response.content[:100]}...")

asyncio.run(main())
```

### Error Handling
```python
from claif import ClaifClient, ProviderError, ConfigurationError

async def robust_query(prompt: str):
    client = ClaifClient()
    
    try:
        response = await client.query(prompt)
        return response.content
    except ConfigurationError as e:
        print(f"Configuration issue: {e}")
        print("Run 'claif config' to set up API keys")
    except ProviderError as e:
        print(f"Provider error: {e}")
        print("Trying different provider...")
        # Retry with different provider
        response = await client.query(prompt, provider="fallback")
        return response.content
```

## Provider-Specific Examples

### Claude Provider (`claif_cla`)
```bash
# Claude with tool usage
claif query "Analyze this code file" --provider claude --tools

# Session management
claif query "Start a coding session" --provider claude --session my-project

# Vision capabilities  
claif query "Describe this image" --provider claude --image path/to/image.jpg
```

### Gemini Provider (`claif_gem`)
```bash
# Gemini with context length optimization
claif query "Long analysis task" --provider gemini --context-length 32000

# Auto-approval mode
claif query "Quick calculation" --provider gemini --auto-approve

# Debug mode
claif query "Test query" --provider gemini --debug
```

### Codex Provider (`claif_cod`)
```bash
# Code generation
claif query "Create a Python class for user management" --provider codex

# Interactive mode
claif query "Refactor this function" --provider codex --mode interactive

# Safe review mode
claif query "Fix this bug" --provider codex --mode review
```

## Integration Tutorials

### CI/CD Integration
```yaml
# GitHub Actions example
name: AI Code Review
on: [pull_request]

jobs:
  ai-review:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Setup Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.12'
      
      - name: Install Claif
        run: |
          pip install claif claif_claude
          
      - name: AI Code Review
        env:
          ANTHROPIC_API_KEY: ${{ secrets.ANTHROPIC_API_KEY }}
        run: |
          git diff HEAD~1 HEAD > changes.diff
          claif query "Review these code changes: $(cat changes.diff)" \
            --provider claude > review.md
          echo "AI_REVIEW<<EOF" >> $GITHUB_ENV
          cat review.md >> $GITHUB_ENV
          echo "EOF" >> $GITHUB_ENV
```

### Scripting Examples
```bash
#!/bin/bash
# Batch processing script

files=("file1.py" "file2.py" "file3.py")

for file in "${files[@]}"; do
    echo "Analyzing $file..."
    claif query "Review this code for bugs: $(cat $file)" \
        --provider claude \
        --output "review_$file.md"
done

echo "All reviews completed!"
```

## Advanced Patterns

### Custom Workflow
```python
class CodeReviewWorkflow:
    def __init__(self):
        self.client = ClaifClient()
    
    async def full_review(self, file_path: str):
        # Security analysis
        security = await self.client.query(
            f"Security review: {file_path}",
            provider="claude"
        )
        
        # Performance analysis  
        performance = await self.client.query(
            f"Performance review: {file_path}",
            provider="codex"
        )
        
        # Style analysis
        style = await self.client.query(
            f"Style review: {file_path}",
            provider="gemini"
        )
        
        return {
            "security": security,
            "performance": performance,
            "style": style
        }
```

## Navigation

- [Basic Usage](basic.md) - Simple query examples
- [Python API](python.md) - Programmatic usage
- [Provider Examples](providers.md) - Provider-specific usage
- [Integration](integration.md) - CI/CD and automation
- [Advanced Patterns](advanced.md) - Complex workflows