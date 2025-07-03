"""Configuration management for Claif framework."""

import contextlib
import json
import os
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional

from loguru import logger

from claif.common.errors import ConfigurationError
from claif.common.types import Provider


@dataclass
class ProviderConfig:
    """
    Configuration settings specific to a single LLM provider.

    Attributes:
        enabled: A boolean indicating if the provider is enabled. Defaults to True.
        model: The default model to use for this provider (e.g., 'claude-3-opus').
        api_key_env: The name of the environment variable holding the API key for this provider.
        timeout: The default timeout in seconds for requests to this provider. Defaults to 120 seconds.
        extra: A dictionary for any additional, provider-specific configuration parameters.
               Defaults to an empty dictionary.
    """

    enabled: bool = True
    model: Optional[str] = None
    api_key_env: Optional[str] = None
    timeout: int = 120
    extra: Dict[str, Any] = field(default_factory=dict)


@dataclass
class Config:
    """
    Main configuration class for the Claif framework.

    This class holds all global and provider-specific settings for Claif.
    Default values are provided for common settings, which can be overridden
    by configuration files or environment variables.

    Attributes:
        default_provider: The default LLM provider to use if not specified otherwise.
                          Defaults to `Provider.CLAUDE`.
        providers: A dictionary mapping `Provider` enum values to `ProviderConfig` objects.
                   This holds specific configurations for each integrated LLM provider.
        cache_enabled: A boolean indicating if response caching is enabled globally. Defaults to True.
        cache_ttl: The time-to-live (in seconds) for cached responses. Defaults to 3600 seconds (1 hour).
        session_dir: The directory path where conversation sessions are stored.
                     Defaults to `~/.claif/sessions`.
        verbose: A boolean indicating if verbose logging is enabled globally. Defaults to False.
        output_format: The default output format for CLI responses (e.g., "text", "json").
                       Defaults to "text".
        retry_config: A dictionary containing global retry settings, including `count`,
                      `delay`, and `backoff` factor. Defaults to `{"count": 3, "delay": 1.0, "backoff": 2.0}`.
        mcp_servers: A dictionary for configuring MCP (Multi-Agent Communication Protocol) servers.
                     Defaults to an empty dictionary.
    """

    default_provider: Provider = Provider.CLAUDE
    providers: Dict[Provider, ProviderConfig] = field(default_factory=lambda: {
        Provider.CLAUDE: ProviderConfig(api_key_env="ANTHROPIC_API_KEY"),
        Provider.GEMINI: ProviderConfig(api_key_env="GEMINI_API_KEY"),
        Provider.CODEX: ProviderConfig(model="o4-mini"),
    })
    cache_enabled: bool = True
    cache_ttl: int = 3600
    session_dir: Optional[str] = None  # Initialized in __post_init__
    verbose: bool = False
    output_format: str = "text"
    retry_config: Dict[str, Any] = field(default_factory=lambda: {"count": 3, "delay": 1.0, "backoff": 2.0})
    mcp_servers: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        """
        Post-initialization hook to set default values for mutable fields
        and ensure `session_dir` is properly initialized.
        """
        # Initialize session_dir if it's None (default_factory for Path is tricky with dataclasses)
        if self.session_dir is None:
            self.session_dir = str(Path.home() / ".claif" / "sessions")


def load_config(config_file: Optional[str] = None) -> Config:
    """
    Loads the Claif configuration from various sources.

    Configuration is loaded in the following order of precedence (later items override earlier ones):
    1. Default values defined in the `Config` dataclass.
    2. Configuration from default JSON files (e.g., `~/.claif/config.json`, `~/.config/claif/config.json`, `claif.json`).
    3. Configuration from a specified `config_file` (if provided).
    4. Environment variables (e.g., `CLAIF_DEFAULT_PROVIDER`).

    Args:
        config_file: Optional path to a custom JSON configuration file.

    Returns:
        A `Config` object representing the loaded and merged configuration.

    Raises:
        ConfigurationError: If a specified configuration file cannot be loaded or parsed.
    """
    config = Config()  # Start with default configuration

    # Define potential paths for configuration files, ordered by precedence.
    config_paths: List[Path] = [
        Path.home() / ".claif" / "config.json",
        Path.home() / ".config" / "claif" / "config.json",
        Path("claif.json"),
    ]

    # If a specific config file is provided, it takes highest precedence among files.
    if config_file:
        config_paths.insert(0, Path(config_file))

    # Load configuration from files.
    # All found config files are loaded, with later ones overriding earlier ones.
    for path in config_paths:
        if path.exists():
            try:
                with open(path, "r") as f:
                    data: Dict[str, Any] = json.load(f)
                    config = merge_config(config, data)  # Merge file data into current config
                logger.debug(f"Loaded configuration from file: {path}")
            except Exception as e:
                msg = f"Failed to load configuration from {path}: {e}"
                logger.error(msg)
                raise ConfigurationError(msg) from e

    # Override configuration with environment variables.
    config = load_env_config(config)

    return config


def merge_config(base: Config, overrides: Dict[str, Any]) -> Config:
    """
    Recursively merges override settings into a base `Config` object.

    This function handles nested dictionaries and ensures that `ProviderConfig`
    objects are correctly instantiated when merging provider-specific settings.

    Args:
        base: The base `Config` object to merge into.
        overrides: A dictionary containing the configuration overrides.

    Returns:
        A new `Config` object with merged settings.
    """
    # Convert the base Config object to a dictionary for easier merging.
    base_dict: Dict[str, Any] = asdict(base)

    def deep_merge(d1: Dict[str, Any], d2: Dict[str, Any]) -> Dict[str, Any]:
        """
        Helper function for recursive dictionary merging.
        """
        result = d1.copy()
        for key, value in d2.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = deep_merge(result[key], value)
            else:
                result[key] = value
        return result

    # Perform the deep merge of the base dictionary and overrides.
    merged_dict: Dict[str, Any] = deep_merge(base_dict, overrides)

    # Special handling for 'providers' section to ensure ProviderConfig objects are created.
    if "providers" in merged_dict and isinstance(merged_dict["providers"], dict):
        new_providers_config: Dict[Provider, ProviderConfig] = {}
        for provider_name, pconfig_data in merged_dict["providers"].items():
            try:
                provider_enum = Provider(provider_name) # Convert string name to Provider enum
                # If the base config already has this provider, merge into it.
                if provider_enum in base.providers and isinstance(pconfig_data, dict):
                    existing_pconfig = base.providers[provider_enum]
                    merged_pconfig_data = deep_merge(asdict(existing_pconfig), pconfig_data)
                    new_providers_config[provider_enum] = ProviderConfig(**merged_pconfig_data)
                elif isinstance(pconfig_data, dict):
                    new_providers_config[provider_enum] = ProviderConfig(**pconfig_data)
                else:
                    # If pconfig_data is not a dictionary, it means the configuration for this provider
                    # is not structured as expected (e.g., it's a simple boolean like `enabled: true`).
                    # In such cases, we log a warning and assign the value directly, assuming it's a simple override.
                    # For more complex scenarios, a more robust schema validation might be needed.
                    logger.warning(
                        f"Provider config for {provider_name} is not a dictionary. "
                        "Skipping detailed merge and assigning value directly."
                    )
                    new_providers_config[provider_enum] = pconfig_data
            except ValueError:
                logger.warning(f"Unknown provider name '{provider_name}' in config. Skipping.")
        merged_dict["providers"] = new_providers_config

    # Reconstruct the Config object from the merged dictionary.
    # This assumes all top-level keys in merged_dict correspond to Config attributes.
    return Config(**merged_dict)


def load_env_config(config: Config) -> Config:
    """
    Loads configuration settings from environment variables and applies them to the `Config` object.

    Environment variables take precedence over file-based configurations.
    Expected environment variable format: `CLAIF_<SETTING_NAME>` (e.g., `CLAIF_DEFAULT_PROVIDER`).

    Args:
        config: The `Config` object to apply environment variables to.

    Returns:
        The `Config` object updated with environment variable settings.
    """
    # Load default provider from environment variable.
    if env_provider := os.getenv("CLAIF_DEFAULT_PROVIDER"):
        with contextlib.suppress(ValueError):
            config.default_provider = Provider(env_provider.lower())
            logger.debug(f"Config: default_provider set from env to {config.default_provider}")

    # Load verbose mode setting.
    if os.getenv("CLAIF_VERBOSE", "").lower() in ("true", "1", "yes"):
        config.verbose = True
        logger.debug("Config: verbose mode enabled from env.")

    # Load output format.
    if env_format := os.getenv("CLAIF_OUTPUT_FORMAT"):
        config.output_format = env_format
        logger.debug(f"Config: output_format set from env to {config.output_format}")

    # Load cache settings.
    if os.getenv("CLAIF_CACHE_ENABLED", "").lower() in ("false", "0", "no"):
        config.cache_enabled = False
        logger.debug("Config: cache_enabled set from env to False.")

    if cache_ttl := os.getenv("CLAIF_CACHE_TTL"):
        with contextlib.suppress(ValueError):
            config.cache_ttl = int(cache_ttl)
            logger.debug(f"Config: cache_ttl set from env to {config.cache_ttl}")

    # Load session directory.
    if session_dir := os.getenv("CLAIF_SESSION_DIR"):
        config.session_dir = session_dir
        logger.debug(f"Config: session_dir set from env to {config.session_dir}")

    # Load retry configuration from environment variables.
    if retry_count := os.getenv("CLAIF_RETRY_COUNT"):
        with contextlib.suppress(ValueError):
            config.retry_config["count"] = int(retry_count)
            logger.debug(f"Config: retry_config.count set from env to {config.retry_config["count"]}")

    if retry_delay := os.getenv("CLAIF_RETRY_DELAY"):
        with contextlib.suppress(ValueError):
            config.retry_config["delay"] = float(retry_delay)
            logger.debug(f"Config: retry_config.delay set from env to {config.retry_config["delay"]}")

    if retry_backoff := os.getenv("CLAIF_RETRY_BACKOFF"):
        with contextlib.suppress(ValueError):
            config.retry_config["backoff"] = float(retry_backoff)
            logger.debug(f"Config: retry_config.backoff set from env to {config.retry_config["backoff"]}")

    return config


def save_config(config: Config, path: Optional[str] = None) -> None:
    """
    Saves the current `Config` object to a JSON file.

    Args:
        config: The `Config` object to save.
        path: Optional. The file path where the configuration should be saved.
              If None, it defaults to `~/.claif/config.json`.

    Raises:
        IOError: If there is an issue writing the file.
    """
    # Determine the save path.
    save_path: Path = Path.home() / ".claif" / "config.json" if path is None else Path(path)

    # Ensure the parent directory exists.
    save_path.parent.mkdir(parents=True, exist_ok=True)

    try:
        with open(save_path, "w") as f:
            # Convert the Config object to a dictionary for JSON serialization.
            json.dump(asdict(config), f, indent=2)
        logger.info(f"Configuration saved to {save_path}")
    except Exception as e:
        msg = f"Failed to save configuration to {save_path}: {e}"
        logger.error(msg)
        raise IOError(msg) from e
