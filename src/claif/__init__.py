"""Claif - Command Line Artificial Intelligence Framework."""

from claif.common import (
    ClaifError,
    ClaifOptions,
    ClaifResponse,
    Config,
    ConfigurationError,
    Message,
    Provider,
    ProviderError,
    ResponseMetrics,
    TextBlock,
    ToolResultBlock,
    ToolUseBlock,
    load_config,
)

try:
    from claif.__version__ import __version__
except ImportError:
    __version__ = "0.0.0+unknown"

__all__ = [
    "ClaifError",
    "ClaifOptions",
    "ClaifResponse",
    "Config",
    "ConfigurationError",
    "Message",
    "Provider",
    "ProviderError",
    "ResponseMetrics",
    "TextBlock",
    "ToolResultBlock",
    "ToolUseBlock",
    "load_config",
]
