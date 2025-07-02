"""Claude provider forClaif."""

from collections.abc import AsyncIterator

import claif_cla

from claif.common import ClaifOptions, Message, logger


class ClaudeProvider:
    """Claude provider forClaif."""

    def __init__(self):
        self.name = "claude"

    async def query(
        self,
        prompt: str,
        options: ClaifOptions,
    ) -> AsyncIterator[Message]:
        """Query Claude."""
        logger.debug(f"Claude provider: {prompt[:50]}...")

        async for message in claif_cla.query(prompt, options):
            yield message
