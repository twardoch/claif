"""Claude provider for Claif."""

from collections.abc import AsyncIterator

import claif_cla

from claif.common import ClaifOptions, Message, logger
from claif.providers.base import BaseProvider


class ClaudeProvider(BaseProvider):
    """Claude provider for Claif."""

    def __init__(self):
        super().__init__("claude")

    async def _query_impl(
        self,
        prompt: str,
        options: ClaifOptions,
    ) -> AsyncIterator[Message]:
        """Query Claude implementation."""
        logger.debug(f"Claude provider: {prompt[:50]}...")

        async for message in claif_cla.query(prompt, options):
            yield message
