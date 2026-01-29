"""Configuration management for Code Guro.

Handles provider selection and configuration.
API keys are stored in environment variables only.
"""

from __future__ import annotations

import json
import os
import stat
from pathlib import Path
from typing import Optional

from rich.console import Console

console = Console()

# Valid provider names
VALID_PROVIDERS = ["anthropic", "openai", "google"]


def get_config_dir() -> Path:
    """Get the configuration directory path.

    Returns:
        Path to ~/.config/code-guro/
    """
    if os.name == "nt":  # Windows
        config_base = Path(os.environ.get("APPDATA", Path.home()))
    else:  # macOS and Linux
        config_base = Path.home() / ".config"

    return config_base / "code-guro"


def ensure_config_dir() -> Path:
    """Create the configuration directory if it doesn't exist.

    Returns:
        Path to the config directory
    """
    config_dir = get_config_dir()
    config_dir.mkdir(parents=True, exist_ok=True)
    return config_dir


def get_config_file() -> Path:
    """Get the path to the config file.

    Returns:
        Path to config.json
    """
    return get_config_dir() / "config.json"


def read_config() -> dict:
    """Read the configuration from disk.

    Returns:
        Configuration dictionary
    """
    config_file = get_config_file()
    if not config_file.exists():
        return {}

    try:
        with open(config_file) as f:
            return json.load(f)
    except (OSError, json.JSONDecodeError):
        return {}


def write_config(config: dict) -> None:
    """Write configuration to disk with secure permissions.

    Args:
        config: Configuration dictionary to save
    """
    config_dir = ensure_config_dir()
    config_file = config_dir / "config.json"

    # Write the file
    with open(config_file, "w") as f:
        json.dump(config, f, indent=2)

    # Set restrictive permissions (chmod 600) on non-Windows systems
    if os.name != "nt":
        os.chmod(config_file, stat.S_IRUSR | stat.S_IWUSR)


def get_provider_config() -> Optional[str]:
    """Get the selected provider from config file.

    Returns:
        Provider name string or None if not configured
    """
    config = read_config()
    provider = config.get("provider")

    # Backwards compatibility: if old config has api_key, assume anthropic
    if not provider and config.get("api_key"):
        return "anthropic"

    return provider


def save_provider_config(provider: str) -> None:
    """Save provider selection to config file.

    Args:
        provider: The provider name to save (must be in VALID_PROVIDERS)
    """
    if provider not in VALID_PROVIDERS:
        raise ValueError(f"Invalid provider: {provider}. Valid providers: {VALID_PROVIDERS}")

    config = read_config()
    config["provider"] = provider
    # Remove old api_key if present (migration)
    if "api_key" in config:
        del config["api_key"]
    write_config(config)


def mask_api_key(api_key: str) -> str:
    """Mask an API key for safe display.

    Args:
        api_key: The API key to mask

    Returns:
        Masked string like "sk-ant-...xxxx" or "sk-...xxxx"
    """
    if not api_key or len(api_key) < 8:
        return "****"
    return f"{api_key[:7]}...{api_key[-4:]}"


def require_provider() -> Optional[str]:
    """Check if a provider is configured and return it.

    Prints helpful error message if not configured.

    Returns:
        Provider name if available, None otherwise
    """
    from code_guro.providers.factory import get_provider

    try:
        provider = get_provider()
    except ValueError:
        console.print(
            "[bold red]Error:[/bold red] No provider configured.\n"
            "\n"
            "Please run [bold cyan]code-guro configure[/bold cyan] to set up your LLM provider.\n"
        )
        return None
    api_key = provider.get_api_key()
    if not api_key:
        console.print(
            "[bold red]Error:[/bold red] No API key configured for this provider.\n"
            "\n"
            f"Please set the [bold cyan]{provider.get_api_key_env_var()}[/bold cyan] "
            "environment variable and try again.\n"
            "\n"
            f"Get your API key at: [link={provider.get_api_key_url()}]"
            f"{provider.get_api_key_url()}[/link]"
        )
        return None

    return provider.get_provider_name().lower()


def is_provider_configured() -> bool:
    """Check if a provider is configured.

    Returns:
        True if provider is configured and API key is available
    """
    try:
        from code_guro.providers.factory import get_provider

        provider = get_provider()
        # Check if API key is available
        return provider.get_api_key() is not None
    except (ValueError, Exception):
        return False


# Backwards compatibility functions (deprecated)
def get_api_key() -> Optional[str]:
    """DEPRECATED: Get API key from environment or legacy config.

    This function is kept for backwards compatibility but should not be used.
    Use get_provider() from providers.factory instead.

    Returns:
        API key string or None if not configured
    """
    # Check environment variables first (legacy Anthropic behavior)
    for env_var in ["CLAUDE_API_KEY", "ANTHROPIC_API_KEY"]:
        key = os.environ.get(env_var)
        if key:
            return key

    # Fall back to legacy config file key if present
    config = read_config()
    return config.get("api_key")


def save_api_key(api_key: str) -> None:
    """DEPRECATED: Save API key to config file.

    This function is kept for backwards compatibility but should not be used.
    API keys are now stored in environment variables.
    """
    config = read_config()
    config["api_key"] = api_key
    write_config(config)


def is_api_key_configured() -> bool:
    """DEPRECATED: Check if API key is configured.

    This function is kept for backwards compatibility.
    Use is_provider_configured() instead.

    Returns:
        True if API key is available
    """
    return get_api_key() is not None
