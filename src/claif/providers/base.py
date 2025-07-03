"""Base provider class with retry logic for Claif."""

from abc import ABC, abstractmethod
from collections.abc import AsyncIterator
from typing import Any, Optional, Type, Tuple

from tenacity import (
    AsyncRetrying,
    RetryError,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
)

from claif.common import ClaifOptions, ClaifTimeoutError, Message, ProviderError, logger


class BaseProvider(ABC):
    """
    Abstract base class for all Claif LLM providers.

    This class provides a standardized interface for querying LLMs and
    implements common functionalities such as retry logic for transient failures.
    Subclasses must implement the `_query_impl` method to define their
    provider-specific query mechanism.
    """

    def __init__(self, name: str) -> None:
        """
        Initializes the BaseProvider.

        Args:
            name: The name of the provider (e.g., "claude", "gemini", "codex").
        """
        self.name: str = name

    @abstractmethod
    async def _query_impl(
        self,
        prompt: str,
        options: ClaifOptions,
    ) -> AsyncIterator[Message]:
        """
        Abstract method for the provider-specific query implementation.

        Subclasses must override this method to define how they interact with
        their respective LLM APIs or CLIs. This method should yield `Message`
        objects as they are received.

        Args:
            prompt: The input prompt for the LLM.
            options: `ClaifOptions` containing query parameters specific to this provider.

        Yields:
            An asynchronous iterator of `Message` objects.

        Raises:
            ProviderError: If a provider-specific error occurs.
            ClaifTimeoutError: If the query times out.
            ConnectionError: If there's a network connection issue.
            Exception: For any other unexpected errors.
        """
        ...

    async def query(
        self,
        prompt: str,
        options: ClaifOptions,
    ) -> AsyncIterator[Message]:
        """
        Sends a query to the LLM provider with built-in retry logic using `tenacity`.

        This method wraps the `_query_impl` with robust retry functionality.
        It leverages `tenacity.AsyncRetrying` to handle transient failures
        (e.g., network issues, provider-specific errors, timeouts) based on
        the `retry_count`, `retry_delay`, and `retry_backoff` configured in `ClaifOptions`.

        Args:
            prompt: The input prompt for the LLM.
            options: `ClaifOptions` containing query parameters and retry settings.

        Yields:
            An asynchronous iterator of `Message` objects received from the LLM.

        Raises:
            ProviderError: If all retry attempts fail due to a provider-specific error
                           or if no response is received after a successful query execution.
            ClaifTimeoutError: If all retry attempts fail due to a timeout.
            ConnectionError: If all retry attempts fail due to a network connection issue.
            Exception: For any other unhandled exceptions that persist after all retries
                       or are not configured to be retried.
        # If retries are explicitly disabled, execute the query once without retry.
        if options.no_retry or options.retry_count <= 0:
            logger.debug(f"{self.name} provider: Retries disabled, performing single attempt.")
            async for message in self._query_impl(prompt, options):
                yield message
            return

        # Define the types of exceptions that should trigger a retry.
        retry_exceptions: Tuple[Type[Exception], ...] = (
            ProviderError,
            ClaifTimeoutError,
            ConnectionError,
            TimeoutError,  # Standard Python TimeoutError
        )

        try:
            # Use AsyncRetrying from tenacity to handle retries.
            async for attempt in AsyncRetrying(
                stop=stop_after_attempt(options.retry_count),  # Maximum number of attempts
                wait=wait_exponential(
                    multiplier=options.retry_delay,
                    min=options.retry_delay,
                    max=options.retry_delay * 10,  # Cap max delay to prevent excessive waits
                ),  # Exponential backoff strategy
                retry=retry_if_exception_type(retry_exceptions),  # Only retry on specific exceptions
                reraise=True,  # Re-raise the last exception if all retries fail
            ):
                with attempt:
                    logger.debug(
                        f"{self.name} provider: Attempt {attempt.retry_state.attempt_number}/{options.retry_count}"
                    )

                    messages_yielded: bool = False
                    try:
                        # Execute the actual query implementation.
                        async for message in self._query_impl(prompt, options):
                            messages_yielded = True
                            yield message

                        # If no messages were yielded, it indicates an issue, so raise an error.
                        if not messages_yielded:
                            raise ProviderError(
                                self.name,
                                "No response received from provider after successful query execution.",
                            )

                        return  # Query successful, exit the retry loop.

                    except retry_exceptions as e:
                        # Catch retryable exceptions and re-raise to trigger tenacity.
                        logger.warning(
                            f"{self.name} provider: Attempt {attempt.retry_state.attempt_number} failed: {e}"
                        )
                        # Tenacity will decide whether to retry or re-raise based on its configuration.
                        raise

        except RetryError as e:
            # This block is reached if all retry attempts have been exhausted.
            # The `reraise=True` in AsyncRetrying ensures that `e.__cause__` holds the last exception.
            # We re-raise the original exception that caused the final failure.
            if e.__cause__ is not None:
                raise e.__cause__
            else:
                # Fallback if for some reason __cause__ is not set (should not happen with reraise=True).
                raise ProviderError(
                    self.name,
                    f"All {options.retry_count} retry attempts failed without a specific cause recorded.",
                    {"retry_error_details": str(e)},
                ) from e
