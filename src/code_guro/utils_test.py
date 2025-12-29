"""Tests for utils module."""

import tempfile
from pathlib import Path

import pytest

from code_guro.utils import (
    BINARY_EXTENSIONS,
    count_tokens,
    estimate_cost,
    format_cost,
    get_file_extension_info,
    is_binary_file,
    is_file_too_large,
    is_github_url,
    parse_gitignore,
    read_file_safely,
    should_ignore,
)


class TestTokenCounting:
    """Tests for token counting functions."""

    def test_count_tokens_empty(self):
        """Empty string should have 0 tokens."""
        assert count_tokens("") == 0

    def test_count_tokens_simple(self):
        """Simple text should return reasonable token count."""
        result = count_tokens("Hello world")
        assert result > 0
        assert result < 10  # Should be a small number

    def test_count_tokens_code(self):
        """Code should be tokenized."""
        code = "def hello():\n    return 'world'"
        result = count_tokens(code)
        assert result > 0


class TestCostEstimation:
    """Tests for cost estimation functions."""

    def test_estimate_cost_zero(self):
        """Zero tokens should cost $0."""
        result = estimate_cost(0, 0)
        assert result == 0.0

    def test_estimate_cost_input_only(self):
        """Should calculate cost for input tokens."""
        result = estimate_cost(1_000_000)  # 1M tokens
        assert result == 3.0  # $3 per million

    def test_estimate_cost_with_output(self):
        """Should calculate cost for input and output."""
        result = estimate_cost(1_000_000, 1_000_000)
        assert result == 18.0  # $3 input + $15 output

    def test_format_cost(self):
        """Should format cost as currency."""
        assert format_cost(1.5) == "$1.50"
        assert format_cost(0.05) == "$0.05"
        assert format_cost(10.0) == "$10.00"


class TestGitignoreParsing:
    """Tests for gitignore parsing."""

    def test_parse_gitignore_empty(self):
        """Non-existent file should return empty set."""
        result = parse_gitignore(Path("/nonexistent/.gitignore"))
        assert result == set()

    def test_parse_gitignore_with_patterns(self):
        """Should parse patterns from gitignore."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".gitignore", delete=False) as f:
            f.write("node_modules\n")
            f.write("*.pyc\n")
            f.write("# comment\n")
            f.write("\n")
            f.write("dist/\n")
            f.flush()

            result = parse_gitignore(Path(f.name))

            assert "node_modules" in result
            assert "*.pyc" in result
            assert "dist/" in result
            assert "# comment" not in result

            Path(f.name).unlink()


class TestShouldIgnore:
    """Tests for ignore pattern matching."""

    def test_should_ignore_node_modules(self):
        """Should ignore node_modules directory itself."""
        root = Path("/project")
        path = Path("/project/node_modules")
        result = should_ignore(path, set(), root)
        assert result is True

    def test_should_ignore_pycache(self):
        """Should ignore __pycache__."""
        root = Path("/project")
        path = Path("/project/__pycache__")
        result = should_ignore(path, set(), root)
        assert result is True

    def test_should_not_ignore_src(self):
        """Should not ignore src directory."""
        root = Path("/project")
        path = Path("/project/src")
        result = should_ignore(path, set(), root)
        assert result is False


class TestBinaryFileDetection:
    """Tests for binary file detection."""

    def test_binary_extensions(self):
        """Should detect common binary extensions."""
        assert ".png" in BINARY_EXTENSIONS
        assert ".jpg" in BINARY_EXTENSIONS
        assert ".exe" in BINARY_EXTENSIONS
        assert ".pdf" in BINARY_EXTENSIONS

    def test_is_binary_file_by_extension(self):
        """Should detect binary by extension."""
        with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as f:
            f.write(b"fake image content")
            result = is_binary_file(Path(f.name))
            assert result is True
            Path(f.name).unlink()


class TestFileTooLarge:
    """Tests for file size checking."""

    def test_is_file_too_large_small(self):
        """Small files should not be too large."""
        with tempfile.NamedTemporaryFile(mode="w", delete=False) as f:
            f.write("small content")
            result = is_file_too_large(Path(f.name))
            assert result is False
            Path(f.name).unlink()

    def test_is_file_too_large_nonexistent(self):
        """Non-existent files should be considered too large (error case)."""
        result = is_file_too_large(Path("/nonexistent/file"))
        assert result is True


class TestReadFileSafely:
    """Tests for safe file reading."""

    def test_read_file_safely_utf8(self):
        """Should read UTF-8 files."""
        with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8", delete=False) as f:
            f.write("Hello, 世界!")
            f.flush()
            result = read_file_safely(Path(f.name))
            assert result == "Hello, 世界!"
            Path(f.name).unlink()

    def test_read_file_safely_nonexistent(self):
        """Should return None for non-existent files."""
        result = read_file_safely(Path("/nonexistent/file.txt"))
        assert result is None


class TestGitHubUrl:
    """Tests for GitHub URL detection."""

    def test_is_github_url_https(self):
        """Should detect HTTPS GitHub URLs."""
        assert is_github_url("https://github.com/user/repo") is True
        assert is_github_url("https://github.com/user/repo.git") is True

    def test_is_github_url_ssh(self):
        """Should detect SSH GitHub URLs."""
        assert is_github_url("git@github.com:user/repo.git") is True

    def test_is_github_url_not_github(self):
        """Should reject non-GitHub URLs."""
        assert is_github_url("https://gitlab.com/user/repo") is False
        assert is_github_url("/local/path") is False
        assert is_github_url("./relative/path") is False


class TestFileExtensionInfo:
    """Tests for file extension descriptions."""

    def test_known_extensions(self):
        """Should return descriptions for known extensions."""
        assert "Python" in get_file_extension_info(".py")
        assert "JavaScript" in get_file_extension_info(".js")
        assert "TypeScript" in get_file_extension_info(".ts")

    def test_unknown_extension(self):
        """Should return generic description for unknown extensions."""
        result = get_file_extension_info(".xyz")
        assert ".xyz file" in result
