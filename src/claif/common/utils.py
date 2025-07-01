"""Common utilities for CLAIF framework."""

import logging
import sys
import time
from typing import Any, Optional, List
from pathlib import Path

from rich.console import Console
from rich.logging import RichHandler
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.syntax import Syntax
from rich.table import Table

from .types import Message, TextBlock, ContentBlock, ResponseMetrics, MessageRole


def get_logger(name: str, verbose: bool = False) -> logging.Logger:
    """Get a configured logger."""
    logger = logging.getLogger(name)
    
    if not logger.handlers:
        level = logging.DEBUG if verbose else logging.INFO
        handler = RichHandler(
            rich_tracebacks=True,
            show_time=False,
            show_path=False,
        )
        handler.setLevel(level)
        logger.addHandler(handler)
        logger.setLevel(level)
    
    return logger


def format_response(message: Message, format: str = "text", syntax_highlighting: bool = True) -> str:
    """Format a message for display."""
    if format == "json":
        import json
        return json.dumps(message_to_dict(message), indent=2)
    
    # Extract text content
    text_parts = []
    if isinstance(message.content, str):
        text_parts.append(message.content)
    else:
        for block in message.content:
            if isinstance(block, TextBlock):
                text_parts.append(block.text)
    
    text = "\n".join(text_parts)
    
    if format == "markdown" and syntax_highlighting:
        # Basic markdown rendering
        console = Console()
        with console.capture() as capture:
            console.print(text)
        return capture.get()
    
    return text


def message_to_dict(message: Message) -> dict:
    """Convert a message to a dictionary."""
    content = message.content
    if isinstance(content, list):
        content = [block_to_dict(block) for block in content]
    
    return {
        "role": message.role.value,
        "content": content,
    }


def block_to_dict(block: ContentBlock) -> dict:
    """Convert a content block to a dictionary."""
    if isinstance(block, TextBlock):
        return {"type": "text", "text": block.text}
    elif hasattr(block, "__dict__"):
        return block.__dict__
    else:
        return {"type": "unknown", "data": str(block)}


def format_metrics(metrics: ResponseMetrics) -> str:
    """Format response metrics for display."""
    table = Table(title="Response Metrics", show_header=False)
    table.add_column("Metric", style="cyan")
    table.add_column("Value", style="green")
    
    table.add_row("Duration", f"{metrics.duration:.2f}s")
    table.add_row("Tokens", str(metrics.tokens_used))
    table.add_row("Cost", f"${metrics.cost:.4f}")
    table.add_row("Provider", metrics.provider.value if metrics.provider else "N/A")
    table.add_row("Model", metrics.model or "N/A")
    table.add_row("Cached", "Yes" if metrics.cached else "No")
    
    console = Console()
    with console.capture() as capture:
        console.print(table)
    return capture.get()


def create_progress_bar(description: str = "Processing...") -> Progress:
    """Create a progress bar for long operations."""
    return Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        transient=True,
    )


def ensure_directory(path: Path) -> None:
    """Ensure a directory exists."""
    path.mkdir(parents=True, exist_ok=True)


def timestamp() -> str:
    """Get current timestamp as string."""
    return time.strftime("%Y%m%d_%H%M%S")


def truncate_text(text: str, max_length: int = 100, suffix: str = "...") -> str:
    """Truncate text to maximum length."""
    if len(text) <= max_length:
        return text
    return text[:max_length - len(suffix)] + suffix


def parse_content_blocks(content: Any) -> List[ContentBlock]:
    """Parse various content formats into content blocks."""
    if isinstance(content, str):
        return [TextBlock(text=content)]
    elif isinstance(content, list):
        blocks = []
        for item in content:
            if isinstance(item, (TextBlock,)):
                blocks.append(item)
            elif isinstance(item, dict):
                if item.get("type") == "text":
                    blocks.append(TextBlock(text=item.get("text", "")))
            else:
                blocks.append(TextBlock(text=str(item)))
        return blocks
    else:
        return [TextBlock(text=str(content))]