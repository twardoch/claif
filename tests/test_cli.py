"""Tests for claif.cli module."""

import sys
from io import StringIO
from unittest.mock import patch, MagicMock, AsyncMock, call

import pytest
import fire

from claif.cli import ClaifCLI, main
from claif.common.types import Message, MessageRole, Provider, ClaifOptions
from claif.common.config import Config


class TestClaifCLI:
    """Test ClaifCLI class."""
    
    @patch("claif.cli._client")
    @patch("claif.cli.load_config")
    def test_cli_init_default(self, mock_load_config, mock_client):
        """Test CLI initialization with defaults."""
        mock_config = Config(
            default_provider=Provider.CLAUDE,
            verbose=False
        )
        mock_load_config.return_value = mock_config
        
        cli = ClaifCLI()
        
        assert cli.client == mock_client
        assert cli.config == mock_config
        mock_load_config.assert_called_once_with(None)
    
    @patch("claif.cli._client")
    @patch("claif.cli.load_config")
    def test_cli_init_verbose(self, mock_load_config, mock_client):
        """Test CLI initialization with verbose mode."""
        mock_config = Config(
            default_provider=Provider.CLAUDE,
            verbose=False
        )
        mock_load_config.return_value = mock_config
        
        cli = ClaifCLI(verbose=True)
        
        assert cli.config.verbose is True
    
    @patch("claif.cli._client")
    @patch("claif.cli.load_config")
    def test_cli_init_with_config(self, mock_load_config, mock_client):
        """Test CLI initialization with config file."""
        mock_config = Config(
            default_provider=Provider.CLAUDE,
            verbose=False
        )
        mock_load_config.return_value = mock_config
        
        cli = ClaifCLI(config_file="/path/to/config.json")
        
        mock_load_config.assert_called_once_with("/path/to/config.json")


class TestClaifCLIQuery:
    """Test query functionality."""
    
    @patch("claif.cli.Console")
    @patch("claif.cli.query")
    @patch("claif.cli.load_config")
    def test_query_basic(self, mock_load_config, mock_query, mock_console_class):
        """Test basic query operation."""
        # Setup
        mock_config = Config(default_provider=Provider.CLAUDE)
        mock_load_config.return_value = mock_config
        mock_console = MagicMock()
        mock_console_class.return_value = mock_console
        
        # Mock async response
        async def mock_query_gen(prompt, options):
            yield Message(role=MessageRole.ASSISTANT, content="Test response")
        
        mock_query.return_value = mock_query_gen("Test query", MagicMock())
        
        cli = ClaifCLI()
        
        # Call query - this is a sync method that uses asyncio.run internally
        cli.query("Test query", provider="claude")
        
        # Verify console output
        mock_console.print.assert_called()
    
    @patch("claif.cli.Console")
    @patch("claif.cli.query")
    @patch("claif.cli.load_config")
    def test_query_with_params(self, mock_load_config, mock_query, mock_console_class):
        """Test query with parameters."""
        # Setup
        mock_config = Config(default_provider=Provider.CLAUDE)
        mock_load_config.return_value = mock_config
        mock_console = MagicMock()
        mock_console_class.return_value = mock_console
        
        # Mock async response
        async def mock_query_gen(prompt, options):
            yield Message(role=MessageRole.ASSISTANT, content="Detailed response")
        
        mock_query.return_value = mock_query_gen("Complex query", MagicMock())
        
        cli = ClaifCLI()
        
        # Call query with parameters
        cli.query(
            "Complex query",
            provider="claude",
            temperature=0.5,
            max_tokens=1000,
            system="Be helpful"
        )
        
        # Verify query was called
        mock_query.assert_called_once()
        call_args = mock_query.call_args
        assert call_args[0][0] == "Complex query"
        options = call_args[0][1]
        assert options.provider == Provider.CLAUDE
        assert options.temperature == 0.5
        assert options.max_tokens == 1000
        assert options.system_prompt == "Be helpful"
    
    @patch("claif.cli.Console")
    @patch("claif.cli.query")
    @patch("claif.cli.load_config")
    def test_query_error_handling(self, mock_load_config, mock_query, mock_console_class):
        """Test query error handling."""
        # Setup
        mock_config = Config(default_provider=Provider.CLAUDE)
        mock_load_config.return_value = mock_config
        mock_console = MagicMock()
        mock_console_class.return_value = mock_console
        
        # Mock query to raise error
        async def mock_query_error(prompt, options):
            raise ValueError("Test error")
            yield  # Make it a generator
        
        mock_query.return_value = mock_query_error("Test", MagicMock())
        
        cli = ClaifCLI()
        
        # Should handle error gracefully
        with patch("sys.exit") as mock_exit:
            cli.query("Test", provider="claude")
            
            # Should print error and exit
            assert any("Error" in str(call) for call in mock_console.print.call_args_list)
            mock_exit.assert_called_once_with(1)
    
    @patch("claif.cli.Console")
    @patch("claif.cli.query")
    @patch("claif.cli.load_config")
    def test_query_with_metrics(self, mock_load_config, mock_query, mock_console_class):
        """Test query with metrics display."""
        # Setup
        mock_config = Config(default_provider=Provider.CLAUDE, verbose=True)
        mock_load_config.return_value = mock_config
        mock_console = MagicMock()
        mock_console_class.return_value = mock_console
        
        # Mock async response
        async def mock_query_gen(prompt, options):
            yield Message(role=MessageRole.ASSISTANT, content="Response")
        
        mock_query.return_value = mock_query_gen("Test", MagicMock())
        
        cli = ClaifCLI(verbose=True)
        
        # Call query with show_metrics
        cli.query("Test", provider="claude", show_metrics=True)
        
        # Should print response and metrics
        assert mock_console.print.call_count >= 2


class TestClaifCLIStream:
    """Test stream functionality."""
    
    @patch("claif.cli.Live")
    @patch("claif.cli.query")
    @patch("claif.cli.load_config")
    def test_stream_basic(self, mock_load_config, mock_query, mock_live_class):
        """Test basic streaming."""
        # Setup
        mock_config = Config(default_provider=Provider.CLAUDE)
        mock_load_config.return_value = mock_config
        mock_live = MagicMock()
        mock_live_class.return_value.__enter__.return_value = mock_live
        
        # Mock streaming response
        async def mock_query_stream(prompt, options):
            yield Message(role=MessageRole.ASSISTANT, content="Part 1")
            yield Message(role=MessageRole.ASSISTANT, content="Part 2")
        
        mock_query.return_value = mock_query_stream("Test", MagicMock())
        
        cli = ClaifCLI()
        
        # Call stream
        cli.stream("Test", provider="claude")
        
        # Verify live updates
        assert mock_live.update.call_count >= 2


class TestClaifCLIParallel:
    """Test parallel query functionality."""
    
    @patch("claif.cli.Console")
    @patch("claif.cli.query_all")
    @patch("claif.cli.load_config")
    def test_parallel_basic(self, mock_load_config, mock_query_all, mock_console_class):
        """Test querying all providers in parallel."""
        # Setup
        mock_config = Config(default_provider=Provider.CLAUDE)
        mock_load_config.return_value = mock_config
        mock_console = MagicMock()
        mock_console_class.return_value = mock_console
        
        # Mock parallel responses
        async def mock_all_responses(prompt, options):
            yield {
                Provider.CLAUDE: [Message(role=MessageRole.ASSISTANT, content="Claude says hi")],
                Provider.GEMINI: [Message(role=MessageRole.ASSISTANT, content="Gemini says hello")],
                Provider.CODEX: []
            }
        
        mock_query_all.return_value = mock_all_responses("Test", MagicMock())
        
        cli = ClaifCLI()
        
        # Call parallel
        cli.parallel("Test query")
        
        # Should print all responses
        assert mock_console.print.call_count >= 3
    
    @patch("claif.cli.Columns")
    @patch("claif.cli.Panel")
    @patch("claif.cli.Console")
    @patch("claif.cli.query_all")
    @patch("claif.cli.load_config")
    def test_parallel_compare_mode(self, mock_load_config, mock_query_all, mock_console_class, mock_panel, mock_columns):
        """Test parallel query with comparison mode."""
        # Setup
        mock_config = Config(default_provider=Provider.CLAUDE)
        mock_load_config.return_value = mock_config
        mock_console = MagicMock()
        mock_console_class.return_value = mock_console
        
        # Mock parallel responses
        async def mock_all_responses(prompt, options):
            yield {
                Provider.CLAUDE: [Message(role=MessageRole.ASSISTANT, content="Claude response")],
                Provider.GEMINI: [Message(role=MessageRole.ASSISTANT, content="Gemini response")]
            }
        
        mock_query_all.return_value = mock_all_responses("Test", MagicMock())
        
        cli = ClaifCLI()
        
        # Call parallel with compare mode
        cli.parallel("Test query", compare=True)
        
        # Should create panels and columns for comparison
        assert mock_panel.call_count >= 2
        mock_columns.assert_called_once()


class TestClaifCLIProviders:
    """Test provider management commands."""
    
    @patch("claif.cli.Table")
    @patch("claif.cli.Console")
    @patch("claif.cli.load_config")
    def test_list_providers(self, mock_load_config, mock_console_class, mock_table_class):
        """Test listing providers."""
        # Setup
        mock_config = Config(
            default_provider=Provider.CLAUDE,
            providers={
                "claude": {"enabled": True, "model": "claude-3"},
                "gemini": {"enabled": True, "model": "gemini-pro"},
                "codex": {"enabled": False}
            }
        )
        mock_load_config.return_value = mock_config
        mock_console = MagicMock()
        mock_console_class.return_value = mock_console
        mock_table = MagicMock()
        mock_table_class.return_value = mock_table
        
        cli = ClaifCLI()
        
        # List providers
        cli.providers(action="list")
        
        # Should create table with provider info
        mock_table_class.assert_called_once()
        assert mock_table.add_row.call_count == 3  # Three providers
        mock_console.print.assert_called_with(mock_table)
    
    @patch("claif.cli.Console")
    @patch("claif.cli.query")
    @patch("claif.cli.load_config")
    async def test_provider_status(self, mock_load_config, mock_query, mock_console_class):
        """Test checking provider status."""
        # Setup
        mock_config = Config(default_provider=Provider.CLAUDE)
        mock_load_config.return_value = mock_config
        mock_console = MagicMock()
        mock_console_class.return_value = mock_console
        
        # Mock health check responses
        async def mock_claude_query(prompt, options):
            yield Message(role=MessageRole.ASSISTANT, content="OK")
        
        async def mock_gemini_query(prompt, options):
            raise Exception("Connection error")
        
        mock_query.side_effect = [
            mock_claude_query("Hello", MagicMock()),
            mock_gemini_query("Hello", MagicMock()),
            mock_claude_query("Hello", MagicMock())  # For codex
        ]
        
        cli = ClaifCLI()
        
        # Check status
        cli.providers(action="status")
        
        # Should print health status for all providers
        print_calls = mock_console.print.call_args_list
        assert any("Healthy" in str(call) for call in print_calls)
        assert any("Unhealthy" in str(call) for call in print_calls)


class TestClaifCLIConfig:
    """Test configuration commands."""
    
    @patch("claif.cli.Console")
    @patch("claif.cli.load_config")
    def test_config_show(self, mock_load_config, mock_console_class):
        """Test showing configuration."""
        # Setup
        mock_config = Config(
            default_provider=Provider.CLAUDE,
            cache_enabled=True,
            cache_ttl=3600,
            verbose=False
        )
        mock_load_config.return_value = mock_config
        mock_console = MagicMock()
        mock_console_class.return_value = mock_console
        
        cli = ClaifCLI()
        
        # Show config
        cli.config(action="show")
        
        # Should print config details
        print_calls = mock_console.print.call_args_list
        assert any("Default Provider: claude" in str(call) for call in print_calls)
        assert any("Cache Enabled: True" in str(call) for call in print_calls)
    
    @patch("claif.cli.Console")
    @patch("claif.cli.load_config")
    def test_config_set(self, mock_load_config, mock_console_class):
        """Test setting configuration values."""
        # Setup
        mock_config = Config(default_provider=Provider.CLAUDE)
        mock_load_config.return_value = mock_config
        mock_console = MagicMock()
        mock_console_class.return_value = mock_console
        
        cli = ClaifCLI()
        
        # Set config values
        cli.config(action="set", default_provider="gemini", cache_enabled=False)
        
        # Config should be updated
        assert cli.config.default_provider == Provider.GEMINI
        assert cli.config.cache_enabled is False
        
        # Should print success messages
        print_calls = mock_console.print.call_args_list
        assert any("Set default provider: gemini" in str(call) for call in print_calls)
    
    @patch("claif.cli.save_config")
    @patch("claif.cli.Console")
    @patch("claif.cli.load_config")
    def test_config_save(self, mock_load_config, mock_console_class, mock_save_config):
        """Test saving configuration."""
        # Setup
        mock_config = Config(default_provider=Provider.CLAUDE)
        mock_load_config.return_value = mock_config
        mock_console = MagicMock()
        mock_console_class.return_value = mock_console
        
        cli = ClaifCLI()
        
        # Save config
        cli.config(action="save", path="/custom/path.json")
        
        # Should call save_config
        mock_save_config.assert_called_once_with(mock_config, "/custom/path.json")
        
        # Should print success
        print_calls = mock_console.print.call_args_list
        assert any("Configuration saved" in str(call) for call in print_calls)


class TestClaifCLIInstall:
    """Test install/uninstall functionality."""
    
    @patch("claif.cli.install_all_tools")
    @patch("claif.cli.Console")
    @patch("claif.cli.load_config")
    def test_install_all(self, mock_load_config, mock_console_class, mock_install_all):
        """Test installing all providers."""
        # Setup
        mock_config = Config(default_provider=Provider.CLAUDE)
        mock_load_config.return_value = mock_config
        mock_console = MagicMock()
        mock_console_class.return_value = mock_console
        
        # Mock install results
        mock_install_all.return_value = {
            "installed": ["claude", "gemini"],
            "failed": ["codex"]
        }
        
        cli = ClaifCLI()
        
        # Install all
        cli.install()
        
        # Should call install_all_tools
        mock_install_all.assert_called_once()
        
        # Should print results
        print_calls = mock_console.print.call_args_list
        assert any("Installed: claude, gemini" in str(call) for call in print_calls)
        assert any("Failed: codex" in str(call) for call in print_calls)


class TestClaifCLIServer:
    """Test server functionality."""
    
    @patch("claif.cli.start_mcp_server")
    @patch("claif.cli.Console")
    @patch("claif.cli.load_config")
    def test_server_start(self, mock_load_config, mock_console_class, mock_start_server):
        """Test starting MCP server."""
        # Setup
        mock_config = Config(default_provider=Provider.CLAUDE)
        mock_load_config.return_value = mock_config
        mock_console = MagicMock()
        mock_console_class.return_value = mock_console
        
        cli = ClaifCLI()
        
        # Start server
        cli.server(host="0.0.0.0", port=9000, reload=True)
        
        # Should call start_mcp_server
        mock_start_server.assert_called_once_with("0.0.0.0", 9000, True, mock_config)
        
        # Should print server info
        print_calls = mock_console.print.call_args_list
        assert any("Starting Claif MCP Server" in str(call) for call in print_calls)
        assert any("Host: 0.0.0.0" in str(call) for call in print_calls)
        assert any("Port: 9000" in str(call) for call in print_calls)


class TestClaifCLIMain:
    """Test main entry point."""
    
    @patch("fire.Fire")
    def test_main_function(self, mock_fire):
        """Test main function."""
        main()
        
        # Should call Fire with ClaifCLI
        mock_fire.assert_called_once_with(ClaifCLI)


class TestClaifCLISession:
    """Test session functionality."""
    
    @patch("claif.cli.Console")
    @patch("claif.cli.load_config")
    def test_session_claude(self, mock_load_config, mock_console_class):
        """Test starting Claude session."""
        # Setup
        mock_config = Config(default_provider=Provider.CLAUDE, verbose=True)
        mock_load_config.return_value = mock_config
        mock_console = MagicMock()
        mock_console_class.return_value = mock_console
        
        cli = ClaifCLI()
        
        # Mock the import to avoid ImportError
        with patch("claif.cli.ClaudeCLI") as mock_claude_cli_class:
            mock_claude_cli = MagicMock()
            mock_claude_cli.interactive = MagicMock()
            mock_claude_cli_class.return_value = mock_claude_cli
            
            # Start Claude session
            cli.session("claude")
            
            # Should create Claude CLI and call interactive
            mock_claude_cli_class.assert_called_once_with(verbose=True)
            mock_claude_cli.interactive.assert_called_once()
            
            # Should print session start message
            print_calls = mock_console.print.call_args_list
            assert any("Starting claude session" in str(call) for call in print_calls)


class TestClaifCLIStatus:
    """Test status command."""
    
    @patch("claif.cli.shutil.which")
    @patch("claif.cli.get_install_location")
    @patch("claif.cli.Console")
    @patch("claif.cli.load_config")
    def test_status_command(self, mock_load_config, mock_console_class, mock_get_location, mock_which):
        """Test status command shows provider installation status."""
        # Setup
        mock_config = Config(default_provider=Provider.CLAUDE)
        mock_load_config.return_value = mock_config
        mock_console = MagicMock()
        mock_console_class.return_value = mock_console
        
        # Mock install location
        mock_get_location.return_value = Path("/home/user/.local/bin/claif")
        
        # Mock which commands
        mock_which.side_effect = lambda cmd: "/home/user/.local/bin/claif/claude" if cmd == "claude" else None
        
        cli = ClaifCLI()
        
        # Mock the provider status imports
        with patch("claif.cli.get_claude_status") as mock_claude_status, \
             patch("claif.cli.get_gemini_status") as mock_gemini_status, \
             patch("claif.cli.get_codex_status") as mock_codex_status:
            
            # Mock provider statuses
            mock_claude_status.return_value = {
                "installed": True,
                "path": "/home/user/.local/bin/claif/claude",
                "type": "wrapper"
            }
            mock_gemini_status.return_value = {"installed": False}
            mock_codex_status.return_value = {"installed": True, "path": "/usr/local/bin/codex", "type": "native"}
            
            # Check status
            cli.status()
            
            # Should show install directory and provider statuses
            print_calls = mock_console.print.call_args_list
            assert any("Install Directory:" in str(call) for call in print_calls)
            assert any("Claude Provider:" in str(call) for call in print_calls)
            assert any("Installed:" in str(call) for call in print_calls)