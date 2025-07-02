"""Configuration management forClaif framework."""

import contextlib
import json
import os
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

from .errors import ConfigurationError
from .types import Provider


@dataclass
class ProviderConfig:
    """Configuration for a specific provider."""

    enabled: bool = True
    model: str | None = None
    api_key_env: str | None = None
    timeout: int = 120
    extra: dict[str, Any] = None

    def __post_init__(self):
        if self.extra is None:
            self.extra = {}


@dataclass
class Config:
    """Main configuration forClaif."""

    default_provider: Provider = Provider.CLAUDE
    providers: dict[str, ProviderConfig] = None
    cache_enabled: bool = True
    cache_ttl: int = 3600
    session_dir: str | None = None
    verbose: bool = False
    output_format: str = "text"
    retry_config: dict[str, Any] = None
    mcp_servers: dict[str, Any] = None

    def __post_init__(self):
        if self.providers is None:
            self.providers = {
                Provider.CLAUDE: ProviderConfig(api_key_env="ANTHROPIC_API_KEY"),
                Provider.GEMINI: ProviderConfig(api_key_env="GEMINI_API_KEY"),
                Provider.CODEX: ProviderConfig(model="o4-mini"),
            }
        if self.retry_config is None:
            self.retry_config = {"count": 3, "delay": 1.0, "backoff": 2.0}
        if self.mcp_servers is None:
            self.mcp_servers = {}
        if self.session_dir is None:
            self.session_dir = str(Path.home() / ".claif" / "sessions")


def load_config(config_file: str | None = None) -> Config:
    """Load configuration from file and environment."""
    config = Config()

    # Load from default locations
    config_paths = [
        Path.home() / ".claif" / "config.json",
        Path.home() / ".config" / "claif" / "config.json",
        Path("claif.json"),
    ]

    if config_file:
        config_paths.insert(0, Path(config_file))

    # Load from file
    for path in config_paths:
        if path.exists():
            try:
                with open(path) as f:
                    data = json.load(f)
                    config = merge_config(config, data)
                break
            except Exception as e:
                msg = f"Failed to load config from {path}: {e}"
                raise ConfigurationError(msg)

    # Override with environment variables
    return load_env_config(config)


def merge_config(base: Config, overrides: dict[str, Any]) -> Config:
    """Merge configuration overrides into base config."""
    base_dict = asdict(base)

    def deep_merge(d1: dict, d2: dict) -> dict:
        result = d1.copy()
        for key, value in d2.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = deep_merge(result[key], value)
            else:
                result[key] = value
        return result

    merged = deep_merge(base_dict, overrides)

    # Handle provider configs
    if "providers" in merged:
        for provider, pconfig in merged["providers"].items():
            if isinstance(pconfig, dict):
                merged["providers"][provider] = ProviderConfig(**pconfig)

    return Config(**merged)


def load_env_config(config: Config) -> Config:
    """Load configuration from environment variables."""
    # Default provider
    if env_provider := os.getenv("CLAIF_DEFAULT_PROVIDER"):
        with contextlib.suppress(ValueError):
            config.default_provider = Provider(env_provider.lower())

    # Verbose mode
    if os.getenv("CLAIF_VERBOSE", "").lower() in ("true", "1", "yes"):
        config.verbose = True

    # Output format
    if env_format := os.getenv("CLAIF_OUTPUT_FORMAT"):
        config.output_format = env_format

    # Cache settings
    if os.getenv("CLAIF_CACHE_ENABLED", "").lower() in ("false", "0", "no"):
        config.cache_enabled = False

    if cache_ttl := os.getenv("CLAIF_CACHE_TTL"):
        with contextlib.suppress(ValueError):
            config.cache_ttl = int(cache_ttl)

    # Session directory
    if session_dir := os.getenv("CLAIF_SESSION_DIR"):
        config.session_dir = session_dir

    return config


def save_config(config: Config, path: str | None = None) -> None:
    """Save configuration to file."""
    path = Path.home() / ".claif" / "config.json" if path is None else Path(path)

    path.parent.mkdir(parents=True, exist_ok=True)

    with open(path, "w") as f:
        json.dump(asdict(config), f, indent=2)
