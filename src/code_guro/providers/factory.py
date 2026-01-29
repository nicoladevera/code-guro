"""Provider factory for creating LLM provider instances."""

import importlib.util
from typing import Optional


def _google_sdk_available() -> bool:
    """Check if the Google Generative AI SDK is available."""
    return importlib.util.find_spec("google.generativeai") is not None


def _get_provider_registry():
    """Lazy import providers to avoid circular dependencies."""
    from code_guro.providers.anthropic_provider import AnthropicProvider
    from code_guro.providers.openai_provider import OpenAIProvider

    registry = {
        "anthropic": AnthropicProvider,
        "openai": OpenAIProvider,
    }

    if _google_sdk_available():
        from code_guro.providers.gemini_provider import GeminiProvider

        registry["google"] = GeminiProvider

    return registry


def get_provider(provider_name: Optional[str] = None):
    """Get a provider instance.

    Args:
        provider_name: Name of provider to use. If None, reads from config.

    Returns:
        LLMProvider instance

    Raises:
        ValueError: If provider name is invalid or not configured
    """
    from code_guro.config import get_provider_config

    if provider_name is None:
        provider_name = get_provider_config()

    if not provider_name:
        raise ValueError(
            "No provider configured. Run 'code-guro configure' to set up a provider."
        )

    provider_name = provider_name.lower()
    providers = _get_provider_registry()

    if provider_name not in providers:
        if provider_name == "google" and not _google_sdk_available():
            raise ValueError(
                "Google provider requires google-generativeai. "
                "Install it with Python 3.9+ to enable Gemini support."
            )
        valid_providers = ", ".join(providers.keys())
        raise ValueError(
            f"Invalid provider '{provider_name}'. Valid providers: {valid_providers}"
        )

    provider_class = providers[provider_name]
    return provider_class()


def list_providers():
    """List all available providers.

    Returns:
        List of provider names
    """
    return list(_get_provider_registry().keys())
