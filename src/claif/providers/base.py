"""Base provider class with retry logic for Claif."""

from abc import ABC, abstractmethod
from collections.abc import AsyncIterator
from typing import Any

from tenacity import (
    AsyncRetrying,
    RetryError,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
)

from claif.common import ClaifOptions, ClaifTimeoutError, Message, ProviderError, logger


class BaseProvider(ABC):
    """Base provider with retry logic for Claif providers."""

    def __init__(self, name: str):
        self.name = name

    @abstractmethod
    async def _query_impl(
        self,
        prompt: str,
        options: ClaifOptions,
    ) -> AsyncIterator[Message]:
        """Implementation-specific query method to be overridden by subclasses."""
        ...

    async def query(
        self,
        prompt: str,
        options: ClaifOptions,
    ) -> AsyncIterator[Message]:
        """Query provider with retry logic."""
        if options.retry_count <= 0:
            logger.debug(f"{self.name} provider: Retry disabled, single attempt")
            async for message in self._query_impl(prompt, options):
                yield message
            return

        retry_exceptions = (
            ProviderError,
            ClaifTimeoutError,
            ConnectionError,
            TimeoutError,
        )

        attempt = 0
        last_error: Exception | None = None

        try:
            async for attempt in AsyncRetrying(
                stop=stop_after_attempt(options.retry_count),
                wait=wait_exponential(
                    multiplier=options.retry_delay,
                    min=options.retry_delay,
                    max=options.retry_delay * 10,
                ),
                retry=retry_if_exception_type(retry_exceptions),
                reraise=True,
            ):
                with attempt:
                    try:
                        logger.debug(
                            f"{self.name} provider: Attempt {attempt.retry_state.attempt_number}/{options.retry_count}"
                        )

                        messages_yielded = False
                        async for message in self._query_impl(prompt, options):
                            messages_yielded = True
                            yield message

                        if not messages_yielded:
                            raise ProviderError(
                                self.name,
                                "No response received from provider",
                            )

                        return

                    except retry_exceptions as e:
                        last_error = e
                        logger.warning(
                            f"{self.name} provider: Attempt {attempt.retry_state.attempt_number} failed: {e}"
                        )
                        if attempt.retry_state.attempt_number >= options.retry_count:
                            raise
                        raise

        except RetryError as e:
            if last_error:
                raise last_error
            raise ProviderError(
                self.name,
                f"All {options.retry_count} retry attempts failed",
                {"retry_error": str(e)},
            )
