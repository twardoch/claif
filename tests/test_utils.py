"""Tests for claif.common.utils module."""

import json
import os
import platform
import time
from pathlib import Path
from unittest.mock import MagicMock, patch, call

import pytest
from rich.progress import Progress

from claif.common.utils import (
    format_response,
    message_to_dict,
    block_to_dict,
    format_metrics,
    ensure_directory,
    get_claif_data_dir,
    get_claif_bin_path,
    get_install_location,
    inject_claif_bin_to_path,
    open_commands_in_terminals,
    prompt_tool_configuration,
    timestamp,
    truncate_text,
    parse_content_blocks,
    create_progress_bar,
    APP_NAME
)
from claif.common.types import Message, MessageRole, TextBlock, ResponseMetrics, Provider


class TestFormatResponse:
    """Test format_response function."""

    def test_format_response_text(self):
        """Test formatting response as text."""
        msg = Message(role=MessageRole.ASSISTANT, content="Hello world")
        result = format_response(msg, format="text")
        assert result == "Hello world"

    def test_format_response_json(self):
        """Test formatting response as JSON."""
        msg = Message(role=MessageRole.USER, content="Test message")
        result = format_response(msg, format="json")
        data = json.loads(result)
        assert data["role"] == "user"
        assert "Test message" in str(data["content"])

    def test_format_response_with_blocks(self):
        """Test formatting response with content blocks."""
        msg = Message(
            role=MessageRole.ASSISTANT,
            content=[
                TextBlock(text="First line"),
                TextBlock(text="Second line")
            ]
        )
        result = format_response(msg, format="text")
        assert "First line" in result
        assert "Second line" in result

    @patch("claif.common.utils.Console")
    def test_format_response_markdown(self, mock_console_class):
        """Test formatting response as markdown."""
        mock_console = MagicMock()
        mock_capture = MagicMock()
        mock_capture.get.return_value = "Rendered markdown"
        mock_console.capture.return_value.__enter__.return_value = mock_capture
        mock_console_class.return_value = mock_console

        msg = Message(role=MessageRole.ASSISTANT, content="# Heading\nText")
        result = format_response(msg, format="markdown")

        assert result == "Rendered markdown"


class TestMessageToDict:
    """Test message_to_dict function."""

    def test_message_to_dict_string_content(self):
        """Test converting message with string content."""
        msg = Message(role=MessageRole.USER, content="Hello")
        result = message_to_dict(msg)

        assert result["role"] == "user"
        assert isinstance(result["content"], list)

    def test_message_to_dict_block_content(self):
        """Test converting message with block content."""
        msg = Message(
            role=MessageRole.ASSISTANT,
            content=[TextBlock(text="Response")]
        )
        result = message_to_dict(msg)

        assert result["role"] == "assistant"
        assert len(result["content"]) == 1
        assert result["content"][0]["type"] == "text"
        assert result["content"][0]["text"] == "Response"


class TestBlockToDict:
    """Test block_to_dict function."""
    
    def test_block_to_dict_text_block(self):
        """Test converting TextBlock to dict."""
        block = TextBlock(text="Test content")
        result = block_to_dict(block)
        
        assert result["type"] == "text"
        assert result["text"] == "Test content"
    
    def test_block_to_dict_unknown(self):
        """Test converting unknown block type."""
        block = MagicMock()
        block.__dict__ = {"type": "custom", "data": "test"}
        result = block_to_dict(block)
        
        assert result == {"type": "custom", "data": "test"}


class TestFormatMetrics:
    """Test format_metrics function."""

    def test_format_metrics_basic(self):
        """Test formatting basic metrics."""
        metrics = ResponseMetrics(
            duration=1.5,
            tokens_used=100,
            cost=0.005
        )
        result = format_metrics(metrics)

        assert "1.50s" in result
        assert "100" in result
        assert "0.0050" in result

    def test_format_metrics_with_provider(self):
        """Test formatting metrics with provider info."""
        metrics = ResponseMetrics(
            duration=0.5,
            tokens_used=50,
            provider=Provider.CLAUDE,
            model="claude-3-opus",
            cached=True
        )
        result = format_metrics(metrics)

        assert "claude" in result
        assert "claude-3-opus" in result
        assert "Yes" in result  # Cached


class TestDirectoryFunctions:
    """Test directory utility functions."""

    def test_ensure_directory(self, tmp_path):
        """Test ensuring directory exists."""
        new_dir = tmp_path / "new" / "nested" / "dir"

        ensure_directory(new_dir)

        assert new_dir.exists()
        assert new_dir.is_dir()

    def test_ensure_directory_existing(self, tmp_path):
        """Test ensuring existing directory."""
        existing = tmp_path / "existing"
        existing.mkdir()

        # Should not raise error
        ensure_directory(existing)

        assert existing.exists()
    
    @patch("platformdirs.user_data_dir")
    def test_get_claif_data_dir(self, mock_data_dir):
        """Test getting claif data directory."""
        mock_data_dir.return_value = "/home/user/.local/share/claif"
        
        result = get_claif_data_dir()
        
        assert result == Path("/home/user/.local/share/claif")
        mock_data_dir.assert_called_once_with(APP_NAME, "claif")
    
    @patch("claif.common.utils.get_claif_data_dir")
    def test_get_claif_bin_path(self, mock_data_dir):
        """Test getting claif bin path."""
        mock_data_dir.return_value = Path("/home/user/.local/share/claif")
        
        result = get_claif_bin_path()
        
        assert result == Path("/home/user/.local/share/claif/bin")


class TestInstallLocation:
    """Test install location functions."""
    
    @patch("os.name", "nt")
    @patch.dict(os.environ, {"LOCALAPPDATA": "C:\\Users\\Test\\AppData\\Local"})
    def test_get_install_location_windows(self):
        """Test getting install location on Windows."""
        result = get_install_location()
        assert result == Path("C:\\Users\\Test\\AppData\\Local\\claif\\bin")
    
    @patch("os.name", "posix")
    @patch("pathlib.Path.home")
    def test_get_install_location_unix(self, mock_home):
        """Test getting install location on Unix."""
        mock_home.return_value = Path("/home/user")
        
        result = get_install_location()
        assert result == Path("/home/user/.local/bin/claif")
    
    @patch("claif.common.utils.get_install_location")
    def test_inject_claif_bin_to_path(self, mock_install_loc):
        """Test injecting claif bin to PATH."""
        mock_install_loc.return_value = Path("/home/user/.local/bin/claif")
        
        with patch.dict(os.environ, {"PATH": "/usr/bin:/bin"}):
            env = inject_claif_bin_to_path()
            
            assert "/home/user/.local/bin/claif" in env["PATH"]
            assert env["PATH"].startswith("/home/user/.local/bin/claif")


class TestTextUtilities:
    """Test text utility functions."""
    
    def test_timestamp(self):
        """Test timestamp generation."""
        with patch("time.strftime", return_value="20231225_120000"):
            result = timestamp()
            assert result == "20231225_120000"
    
    def test_truncate_text_short(self):
        """Test truncating short text."""
        text = "Short text"
        result = truncate_text(text, max_length=20)
        assert result == "Short text"
    
    def test_truncate_text_long(self):
        """Test truncating long text."""
        text = "This is a very long text that needs to be truncated"
        result = truncate_text(text, max_length=20)
        assert result == "This is a very lo..."
        assert len(result) == 20
    
    def test_truncate_text_custom_suffix(self):
        """Test truncating with custom suffix."""
        text = "Long text here"
        result = truncate_text(text, max_length=10, suffix="…")
        assert result == "Long text…"


class TestParseContentBlocks:
    """Test parse_content_blocks function."""
    
    def test_parse_string_content(self):
        """Test parsing string content."""
        blocks = parse_content_blocks("Hello world")
        
        assert len(blocks) == 1
        assert isinstance(blocks[0], TextBlock)
        assert blocks[0].text == "Hello world"
    
    def test_parse_list_content(self):
        """Test parsing list content."""
        content = [
            TextBlock(text="First"),
            {"type": "text", "text": "Second"},
            "Third"
        ]
        blocks = parse_content_blocks(content)
        
        assert len(blocks) == 3
        assert all(isinstance(b, TextBlock) for b in blocks)
        assert blocks[0].text == "First"
        assert blocks[1].text == "Second"
        assert blocks[2].text == "Third"
    
    def test_parse_other_content(self):
        """Test parsing other content types."""
        blocks = parse_content_blocks(123)
        
        assert len(blocks) == 1
        assert blocks[0].text == "123"


class TestProgressBar:
    """Test progress bar creation."""
    
    def test_create_progress_bar(self):
        """Test creating progress bar."""
        progress = create_progress_bar("Testing...")
        
        assert isinstance(progress, Progress)
        # Progress has columns
        assert len(progress.columns) > 0


class TestTerminalCommands:
    """Test terminal command functions."""
    
    @patch("platform.system", return_value="Darwin")
    @patch("subprocess.Popen")
    def test_open_commands_darwin(self, mock_popen, mock_system):
        """Test opening commands on macOS."""
        commands = ["echo test1", "echo test2"]
        
        open_commands_in_terminals(commands)
        
        assert mock_popen.call_count == 2
        # Check osascript was called
        calls = mock_popen.call_args_list
        for call in calls:
            assert "osascript" in call[0][0]
    
    @patch("platform.system", return_value="Windows")
    @patch("subprocess.Popen")
    def test_open_commands_windows(self, mock_popen, mock_system):
        """Test opening commands on Windows."""
        commands = ["echo test"]
        
        open_commands_in_terminals(commands)
        
        mock_popen.assert_called_once()
        call_args = mock_popen.call_args[0][0]
        assert "cmd" in call_args
    
    @patch("platform.system", return_value="Linux")
    @patch("subprocess.Popen")
    def test_open_commands_linux(self, mock_popen, mock_system):
        """Test opening commands on Linux."""
        commands = ["echo test"]
        
        # First terminal exists
        mock_popen.side_effect = [MagicMock(), FileNotFoundError()]
        
        open_commands_in_terminals(commands)
        
        assert mock_popen.call_count >= 1
    
    @patch("platform.system", return_value="Unknown")
    def test_open_commands_unsupported(self, mock_system):
        """Test opening commands on unsupported OS."""
        with pytest.raises(NotImplementedError):
            open_commands_in_terminals(["echo test"])


class TestPromptToolConfiguration:
    """Test prompt_tool_configuration function."""
    
    @patch("builtins.input", return_value="y")
    @patch("claif.common.utils.open_commands_in_terminals")
    def test_prompt_accept(self, mock_open_terminals, mock_input):
        """Test accepting prompt to open terminals."""
        commands = ["configure --api-key"]
        
        prompt_tool_configuration("Test Tool", commands)
        
        mock_input.assert_called_once()
        mock_open_terminals.assert_called_once_with(commands)
    
    @patch("builtins.input", return_value="n")
    @patch("claif.common.utils.open_commands_in_terminals")
    def test_prompt_decline(self, mock_open_terminals, mock_input):
        """Test declining prompt."""
        commands = ["configure --api-key"]
        
        prompt_tool_configuration("Test Tool", commands)
        
        mock_input.assert_called_once()
        mock_open_terminals.assert_not_called()
    
    @patch("builtins.input", side_effect=KeyboardInterrupt)
    @patch("claif.common.utils.open_commands_in_terminals")
    def test_prompt_interrupt(self, mock_open_terminals, mock_input):
        """Test interrupting prompt."""
        commands = ["configure --api-key"]
        
        # Should not raise
        prompt_tool_configuration("Test Tool", commands)
        
        mock_open_terminals.assert_not_called()


class TestConstants:
    """Test module constants."""

    def test_app_name(self):
        """Test APP_NAME constant."""
        assert APP_NAME == "com.twardoch.claif"