"""Tests for claif.client module."""

import asyncio
from unittest.mock import MagicMock, AsyncMock, patch, call

import pytest

from claif.client import ClaifClient, _is_cli_missing_error, _get_provider_install_function
from claif.common.types import Message, MessageRole, Provider, ClaifOptions
from claif.common.errors import ProviderError


class TestClientHelpers:
    """Test client helper functions."""
    
    def test_is_cli_missing_error_true(self):
        """Test detecting CLI missing errors."""
        errors = [
            Exception("command not found"),
            FileNotFoundError("claude not found"),
            RuntimeError("No such file or directory"),
            PermissionError("permission denied"),
            Exception("is not recognized as an internal or external command"),
            Exception("executable not found")
        ]
        
        for error in errors:
            assert _is_cli_missing_error(error) is True
    
    def test_is_cli_missing_error_false(self):
        """Test non-CLI missing errors."""
        errors = [
            Exception("API error"),
            ValueError("Invalid input"),
            RuntimeError("Connection timeout"),
            Exception("Rate limit exceeded")
        ]
        
        for error in errors:
            assert _is_cli_missing_error(error) is False
    
    def test_get_provider_install_function_claude(self):
        """Test getting Claude install function."""
        with patch("claif.client.install_claude") as mock_install:
            func = _get_provider_install_function(Provider.CLAUDE)
            assert func is mock_install
    
    def test_get_provider_install_function_gemini(self):
        """Test getting Gemini install function."""
        with patch("claif.client.install_gemini") as mock_install:
            func = _get_provider_install_function(Provider.GEMINI)
            assert func is mock_install
    
    def test_get_provider_install_function_codex(self):
        """Test getting Codex install function."""
        with patch("claif.client.install_codex") as mock_install:
            func = _get_provider_install_function(Provider.CODEX)
            assert func is mock_install
    
    def test_get_provider_install_function_none(self):
        """Test getting install function for invalid provider."""
        # Create a mock provider that's not in the list
        result = _get_provider_install_function(None)
        assert result is None


class TestClaifClient:
    """Test ClaifClient class."""
    
    def test_client_init(self):
        """Test client initialization."""
        client = ClaifClient()
        
        assert Provider.CLAUDE in client.providers
        assert Provider.GEMINI in client.providers
        assert Provider.CODEX in client.providers
        assert len(client.providers) == 3
    
    @patch("claif.client.ClaudeProvider")
    @patch("claif.client.GeminiProvider")
    @patch("claif.client.CodexProvider")
    def test_client_init_with_providers(self, mock_codex, mock_gemini, mock_claude):
        """Test client creates provider instances."""
        client = ClaifClient()
        
        mock_claude.assert_called_once()
        mock_gemini.assert_called_once()
        mock_codex.assert_called_once()


class TestClaifClientQuery:
    """Test ClaifClient query functionality."""
    
    async def test_query_default_provider(self):
        """Test query with default provider."""
        client = ClaifClient()
        
        # Mock the Claude provider
        mock_provider = AsyncMock()
        async def mock_query(prompt, options):
            yield Message(role=MessageRole.ASSISTANT, content="Claude response")
        mock_provider.query = mock_query
        client.providers[Provider.CLAUDE] = mock_provider
        
        # Query without specifying provider (should use Claude)
        messages = []
        async for msg in client.query("Hello"):
            messages.append(msg)
        
        assert len(messages) == 1
        assert messages[0].content[0].text == "Claude response"
    
    async def test_query_specific_provider(self):
        """Test query with specific provider."""
        client = ClaifClient()
        
        # Mock the Gemini provider
        mock_provider = AsyncMock()
        async def mock_query(prompt, options):
            yield Message(role=MessageRole.ASSISTANT, content="Gemini response")
        mock_provider.query = mock_query
        client.providers[Provider.GEMINI] = mock_provider
        
        # Query with Gemini
        options = ClaifOptions(provider=Provider.GEMINI)
        messages = []
        async for msg in client.query("Hello", options):
            messages.append(msg)
        
        assert len(messages) == 1
        assert messages[0].content[0].text == "Gemini response"
    
    async def test_query_unknown_provider(self):
        """Test query with unknown provider."""
        client = ClaifClient()
        
        # Remove a provider to simulate unknown
        del client.providers[Provider.CODEX]
        
        options = ClaifOptions(provider=Provider.CODEX)
        
        with pytest.raises(ProviderError) as exc_info:
            async for _ in client.query("Hello", options):
                pass
        
        assert "Unknown provider" in str(exc_info.value)
        assert "codex" in str(exc_info.value)
    
    async def test_query_with_options(self):
        """Test query passes options to provider."""
        client = ClaifClient()
        
        # Mock provider to capture options
        mock_provider = AsyncMock()
        captured_options = None
        
        async def mock_query(prompt, options):
            nonlocal captured_options
            captured_options = options
            yield Message(role=MessageRole.ASSISTANT, content="Response")
        
        mock_provider.query = mock_query
        client.providers[Provider.CLAUDE] = mock_provider
        
        # Query with custom options
        options = ClaifOptions(
            provider=Provider.CLAUDE,
            temperature=0.5,
            max_tokens=1000,
            verbose=True
        )
        
        async for _ in client.query("Test", options):
            pass
        
        assert captured_options.temperature == 0.5
        assert captured_options.max_tokens == 1000
        assert captured_options.verbose is True


class TestAutoInstall:
    """Test auto-install functionality."""
    
    @patch("claif.client._get_provider_install_function")
    async def test_auto_install_on_missing_cli(self, mock_get_install):
        """Test auto-install triggers on missing CLI."""
        client = ClaifClient()
        
        # Mock provider that raises CLI missing error
        mock_provider = AsyncMock()
        async def mock_query(prompt, options):
            raise FileNotFoundError("claude not found")
        mock_provider.query = mock_query
        client.providers[Provider.CLAUDE] = mock_provider
        
        # Mock install function
        mock_install = MagicMock(return_value={"installed": True})
        mock_get_install.return_value = mock_install
        
        # Mock recreated provider
        mock_new_provider = AsyncMock()
        async def mock_new_query(prompt, options):
            yield Message(role=MessageRole.ASSISTANT, content="Success after install")
        mock_new_provider.query = mock_new_query
        
        with patch("claif.client.ClaudeProvider", return_value=mock_new_provider):
            messages = []
            async for msg in client.query("Hello"):
                messages.append(msg)
        
        # Should have called install
        mock_install.assert_called_once()
        
        # Should get response from new provider
        assert len(messages) == 1
        assert messages[0].content[0].text == "Success after install"
    
    @patch("claif.client._get_provider_install_function")
    async def test_auto_install_failure(self, mock_get_install):
        """Test handling failed auto-install."""
        client = ClaifClient()
        
        # Mock provider that raises CLI missing error
        mock_provider = AsyncMock()
        async def mock_query(prompt, options):
            raise FileNotFoundError("gemini not found")
        mock_provider.query = mock_query
        client.providers[Provider.GEMINI] = mock_provider
        
        # Mock failed install
        mock_install = MagicMock(return_value={"installed": False, "error": "Install failed"})
        mock_get_install.return_value = mock_install
        
        # Should raise the original error
        with pytest.raises(FileNotFoundError) as exc_info:
            async for _ in client.query("Hello", ClaifOptions(provider=Provider.GEMINI)):
                pass
        
        assert "gemini not found" in str(exc_info.value)
    
    async def test_no_auto_install_for_other_errors(self):
        """Test auto-install doesn't trigger for non-CLI errors."""
        client = ClaifClient()
        
        # Mock provider that raises non-CLI error
        mock_provider = AsyncMock()
        async def mock_query(prompt, options):
            raise RuntimeError("API error")
        mock_provider.query = mock_query
        client.providers[Provider.CODEX] = mock_provider
        
        # Should raise the error without trying to install
        with pytest.raises(RuntimeError) as exc_info:
            async for _ in client.query("Hello", ClaifOptions(provider=Provider.CODEX)):
                pass
        
        assert "API error" in str(exc_info.value)


class TestProviderRecreation:
    """Test provider recreation after install."""
    
    @patch("claif.client._get_provider_install_function")
    @patch("claif.client.ClaudeProvider")
    async def test_recreate_claude_provider(self, mock_claude_class, mock_get_install):
        """Test Claude provider recreation."""
        client = ClaifClient()
        
        # Initial provider
        initial_provider = AsyncMock()
        async def initial_query(prompt, options):
            raise FileNotFoundError("claude not found")
        initial_provider.query = initial_query
        client.providers[Provider.CLAUDE] = initial_provider
        
        # Mock successful install
        mock_install = MagicMock(return_value={"installed": True})
        mock_get_install.return_value = mock_install
        
        # New provider after install
        new_provider = AsyncMock()
        async def new_query(prompt, options):
            yield Message(role=MessageRole.ASSISTANT, content="New Claude")
        new_provider.query = new_query
        mock_claude_class.return_value = new_provider
        
        messages = []
        async for msg in client.query("Hello"):
            messages.append(msg)
        
        # Should have created new provider instance
        assert mock_claude_class.call_count >= 2  # Once in init, once after install
        assert client.providers[Provider.CLAUDE] == new_provider
    
    @patch("claif.client._get_provider_install_function")
    @patch("claif.client.GeminiProvider")
    async def test_recreate_gemini_provider(self, mock_gemini_class, mock_get_install):
        """Test Gemini provider recreation."""
        client = ClaifClient()
        
        # Initial provider
        initial_provider = AsyncMock()
        async def initial_query(prompt, options):
            raise FileNotFoundError("gemini not found")
        initial_provider.query = initial_query
        client.providers[Provider.GEMINI] = initial_provider
        
        # Mock successful install
        mock_install = MagicMock(return_value={"installed": True})
        mock_get_install.return_value = mock_install
        
        # New provider after install
        new_provider = AsyncMock()
        async def new_query(prompt, options):
            yield Message(role=MessageRole.ASSISTANT, content="New Gemini")
        new_provider.query = new_query
        mock_gemini_class.return_value = new_provider
        
        messages = []
        async for msg in client.query("Hello", ClaifOptions(provider=Provider.GEMINI)):
            messages.append(msg)
        
        assert client.providers[Provider.GEMINI] == new_provider


class TestClientEdgeCases:
    """Test edge cases and error scenarios."""
    
    async def test_query_empty_prompt(self):
        """Test query with empty prompt."""
        client = ClaifClient()
        
        mock_provider = AsyncMock()
        async def mock_query(prompt, options):
            assert prompt == ""
            yield Message(role=MessageRole.ASSISTANT, content="Empty response")
        mock_provider.query = mock_query
        client.providers[Provider.CLAUDE] = mock_provider
        
        messages = []
        async for msg in client.query(""):
            messages.append(msg)
        
        assert len(messages) == 1
    
    async def test_query_none_options(self):
        """Test query with None options creates default."""
        client = ClaifClient()
        
        mock_provider = AsyncMock()
        captured_options = None
        
        async def mock_query(prompt, options):
            nonlocal captured_options
            captured_options = options
            yield Message(role=MessageRole.ASSISTANT, content="Response")
        
        mock_provider.query = mock_query
        client.providers[Provider.CLAUDE] = mock_provider
        
        async for _ in client.query("Test", None):
            pass
        
        assert captured_options is not None
        assert isinstance(captured_options, ClaifOptions)
        assert captured_options.provider is None  # Should use default
    
    async def test_multiple_messages_from_provider(self):
        """Test handling multiple messages from provider."""
        client = ClaifClient()
        
        mock_provider = AsyncMock()
        async def mock_query(prompt, options):
            yield Message(role=MessageRole.ASSISTANT, content="First")
            yield Message(role=MessageRole.ASSISTANT, content="Second")
            yield Message(role=MessageRole.ASSISTANT, content="Third")
        
        mock_provider.query = mock_query
        client.providers[Provider.CLAUDE] = mock_provider
        
        messages = []
        async for msg in client.query("Test"):
            messages.append(msg)
        
        assert len(messages) == 3
        assert messages[0].content[0].text == "First"
        assert messages[1].content[0].text == "Second"
        assert messages[2].content[0].text == "Third"