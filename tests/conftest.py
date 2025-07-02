"""Pytest configuration and shared fixtures for claif tests."""

import asyncio
import sys
from pathlib import Path
from typing import Any, AsyncIterator
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from claif.common.types import (
    Message, 
    MessageRole, 
    Provider, 
    ClaifOptions, 
    ClaifResponse,
    ResponseMetrics,
    TextBlock
)


class MockProvider:
    """Mock provider for testing."""
    
    def __init__(self):
        self.name = "mock"
        self.query_count = 0
        self.install_count = 0
        self.installed = True
        self.mock_response = "Mock response"
        self.should_error = False
    
    async def query(self, prompt: str, options: ClaifOptions) -> AsyncIterator[Message]:
        """Mock query implementation."""
        self.query_count += 1
        
        if self.should_error:
            raise RuntimeError("Mock provider error")
        
        # Yield mock messages
        yield Message(
            role=MessageRole.ASSISTANT,
            content=self.mock_response
        )
    
    def is_installed(self) -> bool:
        """Check if provider is installed."""
        return self.installed
    
    async def install(self) -> None:
        """Mock install implementation."""
        self.install_count += 1
        self.installed = True


@pytest.fixture
def mock_provider():
    """Create a mock provider instance."""
    return MockProvider()


@pytest.fixture
def mock_providers():
    """Create multiple mock provider instances."""
    providers = {}
    
    # Create mock1
    mock1 = MockProvider()
    mock1.name = "claude"
    providers[Provider.CLAUDE] = mock1
    
    # Create mock2
    mock2 = MockProvider()
    mock2.name = "gemini"
    mock2.mock_response = "Response from gemini"
    providers[Provider.GEMINI] = mock2
    
    # Create mock3
    mock3 = MockProvider()
    mock3.name = "codex"
    mock3.installed = False
    providers[Provider.CODEX] = mock3
    
    return providers


@pytest.fixture
def sample_options():
    """Create sample ClaifOptions."""
    return ClaifOptions(
        provider=Provider.CLAUDE,
        temperature=0.7,
        max_tokens=100,
        verbose=False
    )


@pytest.fixture
def sample_message():
    """Create a sample Message."""
    return Message(
        role=MessageRole.USER,
        content="Test query"
    )


@pytest.fixture
def sample_response():
    """Create a sample ClaifResponse."""
    return ClaifResponse(
        messages=[
            Message(role=MessageRole.ASSISTANT, content="Test response")
        ],
        metrics=ResponseMetrics(
            duration=0.5,
            tokens_used=50,
            provider=Provider.CLAUDE
        )
    )


@pytest.fixture
async def async_mock():
    """Create an async mock object."""
    return AsyncMock()


@pytest.fixture
def temp_config_dir(tmp_path):
    """Create a temporary config directory."""
    config_dir = tmp_path / "claif_config"
    config_dir.mkdir()
    return config_dir


@pytest.fixture
def mock_config_file(temp_config_dir):
    """Create a mock configuration file."""
    config_file = temp_config_dir / "config.json"
    config_file.write_text("""{
        "default_provider": "claude",
        "providers": {
            "claude": {
                "enabled": true,
                "api_key": "test-key"
            },
            "gemini": {
                "enabled": false
            }
        },
        "parallel_queries": true
    }""")
    return config_file


@pytest.fixture
def mock_env_vars(monkeypatch):
    """Mock environment variables."""
    env_vars = {
        "CLAIF_DEFAULT_PROVIDER": "claude",
        "CLAIF_API_KEY": "test-api-key",
        "CLAIF_LOG_LEVEL": "DEBUG"
    }
    for key, value in env_vars.items():
        monkeypatch.setenv(key, value)
    return env_vars


@pytest.fixture
def mock_subprocess():
    """Mock subprocess module."""
    with patch("subprocess.run") as mock_run:
        mock_run.return_value.returncode = 0
        mock_run.return_value.stdout = "Mock output"
        mock_run.return_value.stderr = ""
        yield mock_run


@pytest.fixture(autouse=True)
def reset_loguru():
    """Reset loguru configuration for each test."""
    from loguru import logger
    logger.remove()
    logger.add(sys.stderr, level="INFO")
    yield
    logger.remove()


@pytest.fixture
def event_loop():
    """Create an event loop for async tests."""
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


# Test data fixtures
@pytest.fixture
def test_messages():
    """Sample messages for testing."""
    return [
        Message(role=MessageRole.SYSTEM, content="You are a helpful assistant."),
        Message(role=MessageRole.USER, content="Hello, how are you?"),
        Message(role=MessageRole.ASSISTANT, content="I'm doing well, thank you!"),
        Message(role=MessageRole.USER, content="What's the weather like?")
    ]


@pytest.fixture
def error_scenarios():
    """Common error scenarios for testing."""
    return {
        "network_error": ConnectionError("Network unreachable"),
        "timeout_error": TimeoutError("Request timed out"),
        "auth_error": PermissionError("Invalid API key"),
        "rate_limit": RuntimeError("Rate limit exceeded"),
        "invalid_json": ValueError("Invalid JSON response")
    }


# Marker fixtures
@pytest.fixture
def slow_test(request):
    """Mark test as slow."""
    if request.config.getoption("--skip-slow", default=False):
        pytest.skip("Skipping slow test")


@pytest.fixture
def requires_network(request):
    """Mark test as requiring network."""
    if request.config.getoption("--offline", default=False):
        pytest.skip("Skipping test requiring network")


# CLI argument fixtures
def pytest_addoption(parser):
    """Add custom command line options."""
    parser.addoption(
        "--skip-slow",
        action="store_true",
        default=False,
        help="Skip slow tests"
    )
    parser.addoption(
        "--offline",
        action="store_true",
        default=False,
        help="Run tests in offline mode"
    )