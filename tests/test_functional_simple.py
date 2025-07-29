# this_file: claif/tests/test_functional_simple.py
"""Simple functional tests for the main claif package without provider dependencies."""

import os
from unittest.mock import MagicMock, patch

import pytest

from claif.client import ClaifClient


class TestClaifClientSimple:
    """Simple functional tests for the unified ClaifClient."""

    def test_provider_auto_detection_claude(self):
        """Test auto-detection of Claude provider based on env var."""
        with patch.dict(os.environ, {"ANTHROPIC_API_KEY": "test-key"}):
            # Mock the import
            mock_claude_client = MagicMock()
            with patch.dict(
                "sys.modules",
                {"claif_cla": MagicMock(), "claif_cla.client": MagicMock(ClaudeClient=mock_claude_client)},
            ):
                client = ClaifClient()
                assert client.provider == "claude"

    def test_provider_auto_detection_gemini(self):
        """Test auto-detection of Gemini provider based on env var."""
        with patch.dict(os.environ, {"GEMINI_API_KEY": "test-key"}, clear=True):
            # Mock the import
            mock_gemini_client = MagicMock()
            with patch.dict(
                "sys.modules",
                {"claif_gem": MagicMock(), "claif_gem.client": MagicMock(GeminiClient=mock_gemini_client)},
            ):
                client = ClaifClient()
                assert client.provider == "gemini"

    def test_provider_auto_detection_codex(self):
        """Test auto-detection of Codex provider based on CLI availability."""
        with patch.dict(os.environ, {}, clear=True):
            with patch("shutil.which", return_value="/usr/local/bin/codex"):
                # Mock the import
                mock_codex_client = MagicMock()
                with patch.dict(
                    "sys.modules",
                    {"claif_cod": MagicMock(), "claif_cod.client": MagicMock(CodexClient=mock_codex_client)},
                ):
                    client = ClaifClient()
                    assert client.provider == "codex"

    def test_provider_auto_detection_lms(self):
        """Test auto-detection of LMS provider as default."""
        with patch.dict(os.environ, {}, clear=True):
            with patch("shutil.which", return_value=None):
                # Mock the import
                mock_lms_client = MagicMock()
                with patch.dict(
                    "sys.modules", {"claif_lms": MagicMock(), "claif_lms.client": MagicMock(LMSClient=mock_lms_client)}
                ):
                    client = ClaifClient()
                    assert client.provider == "lms"

    def test_explicit_provider_selection(self):
        """Test explicit provider selection overrides auto-detection."""
        with patch.dict(os.environ, {"ANTHROPIC_API_KEY": "test-key"}):
            # Mock the import
            mock_gemini_client = MagicMock()
            with patch.dict(
                "sys.modules",
                {"claif_gem": MagicMock(), "claif_gem.client": MagicMock(GeminiClient=mock_gemini_client)},
            ):
                client = ClaifClient(provider="gemini")
                assert client.provider == "gemini"

    def test_unknown_provider_error(self):
        """Test error is raised for unknown provider."""
        with pytest.raises(ValueError) as exc_info:
            ClaifClient(provider="unknown")

        assert "Unknown provider: unknown" in str(exc_info.value)

    def test_chat_namespace_exists(self):
        """Test that chat namespace is created."""
        # Mock the import
        mock_claude_client = MagicMock()
        with patch.dict(
            "sys.modules", {"claif_cla": MagicMock(), "claif_cla.client": MagicMock(ClaudeClient=mock_claude_client)}
        ):
            client = ClaifClient(provider="claude")
            assert hasattr(client, "chat")
            assert hasattr(client.chat, "completions")
            assert hasattr(client.chat.completions, "create")

    def test_completions_create_delegates(self):
        """Test that completions.create delegates to the underlying client."""
        # Create a mock provider client
        mock_provider_client = MagicMock()
        mock_chat = MagicMock()
        mock_completions = MagicMock()
        mock_provider_client.chat = mock_chat
        mock_chat.completions = mock_completions

        # Mock the import
        mock_claude_class = MagicMock(return_value=mock_provider_client)
        with patch.dict(
            "sys.modules", {"claif_cla": MagicMock(), "claif_cla.client": MagicMock(ClaudeClient=mock_claude_class)}
        ):
            client = ClaifClient(provider="claude")

            # Call the method
            client.chat.completions.create(
                model="claude-3-5-sonnet", messages=[{"role": "user", "content": "Hello"}], temperature=0.7
            )

            # Verify delegation - the implementation passes all params
            mock_completions.create.assert_called_once()
            call_args = mock_completions.create.call_args
            assert call_args.kwargs["model"] == "claude-3-5-sonnet"
            assert call_args.kwargs["messages"] == [{"role": "user", "content": "Hello"}]
            assert call_args.kwargs["temperature"] == 0.7

    def test_kwargs_passed_to_provider(self):
        """Test that extra kwargs are passed to provider client."""
        # Mock the import
        mock_claude_class = MagicMock()
        with patch.dict(
            "sys.modules", {"claif_cla": MagicMock(), "claif_cla.client": MagicMock(ClaudeClient=mock_claude_class)}
        ):
            ClaifClient(provider="claude", api_key="test-key", timeout=300, custom_param="value")

            # Verify provider was initialized with kwargs
            mock_claude_class.assert_called_once_with(api_key="test-key", timeout=300, custom_param="value")
