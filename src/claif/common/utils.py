"""Utility functions for Claif framework."""

import json
import os
import platform
import subprocess
import time
from collections.abc import Sequence
from pathlib import Path
from typing import Any, Dict, List, Union

from loguru import logger
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.table import Table

from claif.common.types import ContentBlock, Message, ResponseMetrics, TextBlock
from rich.console import Console
from rich.theme import Theme
from rich.syntax import Syntax

# Define a custom theme for consistent output styling
cli_theme = Theme({
    "info": "dim cyan",
    "warning": "magenta",
    "danger": "bold red",
    "success": "bold green",
    "debug": "dim white"
})
console = Console(theme=cli_theme)

def _print(message: str) -> None:
    """Prints a general message to the console."""
    console.print(message)

def _print_error(message: str) -> None:
    """Prints an error message to the console in red."""
    console.print(f"[danger]Error:[/danger] {message}")

def _print_success(message: str) -> None:
    """Prints a success message to the console in green."""
    console.print(f"[success]Success:[/success] {message}")

def _print_warning(message: str) -> None:
    """Prints a warning message to the console in yellow/magenta."""
    console.print(f"[warning]Warning:[/warning] {message}")

def _confirm(message: str) -> bool:
    """Simple confirmation prompt."""
    response = input(f"{message} (y/N): ").strip().lower()
    return response in ("y", "yes")

def _prompt(message: str) -> str:
    """Simple input prompt."""
    return input(f"{message}: ").strip()

APP_NAME: str = "com.twardoch.claif"


def format_response(message: Message, format: str = "text", syntax_highlighting: bool = True) -> str:
    """
    Formats a given message for display based on the specified format.

    Args:
        message: The `Message` object to format.
        format: The desired output format ('text', 'json', or 'markdown').
        syntax_highlighting: If True and format is 'markdown', attempts to apply syntax highlighting.
                             Note: Actual syntax highlighting depends on `rich` being configured
                             to render code blocks, which is typically handled at the console level.

    Returns:
        A string representation of the message in the specified format.
    """
    if format == "json":
        # Convert the message to a dictionary and then to a JSON string.
        return json.dumps(message_to_dict(message), indent=2)

    # Extract text content from the message. Handles both string and list of ContentBlock types.
    text_parts: List[str] = []
    if isinstance(message.content, str):
        text_parts.append(message.content)
    else:
        for block in message.content:
            if isinstance(block, TextBlock):
                text_parts.append(block.text)
            # Add handling for other ContentBlock types if their text representation is needed

    text: str = "\n".join(text_parts)

    if format == "markdown" and syntax_highlighting:
        # This part is a placeholder. Actual syntax highlighting for markdown
        # content typically requires a markdown renderer that supports it,
        # like `rich.markdown.Markdown` or similar, which would then be printed
        # directly to a rich Console, not captured as a plain string.
        # For now, it just prints the raw text content.
        console = Console()
        with console.capture() as capture:
            console.print(text)
        return capture.get()

    return text


def message_to_dict(message: Message) -> Dict[str, Any]:
    """
    Converts a `Message` object into a dictionary for serialization.

    Args:
        message: The `Message` object to convert.

    Returns:
        A dictionary representation of the message.
    """
    content: Union[str, List[ContentBlock]] = message.content
    if isinstance(content, list):
        # Recursively convert each content block to a dictionary.
        content = [block_to_dict(block) for block in content]

    return {
        "role": message.role.value,
        "content": content,
    }


def block_to_dict(block: ContentBlock) -> Dict[str, Any]:
    """
    Converts a `ContentBlock` object into a dictionary.

    Args:
        block: The `ContentBlock` object to convert.

    Returns:
        A dictionary representation of the content block.
    """
    if isinstance(block, TextBlock):
        return {"type": "text", "text": block.text}
    # For other dataclass-based ContentBlocks (e.g., ToolUseBlock, ToolResultBlock),
    # their __dict__ representation is usually sufficient for serialization.
    if hasattr(block, "__dict__"):
        return block.__dict__
    # Fallback for unexpected types, converting them to a string representation.
    return {"type": "unknown", "data": str(block)}


def format_metrics(metrics: ResponseMetrics) -> str:
    """
    Formats response metrics into a human-readable table for display.

    Args:
        metrics: The `ResponseMetrics` object containing performance data.

    Returns:
        A string containing the formatted metrics table.
    """
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
    """
    Creates and returns a `rich` Progress bar instance.

    Args:
        description: The initial description to display next to the spinner.

    Returns:
        A `rich.progress.Progress` object configured with a spinner and text column.
    """
    return Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        transient=True,  # Progress bar disappears after completion
    )


def ensure_directory(path: Path) -> None:
    """
    Ensures that a given directory path exists.

    If the directory or any parent directories do not exist, they are created.

    Args:
        path: The `Path` object representing the directory to ensure.
    """
    path.mkdir(parents=True, exist_ok=True)


def timestamp() -> str:
    """
    Generates a formatted timestamp string.

    Returns:
        A string representing the current time in YYYYMMDD_HHMMSS format.
    """
    return time.strftime("%Y%m%d_%H%M%S")


def truncate_text(text: str, max_length: int = 100, suffix: str = "...") -> str:
    """
    Truncates a string to a specified maximum length, adding a suffix if truncated.

    Args:
        text: The input string to truncate.
        max_length: The maximum desired length of the string.
        suffix: The suffix to append if the string is truncated. Defaults to "...".

    Returns:
        The truncated string, or the original string if its length is within `max_length`.
    """
    if len(text) <= max_length:
        return text
    return text[: max_length - len(suffix)] + suffix


def parse_content_blocks(content: Any) -> List[ContentBlock]:
    """
    Parses various content formats into a standardized list of `ContentBlock` objects.

    This function attempts to convert raw content (string, list of dicts, etc.)
    into a list of `TextBlock` instances, ensuring consistency for message handling.

    Args:
        content: The raw content to parse. Can be a string, a list of dictionaries,
                 or any other type that can be converted to a string.

    Returns:
        A list of `ContentBlock` objects, primarily `TextBlock` instances.
    """
    if isinstance(content, str):
        return [TextBlock(text=content)]
    if isinstance(content, list):
        blocks: List[ContentBlock] = []
        for item in content:
            if isinstance(item, TextBlock):
                blocks.append(item)
            elif isinstance(item, dict):
                # Attempt to parse dictionary as a TextBlock if it has a 'text' key
                if item.get("type") == "text" and "text" in item:
                    blocks.append(TextBlock(text=item.get("text", "")))
                else:
                    # Fallback for other dictionary structures
                    blocks.append(TextBlock(text=str(item)))
            else:
                # Convert any other item type directly to a string TextBlock
                blocks.append(TextBlock(text=str(item)))
        return blocks
    # Fallback for any other content type, converting it to a string TextBlock
    return [TextBlock(text=str(content))]


def get_claif_data_dir() -> Path:
    """
    Retrieves the base data directory for Claif application data.

    This directory is used for storing configuration, sessions, and other
    application-specific files in a platform-appropriate location.

    Returns:
        A `Path` object pointing to the Claif data directory.
    """
    from platformdirs import user_data_dir

    return Path(user_data_dir(APP_NAME, "claif"))


def get_claif_bin_path() -> Path:
    """
    Retrieves the binary installation directory for Claif-managed tools.

    This is a subdirectory within the main Claif data directory where
    executables installed by Claif (e.g., Claude CLI, Gemini CLI) are placed.

    Returns:
        A `Path` object pointing to the Claif binary directory.
    """
    claif_data_dir: Path = get_claif_data_dir()
    return claif_data_dir / "bin"


def inject_claif_bin_to_path() -> Dict[str, str]:
    """
    Injects the Claif binary directory into the system's PATH environment variable.

    This ensures that executables installed by Claif are discoverable by
    subprocesses launched by the application.

    Returns:
        A dictionary representing the modified environment variables with the
        Claif binary path prepended to the PATH.
    """
    env: Dict[str, str] = os.environ.copy()
    claif_bin_path: Path = get_claif_bin_path() # Use get_claif_bin_path for consistency

    path_sep: str = ";" if os.name == "nt" else ":"
    current_path: str = env.get("PATH", "")

    # Prepend the Claif bin path to the existing PATH if it's not already there.
    if str(claif_bin_path) not in current_path.split(path_sep):
        env["PATH"] = f"{claif_bin_path}{path_sep}{current_path}"
        logger.debug(f"Injected {claif_bin_path} into PATH.")
    else:
        logger.debug(f"{claif_bin_path} already in PATH.")

    return env


def get_install_location() -> Path:
    """
    Retrieves the primary installation location for Claif-managed tools.

    This function determines a platform-appropriate directory where external
    CLI tools (like Claude Code CLI, Gemini CLI) are installed by Claif.

    Returns:
        A `Path` object representing the installation directory.
    """
    if os.name == "nt":
        # On Windows, use %LOCALAPPDATA%\claif\bin
        base: Path = Path(os.environ.get("LOCALAPPDATA", Path.home() / "AppData" / "Local"))
        return base / "claif" / "bin"
    else:
        # On Unix-like systems, use ~/.local/bin/claif
        return Path.home() / ".local" / "bin" / "claif"


def open_commands_in_terminals(commands: Sequence[str]) -> None:
    """
    Opens each provided shell command in a new terminal window.

    This utility attempts to use platform-specific commands to launch new
    terminal instances and execute the given commands within them.

    Args:
        commands: A sequence of shell commands (strings) to be executed.

    Raises:
        NotImplementedError: If the operating system is not supported or a
                             suitable terminal emulator cannot be found.
    """
    system: str = platform.system()
    logger.debug(f"Attempting to open {len(commands)} commands in new terminals on {system}.")

    for cmd in commands:
        logger.debug(f"Opening terminal for command: {cmd}")
        try:
            match system:
                case "Darwin":
                    # macOS: Use osascript to tell Terminal.app to execute the command.
                    subprocess.Popen(
                        [
                            "osascript",
                            "-e",
                            f'tell application "Terminal" to do script "{cmd}"',
                        ]
                    )
                case "Windows":
                    # Windows: Use `start cmd /k` to open a new command prompt and run the command.
                    subprocess.Popen(["cmd", "/c", "start", "cmd", "/k", cmd], shell=True)
                case "Linux":
                    # Linux: Try common terminal emulators in order of preference.
                    terminals: List[List[str]] = [
                        ["gnome-terminal", "--", "bash", "-c", f"{cmd}; exec bash"], # gnome-terminal
                        ["x-terminal-emulator", "-e", f"bash -c '{cmd}; exec bash'"], # Generic X terminal
                        ["xterm", "-e", f"bash -c '{cmd}; exec bash'"], # xterm
                    ]

                    success: bool = False
                    for terminal_cmd in terminals:
                        try:
                            subprocess.Popen(terminal_cmd)
                            success = True
                            break
                        except FileNotFoundError:
                            # Try the next terminal if the current one is not found.
                            continue

                    if not success:
                        logger.warning("No suitable terminal emulator found on Linux for command.")
                        msg = "No suitable terminal emulator found on Linux. Please install gnome-terminal, x-terminal-emulator, or xterm."
                        raise NotImplementedError(msg)
                case _:
                    # Handle unsupported operating systems.
                    msg = f"Unsupported operating system for opening terminals: {system}"
                    raise NotImplementedError(msg)
        except Exception as e:
            logger.warning(f"Failed to open terminal for command '{cmd}': {e}")


def prompt_tool_configuration(tool_name: str, config_commands: List[str]) -> None:
    """
    Prompts the user to configure a tool and optionally opens terminals to run configuration commands.

    Args:
        tool_name: The name of the tool (e.g., 'Claude', 'Gemini') that needs configuration.
        config_commands: A list of shell commands (strings) that can be run to configure the tool.
    """

    if config_commands:
        # Inform the user about the commands that can be run.
        _print(f"\nTo configure {tool_name}, you can run the following commands:")
        for cmd in config_commands:
            _print(f"  [cyan]{cmd}[/cyan]")

        try:
            response: str = input(f"\nWould you like to open terminal(s) to run these commands for {tool_name}? (y/N): ")
            if response.lower().startswith("y"):
                open_commands_in_terminals(config_commands)
                _print("Terminals opened. Please follow the instructions in each terminal to complete the configuration.")
            else:
                _print("Configuration commands not executed. You can run them manually later.")
        except (KeyboardInterrupt, EOFError):
            _print_warning("Configuration prompt interrupted. Please run configuration commands manually.")
    else:
        _print(f"No specific configuration commands provided for {tool_name}.")
