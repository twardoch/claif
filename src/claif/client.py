"""Client implementation forClaif."""

import random
from collections.abc import AsyncIterator

from claif.common import ClaifOptions, Message, Provider, ProviderError, logger
from claif.providers import ClaudeProvider, CodexProvider, GeminiProvider


def _is_cli_missing_error(error: Exception) -> bool:
    """Check if error indicates missing CLI tool."""
    error_str = str(error).lower()
    error_indicators = [
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


def _get_provider_install_function(provider: Provider):
    """Get the install function for a provider."""
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
    """Unified client for all providers."""

    def __init__(self):
        self.providers: dict[Provider, object] = {
            Provider.CLAUDE: ClaudeProvider(),
            Provider.GEMINI: GeminiProvider(),
            Provider.CODEX: CodexProvider(),
        }

    async def query(
        self,
        prompt: str,
        options: ClaifOptions | None = None,
    ) -> AsyncIterator[Message]:
        """Query using specified or default provider with auto-install support."""
        if options is None:
            options = ClaifOptions()

        provider = options.provider or Provider.CLAUDE

        if provider not in self.providers:
            raise ProviderError(
                provider.value,
                f"Unknown provider: {provider}",
            )

        provider_instance = self.providers[provider]
        logger.debug(f"Using provider: {provider.value}")

        try:
            async for message in provider_instance.query(prompt, options):
                yield message
        except Exception as e:
            # Check if this is a missing CLI tool error
            if _is_cli_missing_error(e):
                logger.info(f"{provider.value} CLI not found, attempting auto-install...")

                # Get the appropriate install function
                install_func = _get_provider_install_function(provider)

                if install_func:
                    install_result = install_func()

                    if install_result.get("installed"):
                        logger.info(f"{provider.value} CLI installed, retrying query...")

                        # Recreate provider instance to clear any cached state
                        if provider == Provider.CLAUDE:
                            self.providers[provider] = ClaudeProvider()
                        elif provider == Provider.GEMINI:
                            self.providers[provider] = GeminiProvider()
                        elif provider == Provider.CODEX:
                            self.providers[provider] = CodexProvider()

                        provider_instance = self.providers[provider]

                        # Retry the query
                        try:
                            async for message in provider_instance.query(prompt, options):
                                yield message
                        except Exception as retry_error:
                            logger.error(f"Query failed even after installing {provider.value} CLI: {retry_error}")
                            raise retry_error
                    else:
                        error_msg = install_result.get("message", "Unknown installation error")
                        logger.error(f"Auto-install failed: {error_msg}")
                        msg = f"{provider.value.title()} CLI not found and auto-install failed: {error_msg}"
                        raise Exception(msg) from e
                else:
                    # No install function available
                    msg = f"{provider.value.title()} CLI not found and no auto-install available"
                    raise Exception(msg) from e
            else:
                # Re-raise non-CLI-missing errors unchanged
                raise e

    async def query_random(
        self,
        prompt: str,
        options: ClaifOptions | None = None,
    ) -> AsyncIterator[Message]:
        """Query using a random provider."""
        if options is None:
            options = ClaifOptions()

        # Select random provider
        provider = random.choice(list(self.providers.keys()))
        options.provider = provider

        logger.debug(f"Randomly selected provider: {provider.value}")

        async for message in self.query(prompt, options):
            yield message

    async def query_all(
        self,
        prompt: str,
        options: ClaifOptions | None = None,
    ) -> AsyncIterator[dict[Provider, list[Message]]]:
        """Query all providers in parallel."""
        if options is None:
            options = ClaifOptions()

        import asyncio

        async def query_provider(provider: Provider) -> tuple[Provider, list[Message]]:
            """Query a single provider and collect messages."""
            provider_options = ClaifOptions(**options.__dict__)
            provider_options.provider = provider

            messages = []
            try:
                async for message in self.query(prompt, provider_options):
                    messages.append(message)
            except Exception as e:
                logger.error(f"Provider {provider.value} failed: {e}")
                # Return empty list on failure
                messages = []

            return provider, messages

        # Query all providers in parallel
        tasks = [query_provider(provider) for provider in self.providers]

        results = await asyncio.gather(*tasks)

        # Convert to dict
        provider_messages = dict(results)

        yield provider_messages

    def list_providers(self) -> list[Provider]:
        """List available providers."""
        return list(self.providers.keys())


# Module-level client instance
_client = ClaifClient()


async def query(
    prompt: str,
    options: ClaifOptions | None = None,
) -> AsyncIterator[Message]:
    """Query using the default client with auto-install support."""
    async for message in _client.query(prompt, options):
        yield message


async def query_random(
    prompt: str,
    options: ClaifOptions | None = None,
) -> AsyncIterator[Message]:
    """Query using a random provider."""
    async for message in _client.query_random(prompt, options):
        yield message


async def query_all(
    prompt: str,
    options: ClaifOptions | None = None,
) -> AsyncIterator[dict[Provider, list[Message]]]:
    """Query all providers in parallel."""
    async for results in _client.query_all(prompt, options):
        yield results
