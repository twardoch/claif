"""Claude provider implementation."""

from collections.abc import AsyncIterator

from src.claif.common import ClaifOptions, Message, logger
from src.claif_cla import query as claude_query


class ClaudeProvider:
    """Claude provider for CLAIF."""

    def __init__(self):
        self.name = "claude"

    async def query(
        self,
        prompt: str,
        options: ClaifOptions,
    ) -> AsyncIterator[Message]:
        """Query Claude."""
        logger.debug(f"Claude provider: {prompt[:50]}...")

        async for message in claude_query(prompt, options):
            yield message
