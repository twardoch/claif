# Providers

Claif supports multiple AI providers through dedicated packages. This guide covers the capabilities, configuration, and best practices for each provider.

## Provider Overview

| Provider | Package | Models | Strengths | Use Cases |
|----------|---------|--------|-----------|-----------|
| **Claude** | `claif_cla` | Claude 3 family | Reasoning, analysis, large context | Complex analysis, research, coding |
| **Gemini** | `claif_gem` | Gemini Pro/Flash | Speed, multimodal, efficiency | Quick responses, image analysis |
| **Codex** | `claif_cod` | GPT-4, GPT-3.5 | Code generation, chat | Software development, general chat |

## Claude Provider (`claif_cla`)

### Overview

The Claude provider integrates with Anthropic's Claude models through the Claude Code SDK, providing advanced reasoning capabilities and large context windows.

### Installation

```bash
uv pip install claif_cla
```

### Configuration

```toml
[claude]
api_key = "${ANTHROPIC_API_KEY}"
model = "claude-3-sonnet-20240229"
max_tokens = 4096
temperature = 0.7
top_p = 1.0
top_k = 5
system_prompt = "You are a helpful assistant."
```

### Available Models

| Model | Context | Strengths | Cost |
|-------|---------|-----------|------|
| `claude-3-opus-20240229` | 200K | Most capable, best reasoning | High |
| `claude-3-sonnet-20240229` | 200K | Balanced performance/cost | Medium |
| `claude-3-haiku-20240307` | 200K | Fastest responses | Low |

### Features

#### 1. Large Context Windows

```bash
# Process large files with full context
claif analyze large_document.txt "Summarize the key findings" --provider claude

# Multi-file analysis
claif analyze *.py "Review this codebase for security issues" --provider claude
```

#### 2. Advanced Reasoning

```bash
# Complex problem solving
claif ask --provider claude "Analyze the trade-offs between microservices and monolithic architecture for a team of 5 developers"

# Step-by-step reasoning
claif ask --provider claude "Walk me through the solution to this calculus problem: ∫x²dx"
```

#### 3. Tool Integration

```bash
# Enable tool use
claif config set claude.tools_enabled true

# Use with MCP tools
claif ask --provider claude "Calculate the compound interest on $10,000 at 5% for 10 years using the calculator tool"
```

#### 4. Session Management

```bash
# Start persistent session
claif session start --provider claude --name research_project

# Continue session
claif session resume research_project

# Branch session for experimentation
claif session branch research_project experiment_1
```

### Claude-Specific Commands

```bash
# Claude Code integration
claif claude code "Write a Python web scraper"

# Approval strategies
claif claude set-approval auto      # Auto-approve safe operations
claif claude set-approval review    # Review before execution
claif claude set-approval manual    # Manual approval for all

# Session operations
claif claude session list
claif claude session export research_project > session.json
claif claude session import session.json
```

### Best Practices

#### 1. Context Management

```python
# Use full context for complex tasks
async def analyze_codebase():
    client = ClaifClient(provider="claude")
    
    # Build comprehensive context
    context = []
    for file in glob.glob("src/**/*.py"):
        with open(file) as f:
            context.append(f"File: {file}\n{f.read()}")
    
    full_context = "\n\n".join(context)
    response = await client.send_message(
        f"Analyze this codebase:\n\n{full_context}",
        provider="claude"
    )
    return response
```

#### 2. Structured Outputs

```bash
# Request structured analysis
claif ask --provider claude --format json "Analyze this code and return findings in JSON format with categories: bugs, improvements, security"
```

## Gemini Provider (`claif_gem`)

### Overview

The Gemini provider offers Google's fast and efficient AI models with multimodal capabilities and competitive pricing.

### Installation

```bash
uv pip install claif_gem
```

### Configuration

```toml
[gemini]
api_key = "${GOOGLE_API_KEY}"
model = "gemini-pro"
max_tokens = 2048
temperature = 0.7
top_p = 0.8
top_k = 40

# Safety settings
safety_settings = [
    { category = "HARM_CATEGORY_HARASSMENT", threshold = "BLOCK_MEDIUM_AND_ABOVE" },
    { category = "HARM_CATEGORY_HATE_SPEECH", threshold = "BLOCK_MEDIUM_AND_ABOVE" }
]

# Multimodal settings
vision_enabled = true
max_image_size = "10MB"
```

### Available Models

| Model | Capabilities | Use Cases |
|-------|-------------|-----------|
| `gemini-pro` | Text, code generation | General purpose, coding |
| `gemini-pro-vision` | Text + images | Image analysis, multimodal tasks |
| `gemini-flash` | Fast text generation | Quick responses, high-volume |

### Features

#### 1. Fast Responses

```bash
# Quick answers
claif ask --provider gemini "What's the current time in Tokyo?"

# Rapid code generation
claif code --provider gemini "Python function to validate email addresses"
```

#### 2. Multimodal Capabilities

```bash
# Image analysis
claif analyze image.jpg "Describe what you see in this image" --provider gemini

# Image + text context
claif ask --provider gemini "Based on this diagram (image.png), explain the workflow"
```

#### 3. Cost-Effective Processing

```bash
# Batch processing with Flash model
claif config set gemini.model gemini-flash
claif batch process *.txt "Summarize each file" --provider gemini
```

#### 4. Safety Controls

```bash
# Configure safety settings
claif gemini safety set harassment BLOCK_MEDIUM_AND_ABOVE
claif gemini safety set hate_speech BLOCK_LOW_AND_ABOVE

# Check safety settings
claif gemini safety show
```

### Gemini-Specific Commands

```bash
# Model switching
claif gemini model set gemini-pro-vision
claif gemini model list

# Image processing
claif gemini image analyze photo.jpg "What objects are in this image?"
claif gemini image describe *.png --batch

# Performance tuning
claif gemini tune set top_k 20
claif gemini tune set temperature 0.3
```

### Best Practices

#### 1. Model Selection

```python
# Choose model based on task
async def smart_model_selection(task_type: str, has_images: bool):
    if has_images:
        model = "gemini-pro-vision"
    elif task_type == "quick_response":
        model = "gemini-flash"
    else:
        model = "gemini-pro"
    
    client = ClaifClient(provider="gemini")
    return await client.send_message(prompt, model=model)
```

#### 2. Image Processing

```bash
# Optimize images for processing
claif gemini image resize image.jpg --max-size 4MB
claif gemini image analyze resized_image.jpg "Extract text from this document"
```

## Codex Provider (`claif_cod`)

### Overview

The Codex provider integrates with OpenAI's models, offering strong code generation capabilities and general-purpose chat functionality.

### Installation

```bash
uv pip install claif_cod
```

### Configuration

```toml
[codex]
api_key = "${OPENAI_API_KEY}"
model = "gpt-4"
max_tokens = 4096
temperature = 0.7
top_p = 1.0
frequency_penalty = 0.0
presence_penalty = 0.0

# Organization (optional)
organization = "org-your-org-id"

# Function calling
tools_enabled = true
function_timeout = 30
```

### Available Models

| Model | Context | Strengths | Cost |
|-------|---------|-----------|------|
| `gpt-4` | 8K/32K | Best reasoning, most capable | High |
| `gpt-4-turbo` | 128K | Faster, same capabilities | High |
| `gpt-3.5-turbo` | 16K | Cost-effective, good performance | Low |

### Features

#### 1. Code Generation

```bash
# Generate complete functions
claif code --provider codex "Python class for a binary search tree with insert, search, and delete methods"

# Code explanation
claif analyze code.py --provider codex "Explain how this algorithm works"
```

#### 2. Interactive Development

```bash
# Code review mode
claif codex review --interactive src/

# Auto-fix suggestions
claif codex fix "TypeError: 'NoneType' object is not iterable" --file buggy.py
```

#### 3. Function Calling

```bash
# Enable function calling
claif config set codex.tools_enabled true

# Use with external APIs
claif ask --provider codex "Get the current weather in New York and calculate if I need a jacket (temp < 60°F)"
```

#### 4. Project Context

```bash
# Set working directory context
claif codex context set /path/to/project

# Project-aware suggestions
claif codex suggest "How should I structure the database models for this project?"
```

### Codex-Specific Commands

```bash
# Code operations
claif codex generate "REST API for user management" --language python
claif codex refactor messy_code.py --output clean_code.py
claif codex test generate_tests.py --framework pytest

# Action modes
claif codex mode set review      # Review before execution
claif codex mode set interactive # Interactive approval
claif codex mode set auto        # Auto-execute safe operations

# Project integration
claif codex project init        # Initialize project context
claif codex project scan        # Scan for code patterns
claif codex project stats       # Show project statistics
```

### Best Practices

#### 1. Context-Aware Development

```python
# Maintain project context
async def code_with_context(request: str, project_path: str):
    client = ClaifClient(provider="codex")
    
    # Include relevant project files
    context_files = []
    for file in ["requirements.txt", "README.md", "src/main.py"]:
        if os.path.exists(file):
            with open(file) as f:
                context_files.append(f"File: {file}\n{f.read()}")
    
    context = "\n\n".join(context_files)
    prompt = f"Project context:\n{context}\n\nRequest: {request}"
    
    return await client.send_message(prompt, provider="codex")
```

#### 2. Safe Code Execution

```bash
# Always review generated code
claif codex mode set review

# Use sandboxed execution
claif codex execute --sandbox code.py

# Validate before running
claif codex validate script.py --check-security
```

## Provider Comparison

### Performance Characteristics

| Aspect | Claude | Gemini | Codex |
|--------|--------|--------|-------|
| **Response Speed** | Medium | Fast | Medium |
| **Context Length** | 200K tokens | 32K tokens | 128K tokens |
| **Code Quality** | Excellent | Good | Excellent |
| **Reasoning** | Superior | Good | Very Good |
| **Cost Efficiency** | Medium | High | Medium |
| **Multimodal** | Text only | Text + Images | Text only |

### Use Case Recommendations

#### For Research and Analysis

```bash
# Best choice: Claude for deep analysis
claif ask --provider claude "Analyze the implications of quantum computing on current cryptographic standards"
```

#### For Quick Responses

```bash
# Best choice: Gemini for speed
claif ask --provider gemini "What's the syntax for Python list comprehensions?"
```

#### For Code Generation

```bash
# Best choice: Codex for code-specific tasks
claif code --provider codex "Implement a rate limiter using Redis"
```

#### For Image Analysis

```bash
# Only choice: Gemini with vision
claif analyze --provider gemini diagram.png "Extract the flowchart steps"
```

## Provider Switching

### Dynamic Provider Selection

```bash
# Switch provider per command
claif ask --provider claude "Complex reasoning task"
claif ask --provider gemini "Quick factual question"
claif code --provider codex "Generate Python code"
```

### Automatic Provider Selection

```toml
# Configure automatic selection rules
[auto_selection]
enabled = true

# Rules based on task type
[auto_selection.rules]
code_generation = "codex"
image_analysis = "gemini"
complex_reasoning = "claude"
quick_response = "gemini"
```

### Fallback Configuration

```toml
[fallback]
enabled = true
order = ["claude", "gemini", "codex"]
retry_delay = 2.0
max_retries = 3
```

## Provider-Specific Error Handling

### Claude Errors

```python
from claif.providers.claude import ClaudeRateLimitError, ClaudeContextLimitError

try:
    response = await client.send_message(prompt, provider="claude")
except ClaudeRateLimitError:
    # Wait and retry
    await asyncio.sleep(60)
    response = await client.send_message(prompt, provider="claude")
except ClaudeContextLimitError:
    # Reduce context size
    shorter_prompt = prompt[:50000]  # Truncate
    response = await client.send_message(shorter_prompt, provider="claude")
```

### Gemini Errors

```python
from claif.providers.gemini import GeminiSafetyError, GeminiQuotaError

try:
    response = await client.send_message(prompt, provider="gemini")
except GeminiSafetyError as e:
    # Adjust safety settings or rephrase
    print(f"Content blocked: {e.category}")
except GeminiQuotaError:
    # Switch to different model or provider
    response = await client.send_message(prompt, provider="claude")
```

### Codex Errors

```python
from claif.providers.codex import CodexTokenLimitError, CodexModerationError

try:
    response = await client.send_message(prompt, provider="codex")
except CodexTokenLimitError:
    # Use a model with larger context
    response = await client.send_message(prompt, provider="codex", model="gpt-4-turbo")
except CodexModerationError:
    # Content flagged by OpenAI moderation
    print("Content violates usage policies")
```

## Monitoring and Analytics

### Provider Usage Statistics

```bash
# View usage stats
claif stats show --provider claude --period week
claif stats show --all-providers --period month

# Cost analysis
claif costs estimate --provider gemini --tokens 10000
claif costs compare --providers claude,gemini,codex --task "code generation"
```

### Performance Monitoring

```toml
[monitoring]
enabled = true
metrics = ["response_time", "token_usage", "error_rate"]

[monitoring.alerts]
slow_response_threshold = 30  # seconds
error_rate_threshold = 0.05   # 5%
```

## Best Practices Summary

### 1. Choose the Right Provider

- **Claude**: Complex analysis, research, large documents
- **Gemini**: Quick responses, image analysis, cost efficiency
- **Codex**: Code generation, software development

### 2. Optimize for Cost

```bash
# Use cheaper models for simple tasks
claif config set gemini.model gemini-flash  # For quick queries
claif config set codex.model gpt-3.5-turbo  # For simple code tasks
```

### 3. Handle Errors Gracefully

```python
# Implement provider fallbacks
providers = ["claude", "gemini", "codex"]
for provider in providers:
    try:
        response = await client.send_message(prompt, provider=provider)
        break
    except Exception as e:
        print(f"{provider} failed: {e}")
        continue
```

### 4. Monitor Usage

```bash
# Regular usage reviews
claif stats monthly-report
claif costs budget-check
```

## Next Steps

- [CLI Usage](cli-usage.md) - Master provider-specific commands
- [API Reference](api-reference.md) - Programmatic provider management
- [Development](development.md) - Create custom providers