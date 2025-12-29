"""Shared pytest fixtures and test utilities for code-guro tests."""

from pathlib import Path
from unittest.mock import Mock

import pytest

# ============================================================================
# Fixtures for Sample Data
# ============================================================================


@pytest.fixture
def sample_markdown():
    """Sample markdown content with various features for testing HTML conversion."""
    return """# Test Documentation

This is a test document with various markdown features.

## Code Blocks

Here's a Python code block:

```python
def hello_world():
    print("Hello, world!")
```

## Tables

| Feature | Status |
|---------|--------|
| Tables  | ✓      |
| Code    | ✓      |

## Mermaid Diagram

```mermaid
graph TD
    A[Start] --> B[Process]
    B --> C[End]
```

## Lists

- Item 1
- Item 2
- Item 3
"""


@pytest.fixture
def sample_markdown_simple():
    """Simple markdown content for basic tests."""
    return """# Simple Document

This is a simple test document.

Some content here.
"""


@pytest.fixture
def mock_claude_response():
    """Mock Claude API Message object with content."""
    mock_message = Mock()
    mock_content = Mock()
    mock_content.text = "# Generated Documentation\n\nThis is generated content."
    mock_message.content = [mock_content]
    return mock_message


@pytest.fixture
def mock_analysis_result():
    """Mock AnalysisResult dataclass for generator tests."""
    from code_guro.analyzer import AnalysisResult, FileInfo, FrameworkInfo

    files = [
        FileInfo(
            path=Path("main.py"),
            relative_path="main.py",
            content="print('Hello, world!')",
            tokens=50,
            extension=".py",
            is_entry_point=True,
        ),
        FileInfo(
            path=Path("utils.py"),
            relative_path="utils.py",
            content="def helper():\n    pass",
            tokens=30,
            extension=".py",
            is_entry_point=False,
        ),
    ]

    framework = FrameworkInfo(
        name="Flask",
        version="2.0.0",
        description="A lightweight WSGI web application framework",
        architecture="MVC pattern",
        conventions=["Blueprint-based routing", "Jinja2 templates"],
        gotchas=["Debug mode should be disabled in production"],
    )

    return AnalysisResult(
        root=Path("."),
        files=files,
        frameworks=[framework],
        total_tokens=1000,
        estimated_cost=0.01,
        needs_chunking=False,
        chunk_count=1,
        skipped_files=[],
        warnings=[],
    )


@pytest.fixture
def temp_codebase(tmp_path):
    """Create a minimal codebase structure for testing analyze command."""
    # Create a simple Python project structure
    (tmp_path / "main.py").write_text("print('Hello, world!')")
    (tmp_path / "utils.py").write_text("def helper():\n    pass")
    (tmp_path / "README.md").write_text("# Test Project\n\nTest readme")

    # Create a config file
    (tmp_path / "requirements.txt").write_text("flask==2.0.0\n")

    return tmp_path


@pytest.fixture
def mock_anthropic_client(monkeypatch):
    """Mock the Anthropic client to avoid real API calls during tests."""
    mock_client = Mock()
    mock_message = Mock()
    mock_content = Mock()
    mock_content.text = "# Test Documentation\n\nGenerated test content."
    mock_message.content = [mock_content]
    mock_client.messages.create.return_value = mock_message

    # Mock the Anthropic class constructor
    def mock_anthropic_constructor(*args, **kwargs):
        return mock_client

    monkeypatch.setattr("code_guro.generator.anthropic.Anthropic", mock_anthropic_constructor)
    return mock_client


# ============================================================================
# Helper Functions for Assertions
# ============================================================================


def assert_dual_format_structure(output_dir: Path):
    """Verify that output directory has correct dual-format structure.

    Args:
        output_dir: Path to the output directory to check

    Raises:
        AssertionError: If structure doesn't match expected dual-format layout
    """
    assert output_dir.exists(), f"Output directory {output_dir} does not exist"

    markdown_dir = output_dir / "markdown"
    html_dir = output_dir / "html"

    assert markdown_dir.exists(), f"Markdown directory {markdown_dir} does not exist"
    assert html_dir.exists(), f"HTML directory {html_dir} does not exist"
    assert markdown_dir.is_dir(), f"{markdown_dir} is not a directory"
    assert html_dir.is_dir(), f"{html_dir} is not a directory"

    # Verify both directories have files
    md_files = list(markdown_dir.glob("*.md"))
    html_files = list(html_dir.glob("*.html"))

    assert len(md_files) > 0, f"No markdown files found in {markdown_dir}"
    assert len(html_files) > 0, f"No HTML files found in {html_dir}"

    # Verify equal number of files (one HTML for each markdown)
    assert len(md_files) == len(html_files), (
        f"File count mismatch: {len(md_files)} markdown files, " f"{len(html_files)} HTML files"
    )


def assert_html_has_navigation(html_path: Path, expected_files: list = None):
    """Verify HTML file contains navigation links.

    Args:
        html_path: Path to HTML file to check
        expected_files: Optional list of filenames that should appear in navigation

    Raises:
        AssertionError: If navigation is missing or incorrect
    """
    assert html_path.exists(), f"HTML file {html_path} does not exist"

    content = html_path.read_text()

    # Check for navigation element
    assert "<nav>" in content or "<nav " in content, f"No <nav> element found in {html_path.name}"

    # Check for navigation list
    assert "<ul>" in content, f"No navigation list found in {html_path.name}"

    # If specific files are expected, verify they're in the navigation
    if expected_files:
        for filename in expected_files:
            html_filename = filename.replace(".md", ".html")
            assert html_filename in content, (
                f"Expected file {html_filename} not found in navigation " f"of {html_path.name}"
            )


def assert_html_has_mermaid_support(html_content: str):
    """Verify HTML content includes Mermaid.js support.

    Args:
        html_content: HTML content as string

    Raises:
        AssertionError: If Mermaid.js script tag is missing
    """
    # Check for Mermaid CDN script tag
    assert "mermaid" in html_content.lower(), "Mermaid.js script tag not found in HTML"
    assert (
        "cdn.jsdelivr.net" in html_content or "unpkg.com" in html_content
    ), "Mermaid.js CDN link not found in HTML"


def count_files(directory: Path, pattern: str) -> int:
    """Count files matching a glob pattern in a directory.

    Args:
        directory: Directory to search in
        pattern: Glob pattern (e.g., "*.md", "**/*.html")

    Returns:
        Number of matching files
    """
    if not directory.exists():
        return 0
    return len(list(directory.glob(pattern)))


def read_html_content(html_path: Path) -> str:
    """Read and return HTML file content.

    Args:
        html_path: Path to HTML file

    Returns:
        HTML content as string

    Raises:
        FileNotFoundError: If file doesn't exist
    """
    return html_path.read_text(encoding="utf-8")


def create_markdown_files(directory: Path, count: int = 3, prefix: str = "doc"):
    """Create multiple markdown files for testing.

    Args:
        directory: Directory to create files in
        count: Number of files to create
        prefix: Prefix for filenames

    Returns:
        List of created file paths
    """
    directory.mkdir(parents=True, exist_ok=True)
    files = []

    for i in range(count):
        filename = f"{prefix}-{i:02d}.md"
        filepath = directory / filename
        content = f"# Document {i}\n\nThis is document number {i}.\n"
        filepath.write_text(content)
        files.append(filepath)

    return files
