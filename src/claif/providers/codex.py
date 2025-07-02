"""Codex provider for Claif."""

from collections.abc import AsyncIterator

import claif_cod

from claif.common import ClaifOptions, Message, logger
from claif.providers.base import BaseProvider


class CodexProvider(BaseProvider):
    """Codex provider for Claif."""

    def __init__(self):
        super().__init__("codex")

    async def _query_impl(
        self,
        prompt: str,
        options: ClaifOptions,
    ) -> AsyncIterator[Message]:
        """Query Codex implementation."""
        logger.debug(f"Codex provider: {prompt[:50]}...")

        async for message in claif_cod.query(prompt, options):
            yield message
