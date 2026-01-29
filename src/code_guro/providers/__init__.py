"""LLM Provider abstraction layer for Code Guro.

Supports multiple LLM providers: Anthropic Claude, OpenAI GPT-4o, and Google Gemini.
"""

from abc import ABC, abstractmethod
from typing import Optional, Tuple

__all__ = ["LLMProvider"]


class LLMProvider(ABC):
    """Abstract base class for LLM providers."""

    @abstractmethod
    def get_model_name(self) -> str:
        """Get the default model name for this provider.

        Returns:
            Model name string (e.g., "claude-sonnet-4-20250514")
        """
        pass

    @abstractmethod
    def get_api_key(self) -> Optional[str]:
        """Get the API key for this provider from environment variables.

        Returns:
            API key string or None if not configured
        """
        pass

    @abstractmethod
    def call(
        self,
        prompt: str,
        system: str = "",
        max_tokens: int = 4096,
    ) -> str:
        """Make a call to the LLM API.

        Args:
            prompt: The user prompt
            system: The system prompt
            max_tokens: Maximum tokens in response

        Returns:
            LLM response text

        Raises:
            Various provider-specific exceptions for API errors
        """
        pass

    @abstractmethod
    def validate_api_key(self, api_key: Optional[str] = None) -> Tuple[bool, str]:
        """Validate an API key by making a test request.

        Args:
            api_key: The API key to validate (if None, uses get_api_key())

        Returns:
            Tuple of (is_valid, message)
        """
        pass

    @abstractmethod
    def estimate_cost(self, input_tokens: int, output_tokens: int = 0) -> float:
        """Estimate API cost based on token counts.

        Args:
            input_tokens: Number of input tokens
            output_tokens: Number of output tokens

        Returns:
            Estimated cost in USD
        """
        pass

    @abstractmethod
    def count_tokens(self, text: str) -> int:
        """Count tokens in a text string.

        Args:
            text: The text to count tokens for

        Returns:
            Number of tokens
        """
        pass

    @abstractmethod
    def get_api_key_env_var(self) -> str:
        """Get the environment variable name for this provider's API key.

        Returns:
            Environment variable name (e.g., "ANTHROPIC_API_KEY")
        """
        pass

    @abstractmethod
    def get_api_key_url(self) -> str:
        """Get the URL where users can obtain an API key.

        Returns:
            URL string (e.g., "https://console.anthropic.com")
        """
        pass

    @abstractmethod
    def get_provider_name(self) -> str:
        """Get the human-readable provider name.

        Returns:
            Provider name (e.g., "Anthropic", "OpenAI", "Google")
        """
        pass
