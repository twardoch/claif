"""Gemini provider for Claif."""

from collections.abc import AsyncIterator
from typing import Any

import claif_gem

from claif.common import ClaifOptions, Message, logger
from claif.providers.base import BaseProvider


class GeminiProvider(BaseProvider):
    """
    Implements the Claif provider interface for Google Gemini.

    This class acts as a bridge between the generic Claif client and the
    `claif_gem` package, which handles the actual communication with the
    Gemini CLI.
    """

    def __init__(self) -> None:
        """
        Initializes the GeminiProvider.

        Sets the provider name to "gemini".
        """
        super().__init__("gemini")

    async def _query_impl(
        self,
        prompt: str,
        options: ClaifOptions,
    ) -> AsyncIterator[Message]:
        """
        Sends a query to the Gemini CLI via the `claif_gem` package.

        This is the core implementation method for the Gemini provider,
        called by the `BaseProvider`'s `query` method (which handles retries).

        Args:
            prompt: The input prompt for the Gemini model.
            options: `ClaifOptions` containing query parameters.

        Yields:
            An asynchronous iterator of `Message` objects received from the Gemini CLI.

        Raises:
            Any exceptions raised by `claif_gem.query` (e.g., TransportError, ClaifTimeoutError).
        """
        logger.debug(f"Gemini provider received query: {prompt[:50]}...")

        # Delegate the query to the claif_gem package, which handles subprocess communication.
        async for message in claif_gem.query(prompt, options):
            yield message
