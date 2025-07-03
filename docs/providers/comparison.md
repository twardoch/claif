---
layout: default  
title: Provider Comparison
parent: Providers
nav_order: 2
---

# Provider Comparison Guide

Compare features, capabilities, and use cases across all Claif providers.

## Quick Comparison Table

| Feature | Claude (claif_cla) | Gemini (claif_gem) | Codex (claif_cod) |
|---------|-------------------|-------------------|-------------------|
| **Company** | Anthropic | Google | OpenAI |
| **Best For** | General assistance, analysis | Multimodal tasks, reasoning | Code generation |
| **Streaming** | ✅ Yes | ✅ Yes | ✅ Yes |
| **Vision** | ✅ Yes | ✅ Yes | ❌ No |
| **Tools/Functions** | ✅ Yes (MCP) | ✅ Yes | ✅ Yes |
| **Context Length** | 200K tokens | 1M tokens | 128K tokens |
| **Session Memory** | ✅ Built-in | ❌ Stateless | ⚠️ Limited |
| **Pricing Model** | Per token | Free tier + paid | Per token |
| **Rate Limits** | Generous | Limited free | Varies by tier |
| **Response Speed** | Fast | Very fast | Fast |
| **Code Quality** | Excellent | Good | Best in class |

## Detailed Provider Analysis

### Claude (claif_cla)

**Strengths:**
- Excellent reasoning and analysis capabilities
- Strong safety features and alignment
- Comprehensive session management
- MCP (Model Context Protocol) tool support
- Vision capabilities for image analysis
- Large context window (200K tokens)

**Best Use Cases:**
- Complex reasoning tasks
- Long-form content creation
- Code review and explanation
- Research and analysis
- Multi-turn conversations
- Document analysis with vision

**Unique Features:**
- Session branching and merging
- Approval strategies for tool use
- Built-in safety filters
- Artifacts for code/content
- Constitutional AI principles

**Example Usage:**
```bash
# Long conversation with session
claif-cla "Let's analyze this codebase" --session project-review

# Image analysis
claif-cla "What's in this diagram?" --images architecture.png

# Tool usage with approval
claif-cla "Search for Python async patterns" --tools web_search
```

**Limitations:**
- No real-time data without tools
- Rate limits on free tier
- Occasional over-cautiousness

### Gemini (claif_gem)

**Strengths:**
- Massive context window (1M tokens)
- Excellent multimodal capabilities
- Very fast response times
- Free tier available
- Strong at mathematical reasoning
- Good multilingual support

**Best Use Cases:**
- Document analysis and summarization
- Multimodal tasks (text + images)
- Quick queries and responses
- Educational content
- Creative writing
- Data analysis

**Unique Features:**
- 1 million token context
- Native multimodal design
- Multiple model sizes
- Integration with Google services
- Grounding with Google Search

**Example Usage:**
```bash
# Large document analysis
claif-gem "Summarize this book" --file book.pdf --model gemini-1.5-pro

# Multimodal query
claif-gem "Compare these charts" --images chart1.png chart2.png

# Quick reasoning
claif-gem "Solve this math problem" --model gemini-pro
```

**Limitations:**
- Limited free tier quota
- No persistent sessions
- Less code-focused than others
- Occasional hallucinations

### Codex (claif_cod)

**Strengths:**
- Best-in-class code generation
- Excellent understanding of programming concepts
- Strong at debugging and optimization
- Supports many programming languages
- Good at following coding standards
- Integrates well with development workflows

**Best Use Cases:**
- Code generation and completion
- Bug fixing and debugging
- Code refactoring
- API integration code
- Test generation
- Documentation generation

**Unique Features:**
- Specialized code training
- Fill-in-the-middle capability
- Code explanation modes
- Integration with GitHub Copilot
- Fine-tuning available

**Example Usage:**
```bash
# Generate function
claif-cod "Write a Python async web scraper"

# Debug code
claif-cod "Fix this TypeScript error" --file app.ts

# Refactor code
claif-cod "Refactor to use design patterns" --action-mode review
```

**Limitations:**
- Primarily code-focused
- No vision capabilities
- Higher cost per token
- Limited general knowledge

## Performance Comparison

### Response Time

```
Gemini  : ████████░░ (Fastest)
Claude  : ███████░░░ (Fast)
Codex   : ███████░░░ (Fast)
```

### Context Length

```
Gemini  : ████████████████████ (1M tokens)
Claude  : ████░░░░░░░░░░░░░░░░ (200K tokens)  
Codex   : ██░░░░░░░░░░░░░░░░░░ (128K tokens)
```

### Code Quality

```
Codex   : ████████████████████ (Best)
Claude  : ████████████████░░░░ (Excellent)
Gemini  : ████████████░░░░░░░░ (Good)
```

## Cost Analysis

### Pricing Models

**Claude:**
- Input: $3/million tokens
- Output: $15/million tokens
- Cached input: $0.30/million tokens

**Gemini:**
- Free tier: 60 queries/minute
- Pro tier: $7/million characters
- Flash: $0.35/million characters

**Codex:**
- GPT-4: $30/million tokens (input)
- GPT-4: $60/million tokens (output)
- GPT-3.5: $0.50/million tokens

### Cost Optimization Tips

1. **Use appropriate models**:
   ```bash
   # Quick query - use faster/cheaper model
   claif query "What's 2+2?" --provider gemini --model gemini-flash
   
   # Complex task - use powerful model
   claif query "Analyze this architecture" --provider claude --model claude-3-opus
   ```

2. **Cache responses**:
   ```bash
   # Enable caching for repeated queries
   claif config set cache.enabled true
   ```

3. **Batch requests**:
   ```python
   # Process multiple items efficiently
   async def batch_process(items):
       async with claif.Client() as client:
           tasks = [client.query(item) for item in items]
           return await asyncio.gather(*tasks)
   ```

## Feature-Specific Comparison

### Vision Capabilities

**Claude:**
- High-quality image understanding
- Can read text in images
- Diagram and chart analysis
- Multiple images per query

**Gemini:**
- Native multimodal design
- Video frame analysis
- Real-time image generation
- OCR capabilities

**Codex:**
- No vision support
- Text-only input/output

### Tool/Function Support

**Claude:**
- MCP protocol support
- Built-in tool approval
- Custom tool definitions
- Parallel tool execution

**Gemini:**
- Function calling support
- Google service integration
- Limited tool ecosystem
- Sequential execution

**Codex:**
- Function generation
- API integration code
- No direct tool execution
- Code-based solutions

### Session Management

**Claude:**
```bash
# Full session support
claif-cla "Start project" --session my-project
claif-cla "Continue where we left off" --session my-project
claif-cla "Show session history" --session my-project --history
```

**Gemini:**
```bash
# No built-in sessions
# Must manage context manually
claif-gem "Previous context: [...]" 
```

**Codex:**
```bash
# Limited session support
# Best for single-turn code generation
claif-cod "Generate function" --working-dir ./project
```

## Choosing the Right Provider

### Decision Tree

```
Need code generation?
├── Yes → Codex
└── No
    ├── Need vision/multimodal?
    │   ├── Yes → Gemini or Claude
    │   └── No
    │       ├── Need large context?
    │       │   ├── Yes → Gemini
    │       │   └── No
    │       │       ├── Need session memory?
    │       │       │   ├── Yes → Claude
    │       │       │   └── No → Any provider
```

### Use Case Recommendations

**Choose Claude for:**
- Complex reasoning tasks
- Long conversations
- Safety-critical applications
- Professional writing
- Code review and analysis

**Choose Gemini for:**
- Large document processing
- Quick responses
- Multimodal tasks
- Cost-sensitive applications
- Educational use

**Choose Codex for:**
- Code generation
- API development
- Test creation
- Code refactoring
- Technical documentation

## Multi-Provider Strategies

### Comparative Analysis

```bash
# Get perspectives from all providers
claif query-all "What's the best approach for microservices?"
```

### Provider Routing

```python
# Route based on task type
async def smart_query(prompt: str) -> Message:
    if "code" in prompt.lower():
        return await claif.query(prompt, provider=Provider.CODEX)
    elif "image" in prompt.lower():
        return await claif.query(prompt, provider=Provider.GEMINI)
    else:
        return await claif.query(prompt, provider=Provider.CLAUDE)
```

### Fallback Chains

```python
# Fallback to other providers on failure
async def query_with_fallback(prompt: str) -> Message:
    providers = [Provider.CLAUDE, Provider.GEMINI, Provider.CODEX]
    
    for provider in providers:
        try:
            return await claif.query(prompt, provider=provider)
        except ProviderError:
            continue
    
    raise Exception("All providers failed")
```

## Conclusion

Each provider has unique strengths:

- **Claude**: Best for reasoning and safety
- **Gemini**: Best for scale and multimodal
- **Codex**: Best for code generation

Choose based on your specific needs, and don't hesitate to use multiple providers for different tasks. The Claif framework makes it easy to switch between providers or use them together.