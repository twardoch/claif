"""Gemini provider for Claif."""

from collections.abc import AsyncIterator

import claif_gem

from claif.common import ClaifOptions, Message, logger


class GeminiProvider:
    """Gemini provider for Claif."""

    def __init__(self):
        self.name = "gemini"

    async def query(
        self,
        prompt: str,
        options: ClaifOptions,
    ) -> AsyncIterator[Message]:
        """Query Gemini."""
        logger.debug(f"Gemini provider: {prompt[:50]}...")

        async for message in claif_gem.query(prompt, options):
            yield message
