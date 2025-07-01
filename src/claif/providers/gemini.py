"""Gemini provider implementation."""

from typing import AsyncIterator

from ...claif_gem import query as gemini_query
from ..common import Message, ClaifOptions, get_logger


logger = get_logger(__name__)


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