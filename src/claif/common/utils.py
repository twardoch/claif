"""Utility functions for Claif framework."""

import json
import os
import platform
import subprocess
import time
from collections.abc import Sequence
from pathlib import Path
from typing import Any

from loguru import logger
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.table import Table

from claif.common.types import ContentBlock, Message, ResponseMetrics, TextBlock

APP_NAME = "com.twardoch.claif"


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


def get_claif_data_dir() -> Path:
    """Get the claif data directory path."""
    from platformdirs import user_data_dir

    claif_data_dir = Path(user_data_dir(APP_NAME, "claif"))
    return claif_data_dir


def get_claif_bin_path() -> Path:
    """Get the claif bin directory path."""
    claif_data_dir = get_claif_data_dir()
    return claif_data_dir / "bin"


def inject_claif_bin_to_path() -> dict:
    """Inject Claif bin directory to PATH.

    Returns:
        Environment with Claif bin in PATH
    """
    env = os.environ.copy()
    claif_bin = get_install_location()

    path_sep = ";" if os.name == "nt" else ":"
    current_path = env.get("PATH", "")

    if str(claif_bin) not in current_path:
        env["PATH"] = f"{claif_bin}{path_sep}{current_path}"

    return env


def get_install_location() -> Path:
    """Get the install location for Claif tools.

    Returns:
        Path to install directory
    """
    if os.name == "nt":
        # Windows: use %LOCALAPPDATA%\claif\bin
        base = Path(os.environ.get("LOCALAPPDATA", Path.home() / "AppData" / "Local"))
        return base / "claif" / "bin"
    # Unix-like: use ~/.local/bin/claif
    return Path.home() / ".local" / "bin" / "claif"


def open_commands_in_terminals(commands: Sequence[str]) -> None:
    """Open each command in a new terminal window.

    Uses the simplest built-in terminal for each platform:
    - macOS: Terminal.app
    - Windows: cmd.exe
    - Linux: gnome-terminal or x-terminal-emulator

    Args:
        commands: List of shell commands to run in separate terminals

    Raises:
        NotImplementedError: If running on an unsupported operating system
    """
    system = platform.system()
    logger.debug(f"Opening {len(commands)} commands on {system}")

    for cmd in commands:
        logger.debug(f"Opening terminal for command: {cmd}")
        try:
            match system:
                case "Darwin":
                    # macOS Terminal.app
                    subprocess.Popen(
                        [
                            "osascript",
                            "-e",
                            f'tell application "Terminal" to do script "{cmd}"',
                        ]
                    )
                case "Windows":
                    # Windows CMD
                    subprocess.Popen(["cmd", "/c", "start", "cmd", "/k", cmd], shell=True)
                case "Linux":
                    # Try common Linux terminals
                    terminals = [
                        ["gnome-terminal", "--", "bash", "-c", f"{cmd}; exec bash"],
                        ["x-terminal-emulator", "-e", f"bash -c '{cmd}; exec bash'"],
                        ["xterm", "-e", f"bash -c '{cmd}; exec bash'"],
                    ]

                    success = False
                    for terminal_cmd in terminals:
                        try:
                            subprocess.Popen(terminal_cmd)
                            success = True
                            break
                        except FileNotFoundError:
                            continue

                    if not success:
                        logger.warning("No suitable terminal found on Linux")
                        msg = "No suitable terminal emulator found"
                        raise NotImplementedError(msg)
                case _:
                    msg = f"Unsupported OS: {system}"
                    raise NotImplementedError(msg)
        except Exception as e:
            logger.warning(f"Failed to open terminal for '{cmd}': {e}")


def prompt_tool_configuration(tool_name: str, config_commands: list[str]) -> None:
    """Prompt user to configure a tool and optionally open terminals.

    Args:
        tool_name: Name of the tool (e.g., 'Claude', 'Gemini')
        config_commands: List of configuration commands to show/run
    """

    if config_commands:
        for _cmd in config_commands:
            pass

        try:
            response = input(f"\nOpen terminal(s) to configure {tool_name}? (y/N): ")
            if response.lower().startswith("y"):
                open_commands_in_terminals(config_commands)
            else:
                pass
        except (KeyboardInterrupt, EOFError):
            pass
    else:
        pass
