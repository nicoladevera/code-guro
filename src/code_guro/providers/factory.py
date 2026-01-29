"""Provider factory for creating LLM provider instances."""

from typing import Optional


def _get_provider_registry():
    """Lazy import providers to avoid circular dependencies."""
    from code_guro.providers.anthropic_provider import AnthropicProvider
    from code_guro.providers.gemini_provider import GeminiProvider
    from code_guro.providers.openai_provider import OpenAIProvider

    return {
        "anthropic": AnthropicProvider,
        "openai": OpenAIProvider,
        "google": GeminiProvider,
    }


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
