"""Common type definitions for CLAIF framework."""

from dataclasses import dataclass
from enum import Enum
from typing import Any, Union


class Provider(str, Enum):
    """Supported LLM providers."""

    CLAUDE = "claude"
    GEMINI = "gemini"
    CODEX = "codex"


class MessageRole(str, Enum):
    """Message roles."""

    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"
    RESULT = "result"


@dataclass
class TextBlock:
    """Text content block."""

    type: str = "text"
    text: str = ""


@dataclass
class ToolUseBlock:
    """Tool use content block."""

    type: str = "tool_use"
    id: str = ""
    name: str = ""
    input: dict[str, Any] = None

    def __post_init__(self):
        if self.input is None:
            self.input = {}


@dataclass
class ToolResultBlock:
    """Tool result content block."""

    type: str = "tool_result"
    tool_use_id: str = ""
    content: list[TextBlock | Any] = None
    is_error: bool = False

    def __post_init__(self):
        if self.content is None:
            self.content = []


ContentBlock = Union[TextBlock, ToolUseBlock, ToolResultBlock]


@dataclass
class Message:
    """Base message class."""

    role: MessageRole
    content: str | list[ContentBlock]

    def __post_init__(self):
        if isinstance(self.content, str):
            self.content = [TextBlock(text=self.content)]


@dataclass
class ClaifOptions:
    """Common options for CLAIF queries."""

    provider: Provider | None = None
    model: str | None = None
    temperature: float | None = None
    max_tokens: int | None = None
    system_prompt: str | None = None
    timeout: int | None = None
    verbose: bool = False
    output_format: str = "text"
    config_file: str | None = None
    session_id: str | None = None
    cache: bool = False
    retry_count: int = 3
    retry_delay: float = 1.0


@dataclass
class ResponseMetrics:
    """Metrics for a response."""

    duration: float = 0.0
    tokens_used: int = 0
    cost: float = 0.0
    provider: Provider | None = None
    model: str | None = None
    cached: bool = False


@dataclass
class ClaifResponse:
    """Response from a CLAIF query."""

    messages: list[Message]
    metrics: ResponseMetrics | None = None
    session_id: str | None = None
    error: str | None = None
