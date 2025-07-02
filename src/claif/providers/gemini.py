"""Gemini provider for Claif."""

from collections.abc import AsyncIterator

import claif_gem

from claif.common import ClaifOptions, Message, logger
from claif.providers.base import BaseProvider


class GeminiProvider(BaseProvider):
    """Gemini provider for Claif."""

    def __init__(self):
        super().__init__("gemini")

    async def _query_impl(
        self,
        prompt: str,
        options: ClaifOptions,
    ) -> AsyncIterator[Message]:
        """Query Gemini implementation."""
        logger.debug(f"Gemini provider: {prompt[:50]}...")

        async for message in claif_gem.query(prompt, options):
            yield message
