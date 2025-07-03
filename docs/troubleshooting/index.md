---
layout: default
title: Troubleshooting
nav_order: 9
has_children: true
---

# Troubleshooting Guide

Solutions for common issues and debugging strategies for Claif.

## Common Installation Issues

### Module Not Found Errors
```
ModuleNotFoundError: No module named 'claif'
```

**Solutions:**
1. Verify installation: `uv pip list | grep claif`
2. Check Python environment: `which python`
3. Reinstall: `uv pip uninstall claif && uv pip install claif`
4. Use virtual environment: `uv venv && source .venv/bin/activate`

### Provider Package Issues
```
ProviderError: No providers found
```

**Solutions:**
1. Install a provider: `uv pip install claif_gem`
2. Check provider registration: `claif list`
3. Verify entry points: `python -c "import claif; print(claif.providers)"`

## Configuration Problems

### API Key Issues
```
ConfigurationError: API key not found for provider 'claude'
```

**Solutions:**
1. Set environment variable: `export ANTHROPIC_API_KEY=your_key`
2. Use config command: `claif config`
3. Check config file: `cat ~/.claif/config.toml`
4. Verify key validity: Test with provider's official tools

### Configuration File Errors
```
ValidationError: Invalid configuration format
```

**Solutions:**
1. Check TOML syntax: Use online TOML validator
2. Reset configuration: `rm ~/.claif/config.toml && claif config`
3. Use example config: Copy from documentation
4. Check file permissions: `ls -la ~/.claif/`

## Provider-Specific Issues

### Claude Provider (`claif_cla`)
**Hanging requests:**
- Check network connectivity
- Verify API key permissions
- Increase timeout: `--timeout 300`
- Use debug mode: `--verbose`

**Tool approval issues:**
- Check approval strategy in config
- Use auto-approve mode cautiously
- Review tool permissions

### Gemini Provider (`claif_gem`)
**CLI not found:**
```
TransportError: Gemini CLI not found
```

**Solutions:**
1. Install Gemini CLI: Follow Google's installation guide
2. Set CLI path: `export GEMINI_CLI_PATH=/usr/local/bin/gemini`
3. Verify installation: `which gemini`
4. Check PATH: `echo $PATH`

**Subprocess hanging:**
- Use shorter prompts
- Check CLI arguments
- Increase timeout settings
- Verify CLI version compatibility

### Codex Provider (`claif_cod`)
**Code execution errors:**
- Review action mode settings
- Use review mode for safety
- Check working directory permissions
- Verify project structure

## Performance Issues

### Slow Response Times
**Diagnosis:**
1. Enable verbose logging: `--verbose`
2. Check network latency: `ping api.anthropic.com`
3. Monitor resource usage: `top` or `htop`
4. Profile code execution

**Solutions:**
- Use faster models when available
- Implement response caching
- Optimize prompt length
- Use concurrent requests for multiple queries

### Memory Usage
**High memory consumption:**
1. Check for memory leaks in long-running processes
2. Use streaming responses when available
3. Limit concurrent requests
4. Clear response caches periodically

## Network and Connectivity

### Timeout Errors
```
ClaifTimeoutError: Request timed out after 120s
```

**Solutions:**
1. Increase timeout: `claif query "prompt" --timeout 300`
2. Check network stability
3. Use shorter prompts
4. Retry with backoff

### Proxy Issues
**Corporate proxy setup:**
```bash
export HTTPS_PROXY=http://proxy.company.com:8080
export HTTP_PROXY=http://proxy.company.com:8080
claif query "test" --provider gemini
```

### SSL Certificate Errors
**Solutions:**
1. Update certificates: `pip install --upgrade certifi`
2. Use custom CA bundle: `export SSL_CERT_FILE=/path/to/bundle.pem`
3. Disable SSL verification (not recommended): `export PYTHONHTTPSVERIFY=0`

## Debugging Strategies

### Enable Debug Logging
```bash
# Maximum verbosity
export CLAIF_LOG_LEVEL=DEBUG
claif query "test" --verbose

# Component-specific logging
export CLAIF_LOG_FILTER="claif.providers.gemini"
claif query "test" --provider gemini --verbose
```

### Inspect Configuration
```bash
# Show current config
claif config show

# Validate configuration
claif config validate

# Test provider connection
claif query "test" --provider claude --dry-run
```

### Analyze Logs
```bash
# Save logs to file
claif query "test" --verbose 2> debug.log

# Filter specific issues
grep -i error debug.log
grep -i timeout debug.log
grep -i "provider" debug.log
```

## Getting Help

### Before Reporting Issues
1. **Update to latest version**: `uv pip install --upgrade claif`
2. **Check known issues**: Review GitHub issues
3. **Test with minimal example**: Isolate the problem
4. **Gather debug information**: Save logs and configuration

### Issue Report Template
```
**Environment:**
- Claif version: `claif --version`
- Python version: `python --version`
- OS: `uname -a`
- Provider packages: `uv pip list | grep claif`

**Problem:**
- Expected behavior:
- Actual behavior:
- Error messages:

**Reproduction:**
- Minimal example:
- Configuration used:
- Debug logs:
```

## Navigation

- [Installation Issues](installation.md) - Setup and dependency problems
- [Configuration Issues](configuration.md) - API keys and settings
- [Provider Issues](providers.md) - Provider-specific problems
- [Performance](performance.md) - Speed and resource optimization
- [Network Issues](network.md) - Connectivity and proxy problems
- [Debugging Guide](debugging.md) - Diagnostic tools and techniques