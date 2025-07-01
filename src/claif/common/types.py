"""Common type definitions for CLAIF framework."""

from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, List, Optional, Union


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
    input: Dict[str, Any] = None

    def __post_init__(self):
        if self.input is None:
            self.input = {}


@dataclass
class ToolResultBlock:
    """Tool result content block."""
    type: str = "tool_result"
    tool_use_id: str = ""
    content: List[Union[TextBlock, Any]] = None
    is_error: bool = False

    def __post_init__(self):
        if self.content is None:
            self.content = []


ContentBlock = Union[TextBlock, ToolUseBlock, ToolResultBlock]


@dataclass
class Message:
    """Base message class."""
    role: MessageRole
    content: Union[str, List[ContentBlock]]
    
    def __post_init__(self):
        if isinstance(self.content, str):
            self.content = [TextBlock(text=self.content)]


@dataclass
class ClaifOptions:
    """Common options for CLAIF queries."""
    provider: Optional[Provider] = None
    model: Optional[str] = None
    temperature: Optional[float] = None
    max_tokens: Optional[int] = None
    system_prompt: Optional[str] = None
    timeout: Optional[int] = None
    verbose: bool = False
    output_format: str = "text"
    config_file: Optional[str] = None
    session_id: Optional[str] = None
    cache: bool = False
    retry_count: int = 3
    retry_delay: float = 1.0


@dataclass
class ResponseMetrics:
    """Metrics for a response."""
    duration: float = 0.0
    tokens_used: int = 0
    cost: float = 0.0
    provider: Optional[Provider] = None
    model: Optional[str] = None
    cached: bool = False


@dataclass
class ClaifResponse:
    """Response from a CLAIF query."""
    messages: List[Message]
    metrics: Optional[ResponseMetrics] = None
    session_id: Optional[str] = None
    error: Optional[str] = None