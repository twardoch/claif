"""Gemini provider for Claif."""

from collections.abc import AsyncIterator
from typing import Any

import claif_gem

from claif.common import ClaifOptions, Message, logger
from claif.providers.base import BaseProvider


class GeminiProvider(BaseProvider):
    """
    Implements the Claif provider interface for Google Gemini.

    This class serves as an adapter, translating requests from the generic
    Claif client into calls compatible with the `claif_gem` package, which
    in turn interacts with the Gemini CLI. It ensures seamless integration
    of Gemini models within the Claif framework.
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
        Sends a query to the Gemini CLI via the `claif_gem` package and yields responses.

        This method is the concrete implementation of the `_query_impl` abstract method
        from `BaseProvider`. It is responsible for delegating the prompt and options
        to the `claif_gem.query` function and asynchronously yielding the `Message`
        objects received from it. The `BaseProvider` handles retry logic around this method.

        Args:
            prompt: The input prompt string to be sent to the Gemini model.
            options: An instance of `ClaifOptions` containing various parameters
                     for the query, such as model, temperature, etc.

        Yields:
            Message: A `Message` object representing a chunk of the response from the Gemini CLI.

        Raises:
            Any exceptions raised by `claif_gem.query` (e.g., `claif_gem.TransportError`,
            `claif_gem.ClaifTimeoutError`, or other communication-related errors).
        """
        logger.debug(f"Gemini provider received query: {prompt[:50]}...")

        # Delegate the query to the claif_gem package, which handles subprocess communication.
        async for message in claif_gem.query(prompt, options):
            yield message
