"""Codex provider implementation."""

from collections.abc import AsyncIterator

from src.claif.common import ClaifOptions, Message, logger
from src.claif_cod import query as codex_query


class CodexProvider:
    """Codex provider for CLAIF."""

    def __init__(self):
        self.name = "codex"

    async def query(
        self,
        prompt: str,
        options: ClaifOptions,
    ) -> AsyncIterator[Message]:
        """Query Codex."""
        logger.debug(f"Codex provider: {prompt[:50]}...")

        async for message in codex_query(prompt, options):
            yield message
