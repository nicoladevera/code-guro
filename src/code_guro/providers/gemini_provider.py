"""Google Gemini provider implementation."""

import os
from typing import Optional, Tuple

try:
    import google.generativeai as genai
except ImportError:  # pragma: no cover - handled at runtime for optional dependency
    genai = None
import tiktoken

from code_guro.providers import LLMProvider


class GeminiProvider(LLMProvider):
    """Google Gemini provider."""

    MODEL = "gemini-2.0-flash-exp"
    INPUT_COST_PER_MILLION = 0.075  # $0.075 per million input tokens
    OUTPUT_COST_PER_MILLION = 0.30  # $0.30 per million output tokens

    def __init__(self):
        """Initialize Gemini provider."""
        self._encoding = None
        self._client_initialized = False

    def _ensure_client_initialized(self):
        """Ensure the Gemini client is initialized with API key."""
        if genai is None:
            raise ImportError(
                "google-generativeai is not installed. "
                "Install it with Python 3.9+ to use the Google provider."
            )
        if not self._client_initialized:
            api_key = self.get_api_key()
            if not api_key:
                raise ValueError("Google API key not configured. Set GOOGLE_API_KEY environment variable.")
            genai.configure(api_key=api_key)
            self._client_initialized = True

    def get_model_name(self) -> str:
        """Get the default model name for Gemini.

        Returns:
            Model name string
        """
        return self.MODEL

    def get_api_key(self) -> Optional[str]:
        """Get the Google API key from environment variables.

        Checks GOOGLE_API_KEY first, then GEMINI_API_KEY for backwards compatibility.

        Returns:
            API key string or None if not configured
        """
        # Check GOOGLE_API_KEY (standard)
        key = os.environ.get("GOOGLE_API_KEY")
        if key:
            return key

        # Check GEMINI_API_KEY for backwards compatibility
        key = os.environ.get("GEMINI_API_KEY")
        if key:
            return key

        return None

    def call(
        self,
        prompt: str,
        system: str = "",
        max_tokens: int = 4096,
    ) -> str:
        """Make a call to the Google Gemini API.

        Args:
            prompt: The user prompt
            system: The system prompt (Gemini uses system_instruction parameter)
            max_tokens: Maximum tokens in response

        Returns:
            Gemini's response text

        Raises:
            Exception: Various exceptions for API errors
        """
        self._ensure_client_initialized()

        model = genai.GenerativeModel(
            model_name=self.MODEL,
            system_instruction=system if system else None,
        )

        # Gemini uses generation_config for max_tokens
        generation_config = genai.types.GenerationConfig(max_output_tokens=max_tokens)

        response = model.generate_content(
            prompt,
            generation_config=generation_config,
        )

        # Handle response - Gemini returns text directly
        if hasattr(response, 'text'):
            return response.text
        elif hasattr(response, 'candidates') and response.candidates:
            # Fallback for different response formats
            return response.candidates[0].content.parts[0].text
        else:
            raise ValueError(f"Unexpected response format: {response}")

    def validate_api_key(self, api_key: Optional[str] = None) -> Tuple[bool, str]:
        """Validate a Google API key by making a test request.

        Args:
            api_key: The API key to validate (if None, uses get_api_key())

        Returns:
            Tuple of (is_valid, message)
        """
        if api_key is None:
            api_key = self.get_api_key()

        if not api_key:
            return False, "No API key found. Set GOOGLE_API_KEY environment variable."

        if genai is None:
            return (
                False,
                "google-generativeai is not installed. Install it with Python 3.9+ to use Gemini.",
            )

        try:
            # Temporarily configure with the provided key
            genai.configure(api_key=api_key)
            model = genai.GenerativeModel(model_name="gemini-2.0-flash-exp")
            # Make a minimal request to validate the key
            model.generate_content(
                "Hi", generation_config=genai.types.GenerationConfig(max_output_tokens=10)
            )
            # Reset client initialization state
            self._client_initialized = False
            return True, "API key is valid"
        except Exception as e:
            error_str = str(e).lower()
            if "api_key" in error_str or "authentication" in error_str or "invalid" in error_str:
                return False, "Invalid API key. Please check your key and try again."
            elif "quota" in error_str or "rate" in error_str:
                # Key is valid but rate limited - still counts as valid
                return True, "API key is valid (rate limited)"
            elif "connection" in error_str or "network" in error_str:
                return False, "Could not connect to Google API. Check your internet connection."
            else:
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
        """Count tokens in a text string.

        For Gemini, we use tiktoken as an approximation since the exact tokenizer
        isn't publicly available. The count_tokens API method exists but requires
        a model instance, so we use tiktoken for consistency.

        Args:
            text: The text to count tokens for

        Returns:
            Number of tokens (approximate)
        """
        # Use tiktoken as approximation - Gemini tokenization is similar
        if self._encoding is None:
            self._encoding = tiktoken.get_encoding("cl100k_base")
        return len(self._encoding.encode(text))

    def get_api_key_env_var(self) -> str:
        """Get the environment variable name for Google API key.

        Returns:
            Environment variable name
        """
        return "GOOGLE_API_KEY"

    def get_api_key_url(self) -> str:
        """Get the URL where users can obtain a Google API key.

        Returns:
            URL string
        """
        return "https://aistudio.google.com/app/apikey"

    def get_provider_name(self) -> str:
        """Get the human-readable provider name.

        Returns:
            Provider name
        """
        return "Google"
