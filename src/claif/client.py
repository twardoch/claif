# this_file: claif/src/claif/client.py
"""
Client implementation for the Claif framework.

This module provides a unified client interface for interacting with various
Large Language Model (LLM) providers, including functionality for querying,
auto-installation of missing CLIs, and provider rotation on failure.
"""

import random
from collections.abc import AsyncIterator
from typing import Any, Callable, Dict, List, Tuple, Type

from claif.common import ClaifOptions, ClaifTimeoutError, Message, Provider, ProviderError, logger
from claif.providers import ClaudeProvider, CodexProvider, GeminiProvider


def _is_cli_missing_error(error: Exception) -> bool:
    """
    Checks if a given exception indicates a missing CLI tool.

    This function inspects the string representation of the error for common
    phrases that suggest the CLI executable is not found or accessible.

    Args:
        error: The exception to check.

    Returns:
        True if the error indicates a missing CLI tool, False otherwise.
    """
    error_str: str = str(error).lower()
    error_indicators: List[str] = [
        "command not found",
        "no such file or directory",
        "is not recognized as an internal or external command",
        "cannot find",
        "not found",
        "executable not found",
        "permission denied",
        "filenotfounderror",
        "claude not found",
        "gemini not found",
        "codex not found",
    ]
    return any(indicator in error_str for indicator in error_indicators)


def _get_provider_install_function(provider: Provider) -> Callable[[], Dict[str, Any]] | None:
    """
    Retrieves the appropriate installation function for a given provider.

    This function dynamically imports the installation function from the
    respective provider's `install` module.

    Args:
        provider: The Provider enum member for which to get the install function.

    Returns:
        A callable installation function that returns a dictionary with an
        "installed" key (bool) and a "message" key (str), or None if no
        installation function is available for the given provider.
    """
    if provider == Provider.CLAUDE:
        from claif_cla.install import install_claude
        return install_claude
    if provider == Provider.GEMINI:
        from claif_gem.install import install_gemini
        return install_gemini
    if provider == Provider.CODEX:
        from claif_cod.install import install_codex
        return install_codex
    return None


class ClaifClient:
    """
    A unified client for interacting with various LLM providers within the Claif framework.

    This class abstracts away the complexities of managing different provider
    APIs and CLIs, offering a consistent interface for sending queries,
    handling auto-installation, and implementing provider rotation strategies.
    """

    def __init__(self) -> None:
        """
        Initializes the ClaifClient by instantiating available providers.
        """
        self.providers: Dict[Provider, Any] = {
            Provider.CLAUDE: ClaudeProvider(),
            Provider.GEMINI: GeminiProvider(),
            Provider.CODEX: CodexProvider(),
        }

    async def _recreate_provider_instance(self, provider: Provider) -> Any:
        """
        Recreates a provider instance to clear any cached state after an installation.

        Args:
            provider: The Provider enum member for which to recreate the instance.

        Returns:
            The newly created provider instance.
        """
        if provider == Provider.CLAUDE:
            self.providers[provider] = ClaudeProvider()
        elif provider == Provider.GEMINI:
            self.providers[provider] = GeminiProvider()
        elif provider == Provider.CODEX:
            self.providers[provider] = CodexProvider()
        return self.providers[provider]

    async def query(
        self,
        prompt: str,
        options: ClaifOptions | None = None,
    ) -> AsyncIterator[Message]:
        """
        Sends a query to the specified (or default) LLM provider.

        This method includes logic for automatically attempting to install
        missing CLI tools if a `ProviderError` related to a missing CLI is encountered.

        Args:
            prompt: The input prompt for the LLM.
            options: Optional configuration options for the query, including the target provider.

        Yields:
            An asynchronous iterator of Message objects from the LLM.

        Raises:
            ProviderError: If the specified provider is unknown or if the query
                           fails after auto-installation attempts.
            Exception: For other unexpected errors during the query process.
        """
        if options is None:
            options = ClaifOptions()

        # Determine the target provider, defaulting to CLAUDE if not specified.
        provider: Provider = options.provider or Provider.CLAUDE

        # Validate that the selected provider is registered.
        if provider not in self.providers:
            raise ProviderError(
                provider.value,
                f"Unknown provider: {provider}",
            )

        provider_instance: Any = self.providers[provider]
        logger.debug(f"Using provider: {provider.value}")

        try:
            # Attempt to query the selected provider.
            async for message in provider_instance.query(prompt, options):
                yield message
        except Exception as e:
            # Check if the exception indicates a missing CLI tool.
            if _is_cli_missing_error(e):
                logger.debug(f"{provider.value} CLI not found, attempting auto-install...")

                # Get the installation function for the current provider.
                install_func: Callable[[], Dict[str, Any]] | None = _get_provider_install_function(provider)

                if install_func:
                    # Execute the auto-installation.
                    install_result: Dict[str, Any] = install_func()

                    if install_result.get("installed"):
                        logger.debug(f"{provider.value} CLI installed, retrying query...")

                        # Recreate the provider instance to ensure it picks up the newly installed CLI.
                        provider_instance = await self._recreate_provider_instance(provider)

                        # Retry the original query after successful installation.
                        try:
                            async for message in provider_instance.query(prompt, options):
                                yield message
                        except Exception as retry_error:
                            # If the retry also fails, log the error and re-raise it.
                            logger.error(f"Query failed even after installing {provider.value} CLI: {retry_error}")
                            raise retry_error
                    else:
                        # If auto-install failed, extract the error message and raise a ProviderError.
                        error_msg: str = install_result.get("message", "Unknown auto-installation error.")
                        logger.error(f"Auto-install failed for {provider.value}: {error_msg}")
                        msg: str = f"{provider.value.title()} CLI not found and auto-install failed: {error_msg}"
                        raise ProviderError(provider.value, msg) from e
                else:
                    # If no installation function is available for the provider, raise an error.
                    msg: str = f"{provider.value.title()} CLI not found and no auto-install available."
                    raise ProviderError(provider.value, msg) from e
            else:
                # For any other type of exception, re-raise it directly.
                raise e

    async def query_random(
        self,
        prompt: str,
        options: ClaifOptions | None = None,
    ) -> AsyncIterator[Message]:
        """
        Sends a query to a randomly selected LLM provider.

        Args:
            prompt: The input prompt for the LLM.
            options: Optional configuration options for the query. The `provider`
                     option will be overridden by a random selection.

        Yields:
            An asynchronous iterator of Message objects from the randomly selected LLM.
        """
        if options is None:
            options = ClaifOptions()

        # Randomly select a provider from the available ones.
        provider: Provider = random.choice(list(self.providers.keys()))
        options.provider = provider  # Update options with the selected provider.

        logger.debug(f"Randomly selected provider: {provider.value}")

        # Delegate the query to the main `query` method.
        async for message in self.query(prompt, options):
            yield message

    async def query_all(
        self,
        prompt: str,
        options: ClaifOptions | None = None,
    ) -> AsyncIterator[Dict[Provider, List[Message]]]:
        """
        Sends a query to all available LLM providers in parallel.

        Args:
            prompt: The input prompt for the LLM.
            options: Optional configuration options for the query.

        Yields:
            An asynchronous iterator yielding a dictionary where keys are Provider
            enums and values are lists of Message objects received from each provider.
            If a provider fails, its list of messages will be empty.
        """
        if options is None:
            options = ClaifOptions()

        import asyncio

        async def query_provider(provider: Provider) -> Tuple[Provider, List[Message]]:
            """
            Internal helper to query a single provider and collect its messages.
            Handles exceptions by returning an empty list of messages for failed providers.
            """
            # Create a copy of options for each provider to avoid interference.
            provider_options: ClaifOptions = ClaifOptions(**options.__dict__)
            provider_options.provider = provider

            messages: List[Message] = []
            try:
                # Query the provider and append all received messages.
                async for message in self.query(prompt, provider_options):
                    messages.append(message)
            except Exception as e:
                # Log the error but do not re-raise, allowing parallel execution to continue.
                logger.error(f"Provider {provider.value} failed during parallel query: {e}")
                messages = []  # Ensure an empty list is returned on failure.

            return provider, messages

        # Create a list of tasks, one for each provider, to be executed concurrently.
        tasks: List[asyncio.Task[Tuple[Provider, List[Message]]]] = [
            query_provider(provider) for provider in self.providers
        ]

        # Run all tasks concurrently and wait for their completion.
        results: List[Tuple[Provider, List[Message]]] = await asyncio.gather(*tasks)

        # Convert the list of (provider, messages) tuples into a dictionary.
        provider_messages: Dict[Provider, List[Message]] = dict(results)

        yield provider_messages

    def list_providers(self) -> List[Provider]:
        """
        Lists all currently available LLM providers.

        Returns:
            A list of Provider enum members.
        """
        return list(self.providers.keys())

    async def query_with_rotation(
        self,
        prompt: str,
        options: ClaifOptions | None = None,
    ) -> AsyncIterator[Message]:
        """
        Sends a query to LLM providers with automatic rotation on failures.

        This method attempts to use the primary provider first. If it fails
        (even after its own internal retries), it rotates through other
        available providers until a successful response is received or all
        providers have been exhausted.

        Args:
            prompt: The input prompt for the LLM.
            options: Optional configuration options for the query. The `provider`
                     option, if set, will determine the initial primary provider.

        Yields:
            An asynchronous iterator of Message objects from the successful LLM.

        Raises:
            ProviderError: If all providers fail after their respective retry attempts.
        """
        if options is None:
            options = ClaifOptions()

        # Determine the primary provider from options, or default to CLAUDE.
        primary_provider: Provider = options.provider or Provider.CLAUDE
        
        # Construct the list of providers to try, starting with the primary,
        # followed by all other available providers.
        providers_to_try: List[Provider] = [primary_provider]
        for provider in self.providers:
            if provider != primary_provider:
                providers_to_try.append(provider)

        last_error: Exception | None = None
        providers_tried: List[str] = []

        # Iterate through the list of providers, attempting the query with each.
        for provider in providers_to_try:
            providers_tried.append(provider.value)

            # Create a new options object for the current provider to avoid modifying
            # the original options object and ensure provider-specific settings.
            current_options: ClaifOptions = ClaifOptions(**options.__dict__)
            current_options.provider = provider

            logger.debug(f"Attempting query with provider: {provider.value}")

            try:
                # Attempt the query using the current provider.
                async for message in self.query(prompt, current_options):
                    yield message
                return  # If successful, exit the function.

            except (ProviderError, ClaifTimeoutError, Exception) as e:
                # Catch specific errors that might warrant rotation.
                last_error = e
                logger.warning(
                    f"Provider {provider.value} failed after retries: {e}. "
                    f"Rotating to next provider..."
                )

                # If this was the last provider in the rotation list and it failed,
                # then all providers have been exhausted.
                if provider == providers_to_try[-1]:
                    logger.error(f"All providers failed. Tried: {', '.join(providers_tried)}")
                    # Raise a comprehensive ProviderError indicating the complete failure.
                    raise ProviderError(
                        "all",
                        "All providers failed after retry attempts",
                        {"providers_tried": providers_tried, "last_error": str(last_error)},
                    ) from last_error


# Module-level client instance for convenience.
_client: ClaifClient = ClaifClient()


async def query(
    prompt: str,
    options: ClaifOptions | None = None,
) -> AsyncIterator[Message]:
    """
    Convenience function to query the default ClaifClient instance.

    Args:
        prompt: The input prompt for the LLM.
        options: Optional configuration options for the query.

    Yields:
        An asynchronous iterator of Message objects from the LLM.
    """
    async for message in _client.query(prompt, options):
        yield message


async def query_random(
    prompt: str,
    options: ClaifOptions | None = None,
) -> AsyncIterator[Message]:
    """
    Convenience function to query a random provider using the default ClaifClient instance.

    Args:
        prompt: The input prompt for the LLM.
        options: Optional configuration options for the query.

    Yields:
        An asynchronous iterator of Message objects from the randomly selected LLM.
    """
    async for message in _client.query_random(prompt, options):
        yield message


async def query_all(
    prompt: str,
    options: ClaifOptions | None = None,
) -> AsyncIterator[Dict[Provider, List[Message]]]:
    """
    Convenience function to query all providers in parallel using the default ClaifClient instance.

    Args:
        prompt: The input prompt for the LLM.
        options: Optional configuration options for the query.

    Yields:
        An asynchronous iterator yielding a dictionary of messages from all providers.
    """
    async for results in _client.query_all(prompt, options):
        yield results
