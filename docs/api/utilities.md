---
layout: default
title: Utilities
parent: API Reference
nav_order: 4
---

# Utilities

Helper functions and utility classes provided by the Claif framework.

## Common Utilities

### Message Formatting

#### `format_response(message, format_type="text")`

Format a message response for display.

```python
from claif.common.utils import format_response
from claif import ClaifClient

client = ClaifClient()
response = client.query("Hello")

# Format as text (default)
text = format_response(response)
print(text)

# Format as markdown
markdown = format_response(response, format_type="markdown")

# Format as JSON
json_str = format_response(response, format_type="json")
```

**Parameters:**
- `message` (Message) - The message to format
- `format_type` (str) - Output format ("text", "markdown", "json", "html")

**Returns:** `str` - Formatted message content

#### `format_metrics(metrics)`

Format performance metrics for display.

```python
from claif.common.utils import format_metrics

# Metrics from a query
metrics = {
    'response_time': 2.34,
    'tokens_used': 150,
    'provider': 'claude',
    'model': 'claude-3-sonnet'
}

formatted = format_metrics(metrics)
print(formatted)
# Output:
# Provider: claude (claude-3-sonnet)
# Response time: 2.34s
# Tokens used: 150
```

**Parameters:**
- `metrics` (Dict[str, Any]) - Metrics dictionary

**Returns:** `str` - Formatted metrics display

### Configuration Utilities

#### `load_config(path=None)`

Load configuration from file with fallback defaults.

```python
from claif.common.utils import load_config

# Load from default location
config = load_config()

# Load from specific path
config = load_config("./custom-config.toml")
```

**Parameters:**
- `path` (Optional[str]) - Path to config file

**Returns:** `Config` - Configuration object

#### `validate_config(config)`

Validate configuration object.

```python
from claif.common.utils import validate_config, load_config
from claif.common.errors import ConfigurationError

config = load_config()
try:
    validate_config(config)
    print("Configuration is valid")
except ConfigurationError as e:
    print(f"Invalid configuration: {e}")
```

**Parameters:**
- `config` (Config) - Configuration to validate

**Raises:** `ConfigurationError` - If configuration is invalid

### Provider Utilities

#### `discover_providers()`

Discover and return available providers.

```python
from claif.common.utils import discover_providers

providers = discover_providers()
print(f"Found providers: {list(providers.keys())}")

# Check specific provider
if 'claude' in providers:
    claude_provider = providers['claude']
    print(f"Claude version: {claude_provider.version}")
```

**Returns:** `Dict[str, Provider]` - Dictionary of provider name to provider instance

#### `get_provider_info(provider_name)`

Get detailed information about a provider.

```python
from claif.common.utils import get_provider_info

info = get_provider_info("claude")
print(f"Name: {info['name']}")
print(f"Version: {info['version']}")
print(f"Available: {info['available']}")
print(f"Description: {info['description']}")
print(f"Models: {info['models']}")
```

**Parameters:**
- `provider_name` (str) - Name of the provider

**Returns:** `Dict[str, Any]` - Provider information

#### `check_provider_health(provider_name, timeout=10.0)`

Check if a provider is healthy and responsive.

```python
from claif.common.utils import check_provider_health

# Quick health check
is_healthy = check_provider_health("claude")
print(f"Claude is healthy: {is_healthy}")

# With custom timeout
is_healthy = check_provider_health("gemini", timeout=5.0)
```

**Parameters:**
- `provider_name` (str) - Name of the provider
- `timeout` (float) - Timeout for health check

**Returns:** `bool` - True if provider is healthy

### Logging Utilities

#### `setup_logging(level="INFO", file=None)`

Set up logging configuration.

```python
from claif.common.utils import setup_logging

# Basic setup
setup_logging()

# With custom level
setup_logging(level="DEBUG")

# With log file
setup_logging(level="INFO", file="claif.log")
```

**Parameters:**
- `level` (str) - Logging level ("DEBUG", "INFO", "WARNING", "ERROR")
- `file` (Optional[str]) - Log file path

#### `get_logger(name)`

Get a configured logger instance.

```python
from claif.common.utils import get_logger

logger = get_logger(__name__)
logger.info("Starting operation")
logger.debug("Debug information")
logger.error("Error occurred")
```

**Parameters:**
- `name` (str) - Logger name (usually `__name__`)

**Returns:** `Logger` - Configured logger instance

### File and Path Utilities

#### `get_config_dir()`

Get the Claif configuration directory.

```python
from claif.common.utils import get_config_dir
import os

config_dir = get_config_dir()
print(f"Config directory: {config_dir}")

# Ensure directory exists
os.makedirs(config_dir, exist_ok=True)
```

**Returns:** `Path` - Path to configuration directory

#### `get_cache_dir()`

Get the Claif cache directory.

```python
from claif.common.utils import get_cache_dir

cache_dir = get_cache_dir()
print(f"Cache directory: {cache_dir}")
```

**Returns:** `Path` - Path to cache directory

#### `get_data_dir()`

Get the Claif data directory.

```python
from claif.common.utils import get_data_dir

data_dir = get_data_dir()
print(f"Data directory: {data_dir}")
```

**Returns:** `Path` - Path to data directory

### Validation Utilities

#### `validate_message(message)`

Validate a message object.

```python
from claif.common.utils import validate_message
from claif.common.types import Message, TextBlock
from claif.common.errors import MessageValidationError

message = Message(content=[TextBlock(text="Hello")])

try:
    validate_message(message)
    print("Message is valid")
except MessageValidationError as e:
    print(f"Invalid message: {e}")
```

**Parameters:**
- `message` (Message) - Message to validate

**Raises:** `MessageValidationError` - If message is invalid

#### `validate_options(options, provider_name=None)`

Validate query options.

```python
from claif.common.utils import validate_options
from claif.common.types import ClaifOptions
from claif.common.errors import OptionsValidationError

options = ClaifOptions(temperature=0.7, max_tokens=1000)

try:
    validate_options(options, provider_name="claude")
    print("Options are valid")
except OptionsValidationError as e:
    print(f"Invalid options: {e}")
```

**Parameters:**
- `options` (ClaifOptions) - Options to validate
- `provider_name` (Optional[str]) - Provider to validate against

**Raises:** `OptionsValidationError` - If options are invalid

## Terminal Utilities

### Rich Formatting

#### `print_response(message, style="default")`

Print a formatted response to the terminal.

```python
from claif.common.utils import print_response
from claif import ClaifClient

client = ClaifClient()
response = client.query("Hello")

# Default formatting
print_response(response)

# With different styles
print_response(response, style="markdown")
print_response(response, style="code")
```

**Parameters:**
- `message` (Message) - Message to print
- `style` (str) - Formatting style ("default", "markdown", "code", "json")

#### `print_table(data, headers=None)`

Print data as a formatted table.

```python
from claif.common.utils import print_table

# Provider information table
data = [
    ["claude", "1.0.0", "Available"],
    ["gemini", "1.2.0", "Available"],
    ["codex", "0.9.0", "Unavailable"]
]

print_table(data, headers=["Provider", "Version", "Status"])
```

**Parameters:**
- `data` (List[List[str]]) - Table data
- `headers` (Optional[List[str]]) - Column headers

#### `print_error(error, show_traceback=False)`

Print an error with appropriate formatting.

```python
from claif.common.utils import print_error
from claif.common.errors import ProviderError

try:
    # Some operation that fails
    pass
except ProviderError as e:
    print_error(e)
    
    # With traceback for debugging
    print_error(e, show_traceback=True)
```

**Parameters:**
- `error` (Exception) - Error to print
- `show_traceback` (bool) - Whether to show full traceback

### Progress Indicators

#### `progress_spinner(message="Working...")`

Context manager for showing a progress spinner.

```python
from claif.common.utils import progress_spinner
import time

with progress_spinner("Processing query..."):
    time.sleep(3)  # Simulate work
print("Done!")
```

**Parameters:**
- `message` (str) - Message to display

#### `progress_bar(total, description="Progress")`

Create a progress bar for long operations.

```python
from claif.common.utils import progress_bar
import time

with progress_bar(100, "Downloading...") as bar:
    for i in range(100):
        time.sleep(0.01)
        bar.update(1)
```

**Parameters:**
- `total` (int) - Total number of steps
- `description` (str) - Progress description

## Data Utilities

### Serialization

#### `serialize_message(message)`

Serialize a message to JSON-compatible format.

```python
from claif.common.utils import serialize_message, deserialize_message
from claif.common.types import Message, TextBlock

message = Message(content=[TextBlock(text="Hello")])

# Serialize
data = serialize_message(message)
print(data)  # Dict that can be JSON-serialized

# Deserialize
restored = deserialize_message(data)
print(restored.text)  # "Hello"
```

**Parameters:**
- `message` (Message) - Message to serialize

**Returns:** `Dict[str, Any]` - Serialized message data

#### `deserialize_message(data)`

Deserialize message from JSON-compatible format.

**Parameters:**
- `data` (Dict[str, Any]) - Serialized message data

**Returns:** `Message` - Deserialized message

### Caching

#### `cache_response(key, response, ttl=3600)`

Cache a response with TTL (time-to-live).

```python
from claif.common.utils import cache_response, get_cached_response

# Cache a response
response = client.query("What is AI?")
cache_response("ai_explanation", response, ttl=3600)

# Retrieve cached response
cached = get_cached_response("ai_explanation")
if cached:
    print("Using cached response")
    print(cached.text)
```

**Parameters:**
- `key` (str) - Cache key
- `response` (Message) - Response to cache
- `ttl` (int) - Time-to-live in seconds

#### `get_cached_response(key)`

Get a cached response if available and not expired.

**Parameters:**
- `key` (str) - Cache key

**Returns:** `Optional[Message]` - Cached response or None

#### `clear_cache(key=None)`

Clear cache entries.

```python
from claif.common.utils import clear_cache

# Clear specific key
clear_cache("ai_explanation")

# Clear all cache
clear_cache()
```

**Parameters:**
- `key` (Optional[str]) - Specific key to clear, or None for all

## Network Utilities

### HTTP Helpers

#### `make_request(url, method="GET", **kwargs)`

Make an HTTP request with proper error handling.

```python
from claif.common.utils import make_request
from claif.common.errors import NetworkError

try:
    response = make_request(
        "https://api.example.com/status",
        method="GET",
        headers={"Authorization": "Bearer token"},
        timeout=30
    )
    print(response.json())
except NetworkError as e:
    print(f"Network error: {e}")
```

**Parameters:**
- `url` (str) - URL to request
- `method` (str) - HTTP method
- `**kwargs` - Additional arguments for requests

**Returns:** `requests.Response` - HTTP response

**Raises:** `NetworkError` - On network-related errors

#### `check_connectivity(host="8.8.8.8", port=53, timeout=3)`

Check internet connectivity.

```python
from claif.common.utils import check_connectivity

if check_connectivity():
    print("Internet connection available")
else:
    print("No internet connection")

# Check specific host
if check_connectivity("api.anthropic.com", 443):
    print("Can reach Anthropic API")
```

**Parameters:**
- `host` (str) - Host to check
- `port` (int) - Port to check
- `timeout` (float) - Connection timeout

**Returns:** `bool` - True if connectivity is available

## System Utilities

### Environment Detection

#### `get_platform_info()`

Get platform and system information.

```python
from claif.common.utils import get_platform_info

info = get_platform_info()
print(f"OS: {info['system']}")
print(f"Version: {info['version']}")
print(f"Architecture: {info['architecture']}")
print(f"Python: {info['python_version']}")
```

**Returns:** `Dict[str, str]` - Platform information

#### `is_docker()`

Check if running inside Docker container.

```python
from claif.common.utils import is_docker

if is_docker():
    print("Running in Docker")
else:
    print("Running on host system")
```

**Returns:** `bool` - True if running in Docker

#### `get_terminal_size()`

Get terminal dimensions.

```python
from claif.common.utils import get_terminal_size

width, height = get_terminal_size()
print(f"Terminal: {width}x{height}")
```

**Returns:** `Tuple[int, int]` - Terminal width and height

### Process Management

#### `run_command(command, cwd=None, timeout=None)`

Run a shell command with proper error handling.

```python
from claif.common.utils import run_command
from claif.common.errors import CommandError

try:
    result = run_command(["ls", "-la"], cwd="/tmp", timeout=10)
    print(f"Exit code: {result.returncode}")
    print(f"Output: {result.stdout}")
except CommandError as e:
    print(f"Command failed: {e}")
```

**Parameters:**
- `command` (List[str]) - Command and arguments
- `cwd` (Optional[str]) - Working directory
- `timeout` (Optional[float]) - Command timeout

**Returns:** `subprocess.CompletedProcess` - Command result

**Raises:** `CommandError` - On command execution errors

## Usage Examples

### Complete Error Handling Setup

```python
from claif import ClaifClient
from claif.common.utils import (
    setup_logging, 
    get_logger, 
    print_error, 
    check_connectivity
)
from claif.common.errors import ClaifError

# Setup logging
setup_logging(level="INFO", file="claif.log")
logger = get_logger(__name__)

# Check connectivity first
if not check_connectivity():
    print("No internet connection available")
    exit(1)

client = ClaifClient()

try:
    response = client.query("Hello, AI!")
    print(response.text)
except ClaifError as e:
    logger.error(f"Claif error: {e}")
    print_error(e)
    exit(1)
```

### Configuration and Provider Management

```python
from claif.common.utils import (
    load_config,
    validate_config,
    discover_providers,
    check_provider_health,
    print_table
)

# Load and validate config
config = load_config()
validate_config(config)

# Discover providers
providers = discover_providers()

# Check health and display status
provider_data = []
for name, provider in providers.items():
    is_healthy = check_provider_health(name)
    status = "Healthy" if is_healthy else "Unavailable"
    provider_data.append([name, provider.version, status])

print_table(
    provider_data, 
    headers=["Provider", "Version", "Status"]
)
```

### Response Caching and Formatting

```python
from claif import ClaifClient
from claif.common.utils import (
    cache_response,
    get_cached_response,
    format_response,
    serialize_message
)

client = ClaifClient()
cache_key = "common_question"

# Try to get cached response first
cached = get_cached_response(cache_key)
if cached:
    print("Using cached response:")
    response = cached
else:
    print("Fetching new response:")
    response = client.query("What is machine learning?")
    cache_response(cache_key, response, ttl=3600)

# Format and display
markdown = format_response(response, format_type="markdown")
print(markdown)

# Save to file
with open("response.json", "w") as f:
    json.dump(serialize_message(response), f, indent=2)
```