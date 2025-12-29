"""Custom exceptions and error handling for Code Guro."""

from rich.console import Console

console = Console()


class CodeGuroError(Exception):
    """Base exception for Code Guro."""

    def __init__(self, message: str, hint: str = ""):
        self.message = message
        self.hint = hint
        super().__init__(message)

    def display(self):
        """Display the error message with formatting."""
        console.print(f"\n[bold red]Error:[/bold red] {self.message}")
        if self.hint:
            console.print(f"[dim]{self.hint}[/dim]")
        console.print()


class ConfigurationError(CodeGuroError):
    """Error related to configuration."""

    pass


class APIKeyError(ConfigurationError):
    """Error related to API key."""

    pass


class AnalysisError(CodeGuroError):
    """Error during codebase analysis."""

    pass


class NetworkError(CodeGuroError):
    """Error related to network connectivity."""

    pass


class GitHubError(CodeGuroError):
    """Error related to GitHub operations."""

    pass


# Error message templates
ERROR_MESSAGES = {
    "no_api_key": (
        "No API key configured.",
        "Run 'code-guro configure' to set up your Claude API key.\n"
        "Get your API key at: https://console.anthropic.com",
    ),
    "invalid_api_key": (
        "Invalid API key.",
        "Please check your API key and run 'code-guro configure' to update it.",
    ),
    "directory_not_found": (
        "Directory not found: {path}",
        "Please check the path and try again.",
    ),
    "not_a_directory": (
        "Path is not a directory: {path}",
        "Please provide a directory path, not a file.",
    ),
    "github_clone_failed": (
        "Failed to clone GitHub repository: {url}",
        "Check that the URL is correct and the repository is accessible.\n"
        "Make sure you have git installed and internet connectivity.",
    ),
    "github_auth_failed": (
        "Authentication failed for GitHub repository.",
        "This may be a private repository. Code Guro currently only supports public repos.",
    ),
    "no_internet": (
        "No internet connection detected.",
        "Code Guro requires an internet connection to analyze code.\n"
        "Please check your connection and try again.",
    ),
    "rate_limited": (
        "API rate limit reached.",
        "Please wait a few minutes before trying again.\n"
        "Consider using a different API key if this persists.",
    ),
    "api_timeout": (
        "API request timed out.",
        "This might be due to a large codebase or slow connection.\n"
        "Try again, or analyze a smaller portion of the codebase.",
    ),
    "file_too_large": (
        "File is too large to analyze: {path}",
        "Files larger than 1MB are skipped to avoid excessive API costs.",
    ),
    "encoding_error": (
        "Could not read file due to encoding issues: {path}",
        "The file may use an unsupported character encoding.",
    ),
    "empty_directory": (
        "No analyzable files found in directory.",
        "The directory may be empty or contain only binary/ignored files.",
    ),
}


def get_error(error_type: str, **kwargs) -> CodeGuroError:
    """Get a formatted error with message and hint.

    Args:
        error_type: Key from ERROR_MESSAGES
        **kwargs: Format arguments for the message

    Returns:
        CodeGuroError instance
    """
    if error_type not in ERROR_MESSAGES:
        return CodeGuroError(f"Unknown error: {error_type}")

    message, hint = ERROR_MESSAGES[error_type]
    return CodeGuroError(message.format(**kwargs), hint.format(**kwargs))


def check_internet_connection() -> bool:
    """Check if there is an internet connection.

    Returns:
        True if connected, False otherwise
    """
    import socket

    try:
        socket.create_connection(("api.anthropic.com", 443), timeout=5)
        return True
    except OSError:
        return False


def handle_api_error(error: Exception) -> None:
    """Handle API errors and display appropriate messages.

    Args:
        error: The exception that occurred
    """
    import anthropic

    if isinstance(error, anthropic.AuthenticationError):
        get_error("invalid_api_key").display()
    elif isinstance(error, anthropic.RateLimitError):
        get_error("rate_limited").display()
    elif isinstance(error, anthropic.APIConnectionError):
        if not check_internet_connection():
            get_error("no_internet").display()
        else:
            get_error("api_timeout").display()
    else:
        console.print(f"\n[bold red]Error:[/bold red] {str(error)}")
        console.print()
