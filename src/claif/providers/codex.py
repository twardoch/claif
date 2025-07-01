"""Codex provider for CLAIF."""

from collections.abc import AsyncIterator

import claif_cod

from claif.common import ClaifOptions, Message, logger


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

        async for message in claif_cod.query(prompt, options):
            yield message
