"""Codex provider for Claif."""

from collections.abc import AsyncIterator
from typing import Any

import claif_cod

from claif.common import ClaifOptions, Message, logger
from claif.providers.base import BaseProvider


class CodexProvider(BaseProvider):
    """
    Implements the Claif provider interface for OpenAI Codex.

    This class serves as an adapter, translating requests from the generic
    Claif client into calls compatible with the `claif_cod` package, which
    in turn interacts with the Codex CLI. It ensures seamless integration
    of Codex models within the Claif framework.
    """

    def __init__(self) -> None:
        """
        Initializes the CodexProvider.

        Sets the provider name to "codex".
        """
        super().__init__("codex")

    async def _query_impl(
        self,
        prompt: str,
        options: ClaifOptions,
    ) -> AsyncIterator[Message]:
        """
        Sends a query to the Codex CLI via the `claif_cod` package and yields responses.

        This method is the concrete implementation of the `_query_impl` abstract method
        from `BaseProvider`. It is responsible for delegating the prompt and options
        to the `claif_cod.query` function and asynchronously yielding the `Message`
        objects received from it. The `BaseProvider` handles retry logic around this method.

        Args:
            prompt: The input prompt string to be sent to the Codex model.
            options: An instance of `ClaifOptions` containing various parameters
                     for the query, such as model, temperature, etc.

        Yields:
            Message: A `Message` object representing a chunk of the response from the Codex CLI.

        Raises:
            Any exceptions raised by `claif_cod.query` (e.g., `claif_cod.TransportError`,
            `claif_cod.ClaifTimeoutError`, or other communication-related errors).
        """
        logger.debug(f"Codex provider received query: {prompt[:50]}...")

        # Delegate the query to the claif_cod package, which handles subprocess communication.
        async for message in claif_cod.query(prompt, options):
            yield message
