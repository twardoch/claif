# this_file: claif/tests/test_functional.py
"""Functional tests for the main claif package that validate unified client behavior."""

import os
from unittest.mock import MagicMock, patch

import pytest
from openai.types.chat import ChatCompletion, ChatCompletionChunk
from openai.types.chat.chat_completion import Choice
from openai.types.chat.chat_completion_chunk import Choice as ChunkChoice
from openai.types.chat.chat_completion_chunk import ChoiceDelta
from openai.types.chat.chat_completion_message import ChatCompletionMessage
from openai.types.completion_usage import CompletionUsage

from claif.client import ClaifClient


class TestClaifClientFunctional:
    """Functional tests for the unified ClaifClient."""

    @pytest.fixture
    def mock_claude_client(self):
        """Create a mock Claude client."""
        mock_client = MagicMock()
        mock_chat = MagicMock()
        mock_completions = MagicMock()
        mock_client.chat = mock_chat
        mock_chat.completions = mock_completions

        # Setup response
        timestamp = 1234567890
        mock_response = ChatCompletion(
            id="chatcmpl-claude",
            object="chat.completion",
            created=timestamp,
            model="claude-3-5-sonnet-20241022",
            choices=[
                Choice(
                    index=0,
                    message=ChatCompletionMessage(role="assistant", content="Hello from Claude!"),
                    finish_reason="stop",
                    logprobs=None,
                )
            ],
            usage=CompletionUsage(prompt_tokens=10, completion_tokens=5, total_tokens=15),
        )
        mock_completions.create.return_value = mock_response
        return mock_client

    def test_provider_auto_detection_claude(self):
        """Test auto-detection of Claude provider based on env var."""
        with patch.dict(os.environ, {"ANTHROPIC_API_KEY": "test-key"}):
            client = ClaifClient()
            assert client.provider == "claude"

    def test_provider_auto_detection_gemini(self):
        """Test auto-detection of Gemini provider based on env var."""
        with patch.dict(os.environ, {"GEMINI_API_KEY": "test-key"}, clear=True):
            client = ClaifClient()
            assert client.provider == "gemini"

    def test_provider_auto_detection_codex(self):
        """Test auto-detection of Codex provider based on CLI availability."""
        with patch.dict(os.environ, {}, clear=True), patch("shutil.which", return_value="/usr/local/bin/codex"):
            client = ClaifClient()
            assert client.provider == "codex"

    def test_provider_auto_detection_lms(self):
        """Test auto-detection of LMS provider as default."""
        with patch.dict(os.environ, {}, clear=True), patch("shutil.which", return_value=None):
            client = ClaifClient()
            assert client.provider == "lms"

    def test_explicit_provider_selection(self):
        """Test explicit provider selection overrides auto-detection."""
        with patch.dict(os.environ, {"ANTHROPIC_API_KEY": "test-key"}):
            client = ClaifClient(provider="gemini")
            assert client.provider == "gemini"

    @patch("claif_cla.client.ClaudeClient")
    def test_claude_client_initialization(self, mock_claude_class):
        """Test Claude client is properly initialized."""
        mock_claude_class.return_value = MagicMock()

        client = ClaifClient(provider="claude", api_key="test-key", timeout=300)

        # Verify ClaudeClient was created with correct params
        mock_claude_class.assert_called_once_with(api_key="test-key", timeout=300)
        assert client._client is not None

    @patch("claif_gem.client.GeminiClient")
    def test_gemini_client_initialization(self, mock_gemini_class):
        """Test Gemini client is properly initialized."""
        mock_gemini_class.return_value = MagicMock()

        client = ClaifClient(provider="gemini", api_key="test-key", cli_path="/custom/path")

        # Verify GeminiClient was created with correct params
        mock_gemini_class.assert_called_once_with(api_key="test-key", cli_path="/custom/path")
        assert client._client is not None

    @patch("claif_cod.client.CodexClient")
    def test_codex_client_initialization(self, mock_codex_class):
        """Test Codex client is properly initialized."""
        mock_codex_class.return_value = MagicMock()

        client = ClaifClient(provider="codex", working_dir="/tmp/project")

        # Verify CodexClient was created without api_key
        mock_codex_class.assert_called_once_with(working_dir="/tmp/project")
        assert client._client is not None

    @patch("claif_lms.client.LMSClient")
    def test_lms_client_initialization(self, mock_lms_class):
        """Test LMS client is properly initialized."""
        mock_lms_class.return_value = MagicMock()

        client = ClaifClient(provider="lms", api_key="test-key", base_url="http://localhost:1234")

        # Verify LMSClient was created with correct params
        mock_lms_class.assert_called_once_with(api_key="test-key", base_url="http://localhost:1234")
        assert client._client is not None

    def test_unknown_provider_error(self):
        """Test error is raised for unknown provider."""
        with pytest.raises(ValueError) as exc_info:
            ClaifClient(provider="unknown")

        assert "Unknown provider: unknown" in str(exc_info.value)

    @patch("claif_cla.client.ClaudeClient")
    def test_chat_completions_create(self, mock_claude_class):
        """Test chat.completions.create delegates to provider client."""
        # Setup mock client
        mock_client = MagicMock()
        mock_chat = MagicMock()
        mock_completions = MagicMock()
        mock_client.chat = mock_chat
        mock_chat.completions = mock_completions

        # Setup response
        mock_response = MagicMock(spec=ChatCompletion)
        mock_completions.create.return_value = mock_response
        mock_claude_class.return_value = mock_client

        # Create Claif client
        client = ClaifClient(provider="claude")

        # Execute query
        response = client.chat.completions.create(
            model="claude-3-5-sonnet-20241022", messages=[{"role": "user", "content": "Hello"}], temperature=0.7
        )

        # Verify delegation
        mock_completions.create.assert_called_once_with(
            model="claude-3-5-sonnet-20241022", messages=[{"role": "user", "content": "Hello"}], temperature=0.7
        )
        assert response == mock_response

    @patch("claif_cla.client.ClaudeClient")
    def test_streaming_support(self, mock_claude_class):
        """Test streaming response handling."""
        # Setup mock client
        mock_client = MagicMock()
        mock_chat = MagicMock()
        mock_completions = MagicMock()
        mock_client.chat = mock_chat
        mock_chat.completions = mock_completions

        # Create mock stream
        def mock_stream():
            for word in ["Hello", " from", " Claude!"]:
                chunk = MagicMock(spec=ChatCompletionChunk)
                chunk.choices = [MagicMock(delta=MagicMock(content=word))]
                yield chunk

        mock_completions.create.return_value = mock_stream()
        mock_claude_class.return_value = mock_client

        # Create Claif client
        client = ClaifClient(provider="claude")

        # Execute streaming query
        stream = client.chat.completions.create(
            model="claude-3-5-sonnet-20241022", messages=[{"role": "user", "content": "Hello"}], stream=True
        )

        # Collect chunks
        chunks = list(stream)

        # Verify streaming
        assert len(chunks) == 3
        content = "".join(c.choices[0].delta.content for c in chunks)
        assert content == "Hello from Claude!"

    @patch("claif_cla.client.ClaudeClient")
    @patch("claif_gem.client.GeminiClient")
    def test_provider_switching(self, mock_gemini_class, mock_claude_class):
        """Test switching between providers by creating new client instances."""
        # Setup mock clients
        mock_claude = MagicMock()
        mock_gemini = MagicMock()
        mock_claude_class.return_value = mock_claude
        mock_gemini_class.return_value = mock_gemini

        # Create Claude client
        claude_client = ClaifClient(provider="claude")
        assert claude_client._client == mock_claude

        # Create Gemini client (new instance)
        gemini_client = ClaifClient(provider="gemini")
        assert gemini_client._client == mock_gemini

        # Verify both are independent
        assert claude_client._client != gemini_client._client


class TestClaifClientIntegration:
    """Integration tests that would run against real provider implementations."""

    @pytest.mark.skip(reason="Requires claif_cla package to be installed")
    def test_real_claude_import(self):
        """Test importing real Claude provider."""
        client = ClaifClient(provider="claude")
        assert client.provider == "claude"
        assert hasattr(client._client, "chat")

    @pytest.mark.skip(reason="Requires claif_gem package to be installed")
    def test_real_gemini_import(self):
        """Test importing real Gemini provider."""
        client = ClaifClient(provider="gemini")
        assert client.provider == "gemini"
        assert hasattr(client._client, "chat")

    @pytest.mark.skip(reason="Requires claif_cod package to be installed")
    def test_real_codex_import(self):
        """Test importing real Codex provider."""
        client = ClaifClient(provider="codex")
        assert client.provider == "codex"
        assert hasattr(client._client, "chat")

    @pytest.mark.skip(reason="Requires claif_lms package to be installed")
    def test_real_lms_import(self):
        """Test importing real LMS provider."""
        client = ClaifClient(provider="lms")
        assert client.provider == "lms"
        assert hasattr(client._client, "chat")

    @pytest.mark.skip(reason="Requires provider packages and API keys")
    def test_real_provider_query(self):
        """Test querying a real provider."""
        # This test would require real API keys and provider packages
        client = ClaifClient()  # Auto-detect provider

        response = client.chat.completions.create(
            model="gpt-3.5-turbo",  # Or appropriate model for provider
            messages=[{"role": "user", "content": "Say 'test successful' and nothing else"}],
            max_tokens=10,
        )

        assert "test successful" in response.choices[0].message.content.lower()
