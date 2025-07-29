# this_file: claif/src/claif/cli.py
"""CLI interface for unified Claif with OpenAI-compatible API."""

import sys

import fire
from rich.console import Console
from rich.live import Live
from rich.markdown import Markdown
from rich.panel import Panel
from rich.spinner import Spinner

from claif.client import ClaifClient

console = Console()


class CLI:
    """Command-line interface for unified Claif."""

    def __init__(
        self,
        provider: str | None = None,
        api_key: str | None = None,
        **kwargs,
    ):
        """Initialize CLI with optional provider selection.

        Args:
            provider: Provider to use (claude, gemini, codex, lms). Auto-detects if not specified.
            api_key: API key for the provider
            **kwargs: Additional provider-specific parameters
        """
        try:
            self._client = ClaifClient(provider=provider, api_key=api_key, **kwargs)
            self._provider = self._client.provider
        except Exception as e:
            console.print(f"[red]Error initializing client: {e}[/red]")
            sys.exit(1)

    def query(
        self,
        prompt: str,
        model: str | None = None,
        provider: str | None = None,
        stream: bool = False,
        system: str | None = None,
        json_output: bool = False,
    ):
        """Query the AI provider with a prompt.

        Args:
            prompt: The user prompt to send
            model: Model name to use (provider-specific)
            provider: Override the default provider for this query
            stream: Whether to stream the response
            system: Optional system message
            json_output: Output raw JSON instead of formatted text
        """
        # If provider is specified for this query, create a new client
        if provider and provider != self._provider:
            try:
                client = ClaifClient(provider=provider)
            except Exception as e:
                console.print(f"[red]Error switching provider: {e}[/red]")
                return
        else:
            client = self._client

        # Use default model if not specified
        if not model:
            model = self._get_default_model(client.provider)

        # Build messages
        messages = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})

        try:
            if stream:
                self._stream_response(client, messages, model, json_output)
            else:
                self._sync_response(client, messages, model, json_output)
        except Exception as e:
            console.print(f"[red]Error: {e}[/red]")
            sys.exit(1)

    def _get_default_model(self, provider: str) -> str:
        """Get default model for a provider."""
        defaults = {
            "claude": "claude-3-5-sonnet-20241022",
            "gemini": "gemini-1.5-flash",
            "codex": "gpt-4o",
            "lms": "gpt-3.5-turbo",
        }
        return defaults.get(provider, "gpt-3.5-turbo")

    def _sync_response(self, client: ClaifClient, messages: list, model: str, json_output: bool):
        """Handle synchronous response."""
        provider_name = client.provider.capitalize()
        with console.status(f"[bold green]Querying {provider_name}...", spinner="dots"):
            response = client.chat.completions.create(
                model=model,
                messages=messages,
            )

        if json_output:
            console.print_json(response.model_dump_json(indent=2))
        else:
            content = response.choices[0].message.content
            console.print(
                Panel(
                    Markdown(content),
                    title=f"[bold blue]{provider_name} Response[/bold blue] (Model: {response.model})",
                    border_style="blue",
                )
            )

    def _stream_response(self, client: ClaifClient, messages: list, model: str, json_output: bool):
        """Handle streaming response."""
        provider_name = client.provider.capitalize()

        if json_output:
            # Stream JSON chunks
            for chunk in client.chat.completions.create(
                model=model,
                messages=messages,
                stream=True,
            ):
                console.print_json(chunk.model_dump_json())
        else:
            # Stream formatted text
            content = ""
            with Live(
                Panel(
                    Spinner("dots", text="Waiting for response..."),
                    title=f"[bold blue]{provider_name} Response[/bold blue]",
                    border_style="blue",
                ),
                refresh_per_second=10,
                console=console,
            ) as live:
                for chunk in client.chat.completions.create(
                    model=model,
                    messages=messages,
                    stream=True,
                ):
                    if chunk.choices and chunk.choices[0].delta.content:
                        content += chunk.choices[0].delta.content
                        live.update(
                            Panel(
                                Markdown(content),
                                title=f"[bold blue]{provider_name} Response[/bold blue] (Model: {model})",
                                border_style="blue",
                            )
                        )

    def chat(
        self,
        model: str | None = None,
        provider: str | None = None,
        system: str | None = None,
    ):
        """Start an interactive chat session.

        Args:
            model: Model name to use
            provider: Provider to use for the chat
            system: Optional system message
        """
        # Handle provider switching
        if provider and provider != self._provider:
            try:
                client = ClaifClient(provider=provider)
            except Exception as e:
                console.print(f"[red]Error switching provider: {e}[/red]")
                return
        else:
            client = self._client

        provider_name = client.provider.capitalize()
        model = model or self._get_default_model(client.provider)

        console.print(
            Panel(
                f"[bold green]{provider_name} Interactive Chat[/bold green]\n"
                f"Model: {model}\n"
                "Type 'exit' or 'quit' to end the session.",
                border_style="green",
            )
        )

        messages = []
        if system:
            messages.append({"role": "system", "content": system})

        while True:
            # Get user input
            try:
                user_input = console.input("\n[bold cyan]You:[/bold cyan] ")
            except (EOFError, KeyboardInterrupt):
                break

            if user_input.lower() in ["exit", "quit"]:
                break

            # Add user message
            messages.append({"role": "user", "content": user_input})

            # Get assistant response
            console.print(f"\n[bold magenta]{provider_name}:[/bold magenta] ", end="")

            try:
                content = ""
                for chunk in client.chat.completions.create(
                    model=model,
                    messages=messages,
                    stream=True,
                ):
                    if chunk.choices and chunk.choices[0].delta.content:
                        chunk_content = chunk.choices[0].delta.content
                        content += chunk_content
                        console.print(chunk_content, end="")

                # Add assistant message to history
                messages.append({"role": "assistant", "content": content})
                console.print()  # New line after response

            except Exception as e:
                console.print(f"\n[red]Error: {e}[/red]")
                # Remove the user message if we failed to get a response
                messages.pop()

        console.print("\n[green]Chat session ended.[/green]")

    def providers(self, json_output: bool = False):
        """List available providers and their status.

        Args:
            json_output: Output as JSON instead of formatted table
        """
        providers = [
            {
                "id": "claude",
                "name": "Anthropic Claude",
                "available": self._check_provider("claude"),
                "env_var": "ANTHROPIC_API_KEY",
            },
            {
                "id": "gemini",
                "name": "Google Gemini",
                "available": self._check_provider("gemini"),
                "env_var": "GEMINI_API_KEY or GOOGLE_API_KEY",
            },
            {
                "id": "codex",
                "name": "OpenAI Codex CLI",
                "available": self._check_provider("codex"),
                "env_var": "N/A (CLI-based)",
            },
            {
                "id": "lms",
                "name": "LM Studio",
                "available": self._check_provider("lms"),
                "env_var": "OPENAI_API_KEY + OPENAI_BASE_URL",
            },
        ]

        if json_output:
            console.print_json(data=providers)
        else:
            from rich.table import Table

            table = Table(title="Available Providers")
            table.add_column("ID", style="cyan")
            table.add_column("Name", style="green")
            table.add_column("Available", style="yellow")
            table.add_column("Environment Variable", style="blue")

            for provider in providers:
                available = "✓" if provider["available"] else "✗"
                table.add_row(provider["id"], provider["name"], available, provider["env_var"])

            console.print(table)
            console.print(f"\n[bold]Current provider:[/bold] {self._provider}")

    def _check_provider(self, provider: str) -> bool:
        """Check if a provider is available."""
        try:
            ClaifClient(provider=provider)
            return True
        except:
            return False

    def models(self, provider: str | None = None, json_output: bool = False):
        """List available models for a provider.

        Args:
            provider: Provider to list models for (uses current if not specified)
            json_output: Output as JSON instead of formatted table
        """
        provider = provider or self._provider

        model_info = {
            "claude": [
                {"id": "claude-3-5-sonnet-20241022", "name": "Claude 3.5 Sonnet", "context": "200K"},
                {"id": "claude-3-opus-20240229", "name": "Claude 3 Opus", "context": "200K"},
                {"id": "claude-3-haiku-20240307", "name": "Claude 3 Haiku", "context": "200K"},
            ],
            "gemini": [
                {"id": "gemini-1.5-pro", "name": "Gemini 1.5 Pro", "context": "2M"},
                {"id": "gemini-1.5-flash", "name": "Gemini 1.5 Flash", "context": "1M"},
                {"id": "gemini-2.0-flash-exp", "name": "Gemini 2.0 Flash", "context": "1M"},
            ],
            "codex": [
                {"id": "gpt-4o", "name": "GPT-4o", "context": "128K"},
                {"id": "o1-preview", "name": "O1 Preview", "context": "128K"},
                {"id": "o3", "name": "O3", "context": "N/A"},
            ],
            "lms": [
                {"id": "gpt-3.5-turbo", "name": "GPT-3.5 Turbo", "context": "16K"},
                {"id": "gpt-4", "name": "GPT-4", "context": "128K"},
                {"id": "custom", "name": "Custom Model", "context": "Varies"},
            ],
        }

        models = model_info.get(provider, [])

        if json_output:
            console.print_json(data=models)
        else:
            from rich.table import Table

            table = Table(title=f"Available Models for {provider.capitalize()}")
            table.add_column("Model ID", style="cyan")
            table.add_column("Name", style="green")
            table.add_column("Context Window", style="yellow")

            for model in models:
                table.add_row(model["id"], model["name"], model["context"])

            console.print(table)

    def version(self):
        """Show version information."""
        console.print("claif version 1.0.0")
        console.print(f"Current provider: {self._provider}")


def main():
    """Main entry point for the CLI."""
    fire.Fire(CLI)
