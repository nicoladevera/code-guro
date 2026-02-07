"""Anthropic Claude provider implementation."""

import os
import time
from typing import Optional, Tuple

import anthropic
import tiktoken

from code_guro.providers import LLMProvider


class AnthropicProvider(LLMProvider):
    """Anthropic Claude provider."""

    MODEL = "claude-sonnet-4-20250514"
    INPUT_COST_PER_MILLION = 3.0  # $3 per million input tokens
    OUTPUT_COST_PER_MILLION = 15.0  # $15 per million output tokens

    def __init__(self):
        """Initialize Anthropic provider."""
        self._encoding = None

    def get_model_name(self) -> str:
        """Get the default model name for Anthropic.

        Returns:
            Model name string
        """
        return self.MODEL

    def get_api_key(self) -> Optional[str]:
        """Get the Anthropic API key from config file or environment variables.

        Priority:
        1. Config file (~/.config/code-guro/config.json)
        2. CLAUDE_API_KEY environment variable (backwards compatibility)
        3. ANTHROPIC_API_KEY environment variable (standard)

        Returns:
            API key string or None if not configured
        """
        # Check config file first
        from code_guro.config import get_api_key_from_config

        config_key = get_api_key_from_config("anthropic")
        if config_key:
            return config_key

        # Check CLAUDE_API_KEY for backwards compatibility
        key = os.environ.get("CLAUDE_API_KEY")
        if key:
            return key

        # Check ANTHROPIC_API_KEY (standard)
        key = os.environ.get("ANTHROPIC_API_KEY")
        if key:
            return key

        return None

    def call(
        self,
        prompt: str,
        system: str = "",
        max_tokens: int = 4096,
    ) -> str:
        """Make a call to the Anthropic Claude API with automatic retry on rate limits.

        Args:
            prompt: The user prompt
            system: The system prompt
            max_tokens: Maximum tokens in response

        Returns:
            Claude's response text

        Raises:
            anthropic.AuthenticationError: If API key is invalid
            anthropic.RateLimitError: If rate limited after all retries
            anthropic.APIConnectionError: If connection fails
        """
        api_key = self.get_api_key()
        if not api_key:
            raise ValueError(
                "Anthropic API key not configured. Set ANTHROPIC_API_KEY environment variable."
            )

        client = anthropic.Anthropic(api_key=api_key)

        # Retry configuration
        max_retries = 3
        base_delay = 5  # Start with 5 seconds

        for attempt in range(max_retries + 1):
            try:
                message = client.messages.create(
                    model=self.MODEL,
                    max_tokens=max_tokens,
                    system=system,
                    messages=[{"role": "user", "content": prompt}],
                )

                return message.content[0].text

            except anthropic.RateLimitError:
                # If this was the last attempt, re-raise the error
                if attempt >= max_retries:
                    raise

                # Calculate exponential backoff delay
                delay = base_delay * (2**attempt)

                # Wait before retrying
                time.sleep(delay)

    def validate_api_key(self, api_key: Optional[str] = None) -> Tuple[bool, str]:
        """Validate an Anthropic API key by making a test request.

        Args:
            api_key: The API key to validate (if None, uses get_api_key())

        Returns:
            Tuple of (is_valid, message)
        """
        if api_key is None:
            api_key = self.get_api_key()

        if not api_key:
            return False, "No API key found. Set ANTHROPIC_API_KEY environment variable."

        try:
            client = anthropic.Anthropic(api_key=api_key)
            # Make a minimal request to validate the key
            client.messages.create(
                # Use cheaper model for validation
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

    def estimate_cost(self, input_tokens: int, output_tokens: int = 0) -> float:
        """Estimate API cost based on token counts.

        Args:
            input_tokens: Number of input tokens
            output_tokens: Number of output tokens

        Returns:
            Estimated cost in USD
        """
        input_cost = (input_tokens / 1_000_000) * self.INPUT_COST_PER_MILLION
        output_cost = (output_tokens / 1_000_000) * self.OUTPUT_COST_PER_MILLION
        return input_cost + output_cost

    def count_tokens(self, text: str) -> int:
        """Count tokens in a text string using tiktoken.

        Args:
            text: The text to count tokens for

        Returns:
            Number of tokens
        """
        if self._encoding is None:
            # Claude uses cl100k_base encoding (same as GPT-4)
            self._encoding = tiktoken.get_encoding("cl100k_base")
        return len(self._encoding.encode(text))

    def get_api_key_env_var(self) -> str:
        """Get the environment variable name for Anthropic API key.

        Returns:
            Environment variable name
        """
        return "ANTHROPIC_API_KEY"

    def get_api_key_url(self) -> str:
        """Get the URL where users can obtain an Anthropic API key.

        Returns:
            URL string
        """
        return "https://console.anthropic.com"

    def get_provider_name(self) -> str:
        """Get the human-readable provider name.

        Returns:
            Provider name
        """
        return "Anthropic"
