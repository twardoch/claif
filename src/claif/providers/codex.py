"""Codex provider implementation."""

from typing import AsyncIterator

from ...claif_cod import query as codex_query
from ..common import Message, ClaifOptions, get_logger


logger = get_logger(__name__)


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