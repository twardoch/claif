"""Tests for claif.common.types module."""

import pytest
from dataclasses import dataclass

from claif.common.types import (
    Message,
    MessageRole,
    Provider,
    ClaifOptions,
    ClaifResponse,
    ResponseMetrics,
    TextBlock,
    ToolUseBlock,
    ToolResultBlock
)


class TestMessage:
    """Test Message model."""
    
    def test_create_message_with_string(self):
        """Test creating a message with string content."""
        msg = Message(role=MessageRole.USER, content="Hello")
        assert msg.role == MessageRole.USER
        # Content should be converted to TextBlock list
        assert isinstance(msg.content, list)
        assert len(msg.content) == 1
        assert isinstance(msg.content[0], TextBlock)
        assert msg.content[0].text == "Hello"
    
    def test_create_message_with_blocks(self):
        """Test creating a message with content blocks."""
        blocks = [
            TextBlock(text="Hello"),
            TextBlock(text="World")
        ]
        msg = Message(role=MessageRole.ASSISTANT, content=blocks)
        assert msg.role == MessageRole.ASSISTANT
        assert len(msg.content) == 2
        assert msg.content[0].text == "Hello"
        assert msg.content[1].text == "World"
    
    def test_message_roles(self):
        """Test different message roles."""
        roles = [MessageRole.USER, MessageRole.ASSISTANT, MessageRole.SYSTEM, MessageRole.RESULT]
        for role in roles:
            msg = Message(role=role, content="Test")
            assert msg.role == role


class TestContentBlocks:
    """Test content block types."""
    
    def test_text_block(self):
        """Test TextBlock creation."""
        block = TextBlock(text="Hello world")
        assert block.type == "text"
        assert block.text == "Hello world"
    
    def test_text_block_defaults(self):
        """Test TextBlock with defaults."""
        block = TextBlock()
        assert block.type == "text"
        assert block.text == ""
    
    def test_tool_use_block(self):
        """Test ToolUseBlock creation."""
        block = ToolUseBlock(
            id="tool-123",
            name="search",
            input={"query": "test"}
        )
        assert block.type == "tool_use"
        assert block.id == "tool-123"
        assert block.name == "search"
        assert block.input == {"query": "test"}
    
    def test_tool_use_block_defaults(self):
        """Test ToolUseBlock with defaults."""
        block = ToolUseBlock()
        assert block.type == "tool_use"
        assert block.id == ""
        assert block.name == ""
        assert block.input == {}
    
    def test_tool_result_block(self):
        """Test ToolResultBlock creation."""
        block = ToolResultBlock(
            tool_use_id="tool-123",
            content=[TextBlock(text="Result")],
            is_error=False
        )
        assert block.type == "tool_result"
        assert block.tool_use_id == "tool-123"
        assert len(block.content) == 1
        assert block.content[0].text == "Result"
        assert block.is_error is False
    
    def test_tool_result_block_defaults(self):
        """Test ToolResultBlock with defaults."""
        block = ToolResultBlock()
        assert block.type == "tool_result"
        assert block.tool_use_id == ""
        assert block.content == []
        assert block.is_error is False


class TestClaifOptions:
    """Test ClaifOptions model."""
    
    def test_default_options(self):
        """Test creating options with defaults."""
        options = ClaifOptions()
        assert options.provider is None
        assert options.model is None
        assert options.temperature is None
        assert options.max_tokens is None
        assert options.system_prompt is None
        assert options.timeout is None
        assert options.verbose is False
        assert options.output_format == "text"
        assert options.config_file is None
        assert options.session_id is None
        assert options.cache is False
        assert options.retry_count == 3
        assert options.retry_delay == 1.0
    
    def test_options_with_values(self):
        """Test options with custom values."""
        options = ClaifOptions(
            provider=Provider.CLAUDE,
            model="claude-3-opus",
            temperature=0.5,
            max_tokens=1000,
            system_prompt="You are helpful",
            timeout=30,
            verbose=True,
            output_format="json",
            session_id="session-123",
            cache=True,
            retry_count=5,
            retry_delay=2.0
        )
        assert options.provider == Provider.CLAUDE
        assert options.model == "claude-3-opus"
        assert options.temperature == 0.5
        assert options.max_tokens == 1000
        assert options.system_prompt == "You are helpful"
        assert options.timeout == 30
        assert options.verbose is True
        assert options.output_format == "json"
        assert options.session_id == "session-123"
        assert options.cache is True
        assert options.retry_count == 5
        assert options.retry_delay == 2.0


class TestProvider:
    """Test Provider enum."""
    
    def test_provider_values(self):
        """Test provider enum values."""
        assert Provider.CLAUDE.value == "claude"
        assert Provider.GEMINI.value == "gemini"
        assert Provider.CODEX.value == "codex"
    
    def test_provider_comparison(self):
        """Test provider comparisons."""
        assert Provider.CLAUDE == Provider.CLAUDE
        assert Provider.CLAUDE != Provider.GEMINI
        assert Provider.CLAUDE.value == "claude"


class TestResponseMetrics:
    """Test ResponseMetrics model."""
    
    def test_default_metrics(self):
        """Test metrics with defaults."""
        metrics = ResponseMetrics()
        assert metrics.duration == 0.0
        assert metrics.tokens_used == 0
        assert metrics.cost == 0.0
        assert metrics.provider is None
        assert metrics.model is None
        assert metrics.cached is False
    
    def test_metrics_with_values(self):
        """Test metrics with custom values."""
        metrics = ResponseMetrics(
            duration=1.5,
            tokens_used=150,
            cost=0.0075,
            provider=Provider.GEMINI,
            model="gemini-pro",
            cached=True
        )
        assert metrics.duration == 1.5
        assert metrics.tokens_used == 150
        assert metrics.cost == 0.0075
        assert metrics.provider == Provider.GEMINI
        assert metrics.model == "gemini-pro"
        assert metrics.cached is True


class TestClaifResponse:
    """Test ClaifResponse model."""
    
    def test_response_basic(self):
        """Test basic response creation."""
        messages = [
            Message(role=MessageRole.ASSISTANT, content="Hello!")
        ]
        response = ClaifResponse(messages=messages)
        assert len(response.messages) == 1
        assert response.messages[0].content[0].text == "Hello!"
        assert response.metrics is None
        assert response.session_id is None
        assert response.error is None
    
    def test_response_with_metrics(self):
        """Test response with metrics."""
        messages = [
            Message(role=MessageRole.ASSISTANT, content="Response")
        ]
        metrics = ResponseMetrics(
            duration=0.5,
            tokens_used=50,
            provider=Provider.CLAUDE
        )
        response = ClaifResponse(
            messages=messages,
            metrics=metrics,
            session_id="session-123"
        )
        assert response.metrics.duration == 0.5
        assert response.metrics.tokens_used == 50
        assert response.session_id == "session-123"
    
    def test_response_with_error(self):
        """Test response with error."""
        response = ClaifResponse(
            messages=[],
            error="API rate limit exceeded"
        )
        assert len(response.messages) == 0
        assert response.error == "API rate limit exceeded"
    
    def test_empty_response(self):
        """Test empty response."""
        response = ClaifResponse(messages=[])
        assert len(response.messages) == 0
        assert response.error is None