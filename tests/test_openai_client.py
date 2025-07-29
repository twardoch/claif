# this_file: claif/tests/test_openai_client.py
"""Tests for unified Claif client with OpenAI compatibility."""

import unittest
from unittest.mock import MagicMock, patch

import pytest
from openai.types.chat import ChatCompletion

from claif.client import ClaifClient


class TestClaifClient(unittest.TestCase):
    """Test cases for ClaifClient."""

    @patch.dict("os.environ", {}, clear=True)
    def test_init_default(self):
        """Test client initialization with defaults."""
        # Should default to LMS when no provider can be detected
        with patch("claif.client.ClaifClient._is_codex_available", return_value=False):
            client = ClaifClient()
            assert client.provider == "lms"

    @patch.dict("os.environ", {"ANTHROPIC_API_KEY": "test-key"})
    def test_auto_detect_claude(self):
        """Test auto-detection of Claude provider."""
        client = ClaifClient()
        assert client.provider == "claude"

    @patch.dict("os.environ", {"GEMINI_API_KEY": "test-key"})
    def test_auto_detect_gemini(self):
        """Test auto-detection of Gemini provider."""
        client = ClaifClient()
        assert client.provider == "gemini"

    @patch.dict("os.environ", {"OPENAI_API_KEY": "test-key", "OPENAI_BASE_URL": "http://localhost:1234/v1"})
    def test_auto_detect_lms(self):
        """Test auto-detection of LM Studio provider."""
        client = ClaifClient()
        assert client.provider == "lms"

    def test_explicit_provider(self):
        """Test explicit provider selection."""
        # Mock all provider imports
        with patch("claif_cla.client.ClaudeClient"):
            client = ClaifClient(provider="claude")
            assert client.provider == "claude"

    def test_invalid_provider(self):
        """Test error on invalid provider."""
        with pytest.raises(ValueError):
            ClaifClient(provider="invalid")

    def test_namespace_structure(self):
        """Test that the client has the correct namespace structure."""
        with patch("claif_lms.client.LMSClient"):
            client = ClaifClient(provider="lms")
            assert client.chat is not None
            assert client.chat.completions is not None
            assert hasattr(client.chat.completions, "create")

    def test_claude_convenience_constructor(self):
        """Test Claude convenience constructor."""
        with patch("claif_cla.client.ClaudeClient"):
            client = ClaifClient.claude(api_key="test-key")
            assert client.provider == "claude"

    def test_gemini_convenience_constructor(self):
        """Test Gemini convenience constructor."""
        with patch("claif_gem.client.GeminiClient"):
            client = ClaifClient.gemini(api_key="test-key")
            assert client.provider == "gemini"

    def test_codex_convenience_constructor(self):
        """Test Codex convenience constructor."""
        with patch("claif_cod.client.CodexClient"):
            client = ClaifClient.codex()
            assert client.provider == "codex"

    def test_lms_convenience_constructor(self):
        """Test LMS convenience constructor."""
        with patch("claif_lms.client.LMSClient"):
            client = ClaifClient.lms(api_key="test-key", base_url="http://localhost:1234/v1")
            assert client.provider == "lms"

    def test_create_method_delegation(self):
        """Test that create method delegates to provider."""
        # Mock LMSClient
        mock_lms_class = MagicMock()
        mock_lms_instance = MagicMock()
        mock_lms_class.return_value = mock_lms_instance

        # Mock the response
        mock_response = MagicMock(spec=ChatCompletion)
        mock_lms_instance.chat.completions.create.return_value = mock_response

        with patch("claif_lms.client.LMSClient", mock_lms_class):
            client = ClaifClient(provider="lms")

            # Call create
            response = client.chat.completions.create(
                model="gpt-3.5-turbo", messages=[{"role": "user", "content": "Hello"}]
            )

            # Verify delegation
            mock_lms_instance.chat.completions.create.assert_called_once()
            assert response == mock_response

    def test_backward_compatibility(self):
        """Test the backward compatibility create method."""
        # Mock LMSClient
        mock_lms_class = MagicMock()
        mock_lms_instance = MagicMock()
        mock_lms_class.return_value = mock_lms_instance

        with patch("claif_lms.client.LMSClient", mock_lms_class):
            client = ClaifClient(provider="lms")

            # Mock the nested create method
            mock_create = MagicMock()
            client.chat.completions.create = mock_create

            # Call backward compatibility method
            client.create(model="test", messages=[])

            # Verify it calls the new method
            mock_create.assert_called_once_with(model="test", messages=[])

    @patch("shutil.which")
    def test_is_codex_available(self, mock_which):
        """Test Codex availability check."""
        # Test when codex is available
        mock_which.return_value = "/usr/bin/codex"
        with patch("claif_lms.client.LMSClient"):
            client = ClaifClient(provider="lms")
            assert client._is_codex_available()

        # Test when codex is not available
        mock_which.return_value = None
        with patch("claif_lms.client.LMSClient"):
            client = ClaifClient(provider="lms")
            assert not client._is_codex_available()


if __name__ == "__main__":
    unittest.main()
