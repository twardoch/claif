"""Fire-based CLI for unified CLAIF wrapper."""

import asyncio
import sys
import time

import fire
from rich.columns import Columns
from rich.console import Console
from rich.live import Live
from rich.panel import Panel
from rich.table import Table

from claif.client import _client, query, query_all, query_random
from claif.common import (
    ClaifOptions,
    Config,
    MessageRole,
    Provider,
    ResponseMetrics,
    format_metrics,
    format_response,
    load_config,
    logger,
    save_config,
)
from claif.server import start_mcp_server

console = Console()


class ClaifCLI:
    """Unified CLAIF CLI with Fire interface."""

    def __init__(self, config_file: str | None = None, verbose: bool = False):
        """Initialize CLI with optional config file."""
        logger.remove()
        log_level = "DEBUG" if verbose else "INFO"
        logger.add(sys.stderr, level=log_level)
        self.config = load_config(config_file)
        if verbose:
            self.config.verbose = True
        self.client = _client
        logger.debug("Initialized CLAIF CLI")

    def query(
        self,
        prompt: str,
        provider: str | None = None,
        model: str | None = None,
        temperature: float | None = None,
        max_tokens: int | None = None,
        system: str | None = None,
        timeout: int | None = None,
        output_format: str = "text",
        show_metrics: bool = False,
        cache: bool = True,
    ) -> None:
        """Execute a query to specified provider.

        Args:
            prompt: The prompt to send
            provider: Provider to use (claude, gemini, codex)
            model: Model to use (provider-specific)
            temperature: Sampling temperature (0-1)
            max_tokens: Maximum tokens in response
            system: System prompt
            timeout: Timeout in seconds
            output_format: Output format (text, json, markdown)
            show_metrics: Show response metrics
            cache: Enable response caching
        """
        # Parse provider
        provider_enum = None
        if provider:
            try:
                provider_enum = Provider(provider.lower())
            except ValueError:
                console.print(f"[red]Unknown provider: {provider}[/red]")
                console.print(f"Available providers: {', '.join(p.value for p in Provider)}")
                sys.exit(1)

        options = ClaifOptions(
            provider=provider_enum or self.config.default_provider,
            model=model,
            temperature=temperature,
            max_tokens=max_tokens,
            system_prompt=system,
            timeout=timeout,
            output_format=output_format,
            cache=cache,
            verbose=self.config.verbose,
        )

        start_time = time.time()

        try:
            # Run async query
            messages = asyncio.run(self._query_async(prompt, options))

            # Format and display response
            for message in messages:
                formatted = format_response(message, output_format)
                console.print(formatted)

            # Show metrics if requested
            if show_metrics:
                duration = time.time() - start_time
                metrics = ResponseMetrics(
                    duration=duration,
                    provider=options.provider,
                    model=model or "default",
                )
                console.print("\n" + format_metrics(metrics))

        except Exception as e:
            console.print(f"[red]Error: {e}[/red]")
            if self.config.verbose:
                console.print_exception()
            sys.exit(1)

    async def _query_async(self, prompt: str, options: ClaifOptions) -> list:
        """Execute async query and collect messages."""
        messages = []
        async for message in query(prompt, options):
            messages.append(message)
        return messages

    def stream(
        self,
        prompt: str,
        provider: str | None = None,
        model: str | None = None,
        temperature: float | None = None,
        system: str | None = None,
    ) -> None:
        """Stream responses with live display.

        Args:
            prompt: The prompt to send
            provider: Provider to use
            model: Model to use
            temperature: Sampling temperature (0-1)
            system: System prompt
        """
        # Parse provider
        provider_enum = None
        if provider:
            try:
                provider_enum = Provider(provider.lower())
            except ValueError:
                console.print(f"[red]Unknown provider: {provider}[/red]")
                sys.exit(1)

        options = ClaifOptions(
            provider=provider_enum or self.config.default_provider,
            model=model,
            temperature=temperature,
            system_prompt=system,
            verbose=self.config.verbose,
        )

        try:
            asyncio.run(self._stream_async(prompt, options))
        except KeyboardInterrupt:
            console.print("\n[yellow]Stream interrupted[/yellow]")
        except Exception as e:
            console.print(f"[red]Error: {e}[/red]")
            if self.config.verbose:
                console.print_exception()
            sys.exit(1)

    async def _stream_async(self, prompt: str, options: ClaifOptions) -> None:
        """Stream responses with live display."""
        content_buffer = []

        provider_name = options.provider.value if options.provider else "default"

        with Live(console=console, refresh_per_second=10) as live:
            live.update(f"[dim]Streaming from {provider_name}...[/dim]")

            async for message in query(prompt, options):
                # Update live display
                if isinstance(message.content, str):
                    content_buffer.append(message.content)
                elif isinstance(message.content, list):
                    for block in message.content:
                        if hasattr(block, "text"):
                            content_buffer.append(block.text)

                live.update("".join(content_buffer))

    def random(
        self,
        prompt: str,
        model: str | None = None,
        temperature: float | None = None,
        system: str | None = None,
        show_provider: bool = True,
    ) -> None:
        """Query a random provider.

        Args:
            prompt: The prompt to send
            model: Model to use (if supported by selected provider)
            temperature: Sampling temperature (0-1)
            system: System prompt
            show_provider: Show which provider was selected
        """
        options = ClaifOptions(
            model=model,
            temperature=temperature,
            system_prompt=system,
            verbose=self.config.verbose,
        )

        try:
            # Track which provider was used
            selected_provider = None

            async def track_provider():
                messages = []
                async for message in query_random(prompt, options):
                    messages.append(message)
                # Get provider from options after random selection
                nonlocal selected_provider
                selected_provider = options.provider
                return messages

            messages = asyncio.run(track_provider())

            if show_provider and selected_provider:
                console.print(f"[cyan]Selected provider: {selected_provider.value}[/cyan]\n")

            for message in messages:
                console.print(format_response(message))

        except Exception as e:
            console.print(f"[red]Error: {e}[/red]")
            if self.config.verbose:
                console.print_exception()
            sys.exit(1)

    def parallel(
        self,
        prompt: str,
        model: str | None = None,
        temperature: float | None = None,
        system: str | None = None,
        compare: bool = False,
    ) -> None:
        """Query all providers in parallel.

        Args:
            prompt: The prompt to send
            model: Model to use (provider-specific defaults apply)
            temperature: Sampling temperature (0-1)
            system: System prompt
            compare: Show responses side-by-side for comparison
        """
        options = ClaifOptions(
            model=model,
            temperature=temperature,
            system_prompt=system,
            verbose=self.config.verbose,
        )

        try:
            results = asyncio.run(self._parallel_query(prompt, options))

            if compare:
                # Show side-by-side comparison
                panels = []
                for provider, messages in results.items():
                    content = (
                        "\n".join(format_response(msg) for msg in messages) if messages else "[dim]No response[/dim]"
                    )

                    panel = Panel(
                        content,
                        title=f"[bold]{provider.value}[/bold]",
                        border_style="cyan" if messages else "red",
                    )
                    panels.append(panel)

                console.print(Columns(panels, equal=True, expand=True))
            else:
                # Show responses sequentially
                for provider, messages in results.items():
                    console.print(f"\n[bold cyan]{provider.value}:[/bold cyan]")

                    if messages:
                        for message in messages:
                            console.print(format_response(message))
                    else:
                        console.print("[dim]No response or error occurred[/dim]")

                    console.print("-" * 50)

        except Exception as e:
            console.print(f"[red]Error: {e}[/red]")
            if self.config.verbose:
                console.print_exception()
            sys.exit(1)

    async def _parallel_query(self, prompt: str, options: ClaifOptions) -> dict:
        """Execute parallel queries."""
        async for results in query_all(prompt, options):
            return results
        return None

    def providers(self, action: str = "list") -> None:
        """Manage providers.

        Args:
            action: Action to perform (list, status)
        """
        if action == "list":
            console.print("[bold]Available Providers:[/bold]")

            table = Table(show_header=True, header_style="bold cyan")
            table.add_column("Provider", style="green")
            table.add_column("Status")
            table.add_column("Default Model")

            for provider in Provider:
                provider_config = self.config.providers.get(provider.value, {})

                if hasattr(provider_config, "enabled"):
                    enabled = provider_config.enabled
                    model = provider_config.model or "default"
                else:
                    enabled = provider_config.get("enabled", True)
                    model = provider_config.get("model", "default")

                status = "[green]Enabled[/green]" if enabled else "[red]Disabled[/red]"

                # Mark default provider
                if provider == self.config.default_provider:
                    status += " [yellow](default)[/yellow]"

                table.add_row(provider.value, status, model)

            console.print(table)

        elif action == "status":
            # Check health of each provider
            console.print("[bold]Provider Health Check:[/bold]")

            async def check_provider(provider: Provider) -> tuple[Provider, bool]:
                try:
                    options = ClaifOptions(
                        provider=provider,
                        max_tokens=10,
                        timeout=5,
                    )
                    message_count = 0
                    async for _ in query("Hello", options):
                        message_count += 1
                        break
                    return provider, message_count > 0
                except Exception:
                    return provider, False

            async def check_all():
                tasks = [check_provider(p) for p in Provider]
                return await asyncio.gather(*tasks)

            results = asyncio.run(check_all())

            for provider, healthy in results:
                status = "[green]✓ Healthy[/green]" if healthy else "[red]✗ Unhealthy[/red]"
                console.print(f"  {provider.value}: {status}")

        else:
            console.print(f"[red]Unknown action: {action}[/red]")
            console.print("Available actions: list, status")

    def server(
        self,
        host: str = "localhost",
        port: int = 8000,
        reload: bool = False,
    ) -> None:
        """Start the FastMCP server.

        Args:
            host: Host to bind to
            port: Port to bind to
            reload: Enable auto-reload for development
        """
        console.print("[bold]Starting CLAIF MCP Server[/bold]")
        console.print(f"Host: {host}")
        console.print(f"Port: {port}")
        console.print(f"Reload: {reload}")
        console.print("\n[yellow]Press Ctrl+C to stop[/yellow]")

        try:
            start_mcp_server(host, port, reload, self.config)
        except KeyboardInterrupt:
            console.print("\n[yellow]Server stopped[/yellow]")
        except Exception as e:
            console.print(f"[red]Server error: {e}[/red]")
            sys.exit(1)

    def config(self, action: str = "show", **kwargs) -> None:
        """Manage CLAIF configuration.

        Args:
            action: Action to perform (show, set, save)
            **kwargs: Configuration values for 'set' action
        """
        if action == "show":
            console.print("[bold]CLAIF Configuration:[/bold]")
            logger.debug(f"Displaying config: {self.config}")
            console.print(f"  Default Provider: {self.config.default_provider.value}")
            console.print(f"  Cache Enabled: {self.config.cache_enabled}")
            console.print(f"  Cache TTL: {self.config.cache_ttl}s")
            console.print(f"  Session Directory: {self.config.session_dir}")
            console.print(f"  Verbose: {self.config.verbose}")
            console.print(f"  Output Format: {self.config.output_format}")

            console.print("\n[bold]Provider Settings:[/bold]")
            for provider_name, provider_config in self.config.providers.items():
                console.print(f"\n  {provider_name}:")
                if hasattr(provider_config, "__dict__"):
                    for key, value in provider_config.__dict__.items():
                        if key != "extra":
                            console.print(f"    {key}: {value}")

        elif action == "set":
            if not kwargs:
                console.print("[red]No configuration values provided[/red]")
                return

            logger.debug(f"Updating config with: {kwargs}")
            # Update configuration
            for key, value in kwargs.items():
                if key == "default_provider":
                    try:
                        self.config.default_provider = Provider(value.lower())
                        console.print(f"[green]Set default provider: {value}[/green]")
                    except ValueError:
                        console.print(f"[red]Invalid provider: {value}[/red]")
                elif hasattr(self.config, key):
                    setattr(self.config, key, value)
                    console.print(f"[green]Set {key}: {value}[/green]")
                else:
                    console.print(f"[yellow]Unknown setting: {key}[/yellow]")

        elif action == "save":
            path = kwargs.get("path")
            save_config(self.config, path)
            saved_path = path or "~/.claif/config.json"
            logger.info(f"Configuration saved to: {saved_path}")
            console.print(f"[green]Configuration saved to: {saved_path}[/green]")

        else:
            console.print(f"[red]Unknown action: {action}[/red]")
            console.print("Available actions: show, set, save")

    def session(self, provider: str, *args, **kwargs) -> None:
        """Start a provider-specific session.

        Args:
            provider: Provider to use (claude, gemini, codex)
            *args: Arguments to pass to provider CLI
            **kwargs: Keyword arguments to pass to provider CLI
        """
        # Import the appropriate CLI module
        if provider == "claude":
            from claif_cla.cli import ClaudeCLI

            cli = ClaudeCLI(verbose=self.config.verbose)
        elif provider == "gemini":
            from claif_gem.cli import GeminiCLI

            cli = GeminiCLI(verbose=self.config.verbose)
        elif provider == "codex":
            from claif_cod.cli import CodexCLI

            cli = CodexCLI(verbose=self.config.verbose)
        else:
            console.print(f"[red]Unknown provider: {provider}[/red]")
            console.print("Available providers: claude, gemini, codex")
            return

        # Start interactive session
        console.print(f"[bold]Starting {provider} session...[/bold]")

        # If the provider CLI has an interactive method, use it
        if hasattr(cli, "interactive"):
            cli.interactive()
        else:
            logger.warning(f"Interactive mode not available for {provider}")
            console.print(f"[yellow]Interactive mode not available for {provider}[/yellow]")


def main():
    """Main entry point for Fire CLI."""
    fire.Fire(ClaifCLI)
