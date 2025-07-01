"""Client implementation for CLAIF."""

import random
from collections.abc import AsyncIterator

from claif.common import ClaifOptions, Message, Provider, ProviderError, logger
from claif.providers import ClaudeProvider, CodexProvider, GeminiProvider


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
        """Query using specified or default provider."""
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

        async for message in provider_instance.query(prompt, options):
            yield message

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
    """Query using the default client."""
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
