"""Configuration management for Code Guro.

Handles API key storage, retrieval, and validation.
"""

import json
import os
import stat
from pathlib import Path
from typing import Optional

import anthropic
from rich.console import Console

console = Console()

# Environment variable name for API key (takes precedence)
API_KEY_ENV_VAR = "CLAUDE_API_KEY"

# Alternative environment variable name (Anthropic SDK default)
ANTHROPIC_API_KEY_ENV_VAR = "ANTHROPIC_API_KEY"


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
        with open(config_file, "r") as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError):
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


def get_api_key() -> Optional[str]:
    """Get the Claude API key from environment or config file.

    Environment variables take precedence over config file.

    Returns:
        API key string or None if not configured
    """
    # Check environment variables first (in order of preference)
    for env_var in [API_KEY_ENV_VAR, ANTHROPIC_API_KEY_ENV_VAR]:
        key = os.environ.get(env_var)
        if key:
            return key

    # Fall back to config file
    config = read_config()
    return config.get("api_key")


def save_api_key(api_key: str) -> None:
    """Save API key to config file.

    Args:
        api_key: The Claude API key to save
    """
    config = read_config()
    config["api_key"] = api_key
    write_config(config)


def validate_api_key(api_key: str) -> tuple[bool, str]:
    """Validate an API key by making a test request.

    Args:
        api_key: The API key to validate

    Returns:
        Tuple of (is_valid, message)
    """
    try:
        client = anthropic.Anthropic(api_key=api_key)
        # Make a minimal request to validate the key
        client.messages.create(
            model="claude-3-haiku-20240307",
            max_tokens=10,
            messages=[{"role": "user", "content": "Hi"}],
        )
        return True, "API key is valid"
    except anthropic.AuthenticationError:
        return False, "Invalid API key. Please check your key and try again."
    except anthropic.RateLimitError:
        # Key is valid but rate limited - still counts as valid
        return True, "API key is valid (rate limited)"
    except anthropic.APIConnectionError:
        return False, "Could not connect to Anthropic API. Check your internet connection."
    except Exception as e:
        return False, f"Error validating API key: {str(e)}"


def mask_api_key(api_key: str) -> str:
    """Mask an API key for safe display.

    Args:
        api_key: The API key to mask

    Returns:
        Masked string like "sk-ant-...xxxx"
    """
    if not api_key or len(api_key) < 8:
        return "****"
    return f"{api_key[:7]}...{api_key[-4:]}"


def require_api_key() -> Optional[str]:
    """Check if API key is configured and return it.

    Prints helpful error message if not configured.

    Returns:
        API key if available, None otherwise
    """
    api_key = get_api_key()
    if not api_key:
        console.print(
            "[bold red]Error:[/bold red] No API key configured.\n"
            "\n"
            "Please run [bold cyan]code-guro configure[/bold cyan] to set up your Claude API key.\n"
            "\n"
            "You can get an API key at: [link=https://console.anthropic.com]console.anthropic.com[/link]"
        )
        return None
    return api_key


def is_api_key_configured() -> bool:
    """Check if an API key is configured.

    Returns:
        True if API key is available
    """
    return get_api_key() is not None
