"""Gemini provider implementation."""

from collections.abc import AsyncIterator

from src.claif.common import ClaifOptions, Message, logger
from src.claif_gem import query as gemini_query


class GeminiProvider:
    """Gemini provider for CLAIF."""

    def __init__(self):
        self.name = "gemini"

    async def query(
        self,
        prompt: str,
        options: ClaifOptions,
    ) -> AsyncIterator[Message]:
        """Query Gemini."""
        logger.debug(f"Gemini provider: {prompt[:50]}...")

        async for message in gemini_query(prompt, options):
            yield message
