"""OpenAI GPT-4o provider implementation."""

import os
from typing import Optional, Tuple

import openai
import tiktoken

from code_guro.providers import LLMProvider


class OpenAIProvider(LLMProvider):
    """OpenAI GPT-4o provider."""

    MODEL = "gpt-4o-2024-11-20"
    INPUT_COST_PER_MILLION = 2.50  # $2.50 per million input tokens
    OUTPUT_COST_PER_MILLION = 10.0  # $10 per million output tokens

    def __init__(self):
        """Initialize OpenAI provider."""
        self._encoding = None

    def get_model_name(self) -> str:
        """Get the default model name for OpenAI.

        Returns:
            Model name string
        """
        return self.MODEL

    def get_api_key(self) -> Optional[str]:
        """Get the OpenAI API key from environment variables.

        Returns:
            API key string or None if not configured
        """
        return os.environ.get("OPENAI_API_KEY")

    def call(
        self,
        prompt: str,
        system: str = "",
        max_tokens: int = 4096,
    ) -> str:
        """Make a call to the OpenAI API.

        Args:
            prompt: The user prompt
            system: The system prompt
            max_tokens: Maximum tokens in response

        Returns:
            OpenAI's response text

        Raises:
            openai.AuthenticationError: If API key is invalid
            openai.RateLimitError: If rate limited
            openai.APIConnectionError: If connection fails
        """
        api_key = self.get_api_key()
        if not api_key:
            raise ValueError("OpenAI API key not configured. Set OPENAI_API_KEY environment variable.")

        client = openai.OpenAI(api_key=api_key)

        # Build messages list
        messages = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})

        response = client.chat.completions.create(
            model=self.MODEL,
            max_tokens=max_tokens,
            messages=messages,
        )

        return response.choices[0].message.content

    def validate_api_key(self, api_key: Optional[str] = None) -> Tuple[bool, str]:
        """Validate an OpenAI API key by making a test request.

        Args:
            api_key: The API key to validate (if None, uses get_api_key())

        Returns:
            Tuple of (is_valid, message)
        """
        if api_key is None:
            api_key = self.get_api_key()

        if not api_key:
            return False, "No API key found. Set OPENAI_API_KEY environment variable."

        try:
            client = openai.OpenAI(api_key=api_key)
            # Make a minimal request to validate the key
            client.chat.completions.create(
                model="gpt-4o-mini",  # Use a widely available, low-cost model for validation
                max_tokens=10,
                messages=[{"role": "user", "content": "Hi"}],
            )
            return True, "API key is valid"
        except openai.AuthenticationError:
            return False, "Invalid API key. Please check your key and try again."
        except openai.RateLimitError:
            # Key is valid but rate limited - still counts as valid
            return True, "API key is valid (rate limited)"
        except openai.APIConnectionError:
            return False, "Could not connect to OpenAI API. Check your internet connection."
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
            # OpenAI uses cl100k_base encoding
            self._encoding = tiktoken.get_encoding("cl100k_base")
        return len(self._encoding.encode(text))

    def get_api_key_env_var(self) -> str:
        """Get the environment variable name for OpenAI API key.

        Returns:
            Environment variable name
        """
        return "OPENAI_API_KEY"

    def get_api_key_url(self) -> str:
        """Get the URL where users can obtain an OpenAI API key.

        Returns:
            URL string
        """
        return "https://platform.openai.com/api-keys"

    def get_provider_name(self) -> str:
        """Get the human-readable provider name.

        Returns:
            Provider name
        """
        return "OpenAI"
