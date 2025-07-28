"""Claude provider for Claif."""

from collections.abc import AsyncIterator
from typing import Any

import claif_cla

from claif.common import ClaifOptions, Message, logger
from claif.providers.base import BaseProvider


class ClaudeProvider(BaseProvider):
    """
    Implements the Claif provider interface for Anthropic Claude.

    This class serves as an adapter, translating requests from the generic
    Claif client into calls compatible with the `claif_cla` package, which
    in turn interacts with the Claude Code CLI. It ensures seamless integration
    of Claude models within the Claif framework.
    """

    def __init__(self) -> None:
        """
        Initializes the ClaudeProvider.

        Sets the provider name to "claude".
        """
        super().__init__("claude")

    async def _query_impl(
        self,
        prompt: str,
        options: ClaifOptions,
    ) -> AsyncIterator[Message]:
        """
        Sends a query to the Claude CLI via the `claif_cla` package and yields responses.

        This method is the concrete implementation of the `_query_impl` abstract method
        from `BaseProvider`. It is responsible for delegating the prompt and options
        to the `claif_cla.query` function and asynchronously yielding the `Message`
        objects received from it. The `BaseProvider` handles retry logic around this method.

        Args:
            prompt: The input prompt string to be sent to the Claude model.
            options: An instance of `ClaifOptions` containing various parameters
                     for the query, such as model, temperature, etc.

        Yields:
            Message: A `Message` object representing a chunk of the response from the Claude CLI.

        Raises:
            Any exceptions raised by `claif_cla.query` (e.g., `claif_cla.TransportError`,
            `claif_cla.ClaifTimeoutError`, or other communication-related errors).
        """
        logger.debug(f"Claude provider received query: {prompt[:50]}...")

        # Delegate the query to the claif_cla package, which handles subprocess communication.
        async for message in claif_cla.query(prompt, options):
            yield message
