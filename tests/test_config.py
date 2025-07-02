"""Tests for claif.common.config module."""

import json
import os
from pathlib import Path
from unittest.mock import patch, mock_open

import pytest

from claif.common.config import (
    Config,
    ProviderConfig,
    load_config,
    save_config,
    merge_config,
    load_env_config
)
from claif.common.types import Provider
from claif.common.errors import ConfigurationError


class TestProviderConfig:
    """Test ProviderConfig model."""
    
    def test_provider_config_defaults(self):
        """Test ProviderConfig default values."""
        config = ProviderConfig()
        
        assert config.enabled is True
        assert config.model is None
        assert config.api_key_env is None
        assert config.timeout == 120
        assert config.extra == {}
    
    def test_provider_config_with_values(self):
        """Test ProviderConfig with all values."""
        config = ProviderConfig(
            enabled=False,
            model="claude-3-opus",
            api_key_env="MY_API_KEY",
            timeout=60,
            extra={"temperature": 0.5, "max_tokens": 1000}
        )
        
        assert config.enabled is False
        assert config.model == "claude-3-opus"
        assert config.api_key_env == "MY_API_KEY"
        assert config.timeout == 60
        assert config.extra["temperature"] == 0.5
        assert config.extra["max_tokens"] == 1000
    
    def test_provider_config_none_extra(self):
        """Test ProviderConfig with None extra."""
        config = ProviderConfig(extra=None)
        assert config.extra == {}


class TestConfig:
    """Test Config model."""
    
    def test_config_defaults(self):
        """Test Config default values."""
        config = Config()
        
        assert config.default_provider == Provider.CLAUDE
        assert config.cache_enabled is True
        assert config.cache_ttl == 3600
        assert config.session_dir is None
        assert config.verbose is False
        assert config.output_format == "text"
        
        # Check default providers
        assert Provider.CLAUDE in config.providers
        assert Provider.GEMINI in config.providers
        assert Provider.CODEX in config.providers
        
        # Check provider configs
        assert config.providers[Provider.CLAUDE].api_key_env == "ANTHROPIC_API_KEY"
        assert config.providers[Provider.GEMINI].api_key_env == "GEMINI_API_KEY"
        assert config.providers[Provider.CODEX].model == "o4-mini"
    
    def test_config_with_custom_values(self):
        """Test Config with custom values."""
        custom_providers = {
            Provider.CLAUDE: ProviderConfig(
                enabled=True,
                model="claude-3-opus",
                api_key_env="CLAUDE_KEY"
            ),
            Provider.GEMINI: ProviderConfig(
                enabled=False
            )
        }
        
        config = Config(
            default_provider=Provider.GEMINI,
            providers=custom_providers,
            cache_enabled=False,
            cache_ttl=7200,
            session_dir="/tmp/claif",
            verbose=True,
            output_format="json",
            retry_config={"max_retries": 5, "delay": 2.0},
            mcp_servers={"test": {"url": "http://localhost:8000"}}
        )
        
        assert config.default_provider == Provider.GEMINI
        assert config.providers == custom_providers
        assert config.cache_enabled is False
        assert config.cache_ttl == 7200
        assert config.session_dir == "/tmp/claif"
        assert config.verbose is True
        assert config.output_format == "json"
        assert config.retry_config["max_retries"] == 5
        assert config.mcp_servers["test"]["url"] == "http://localhost:8000"
    
    def test_config_none_values(self):
        """Test Config with None values."""
        config = Config(
            providers=None,
            retry_config=None,
            mcp_servers=None
        )
        
        # Should initialize with defaults
        assert config.providers is not None
        assert len(config.providers) == 3
        assert config.retry_config is not None
        assert config.mcp_servers is not None


class TestConfigPath:
    """Test configuration path handling."""
    
    @patch("platformdirs.user_config_dir")
    def test_get_config_path_default(self, mock_config_dir):
        """Test getting default config path."""
        mock_config_dir.return_value = "/home/user/.config"
        
        path = get_config_path()
        
        assert isinstance(path, Path)
        assert path.name == "config.json"
        assert "claif" in str(path)
        mock_config_dir.assert_called_once_with("claif", appauthor=False)
    
    def test_get_config_path_from_env(self, monkeypatch):
        """Test getting config path from environment variable."""
        custom_path = "/custom/path/claif.json"
        monkeypatch.setenv("CLAIF_CONFIG", custom_path)
        
        path = get_config_path()
        
        assert path == Path(custom_path)
    
    @patch("platformdirs.user_config_dir")
    def test_get_config_path_creates_directory(self, mock_config_dir, tmp_path):
        """Test that config directory is created if it doesn't exist."""
        config_dir = tmp_path / "new_config"
        mock_config_dir.return_value = str(config_dir)
        
        path = get_config_path()
        
        assert config_dir.exists()
        assert config_dir.is_dir()


class TestDefaultConfig:
    """Test default configuration."""
    
    def test_get_default_config(self):
        """Test getting default configuration."""
        config = get_default_config()
        
        assert isinstance(config, Config)
        assert config.default_provider == Provider.CLAUDE
        assert config.cache_enabled is True
        assert config.verbose is False
        assert len(config.providers) == 3
    
    def test_default_config_immutable(self):
        """Test that default config is a new instance each time."""
        config1 = get_default_config()
        config2 = get_default_config()
        
        # Modify config1
        config1.default_provider = Provider.GEMINI
        config1.verbose = True
        
        # config2 should not be affected
        assert config2.default_provider == Provider.CLAUDE
        assert config2.verbose is False


class TestLoadConfig:
    """Test configuration loading."""
    
    def test_load_config_file_exists(self, tmp_path):
        """Test loading existing config file."""
        config_file = tmp_path / "config.json"
        config_data = {
            "default_provider": "gemini",
            "cache_enabled": False,
            "verbose": True,
            "providers": {
                "claude": {
                    "enabled": True,
                    "model": "claude-3-opus"
                }
            }
        }
        config_file.write_text(json.dumps(config_data))
        
        config = load_config(config_file)
        
        assert config.default_provider == Provider.GEMINI
        assert config.cache_enabled is False
        assert config.verbose is True
        assert config.providers[Provider.CLAUDE].model == "claude-3-opus"
    
    def test_load_config_file_not_exists(self, tmp_path):
        """Test loading non-existent config file returns default."""
        config_file = tmp_path / "missing.json"
        
        config = load_config(config_file)
        
        # Should return default config
        assert config.default_provider == Provider.CLAUDE
        assert config.cache_enabled is True
    
    def test_load_config_invalid_json(self, tmp_path):
        """Test loading invalid JSON raises error."""
        config_file = tmp_path / "invalid.json"
        config_file.write_text("{ invalid json }")
        
        with pytest.raises(ConfigurationError) as exc_info:
            load_config(config_file)
        
        assert "Failed to parse" in str(exc_info.value)
    
    def test_load_config_invalid_provider(self, tmp_path):
        """Test loading config with invalid provider."""
        config_file = tmp_path / "config.json"
        config_data = {
            "default_provider": "invalid_provider"
        }
        config_file.write_text(json.dumps(config_data))
        
        with pytest.raises(ConfigurationError) as exc_info:
            load_config(config_file)
        
        assert "Invalid provider" in str(exc_info.value)
    
    def test_load_config_partial_data(self, tmp_path):
        """Test loading partial config data."""
        config_file = tmp_path / "partial.json"
        config_data = {
            "verbose": True,
            "cache_ttl": 7200
        }
        config_file.write_text(json.dumps(config_data))
        
        config = load_config(config_file)
        
        assert config.verbose is True
        assert config.cache_ttl == 7200
        # Should have defaults for missing fields
        assert config.default_provider == Provider.CLAUDE
        assert config.cache_enabled is True


class TestSaveConfig:
    """Test configuration saving."""
    
    def test_save_config_basic(self, tmp_path):
        """Test saving basic configuration."""
        config_file = tmp_path / "config.json"
        config = Config(
            default_provider=Provider.GEMINI,
            verbose=True,
            cache_ttl=7200
        )
        
        save_config(config, config_file)
        
        assert config_file.exists()
        saved_data = json.loads(config_file.read_text())
        assert saved_data["default_provider"] == "gemini"
        assert saved_data["verbose"] is True
        assert saved_data["cache_ttl"] == 7200
    
    def test_save_config_with_providers(self, tmp_path):
        """Test saving config with provider settings."""
        config_file = tmp_path / "config.json"
        config = Config()
        config.providers[Provider.CLAUDE].model = "claude-3-opus"
        config.providers[Provider.CLAUDE].timeout = 60
        
        save_config(config, config_file)
        
        saved_data = json.loads(config_file.read_text())
        assert saved_data["providers"]["claude"]["model"] == "claude-3-opus"
        assert saved_data["providers"]["claude"]["timeout"] == 60
    
    def test_save_config_creates_directory(self, tmp_path):
        """Test saving config creates parent directory."""
        config_file = tmp_path / "new_dir" / "config.json"
        config = Config()
        
        save_config(config, config_file)
        
        assert config_file.exists()
        assert config_file.parent.exists()
    
    def test_save_config_overwrite(self, tmp_path):
        """Test saving config overwrites existing file."""
        config_file = tmp_path / "config.json"
        config_file.write_text('{"old": "data"}')
        
        config = Config(verbose=True)
        save_config(config, config_file)
        
        saved_data = json.loads(config_file.read_text())
        assert "old" not in saved_data
        assert saved_data["verbose"] is True
    
    def test_save_config_permission_error(self, tmp_path):
        """Test handling permission error when saving."""
        config_file = tmp_path / "readonly" / "config.json"
        config_file.parent.mkdir()
        
        # Make directory read-only
        os.chmod(config_file.parent, 0o444)
        
        config = Config()
        
        try:
            with pytest.raises(ConfigurationError) as exc_info:
                save_config(config, config_file)
            assert "Failed to save" in str(exc_info.value)
        finally:
            # Cleanup - restore permissions
            os.chmod(config_file.parent, 0o755)


class TestConfigIntegration:
    """Test configuration integration scenarios."""
    
    def test_config_roundtrip(self, tmp_path):
        """Test saving and loading configuration."""
        config_file = tmp_path / "config.json"
        
        # Create config with custom values
        original = Config(
            default_provider=Provider.GEMINI,
            cache_enabled=False,
            verbose=True,
            session_dir="/tmp/sessions",
            providers={
                Provider.CLAUDE: ProviderConfig(
                    model="claude-3-opus",
                    timeout=90
                ),
                Provider.GEMINI: ProviderConfig(
                    enabled=False
                )
            }
        )
        
        # Save
        save_config(original, config_file)
        
        # Load
        loaded = load_config(config_file)
        
        # Verify
        assert loaded.default_provider == Provider.GEMINI
        assert loaded.cache_enabled is False
        assert loaded.verbose is True
        assert loaded.session_dir == "/tmp/sessions"
        assert loaded.providers[Provider.CLAUDE].model == "claude-3-opus"
        assert loaded.providers[Provider.CLAUDE].timeout == 90
        assert loaded.providers[Provider.GEMINI].enabled is False
    
    def test_config_environment_override(self, tmp_path, monkeypatch):
        """Test environment variables override config file."""
        config_file = tmp_path / "config.json"
        
        # Save config with one set of values
        config = Config(
            default_provider=Provider.CLAUDE,
            verbose=False
        )
        save_config(config, config_file)
        
        # Set environment variables
        monkeypatch.setenv("CLAIF_DEFAULT_PROVIDER", "gemini")
        monkeypatch.setenv("CLAIF_VERBOSE", "true")
        
        # Load config - env vars should override
        loaded = load_config(config_file)
        
        assert loaded.default_provider == Provider.GEMINI
        assert loaded.verbose is True