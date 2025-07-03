# this_file: claif/src/claif/common/types.py
"""
Common type definitions for the Claif framework.

This module centralizes the definition of core data structures and enums
used across different components and providers within the Claif ecosystem.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, List, Optional, Union


class Provider(str, Enum):
    """
    Enumeration of supported Large Language Model (LLM) providers.

    Each member represents a distinct LLM service integrated with Claif.
    """

    CLAUDE = "claude"
    GEMINI = "gemini"
    CODEX = "codex"


class MessageRole(str, Enum):
    """
    Defines the roles of participants in a conversational exchange.

    These roles are used to categorize messages sent to or received from LLMs.
    """

    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"
    RESULT = "result"


@dataclass
class TextBlock:
    """
    Represents a block of plain text content within a message.

    Attributes:
        type: A string indicating the type of the block, always "text".
        text: The actual textual content.
    """

    type: str = "text"
    text: str = ""


@dataclass
class ToolUseBlock:
    """
    Represents a block indicating the use of a tool by the LLM.

    This block typically contains information about the tool being invoked
    and the arguments provided to it.

    Attributes:
        type: A string indicating the type of the block, always "tool_use".
        id: A unique identifier for this tool use instance.
        name: The name of the tool being called.
        input: A dictionary containing the arguments passed to the tool.
               Defaults to an empty dictionary if not provided.
    """

    type: str = "tool_use"
    id: str = ""
    name: str = ""
    # Use `field(default_factory=dict)` for mutable default arguments
    # to prevent unexpected shared state across instances.
    input: dict[str, Any] = field(default_factory=dict)


@dataclass
class ToolResultBlock:
    """
    Represents a block containing the result of a tool invocation.

    This block is used to convey the output or status of a tool's execution
    back to the LLM or the user.

    Attributes:
        type: A string indicating the type of the block, always "tool_result".
        tool_use_id: The ID of the `ToolUseBlock` this result corresponds to.
        content: A list of content blocks representing the tool's output.
                 Can be a list of `TextBlock` or other structured data.
                 Defaults to an empty list if not provided.
        is_error: A boolean indicating if the tool execution resulted in an error.
    """

    type: str = "tool_result"
    tool_use_id: str = ""
    # Use `field(default_factory=list)` for mutable default arguments.
    content: List[Union[TextBlock, Any]] = field(default_factory=list)
    is_error: bool = False


# A Union type representing any possible content block within a message.
ContentBlock = Union[TextBlock, ToolUseBlock, ToolResultBlock]


@dataclass
class Message:
    """
    Represents a single message in a conversational turn.

    Messages can contain either a simple string content or a list of structured
    content blocks, allowing for rich and multimodal interactions.

    Attributes:
        role: The role of the sender of the message (e.g., user, assistant).
        content: The content of the message, which can be a plain string
                 or a list of `ContentBlock` objects.
    """

    role: MessageRole
    content: Union[str, List[ContentBlock]]

    def __post_init__(self) -> None:
        """
        Post-initialization hook to normalize string content into a list of TextBlock.

        If the `content` is provided as a string, it is automatically wrapped
        into a list containing a single `TextBlock` for internal consistency.
        """
        if isinstance(self.content, str):
            self.content = [TextBlock(text=self.content)]


@dataclass
class ClaifOptions:
    """
    Common configuration options applicable across various Claif operations.

    These options provide a standardized way to control behavior such as
    provider selection, model parameters, and retry strategies.

    Attributes:
        provider: The preferred LLM provider to use. If None, a default might be chosen.
        model: The specific model name to use with the selected provider.
        temperature: Controls the randomness of the output (typically 0.0 to 1.0).
        max_tokens: The maximum number of tokens to generate in the response.
        system_prompt: An initial system-level instruction or context for the LLM.
        timeout: Maximum time in seconds to wait for a response.
        verbose: If True, enables verbose logging for debugging.
        output_format: The desired format for the output (e.g., "text", "json").
        config_file: Path to a specific configuration file to load.
        session_id: A unique identifier for the current conversational session.
        cache: If True, enables caching of responses for this query.
        retry_count: Number of times to retry a failed operation.
        retry_delay: Initial delay in seconds before retrying.
        no_retry: If True, disables all retry attempts.
    """

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
    no_retry: bool = False


@dataclass
class ResponseMetrics:
    """
    Captures performance and usage metrics for an LLM response.

    This data helps in analyzing the efficiency and cost of queries.

    Attributes:
        duration: The total time taken for the response in seconds.
        tokens_used: The number of tokens consumed by the query (input + output).
        cost: The estimated monetary cost of the query.
        provider: The LLM provider that generated the response.
        model: The specific model used for the response.
        cached: A boolean indicating if the response was served from cache.
    """

    duration: float = 0.0
    tokens_used: int = 0
    cost: float = 0.0
    provider: Optional[Provider] = None
    model: Optional[str] = None
    cached: bool = False


@dataclass
class ClaifResponse:
    """
    Encapsulates the complete response from a Claif query operation.

    This includes the messages generated by the LLM, associated metrics,
    session information, and any top-level error messages.

    Attributes:
        messages: A list of `Message` objects representing the LLM's output.
        metrics: Optional performance and usage metrics for the response.
        session_id: Optional unique identifier for the session.
        error: Optional error message if the query failed at a high level.
    """

    messages: List[Message]
    metrics: Optional[ResponseMetrics] = None
    session_id: Optional[str] = None
    error: Optional[str] = None
