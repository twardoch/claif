"""Tests for claif.cli module."""

import sys
from io import StringIO
from unittest.mock import AsyncMock, MagicMock, call, patch

import fire
import pytest

from claif.cli import ClaifCLI, main
from claif.common.config import Config
from claif.common.types import ClaifOptions, Message, MessageRole, Provider


class TestClaifCLI:
    """Test ClaifCLI class."""

    @patch("claif.cli._client")
    @patch("claif.cli.load_config")
    def test_cli_init_default(self, mock_load_config, mock_client):
        """Test CLI initialization with defaults."""
        mock_config = Config(default_provider=Provider.CLAUDE, verbose=False)
        mock_load_config.return_value = mock_config

        cli = ClaifCLI()

        assert cli.client == mock_client
        assert cli.config == mock_config
        mock_load_config.assert_called_once_with(None)

    @patch("claif.cli._client")
    @patch("claif.cli.load_config")
    def test_cli_init_verbose(self, mock_load_config, mock_client):
        """Test CLI initialization with verbose mode."""
        mock_config = Config(default_provider=Provider.CLAUDE, verbose=False)
        mock_load_config.return_value = mock_config

        cli = ClaifCLI(verbose=True)

        assert cli.config.verbose is True

    @patch("claif.cli._client")
    @patch("claif.cli.load_config")
    def test_cli_init_with_config(self, mock_load_config, mock_client):
        """Test CLI initialization with config file."""
        mock_config = Config(default_provider=Provider.CLAUDE, verbose=False)
        mock_load_config.return_value = mock_config

        ClaifCLI(config_file="/path/to/config.json")

        mock_load_config.assert_called_once_with("/path/to/config.json")


class TestClaifCLIQuery:
    """Test query functionality."""

    @patch("claif.cli.console")
    @patch("claif.client.query")
    @patch("claif.cli.load_config")
    def test_query_basic(self, mock_load_config, mock_query, mock_console):
        """Test basic query operation."""
        # Setup
        mock_config = Config(default_provider=Provider.CLAUDE)
        mock_load_config.return_value = mock_config

        # Mock async response
        async def mock_query_gen(prompt, options):
            yield Message(role=MessageRole.ASSISTANT, content="Test response")

        mock_query.return_value = mock_query_gen("Test query", MagicMock())

        cli = ClaifCLI()

        # Call query - this is a sync method that uses asyncio.run internally
        cli.query("Test query", provider="claude")

        # Verify console output
        mock_console.print.assert_called()

    @patch("claif.cli.console")
    @patch("claif.client.query")
    @patch("claif.cli.load_config")
    def test_query_with_params(self, mock_load_config, mock_query, mock_console):
        """Test query with parameters."""
        # Setup
        mock_config = Config(default_provider=Provider.CLAUDE)
        mock_load_config.return_value = mock_config

        # Mock async response
        async def mock_query_gen(prompt, options):
            yield Message(role=MessageRole.ASSISTANT, content="Detailed response")

        mock_query.return_value = mock_query_gen("Complex query", MagicMock())

        cli = ClaifCLI()

        # Call query with parameters
        cli.query("Complex query", provider="claude", temperature=0.5, max_tokens=1000, system="Be helpful")

        # Verify query was called
        mock_query.assert_called_once()
        call_args = mock_query.call_args
        assert call_args[0][0] == "Complex query"
        options = call_args[0][1]
        assert options.provider == Provider.CLAUDE
        assert options.temperature == 0.5
        assert options.max_tokens == 1000
        assert options.system_prompt == "Be helpful"

    @patch("claif.cli.console")
    @patch("claif.client.query")
    @patch("claif.cli.load_config")
    def test_query_error_handling(self, mock_load_config, mock_query, mock_console):
        """Test query error handling."""
        # Setup
        mock_config = Config(default_provider=Provider.CLAUDE)
        mock_load_config.return_value = mock_config

        # Mock query to raise error
        async def mock_query_error(prompt, options):
            msg = "Test error"
            raise ValueError(msg)
            yield  # Make it a generator

        mock_query.return_value = mock_query_error("Test", MagicMock())

        cli = ClaifCLI()

        # Should handle error gracefully
        with patch("sys.exit") as mock_exit:
            cli.query("Test", provider="claude")

            # Should print error and exit
            assert any("Error" in str(call) for call in mock_console.print.call_args_list)
            mock_exit.assert_called_once_with(1)

    @patch("claif.cli.console")
    @patch("claif.client.query")
    @patch("claif.cli.load_config")
    def test_query_with_metrics(self, mock_load_config, mock_query, mock_console):
        """Test query with metrics display."""
        # Setup
        mock_config = Config(default_provider=Provider.CLAUDE, verbose=True)
        mock_load_config.return_value = mock_config

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
    @patch("claif.client.query")
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

    @patch("claif.cli.console")
    @patch("claif.client.query_all")
    @patch("claif.cli.load_config")
    def test_parallel_basic(self, mock_load_config, mock_query_all, mock_console):
        """Test querying all providers in parallel."""
        # Setup
        mock_config = Config(default_provider=Provider.CLAUDE)
        mock_load_config.return_value = mock_config

        # Mock parallel responses
        async def mock_all_responses(prompt, options):
            yield {
                Provider.CLAUDE: [Message(role=MessageRole.ASSISTANT, content="Claude says hi")],
                Provider.GEMINI: [Message(role=MessageRole.ASSISTANT, content="Gemini says hello")],
                Provider.CODEX: [],
            }

        mock_query_all.return_value = mock_all_responses("Test", MagicMock())

        cli = ClaifCLI()

        # Call parallel
        cli.parallel("Test query")

        # Should print all responses
        assert mock_console.print.call_count >= 3

    @patch("claif.cli.Columns")
    @patch("claif.cli.Panel")
    @patch("claif.cli.console")
    @patch("claif.client.query_all")
    @patch("claif.cli.load_config")
    def test_parallel_compare_mode(
        self, mock_load_config, mock_query_all, mock_console, mock_panel, mock_columns
    ):
        """Test parallel query with comparison mode."""
        # Setup
        mock_config = Config(default_provider=Provider.CLAUDE)
        mock_load_config.return_value = mock_config

        # Mock parallel responses
        async def mock_all_responses(prompt, options):
            yield {
                Provider.CLAUDE: [Message(role=MessageRole.ASSISTANT, content="Claude response")],
                Provider.GEMINI: [Message(role=MessageRole.ASSISTANT, content="Gemini response")],
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
    @patch("claif.cli.console")
    @patch("claif.cli.load_config")
    def test_list_providers(self, mock_load_config, mock_console, mock_table_class):
        """Test listing providers."""
        # Setup
        mock_config = Config(
            default_provider=Provider.CLAUDE,
            providers={
                "claude": {"enabled": True, "model": "claude-3"},
                "gemini": {"enabled": True, "model": "gemini-pro"},
                "codex": {"enabled": False},
            },
        )
        mock_load_config.return_value = mock_config
        mock_table = MagicMock()
        mock_table_class.return_value = mock_table

        cli = ClaifCLI()

        # Call providers
        cli.providers()

        # Should create and display table
        mock_table_class.assert_called_once()
        assert mock_table.add_row.call_count >= 3
        mock_console.print.assert_called_with(mock_table)

    @patch("claif.cli.console")
    @patch("claif.cli._client")
    @patch("claif.cli.load_config")
    def test_provider_status(self, mock_load_config, mock_client, mock_console):
        """Test provider status check."""
        # Setup
        mock_config = Config(default_provider=Provider.CLAUDE)
        mock_load_config.return_value = mock_config
        mock_client.is_provider_available = MagicMock(side_effect=lambda p: p != Provider.CODEX)

        cli = ClaifCLI()

        # Call status
        cli.status()

        # Should check and print status for all providers
        assert mock_client.is_provider_available.call_count == 3
        assert mock_console.print.call_count >= 3


class TestClaifCLIConfig:
    """Test configuration commands."""

    @patch("claif.cli.console")
    @patch("claif.cli.load_config")
    def test_config_show(self, mock_load_config, mock_console):
        """Test showing configuration."""
        # Setup
        mock_config = Config(default_provider=Provider.CLAUDE, verbose=True)
        mock_load_config.return_value = mock_config

        cli = ClaifCLI()

        # Call config
        cli.config()

        # Should print config
        mock_console.print.assert_called()

    @patch("claif.cli.console")
    @patch("claif.cli.save_config")
    @patch("claif.cli.load_config")
    def test_config_set(self, mock_load_config, mock_save_config, mock_console):
        """Test setting configuration values."""
        # Setup
        mock_config = Config(default_provider=Provider.CLAUDE)
        mock_load_config.return_value = mock_config

        cli = ClaifCLI()

        # Set provider
        cli.config(set_provider="gemini")

        # Should update and save config
        assert cli.config.default_provider == Provider.GEMINI
        mock_save_config.assert_called_once_with(cli.config)

        # Set verbose
        cli.config(set_verbose=True)
        assert cli.config.verbose is True

    @patch("claif.cli.console")
    @patch("claif.cli.save_config")
    @patch("claif.cli.load_config")
    def test_config_save(self, mock_load_config, mock_save_config, mock_console):
        """Test saving configuration."""
        # Setup
        mock_config = Config(default_provider=Provider.CLAUDE)
        mock_load_config.return_value = mock_config

        cli = ClaifCLI()

        # Call config with save
        cli.config(save="/path/to/config.json")

        # Should save to specified path
        mock_save_config.assert_called_once_with(mock_config, "/path/to/config.json")


class TestClaifCLIInstall:
    """Test installation commands."""

    @patch("claif.cli.console")
    @patch("claif.cli._client")
    @patch("claif.cli.load_config")
    def test_install_all(self, mock_load_config, mock_client, mock_console):
        """Test installing all providers."""
        # Setup
        mock_config = Config(default_provider=Provider.CLAUDE)
        mock_load_config.return_value = mock_config
        mock_client.install_all_providers = AsyncMock()

        cli = ClaifCLI()

        # Call install all
        cli.install(all=True)

        # Should install all providers
        mock_client.install_all_providers.assert_called_once()


class TestClaifCLIServer:
    """Test MCP server functionality."""

    @patch("claif.cli.start_mcp_server")
    @patch("claif.cli.load_config")
    def test_server_start(self, mock_load_config, mock_start_server):
        """Test starting MCP server."""
        # Setup
        mock_config = Config(default_provider=Provider.CLAUDE)
        mock_load_config.return_value = mock_config

        cli = ClaifCLI()

        # Call server
        cli.server(host="0.0.0.0", port=8080)

        # Should start server
        mock_start_server.assert_called_once_with("0.0.0.0", 8080)


class TestClaifCLIMain:
    """Test main entry point."""

    @patch("claif.cli.fire.Fire")
    def test_main_function(self, mock_fire):
        """Test main function."""
        main()

        # Should launch Fire with ClaifCLI
        mock_fire.assert_called_once_with(ClaifCLI)


class TestClaifCLISession:
    """Test session commands."""

    @patch("claif.cli.console")
    @patch("claif.cli.load_config")
    def test_session_claude(self, mock_load_config, mock_console):
        """Test session command for Claude provider."""
        # Setup
        mock_config = Config(default_provider=Provider.CLAUDE)
        mock_load_config.return_value = mock_config

        cli = ClaifCLI()

        # Mock the provider to have session method
        with patch.object(cli.client, "get_provider") as mock_get_provider:
            mock_provider = MagicMock()
            mock_provider.session = MagicMock()
            mock_get_provider.return_value = mock_provider

            # Call session
            cli.session(list=True, provider="claude")

            # Should call provider's session method
            mock_provider.session.assert_called_once_with(list=True, provider="claude")


class TestClaifCLIStatus:
    """Test status command."""

    @patch("claif.cli.Table")
    @patch("claif.cli.console")
    @patch("claif.cli._client")
    @patch("claif.cli.load_config")
    def test_status_command(self, mock_load_config, mock_client, mock_console, mock_table_class):
        """Test comprehensive status display."""
        # Setup
        mock_config = Config(
            default_provider=Provider.CLAUDE,
            providers={
                "claude": {"enabled": True},
                "gemini": {"enabled": True},
                "codex": {"enabled": False},
            },
        )
        mock_load_config.return_value = mock_config
        mock_client.is_provider_available = MagicMock(return_value=True)
        mock_table = MagicMock()
        mock_table_class.return_value = mock_table

        cli = ClaifCLI()

        # Call status
        cli.status()

        # Should create status table
        mock_table_class.assert_called()
        assert mock_table.add_row.call_count >= 3