# Troubleshooting

This comprehensive troubleshooting guide helps you diagnose and resolve common issues with Claif installation, configuration, and usage.

## Quick Diagnostics

### Health Check Command

Start with the built-in diagnostic tool:

```bash
# Overall system check
claif doctor

# Provider-specific check
claif doctor --provider claude

# Network connectivity test
claif doctor --network

# Configuration validation
claif doctor --config
```

Example output:
```
Claif Health Check Report
═════════════════════════

✓ Python version: 3.12.1 (compatible)
✓ Claif version: 1.0.1
✓ Configuration: Valid

Providers:
✓ claude (claif_cla 1.0.1) - Configured
✗ gemini (claif_gem) - Missing API key
✗ codex - Package not installed

Network:
✓ Internet connectivity
✓ DNS resolution
⚠ Slow response from claude API (2.3s)

Recommendations:
• Install claif_cod for Codex support
• Set GOOGLE_API_KEY for Gemini
• Check Claude API rate limits
```

### Debug Mode

Enable detailed debugging:

```bash
# Global debug mode
claif --debug ask "test question"

# Provider-specific debugging
claif ask "test" --provider claude --debug

# Save debug output
claif --debug ask "test" 2> debug.log
```

## Installation Issues

### Command Not Found

**Problem**: `claif: command not found`

**Causes & Solutions**:

1. **Claif not in PATH**:
   ```bash
   # Check installation location
   pip show claif
   
   # Add to PATH (bash/zsh)
   echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc
   source ~/.bashrc
   
   # Or use full path
   ~/.local/bin/claif --version
   ```

2. **Virtual environment not activated**:
   ```bash
   # Activate your virtual environment
   source venv/bin/activate  # Linux/macOS
   venv\Scripts\activate     # Windows
   
   # Verify claif is available
   which claif
   ```

3. **Installation failed**:
   ```bash
   # Reinstall claif
   pip uninstall claif
   pip install claif
   
   # Or with uv
   uv pip install claif
   ```

### Package Installation Errors

**Problem**: `pip install claif` fails

**Causes & Solutions**:

1. **Python version incompatibility**:
   ```bash
   # Check Python version
   python --version
   
   # Claif requires Python 3.12+
   # Update Python or use pyenv
   pyenv install 3.12.1
   pyenv global 3.12.1
   ```

2. **Network/proxy issues**:
   ```bash
   # Use different index
   pip install --index-url https://pypi.python.org/simple/ claif
   
   # Configure proxy
   pip install --proxy http://proxy.company.com:8080 claif
   
   # Use trusted hosts
   pip install --trusted-host pypi.org --trusted-host pypi.python.org claif
   ```

3. **Permission errors**:
   ```bash
   # Install for user only
   pip install --user claif
   
   # Fix permissions (Linux/macOS)
   sudo chown -R $USER ~/.local/
   ```

### Provider Package Issues

**Problem**: Provider packages not found

**Solutions**:

```bash
# Check installed packages
pip list | grep claif

# Install missing providers
pip install claif_cla claif_gem claif_cod

# Verify provider registration
claif providers list

# Refresh provider cache
claif providers refresh
```

## Configuration Issues

### API Key Problems

**Problem**: `AuthenticationError: Invalid API key`

**Diagnosis**:
```bash
# Check if API key is set
claif config show claude.api_key

# Verify environment variable
echo $ANTHROPIC_API_KEY

# Test key validity
claif doctor --provider claude
```

**Solutions**:

1. **Set API key correctly**:
   ```bash
   # Via configuration
   claif config set claude.api_key your-actual-key
   
   # Via environment variable
   export ANTHROPIC_API_KEY="your-actual-key"
   
   # Verify it's set
   claif config show claude.api_key
   ```

2. **Check key format**:
   ```bash
   # Claude keys start with 'sk-ant-'
   # Gemini keys are typically 39 characters
   # OpenAI keys start with 'sk-'
   
   # Ensure no extra spaces or quotes
   echo "$ANTHROPIC_API_KEY" | wc -c
   ```

3. **Key permissions**:
   ```bash
   # Ensure your API key has the right permissions
   # Check your provider's dashboard for key status
   curl -H "Authorization: Bearer $ANTHROPIC_API_KEY" \
        https://api.anthropic.com/v1/messages \
        -d '{"model":"claude-3-haiku-20240307","max_tokens":10,"messages":[{"role":"user","content":"hi"}]}'
   ```

### Configuration Loading Issues

**Problem**: Configuration not loading correctly

**Diagnosis**:
```bash
# Show configuration sources
claif config show --sources

# Show effective configuration
claif config effective

# Validate configuration
claif config validate
```

**Solutions**:

1. **Configuration file permissions**:
   ```bash
   # Check file permissions
   ls -la ~/.config/claif/config.toml
   
   # Fix permissions
   chmod 600 ~/.config/claif/config.toml
   ```

2. **TOML syntax errors**:
   ```bash
   # Validate TOML syntax
   python -c "import tomli; tomli.load(open('~/.config/claif/config.toml', 'rb'))"
   
   # Reset configuration if corrupted
   claif config reset
   ```

3. **Environment variable conflicts**:
   ```bash
   # Check for conflicting environment variables
   env | grep CLAIF
   
   # Unset problematic variables
   unset CLAIF_PROVIDER
   ```

## Provider-Specific Issues

### Claude Provider Issues

**Problem**: Claude requests failing

**Common Issues**:

1. **Rate limiting**:
   ```bash
   # Error: Rate limit exceeded
   # Solution: Wait or implement backoff
   claif config set claude.max_retries 5
   claif config set claude.retry_delay 10
   ```

2. **Model not available**:
   ```bash
   # Check available models
   claif providers show claude
   
   # Use supported model
   claif config set claude.model claude-3-sonnet-20240229
   ```

3. **Context length exceeded**:
   ```bash
   # Reduce context or use a model with larger context
   claif ask --max-tokens 2000 "shorter question"
   ```

### Gemini Provider Issues

**Problem**: Gemini safety errors

**Solutions**:

1. **Adjust safety settings**:
   ```bash
   # Configure safety thresholds
   claif config set gemini.safety_settings '[
     {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"}
   ]'
   ```

2. **Use different model**:
   ```bash
   # Try Gemini Flash for less restrictive content policy
   claif config set gemini.model gemini-flash
   ```

### Codex Provider Issues

**Problem**: OpenAI moderation errors

**Solutions**:

1. **Rephrase content**:
   ```bash
   # Avoid flagged content
   # Review OpenAI usage policies
   ```

2. **Use different provider**:
   ```bash
   # Fallback to Claude or Gemini
   claif ask --provider claude "alternative phrasing"
   ```

## Network and Connectivity Issues

### Connection Timeouts

**Problem**: `NetworkError: Connection timeout`

**Solutions**:

1. **Increase timeout**:
   ```bash
   # Global timeout
   claif config set general.timeout 120
   
   # Per-request timeout
   claif ask --timeout 180 "complex question"
   ```

2. **Check network connectivity**:
   ```bash
   # Test internet connection
   ping google.com
   
   # Test provider endpoints
   curl -I https://api.anthropic.com
   curl -I https://generativelanguage.googleapis.com
   curl -I https://api.openai.com
   ```

3. **Proxy configuration**:
   ```bash
   # Configure HTTP proxy
   export HTTP_PROXY=http://proxy.company.com:8080
   export HTTPS_PROXY=http://proxy.company.com:8080
   
   # Or in configuration
   claif config set network.proxy "http://proxy.company.com:8080"
   ```

### SSL/TLS Issues

**Problem**: SSL certificate errors

**Solutions**:

1. **Update certificates**:
   ```bash
   # Update system certificates (Ubuntu/Debian)
   sudo apt-get update && sudo apt-get install ca-certificates
   
   # macOS
   brew install ca-certificates
   ```

2. **Bypass SSL verification (not recommended for production)**:
   ```bash
   claif config set network.verify_ssl false
   ```

## Performance Issues

### Slow Response Times

**Problem**: Responses are very slow

**Diagnosis**:
```bash
# Measure response time
time claif ask "test question"

# Check provider status
claif providers status

# Monitor with debug output
claif --debug ask "test" | grep -i time
```

**Solutions**:

1. **Use faster models**:
   ```bash
   # Switch to faster models
   claif config set claude.model claude-3-haiku-20240307
   claif config set gemini.model gemini-flash
   claif config set codex.model gpt-3.5-turbo
   ```

2. **Optimize requests**:
   ```bash
   # Reduce max_tokens
   claif config set claude.max_tokens 1000
   
   # Enable streaming for perceived speed
   claif config set output.streaming true
   ```

3. **Use connection pooling**:
   ```bash
   # Configure connection pooling
   claif config set performance.max_connections 10
   claif config set performance.keep_alive true
   ```

### High Memory Usage

**Problem**: Claif consuming too much memory

**Solutions**:

1. **Limit context size**:
   ```bash
   # Reduce context length
   claif config set general.max_context_messages 10
   
   # Clear session history
   claif session clear current
   ```

2. **Disable caching**:
   ```bash
   # Disable response caching
   claif config set cache.enabled false
   ```

## CLI and Usage Issues

### Interactive Mode Problems

**Problem**: Interactive chat mode not working

**Solutions**:

1. **Terminal compatibility**:
   ```bash
   # Use different terminal
   # Ensure terminal supports ANSI colors
   
   # Disable colors if needed
   claif chat --no-color
   ```

2. **Input handling issues**:
   ```bash
   # Check readline support
   python -c "import readline; print('Readline available')"
   
   # Use alternative input method
   echo "test message" | claif chat
   ```

### File Processing Issues

**Problem**: Cannot analyze files

**Solutions**:

1. **File permissions**:
   ```bash
   # Check file permissions
   ls -la myfile.txt
   
   # Fix permissions
   chmod 644 myfile.txt
   ```

2. **File encoding**:
   ```bash
   # Check file encoding
   file myfile.txt
   
   # Convert if necessary
   iconv -f ISO-8859-1 -t UTF-8 myfile.txt > myfile_utf8.txt
   ```

3. **File size limits**:
   ```bash
   # Check file size
   du -h myfile.txt
   
   # Split large files
   split -l 1000 large_file.txt chunk_
   ```

## Session Management Issues

### Session Not Saving

**Problem**: Sessions not persisting

**Solutions**:

1. **Check session directory**:
   ```bash
   # Verify session directory exists
   ls -la ~/.config/claif/sessions/
   
   # Create if missing
   mkdir -p ~/.config/claif/sessions/
   chmod 700 ~/.config/claif/sessions/
   ```

2. **Session storage permissions**:
   ```bash
   # Fix permissions
   chmod 600 ~/.config/claif/sessions/*.json
   ```

3. **Session corruption**:
   ```bash
   # Validate session files
   claif session validate
   
   # Repair corrupted sessions
   claif session repair
   ```

## Common Error Messages

### "Provider not available"

```bash
Error: Provider 'claude' is not available

# Solutions:
1. Install provider package: pip install claif_cla
2. Check configuration: claif config show claude
3. Refresh providers: claif providers refresh
```

### "Model not supported"

```bash
Error: Model 'gpt-5' is not supported by provider 'codex'

# Solutions:
1. Check available models: claif providers show codex
2. Use supported model: claif config set codex.model gpt-4
```

### "Context length exceeded"

```bash
Error: Context length exceeds model limit

# Solutions:
1. Reduce context: claif ask --max-tokens 2000 "question"
2. Use model with larger context: claif config set claude.model claude-3-opus
3. Clear session: claif session clear
```

### "Rate limit exceeded"

```bash
Error: Rate limit exceeded, retry after 60 seconds

# Solutions:
1. Wait and retry
2. Configure retries: claif config set general.max_retries 3
3. Use different provider: claif ask --provider gemini "question"
```

## Advanced Debugging

### Logging Configuration

```bash
# Enable detailed logging
claif config set logging.level DEBUG
claif config set logging.file ~/.config/claif/debug.log

# Monitor log file
tail -f ~/.config/claif/debug.log
```

### Network Debugging

```bash
# Trace network requests
export PYTHONPATH=/path/to/claif
python -c "
import logging
logging.basicConfig(level=logging.DEBUG)
import aiohttp
aiohttp.log.client_logger.setLevel(logging.DEBUG)
"

# Use with claif
claif --debug ask "test"
```

### Provider Testing

```bash
# Test individual provider
python -c "
import asyncio
from claif.providers.claude import ClaudeProvider

async def test():
    provider = ClaudeProvider({'api_key': 'your-key'})
    response = await provider.send_message('hello')
    print(response)

asyncio.run(test())
"
```

## Environment-Specific Issues

### Docker Issues

**Problem**: Claif not working in Docker

**Solutions**:

1. **Environment variables**:
   ```dockerfile
   # In Dockerfile
   ENV ANTHROPIC_API_KEY="your-key"
   ENV CLAIF_CONFIG_DIR="/app/config"
   ```

2. **File permissions**:
   ```dockerfile
   # Create claif user
   RUN useradd -m claif
   USER claif
   ```

### CI/CD Issues

**Problem**: Claif failing in CI/CD

**Solutions**:

1. **Environment setup**:
   ```yaml
   # GitHub Actions example
   - name: Setup Claif
     run: |
       pip install claif claif_cla
       claif config set general.provider claude
       claif config set output.color false
     env:
       ANTHROPIC_API_KEY: ${{ secrets.ANTHROPIC_API_KEY }}
   ```

2. **Non-interactive mode**:
   ```bash
   # Disable interactive features
   claif config set output.interactive false
   claif config set output.pager never
   ```

## Getting Help

### Community Resources

1. **GitHub Issues**: [Report bugs](https://github.com/twardoch/claif/issues)
2. **Discussions**: [Ask questions](https://github.com/twardoch/claif/discussions)
3. **Documentation**: [Read docs](https://twardoch.github.io/claif/)

### Reporting Issues

When reporting issues, include:

1. **Environment information**:
   ```bash
   claif doctor > issue_report.txt
   python --version >> issue_report.txt
   pip list | grep claif >> issue_report.txt
   ```

2. **Configuration** (remove sensitive data):
   ```bash
   claif config show > config_sanitized.txt
   # Remove API keys before sharing
   ```

3. **Debug output**:
   ```bash
   claif --debug [command] > debug_output.txt 2>&1
   ```

4. **Steps to reproduce** the issue
5. **Expected vs actual behavior**

### Self-Help Checklist

Before asking for help:

- [ ] Read relevant documentation section
- [ ] Run `claif doctor` to check system health
- [ ] Try with `--debug` flag for detailed output
- [ ] Search existing GitHub issues
- [ ] Test with minimal configuration
- [ ] Verify API keys and permissions
- [ ] Check network connectivity
- [ ] Try different provider if available

## Quick Reference

### Essential Commands

```bash
# Health check
claif doctor

# Debug mode
claif --debug [command]

# Reset configuration
claif config reset

# Check providers
claif providers list

# Test provider
claif providers test [provider]

# Validate config
claif config validate

# Clear cache
claif cache clear

# View logs
tail -f ~/.config/claif/claif.log
```

### Configuration Paths

- **Global config**: `~/.config/claif/config.toml`
- **Project config**: `./claif.toml`
- **Log file**: `~/.config/claif/claif.log`
- **Sessions**: `~/.config/claif/sessions/`
- **Cache**: `~/.config/claif/cache/`

With these troubleshooting techniques, you should be able to diagnose and resolve most Claif issues. For persistent problems, don't hesitate to reach out to the community for support.