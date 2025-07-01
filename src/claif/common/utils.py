"""Utility functions for CLAIF framework."""

import json
import os
import time
from collections.abc import AsyncIterator
from datetime import datetime
from functools import wraps
from io import StringIO
from pathlib import Path
from typing import Any

from loguru import logger
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.table import Table

from .types import ContentBlock, Message, ResponseMetrics, TextBlock


def format_response(message: Message, format: str = "text", syntax_highlighting: bool = True) -> str:
    """Format a message for display."""
    if format == "json":
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
    if hasattr(block, "__dict__"):
        return block.__dict__
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
    return text[: max_length - len(suffix)] + suffix


def parse_content_blocks(content: Any) -> list[ContentBlock]:
    """Parse various content formats into content blocks."""
    if isinstance(content, str):
        return [TextBlock(text=content)]
    if isinstance(content, list):
        blocks = []
        for item in content:
            if isinstance(item, TextBlock):
                blocks.append(item)
            elif isinstance(item, dict):
                if item.get("type") == "text":
                    blocks.append(TextBlock(text=item.get("text", "")))
            else:
                blocks.append(TextBlock(text=str(item)))
        return blocks
    return [TextBlock(text=str(content))]


def get_claif_bin_path() -> Path:
    """Get the claif bin directory path."""
    from platformdirs import user_data_dir

    claif_data_dir = Path(user_data_dir("claif", "claif"))
    return claif_data_dir / "bin"


def inject_claif_bin_to_path() -> dict[str, str]:
    """Inject claif bin directory into PATH environment variable.

    Returns:
        Environment dict with claif bin directory prepended to PATH
    """
    env = os.environ.copy()
    claif_bin = get_claif_bin_path()

    if claif_bin.exists():
        current_path = env.get("PATH", "")
        claif_bin_str = str(claif_bin)

        # Only add if not already in PATH
        if claif_bin_str not in current_path.split(os.pathsep):
            env["PATH"] = f"{claif_bin_str}{os.pathsep}{current_path}"
            logger.debug(f"Injected claif bin directory into PATH: {claif_bin}")

    return env
