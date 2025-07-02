"""Tests for claif.server module."""

import asyncio
from unittest.mock import patch, MagicMock, AsyncMock

import pytest
from pydantic import BaseModel

from claif.server import (
    mcp,
    claif_query,
    claif_query_random,
    claif_query_all,
    claif_list_providers,
    claif_health_check,
    start_mcp_server,
    main,
    QueryRequest,
    QueryResponse,
    ProviderInfo
)
from claif.common.types import Message, MessageRole, Provider


class TestClaifQuery:
    """Test claif_query tool."""
    
    @patch("claif.server.query")
    async def test_query_basic(self, mock_query):
        """Test basic query operation."""
        # Mock response
        async def mock_query_gen(prompt, options):
            yield Message(role=MessageRole.ASSISTANT, content="Test response")
        
        mock_query.return_value = mock_query_gen("Test", MagicMock())
        
        # Create request
        request = QueryRequest(
            prompt="Test query",
            provider="claude",
            temperature=0.7,
            max_tokens=100
        )
        
        # Execute query
        response = await claif_query(request)
        
        assert isinstance(response, QueryResponse)
        assert len(response.messages) == 1
        assert response.messages[0]["role"] == "assistant"
        assert response.messages[0]["content"] == "Test response"
        assert response.provider == "claude"
    
    @patch("claif.server.query")
    async def test_query_invalid_provider(self, mock_query):
        """Test query with invalid provider."""
        request = QueryRequest(
            prompt="Test",
            provider="invalid_provider"
        )
        
        response = await claif_query(request)
        
        assert response.error is not None
        assert "Unknown provider" in response.error
        assert len(response.messages) == 0
    
    @patch("claif.server.query")
    async def test_query_error_handling(self, mock_query):
        """Test query error handling."""
        # Mock error
        async def mock_query_error(prompt, options):
            raise RuntimeError("Test error")
            yield  # Make it a generator
        
        mock_query.return_value = mock_query_error("Test", MagicMock())
        
        request = QueryRequest(prompt="Test")
        response = await claif_query(request)
        
        assert response.error is not None
        assert "Test error" in response.error
        assert len(response.messages) == 0


class TestClaifQueryRandom:
    """Test claif_query_random tool."""
    
    @patch("claif.server.query_random")
    async def test_query_random(self, mock_query_random):
        """Test random provider query."""
        # Mock response with provider tracking
        mock_options = MagicMock()
        mock_options.provider = Provider.GEMINI
        
        async def mock_random_gen(prompt, options):
            # Simulate provider selection
            options.provider = Provider.GEMINI
            yield Message(role=MessageRole.ASSISTANT, content="Random response")
        
        mock_query_random.return_value = mock_random_gen("Test", mock_options)
        
        request = QueryRequest(
            prompt="Test query",
            temperature=0.5
        )
        
        response = await claif_query_random(request)
        
        assert isinstance(response, QueryResponse)
        assert len(response.messages) == 1
        assert response.messages[0]["content"] == "Random response"
        assert response.provider == "gemini"
    
    @patch("claif.server.query_random")
    async def test_query_random_error(self, mock_query_random):
        """Test random query error handling."""
        async def mock_error_gen(prompt, options):
            raise Exception("Random error")
            yield
        
        mock_query_random.return_value = mock_error_gen("Test", MagicMock())
        
        request = QueryRequest(prompt="Test")
        response = await claif_query_random(request)
        
        assert response.error is not None
        assert "Random error" in response.error


class TestClaifQueryAll:
    """Test claif_query_all tool."""
    
    @patch("claif.server.query_all")
    async def test_query_all(self, mock_query_all):
        """Test querying all providers."""
        # Mock parallel responses
        async def mock_all_gen(prompt, options):
            yield {
                Provider.CLAUDE: [
                    Message(role=MessageRole.ASSISTANT, content="Claude response")
                ],
                Provider.GEMINI: [
                    Message(role=MessageRole.ASSISTANT, content="Gemini response")
                ],
                Provider.CODEX: []
            }
        
        mock_query_all.return_value = mock_all_gen("Test", MagicMock())
        
        request = QueryRequest(prompt="Test query")
        responses = await claif_query_all(request)
        
        assert isinstance(responses, dict)
        assert "claude" in responses
        assert "gemini" in responses
        assert "codex" in responses
        
        assert responses["claude"].messages[0]["content"] == "Claude response"
        assert responses["gemini"].messages[0]["content"] == "Gemini response"
        assert len(responses["codex"].messages) == 0
    
    @patch("claif.server.query_all")
    async def test_query_all_error(self, mock_query_all):
        """Test parallel query error handling."""
        async def mock_error_gen(prompt, options):
            raise Exception("Parallel error")
            yield
        
        mock_query_all.return_value = mock_error_gen("Test", MagicMock())
        
        request = QueryRequest(prompt="Test")
        responses = await claif_query_all(request)
        
        assert "error" in responses
        assert responses["error"].error is not None
        assert "Parallel error" in responses["error"].error


class TestProviderTools:
    """Test provider listing and health check tools."""
    
    async def test_list_providers(self):
        """Test listing all providers."""
        providers = await claif_list_providers()
        
        assert isinstance(providers, list)
        assert len(providers) == 3  # Claude, Gemini, Codex
        
        provider_names = [p.name for p in providers]
        assert "claude" in provider_names
        assert "gemini" in provider_names
        assert "codex" in provider_names
        
        # All should be enabled by default
        assert all(p.enabled for p in providers)
    
    @patch("claif.server.query")
    async def test_health_check_single(self, mock_query):
        """Test health check for single provider."""
        # Mock successful query
        async def mock_query_gen(prompt, options):
            yield Message(role=MessageRole.ASSISTANT, content="OK")
        
        mock_query.return_value = mock_query_gen("Hello", MagicMock())
        
        result = await claif_health_check(provider="claude")
        
        assert result == {"claude": True}
    
    @patch("claif.server.query")
    async def test_health_check_all(self, mock_query):
        """Test health check for all providers."""
        # Mock mixed results
        call_count = 0
        
        async def mock_query_gen(prompt, options):
            nonlocal call_count
            call_count += 1
            if call_count == 1:  # Claude succeeds
                yield Message(role=MessageRole.ASSISTANT, content="OK")
            elif call_count == 2:  # Gemini fails
                raise Exception("Connection error")
            else:  # Codex succeeds
                yield Message(role=MessageRole.ASSISTANT, content="OK")
        
        mock_query.side_effect = [
            mock_query_gen("Hello", MagicMock()),
            mock_query_gen("Hello", MagicMock()),
            mock_query_gen("Hello", MagicMock())
        ]
        
        result = await claif_health_check()
        
        assert isinstance(result, dict)
        assert len(result) == 3
        # Results depend on execution order, but should have mix of True/False


class TestServerStart:
    """Test server startup functionality."""
    
    @patch("claif.server.uvicorn.run")
    def test_start_mcp_server_default(self, mock_uvicorn_run):
        """Test starting server with defaults."""
        start_mcp_server()
        
        mock_uvicorn_run.assert_called_once_with(
            mcp,
            host="localhost",
            port=8000,
            reload=False,
            log_level="info"
        )
    
    @patch("claif.server.uvicorn.run")
    @patch("claif.server.logger")
    def test_start_mcp_server_custom(self, mock_logger, mock_uvicorn_run):
        """Test starting server with custom settings."""
        mock_logger.level = 30  # WARNING level
        mock_config = MagicMock(default_provider=Provider.GEMINI)
        
        start_mcp_server(
            host="0.0.0.0",
            port=9000,
            reload=True,
            config=mock_config
        )
        
        mock_uvicorn_run.assert_called_once_with(
            mcp,
            host="0.0.0.0",
            port=9000,
            reload=True,
            log_level="warning"
        )


class TestServerMain:
    """Test server main entry point."""
    
    @patch("claif.server.fire.Fire")
    def test_main_function(self, mock_fire):
        """Test main function."""
        main()
        
        mock_fire.assert_called_once_with(start_mcp_server)


class TestRequestResponseModels:
    """Test Pydantic models."""
    
    def test_query_request_model(self):
        """Test QueryRequest model."""
        request = QueryRequest(
            prompt="Test prompt",
            provider="claude",
            temperature=0.7
        )
        
        assert request.prompt == "Test prompt"
        assert request.provider == "claude"
        assert request.temperature == 0.7
        assert request.cache is True  # Default
    
    def test_query_response_model(self):
        """Test QueryResponse model."""
        response = QueryResponse(
            messages=[{"role": "assistant", "content": "Test"}],
            provider="gemini",
            model="gemini-pro"
        )
        
        assert len(response.messages) == 1
        assert response.provider == "gemini"
        assert response.model == "gemini-pro"
        assert response.error is None
    
    def test_provider_info_model(self):
        """Test ProviderInfo model."""
        info = ProviderInfo(
            name="claude",
            enabled=True,
            default_model="claude-3-opus"
        )
        
        assert info.name == "claude"
        assert info.enabled is True
        assert info.default_model == "claude-3-opus"