"""Tests for claif provider implementations."""

from unittest.mock import patch, MagicMock, AsyncMock

import pytest

from claif.providers import ClaudeProvider, GeminiProvider, CodexProvider
from claif.common.types import Message, MessageRole, Provider, ClaifOptions
from claif.common.errors import ProviderError
from claif.common.install import InstallError


class TestClaudeProvider:
    """Test Claude provider implementation."""
    
    def test_provider_init(self):
        """Test Claude provider initialization."""
        provider = ClaudeProvider()
        assert provider is not None
    
    @patch("subprocess.run")
    async def test_query_mock(self, mock_run):
        """Test Claude provider query with mocked subprocess."""
        # Mock successful claude command execution
        mock_run.return_value = MagicMock(
            returncode=0,
            stdout='{"type": "message", "content": [{"type": "text", "text": "Hello from Claude"}]}'
        )
        
        provider = ClaudeProvider()
        options = ClaifOptions(provider=Provider.CLAUDE)
        
        messages = []
        async for msg in provider.query("Hello", options):
            messages.append(msg)
        
        assert len(messages) > 0
        assert isinstance(messages[0], Message)
    
    @patch("subprocess.run")
    async def test_query_error(self, mock_run):
        """Test Claude provider query error handling."""
        # Mock failed claude command
        mock_run.side_effect = FileNotFoundError("claude not found")
        
        provider = ClaudeProvider()
        options = ClaifOptions(provider=Provider.CLAUDE)
        
        with pytest.raises(FileNotFoundError):
            async for _ in provider.query("Hello", options):
                pass


class TestGeminiProvider:
    """Test Gemini provider implementation."""
    
    def test_provider_init(self):
        """Test Gemini provider initialization."""
        provider = GeminiProvider()
        assert provider is not None
    
    @patch("subprocess.run")
    async def test_query_mock(self, mock_run):
        """Test Gemini provider query with mocked subprocess."""
        # Mock successful gemini command execution
        mock_run.return_value = MagicMock(
            returncode=0,
            stdout="Hello from Gemini"
        )
        
        provider = GeminiProvider()
        options = ClaifOptions(provider=Provider.GEMINI)
        
        messages = []
        async for msg in provider.query("Hello", options):
            messages.append(msg)
        
        assert len(messages) > 0
        assert isinstance(messages[0], Message)
    
    @patch("subprocess.run")
    async def test_query_with_options(self, mock_run):
        """Test Gemini provider with custom options."""
        mock_run.return_value = MagicMock(
            returncode=0,
            stdout="Response with options"
        )
        
        provider = GeminiProvider()
        options = ClaifOptions(
            provider=Provider.GEMINI,
            model="gemini-pro",
            temperature=0.5,
            max_tokens=1000
        )
        
        messages = []
        async for msg in provider.query("Test", options):
            messages.append(msg)
        
        # Check that subprocess was called with appropriate args
        mock_run.assert_called_once()
        call_args = mock_run.call_args[0][0]
        assert "gemini" in call_args[0]


class TestCodexProvider:
    """Test Codex provider implementation."""
    
    def test_provider_init(self):
        """Test Codex provider initialization."""
        provider = CodexProvider()
        assert provider is not None
    
    @patch("subprocess.run")
    async def test_query_mock(self, mock_run):
        """Test Codex provider query with mocked subprocess."""
        # Mock successful codex command execution
        mock_run.return_value = MagicMock(
            returncode=0,
            stdout="Hello from Codex"
        )
        
        provider = CodexProvider()
        options = ClaifOptions(provider=Provider.CODEX)
        
        messages = []
        async for msg in provider.query("Hello", options):
            messages.append(msg)
        
        assert len(messages) > 0
        assert isinstance(messages[0], Message)
    
    @patch("subprocess.run")
    async def test_query_timeout(self, mock_run):
        """Test Codex provider timeout handling."""
        # Mock timeout
        mock_run.side_effect = TimeoutError("Command timed out")
        
        provider = CodexProvider()
        options = ClaifOptions(
            provider=Provider.CODEX,
            timeout=5
        )
        
        with pytest.raises(TimeoutError):
            async for _ in provider.query("Test", options):
                pass


class TestProviderComparison:
    """Test comparing different providers."""
    
    def test_all_providers_exist(self):
        """Test that all expected providers can be instantiated."""
        providers = [
            ClaudeProvider(),
            GeminiProvider(),
            CodexProvider()
        ]
        
        assert len(providers) == 3
        assert all(p is not None for p in providers)
    
    @patch("subprocess.run")
    async def test_provider_responses_format(self, mock_run):
        """Test that all providers return messages in the same format."""
        # Mock successful responses for each
        mock_run.return_value = MagicMock(
            returncode=0,
            stdout="Test response"
        )
        
        providers = [
            (ClaudeProvider(), Provider.CLAUDE),
            (GeminiProvider(), Provider.GEMINI),
            (CodexProvider(), Provider.CODEX)
        ]
        
        for provider, provider_type in providers:
            options = ClaifOptions(provider=provider_type)
            
            messages = []
            async for msg in provider.query("Test", options):
                messages.append(msg)
            
            # All should return at least one message
            assert len(messages) > 0
            # All messages should be Message instances
            assert all(isinstance(msg, Message) for msg in messages)
            # All messages should have assistant role
            assert all(msg.role == MessageRole.ASSISTANT for msg in messages)