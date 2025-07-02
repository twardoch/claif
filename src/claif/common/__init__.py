"""Common utilities for Claif framework."""

from loguru import logger

from src.claif.common.config import Config, load_config, save_config
from src.claif.common.errors import (
    ClaifError,
    ClaifTimeoutError,
    ConfigurationError,
    ProviderError,
    SessionError,
    TransportError,
    ValidationError,
)
from src.claif.common.install import InstallError, find_executable, install_provider, uninstall_provider
from src.claif.common.types import (
    ClaifOptions,
    ClaifResponse,
    Message,
    MessageRole,
    Provider,
    ResponseMetrics,
    TextBlock,
    ToolResultBlock,
    ToolUseBlock,
)
from src.claif.common.utils import format_metrics, format_response

__all__ = [
    "ClaifError",
    "ClaifOptions",
    "ClaifResponse",
    "ClaifTimeoutError",
    "Config",
    "ConfigurationError",
    "InstallError",
    "Message",
    "MessageRole",
    "Provider",
    "ProviderError",
    "ResponseMetrics",
    "SessionError",
    "TextBlock",
    "ToolResultBlock",
    "ToolUseBlock",
    "TransportError",
    "ValidationError",
    "find_executable",
    "format_metrics",
    "format_response",
    "install_provider",
    "load_config",
    "logger",
    "save_config",
    "uninstall_provider",
]
