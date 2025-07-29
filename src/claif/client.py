# this_file: claif/src/claif/client.py
"""Unified Claif client with OpenAI Responses API compatibility."""

import os
from collections.abc import Iterator
from typing import Any, Literal

from openai import NOT_GIVEN, NotGiven
from openai.types.chat import (
    ChatCompletion,
    ChatCompletionChunk,
    ChatCompletionMessageParam,
)


class ClaifClient:
    """Unified client for all Claif providers with OpenAI-compatible API."""

    def __init__(
        self,
        provider: Literal["claude", "gemini", "codex", "lms"] | None = None,
        api_key: str | None = None,
        **kwargs,
    ):
        """Initialize the Claif client with a specific provider or auto-detection.

        Args:
            provider: Provider to use (claude, gemini, codex, lms). If None, auto-detects.
            api_key: API key for the provider (provider-specific env vars used if not set)
            **kwargs: Additional provider-specific parameters
        """
        self.provider = provider or self._detect_provider()
        self._client = None
        self._kwargs = kwargs

        # Initialize the appropriate provider client
        if self.provider == "claude":
            from claif_cla.client import ClaudeClient

            self._client = ClaudeClient(api_key=api_key, **kwargs)
        elif self.provider == "gemini":
            from claif_gem.client import GeminiClient

            self._client = GeminiClient(api_key=api_key, **kwargs)
        elif self.provider == "codex":
            from claif_cod.client import CodexClient

            self._client = CodexClient(**kwargs)  # Codex doesn't use API key
        elif self.provider == "lms":
            from claif_lms.client import LMSClient

            self._client = LMSClient(api_key=api_key, **kwargs)
        else:
            msg = f"Unknown provider: {self.provider}"
            raise ValueError(msg)

        # Create a namespace-like structure to match OpenAI client
        self.chat = self._ChatNamespace(self)

    def _detect_provider(self) -> str:
        """Auto-detect provider based on environment variables."""
        if os.getenv("ANTHROPIC_API_KEY"):
            return "claude"
        if os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY"):
            return "gemini"
        if os.getenv("OPENAI_API_KEY") and os.getenv("OPENAI_BASE_URL", "").endswith("v1"):
            return "lms"  # LM Studio uses OpenAI-compatible endpoints
        if os.getenv("CODEX_CLI_PATH") or self._is_codex_available():
            return "codex"
        # Default to LMS as it's most flexible
        return "lms"

    def _is_codex_available(self) -> bool:
        """Check if Codex CLI is available."""
        import shutil

        return shutil.which("codex") is not None

    class _ChatNamespace:
        """Namespace for chat-related methods to match OpenAI client structure."""

        def __init__(self, parent: "ClaifClient"):
            self.parent = parent
            self.completions = self.parent._CompletionsNamespace(parent)

    class _CompletionsNamespace:
        """Namespace for completions methods to match OpenAI client structure."""

        def __init__(self, parent: "ClaifClient"):
            self.parent = parent

        def create(
            self,
            *,
            messages: list[ChatCompletionMessageParam],
            model: str,
            frequency_penalty: float | None | NotGiven = NOT_GIVEN,
            function_call: Any | None | NotGiven = NOT_GIVEN,
            functions: list[Any] | None | NotGiven = NOT_GIVEN,
            logit_bias: dict[str, int] | None | NotGiven = NOT_GIVEN,
            logprobs: bool | None | NotGiven = NOT_GIVEN,
            max_tokens: int | None | NotGiven = NOT_GIVEN,
            n: int | None | NotGiven = NOT_GIVEN,
            presence_penalty: float | None | NotGiven = NOT_GIVEN,
            response_format: Any | None | NotGiven = NOT_GIVEN,
            seed: int | None | NotGiven = NOT_GIVEN,
            stop: str | None | list[str] | NotGiven = NOT_GIVEN,
            stream: bool | None | NotGiven = NOT_GIVEN,
            temperature: float | None | NotGiven = NOT_GIVEN,
            tool_choice: Any | None | NotGiven = NOT_GIVEN,
            tools: list[Any] | None | NotGiven = NOT_GIVEN,
            top_logprobs: int | None | NotGiven = NOT_GIVEN,
            top_p: float | None | NotGiven = NOT_GIVEN,
            user: str | NotGiven = NOT_GIVEN,
            # Additional parameters
            extra_headers: Any | None | NotGiven = NOT_GIVEN,
            extra_query: Any | None | NotGiven = NOT_GIVEN,
            extra_body: Any | None | NotGiven = NOT_GIVEN,
            timeout: float | NotGiven = NOT_GIVEN,
        ) -> ChatCompletion | Iterator[ChatCompletionChunk]:
            """Create a chat completion using the configured provider.

            This method provides compatibility with OpenAI's chat.completions.create API.
            """
            # Delegate to the provider's implementation
            return self.parent._client.chat.completions.create(
                messages=messages,
                model=model,
                frequency_penalty=frequency_penalty,
                function_call=function_call,
                functions=functions,
                logit_bias=logit_bias,
                logprobs=logprobs,
                max_tokens=max_tokens,
                n=n,
                presence_penalty=presence_penalty,
                response_format=response_format,
                seed=seed,
                stop=stop,
                stream=stream,
                temperature=temperature,
                tool_choice=tool_choice,
                tools=tools,
                top_logprobs=top_logprobs,
                top_p=top_p,
                user=user,
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
            )

    # Convenience method for backward compatibility
    def create(self, **kwargs) -> ChatCompletion:
        """Create a chat completion (backward compatibility method)."""
        return self.chat.completions.create(**kwargs)

    # Provider-specific convenience constructors
    @classmethod
    def claude(cls, api_key: str | None = None, **kwargs) -> "ClaifClient":
        """Create a Claif client configured for Claude."""
        return cls(provider="claude", api_key=api_key, **kwargs)

    @classmethod
    def gemini(cls, api_key: str | None = None, **kwargs) -> "ClaifClient":
        """Create a Claif client configured for Gemini."""
        return cls(provider="gemini", api_key=api_key, **kwargs)

    @classmethod
    def codex(cls, **kwargs) -> "ClaifClient":
        """Create a Claif client configured for Codex."""
        return cls(provider="codex", **kwargs)

    @classmethod
    def lms(cls, api_key: str | None = None, base_url: str | None = None, **kwargs) -> "ClaifClient":
        """Create a Claif client configured for LM Studio."""
        return cls(provider="lms", api_key=api_key, base_url=base_url, **kwargs)
