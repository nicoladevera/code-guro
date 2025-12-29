"""Utility functions for Code Guro.

Includes file handling, token counting, and cost estimation.
"""

import fnmatch
import os
import re
from pathlib import Path
from typing import Generator, Optional, Set

import tiktoken

# Binary file extensions to skip
BINARY_EXTENSIONS = {
    # Images
    ".png", ".jpg", ".jpeg", ".gif", ".bmp", ".ico", ".svg", ".webp", ".tiff",
    # Audio/Video
    ".mp3", ".mp4", ".wav", ".avi", ".mov", ".mkv", ".flac", ".ogg",
    # Archives
    ".zip", ".tar", ".gz", ".rar", ".7z", ".bz2",
    # Executables
    ".exe", ".dll", ".so", ".dylib", ".bin",
    # Fonts
    ".ttf", ".otf", ".woff", ".woff2", ".eot",
    # Documents
    ".pdf", ".doc", ".docx", ".xls", ".xlsx", ".ppt", ".pptx",
    # Other binary
    ".pyc", ".pyo", ".class", ".o", ".a", ".lib",
    ".sqlite", ".db", ".sqlite3",
    ".lock",  # Lock files can be large and aren't useful for analysis
}

# Files and directories to always skip
ALWAYS_SKIP = {
    ".git",
    ".svn",
    ".hg",
    "node_modules",
    "__pycache__",
    ".pytest_cache",
    ".mypy_cache",
    ".ruff_cache",
    ".tox",
    ".nox",
    ".eggs",
    "*.egg-info",
    ".venv",
    "venv",
    "env",
    ".env",
    "dist",
    "build",
    ".next",
    ".nuxt",
    ".output",
    "coverage",
    ".coverage",
    ".nyc_output",
}

# Maximum file size to read (1MB)
MAX_FILE_SIZE = 1024 * 1024

# Claude API pricing (as of MVP)
CLAUDE_INPUT_COST_PER_MILLION = 3.0  # $3 per million input tokens
CLAUDE_OUTPUT_COST_PER_MILLION = 15.0  # $15 per million output tokens

# Context window limits
MAX_CONTEXT_TOKENS = 200000  # Claude 3.5 Sonnet context
SAFE_CONTEXT_TOKENS = 150000  # Leave room for response


def get_encoding():
    """Get the tiktoken encoding for Claude models."""
    # Claude uses cl100k_base encoding (same as GPT-4)
    return tiktoken.get_encoding("cl100k_base")


def count_tokens(text: str) -> int:
    """Count tokens in a text string.

    Args:
        text: The text to count tokens for

    Returns:
        Number of tokens
    """
    encoding = get_encoding()
    return len(encoding.encode(text))


def estimate_cost(input_tokens: int, output_tokens: int = 0) -> float:
    """Estimate API cost based on token counts.

    Args:
        input_tokens: Number of input tokens
        output_tokens: Estimated output tokens (default 0)

    Returns:
        Estimated cost in USD
    """
    input_cost = (input_tokens / 1_000_000) * CLAUDE_INPUT_COST_PER_MILLION
    output_cost = (output_tokens / 1_000_000) * CLAUDE_OUTPUT_COST_PER_MILLION
    return input_cost + output_cost


def format_cost(cost: float) -> str:
    """Format a cost value for display.

    Args:
        cost: Cost in USD

    Returns:
        Formatted string like "$0.15"
    """
    return f"${cost:.2f}"


def parse_gitignore(gitignore_path: Path) -> Set[str]:
    """Parse a .gitignore file and return patterns.

    Args:
        gitignore_path: Path to .gitignore file

    Returns:
        Set of gitignore patterns
    """
    patterns = set()
    if not gitignore_path.exists():
        return patterns

    try:
        with open(gitignore_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                # Skip empty lines and comments
                if not line or line.startswith("#"):
                    continue
                patterns.add(line)
    except (IOError, UnicodeDecodeError):
        pass

    return patterns


def should_ignore(path: Path, patterns: Set[str], root: Path) -> bool:
    """Check if a path should be ignored based on gitignore patterns.

    Args:
        path: Path to check
        patterns: Set of gitignore patterns
        root: Root directory of the project

    Returns:
        True if the path should be ignored
    """
    # Get relative path from root
    try:
        rel_path = path.relative_to(root)
    except ValueError:
        return False

    rel_str = str(rel_path)
    name = path.name

    # Check against always-skip patterns
    for skip in ALWAYS_SKIP:
        if fnmatch.fnmatch(name, skip):
            return True
        if fnmatch.fnmatch(rel_str, skip):
            return True

    # Check against gitignore patterns
    for pattern in patterns:
        # Handle directory patterns (ending with /)
        if pattern.endswith("/"):
            pattern = pattern[:-1]
            if path.is_dir() and fnmatch.fnmatch(name, pattern):
                return True

        # Handle patterns with path separators
        if "/" in pattern:
            if fnmatch.fnmatch(rel_str, pattern):
                return True
            if fnmatch.fnmatch(rel_str, pattern.lstrip("/")):
                return True
        else:
            # Pattern applies to any level
            if fnmatch.fnmatch(name, pattern):
                return True

    return False


def is_binary_file(path: Path) -> bool:
    """Check if a file is binary based on extension and content.

    Args:
        path: Path to the file

    Returns:
        True if the file appears to be binary
    """
    # Check extension
    if path.suffix.lower() in BINARY_EXTENSIONS:
        return True

    # Check content for null bytes
    try:
        with open(path, "rb") as f:
            chunk = f.read(8192)
            if b"\x00" in chunk:
                return True
    except (IOError, OSError):
        return True

    return False


def is_file_too_large(path: Path) -> bool:
    """Check if a file exceeds the maximum size limit.

    Args:
        path: Path to the file

    Returns:
        True if file is larger than MAX_FILE_SIZE
    """
    try:
        return path.stat().st_size > MAX_FILE_SIZE
    except (IOError, OSError):
        return True


def read_file_safely(path: Path) -> Optional[str]:
    """Read a file with proper encoding handling.

    Args:
        path: Path to the file

    Returns:
        File contents as string, or None if unreadable
    """
    encodings = ["utf-8", "utf-8-sig", "latin-1", "cp1252"]

    for encoding in encodings:
        try:
            with open(path, "r", encoding=encoding) as f:
                return f.read()
        except (UnicodeDecodeError, UnicodeError):
            continue
        except (IOError, OSError):
            return None

    return None


def traverse_directory(
    root: Path,
    respect_gitignore: bool = True,
) -> Generator[Path, None, None]:
    """Traverse a directory and yield all text files.

    Args:
        root: Root directory to traverse
        respect_gitignore: Whether to respect .gitignore patterns

    Yields:
        Paths to text files
    """
    root = root.resolve()

    # Parse gitignore if present
    gitignore_patterns = set()
    if respect_gitignore:
        gitignore_patterns = parse_gitignore(root / ".gitignore")

    for dirpath, dirnames, filenames in os.walk(root):
        current = Path(dirpath)

        # Filter out ignored directories (modify in place for os.walk)
        dirnames[:] = [
            d
            for d in dirnames
            if not should_ignore(current / d, gitignore_patterns, root)
        ]

        for filename in filenames:
            filepath = current / filename

            # Skip ignored files
            if should_ignore(filepath, gitignore_patterns, root):
                continue

            # Skip binary files
            if is_binary_file(filepath):
                continue

            yield filepath


def is_github_url(path: str) -> bool:
    """Check if a path is a GitHub URL.

    Args:
        path: The path to check

    Returns:
        True if it's a GitHub URL
    """
    github_patterns = [
        r"^https?://github\.com/[\w-]+/[\w.-]+/?$",
        r"^https?://github\.com/[\w-]+/[\w.-]+\.git$",
        r"^git@github\.com:[\w-]+/[\w.-]+\.git$",
    ]
    return any(re.match(pattern, path) for pattern in github_patterns)


def get_file_extension_info(ext: str) -> str:
    """Get a beginner-friendly description of a file extension.

    Args:
        ext: File extension (e.g., ".py")

    Returns:
        Description of the file type
    """
    extensions = {
        ".py": "Python source file",
        ".js": "JavaScript source file",
        ".ts": "TypeScript source file",
        ".jsx": "React JavaScript component",
        ".tsx": "React TypeScript component",
        ".vue": "Vue.js single-file component",
        ".html": "HTML web page",
        ".css": "Cascading Style Sheet",
        ".scss": "Sass stylesheet",
        ".less": "Less stylesheet",
        ".json": "JSON data file",
        ".yaml": "YAML configuration file",
        ".yml": "YAML configuration file",
        ".toml": "TOML configuration file",
        ".md": "Markdown documentation",
        ".txt": "Plain text file",
        ".sql": "SQL database query",
        ".sh": "Shell script",
        ".bash": "Bash shell script",
        ".zsh": "Zsh shell script",
        ".rb": "Ruby source file",
        ".erb": "Embedded Ruby template",
        ".go": "Go source file",
        ".rs": "Rust source file",
        ".java": "Java source file",
        ".kt": "Kotlin source file",
        ".swift": "Swift source file",
        ".c": "C source file",
        ".cpp": "C++ source file",
        ".h": "C/C++ header file",
        ".hpp": "C++ header file",
        ".cs": "C# source file",
        ".php": "PHP source file",
        ".r": "R source file",
        ".scala": "Scala source file",
        ".ex": "Elixir source file",
        ".exs": "Elixir script file",
        ".erl": "Erlang source file",
        ".hs": "Haskell source file",
        ".lua": "Lua source file",
        ".pl": "Perl source file",
        ".dockerfile": "Docker configuration",
        ".env": "Environment variables file",
        ".gitignore": "Git ignore configuration",
        ".eslintrc": "ESLint configuration",
        ".prettierrc": "Prettier configuration",
    }
    return extensions.get(ext.lower(), f"{ext} file")
