"""Claude provider implementation."""

from typing import AsyncIterator

from ...claif_cla import query as claude_query
from ..common import Message, ClaifOptions, get_logger


logger = get_logger(__name__)


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