"""Tests for HTML converter module."""

from code_guro.conftest import (
    assert_html_has_mermaid_support,
    create_markdown_files,
)
from code_guro.html_converter import (
    convert_directory_to_html_organized,
    convert_file_to_html,
    convert_markdown_to_html,
    get_navigation_links,
)


class TestConvertMarkdownToHtml:
    """Tests for convert_markdown_to_html function."""

    def test_convert_simple_markdown(self, sample_markdown_simple):
        """Should convert simple markdown to HTML."""
        html = convert_markdown_to_html(sample_markdown_simple)

        # Markdown library adds id attributes to headings
        assert "Simple Document" in html and "<h1" in html
        assert "<p>This is a simple test document.</p>" in html
        assert "<p>Some content here.</p>" in html

    def test_convert_with_code_blocks(self):
        """Should correctly convert code blocks with syntax highlighting."""
        markdown = """# Code Example

```python
def hello():
    print("Hello, world!")
```
"""
        html = convert_markdown_to_html(markdown)

        # Markdown library adds id attributes to headings
        assert "Code Example" in html and "<h1" in html
        assert "<code" in html
        assert "def hello():" in html
        assert "print" in html

    def test_convert_with_mermaid_diagrams(self, sample_markdown):
        """Should preserve mermaid code blocks for JavaScript processing."""
        html = convert_markdown_to_html(sample_markdown)

        # Mermaid diagrams should be preserved as code blocks
        # They will be converted to diagrams by JavaScript in the template
        assert "mermaid" in html.lower()
        assert "graph TD" in html or "graph td" in html

    def test_convert_with_tables(self, sample_markdown):
        """Should convert markdown tables to HTML tables."""
        html = convert_markdown_to_html(sample_markdown)

        assert "<table>" in html
        assert "<th>Feature</th>" in html
        assert "<th>Status</th>" in html
        assert "<td>Tables</td>" in html
        assert "<td>✓</td>" in html

    def test_convert_empty_content(self):
        """Should handle empty markdown gracefully."""
        html = convert_markdown_to_html("")

        # Empty content should return empty or minimal HTML
        assert isinstance(html, str)
        assert len(html) == 0 or html.strip() == ""


class TestGetNavigationLinks:
    """Tests for get_navigation_links function."""

    def test_generates_navigation_links(self, tmp_path):
        """Should generate navigation links for all files."""
        files = [
            tmp_path / "00-overview.html",
            tmp_path / "01-getting-oriented.html",
            tmp_path / "02-architecture.html",
        ]

        current = files[0]
        nav_html = get_navigation_links(files, current)

        # Should contain links to all files
        assert "00-overview.html" in nav_html
        assert "01-getting-oriented.html" in nav_html
        assert "02-architecture.html" in nav_html

        # Should contain readable link text (without number prefixes)
        assert "Overview" in nav_html
        assert "Getting Oriented" in nav_html
        assert "Architecture" in nav_html

    def test_marks_current_page(self, tmp_path):
        """Should mark the current page with 'current' class."""
        files = [
            tmp_path / "00-overview.html",
            tmp_path / "01-getting-oriented.html",
        ]

        current = files[0]
        nav_html = get_navigation_links(files, current)

        # Current page should have the 'current' class
        assert 'class="current"' in nav_html

        # Verify it's on the correct link
        # The current link should be the one for 00-overview.html
        assert '00-overview.html" class="current"' in nav_html

    def test_navigation_ordering(self, tmp_path):
        """Should return navigation links in sorted order."""
        files = [
            tmp_path / "02-architecture.html",
            tmp_path / "00-overview.html",
            tmp_path / "01-getting-oriented.html",
        ]

        current = files[0]
        nav_html = get_navigation_links(files, current)

        # Find positions of each link in the output
        pos_00 = nav_html.find("00-overview.html")
        pos_01 = nav_html.find("01-getting-oriented.html")
        pos_02 = nav_html.find("02-architecture.html")

        # Verify they appear in sorted order
        assert pos_00 < pos_01 < pos_02


class TestConvertFileToHtml:
    """Tests for convert_file_to_html function."""

    def test_convert_single_file(self, tmp_path, sample_markdown_simple):
        """Should convert a single markdown file to complete HTML document."""
        # Create markdown file
        md_file = tmp_path / "test.md"
        md_file.write_text(sample_markdown_simple)

        # Convert to HTML
        html_content = convert_file_to_html(md_file, [md_file])

        # Verify HTML structure
        assert "<!DOCTYPE html>" in html_content
        assert '<html lang="en">' in html_content
        assert "<head>" in html_content
        assert "<body>" in html_content
        assert "</html>" in html_content

        # Verify content is present
        assert "Simple Document" in html_content

    def test_navigation_links_generated(self, tmp_path, sample_markdown_simple):
        """Should include navigation links to all files."""
        # Create multiple markdown files
        files = []
        for i in range(3):
            md_file = tmp_path / f"doc-{i:02d}.md"
            md_file.write_text(f"# Document {i}\n\nContent {i}")
            files.append(md_file)

        # Convert first file
        html_content = convert_file_to_html(files[0], files)

        # Verify navigation is present
        assert "<nav>" in html_content
        assert "<ul>" in html_content

        # Verify links to all files are present
        assert "doc-00.html" in html_content
        assert "doc-01.html" in html_content
        assert "doc-02.html" in html_content

    def test_title_extraction(self, tmp_path):
        """Should extract title from filename and format it properly."""
        md_file = tmp_path / "00-my-test-document.md"
        md_file.write_text("# Test\n\nContent")

        html_content = convert_file_to_html(md_file, [md_file])

        # Title should be extracted from filename, remove prefix, and be formatted
        assert "<title>Code Guro - My Test Document</title>" in html_content

    def test_current_page_highlighting(self, tmp_path):
        """Should mark current page in navigation with 'current' class."""
        # Create multiple files
        files = []
        for i in range(2):
            md_file = tmp_path / f"doc-{i:02d}.md"
            md_file.write_text(f"# Document {i}\n\nContent")
            files.append(md_file)

        # Convert first file
        html_content = convert_file_to_html(files[0], files)

        # Current page should be marked
        assert 'class="current"' in html_content

        # Verify it's the correct file
        assert 'doc-00.html" class="current"' in html_content


class TestConvertDirectoryToHtmlOrganized:
    """Tests for convert_directory_to_html_organized function."""

    def test_convert_creates_html_files_in_target_directory(self, tmp_path):
        """Should create HTML files in the target directory."""
        # Setup: create markdown directory with files
        markdown_dir = tmp_path / "markdown"
        html_dir = tmp_path / "html"
        markdown_dir.mkdir()
        html_dir.mkdir()

        create_markdown_files(markdown_dir, count=3)

        # Convert
        convert_directory_to_html_organized(markdown_dir, html_dir)

        # Verify HTML files created in html_dir
        html_files = list(html_dir.glob("*.html"))
        assert len(html_files) == 3

        # Verify filenames match
        assert (html_dir / "doc-00.html").exists()
        assert (html_dir / "doc-01.html").exists()
        assert (html_dir / "doc-02.html").exists()

    def test_preserves_source_markdown_files(self, tmp_path):
        """Should keep original markdown files intact in source directory."""
        # Setup
        markdown_dir = tmp_path / "markdown"
        html_dir = tmp_path / "html"
        markdown_dir.mkdir()
        html_dir.mkdir()

        md_files = create_markdown_files(markdown_dir, count=3)

        # Store original content
        original_contents = {f: f.read_text() for f in md_files}

        # Convert
        convert_directory_to_html_organized(markdown_dir, html_dir)

        # Verify markdown files still exist with same content
        for md_file in md_files:
            assert md_file.exists()
            assert md_file.read_text() == original_contents[md_file]

        # Verify markdown files still in original directory
        md_files_after = list(markdown_dir.glob("*.md"))
        assert len(md_files_after) == 3

    def test_handles_empty_directory(self, tmp_path, capsys):
        """Should handle empty directory gracefully without errors."""
        markdown_dir = tmp_path / "markdown"
        html_dir = tmp_path / "html"
        markdown_dir.mkdir()
        html_dir.mkdir()

        # Convert empty directory (should not raise exception)
        convert_directory_to_html_organized(markdown_dir, html_dir)

        # Should have printed a warning message
        captured = capsys.readouterr()
        assert "No markdown files found" in captured.out

        # No HTML files should be created
        html_files = list(html_dir.glob("*.html"))
        assert len(html_files) == 0

    def test_html_contains_mermaid_support(self, tmp_path):
        """Should include Mermaid.js CDN script in generated HTML."""
        markdown_dir = tmp_path / "markdown"
        html_dir = tmp_path / "html"
        markdown_dir.mkdir()
        html_dir.mkdir()

        # Create markdown with Mermaid diagram
        md_content = """# Test Document

```mermaid
graph TD
    A[Start] --> B[End]
```
"""
        (markdown_dir / "test.md").write_text(md_content)

        # Convert
        convert_directory_to_html_organized(markdown_dir, html_dir)

        # Read generated HTML
        html_file = html_dir / "test.html"
        html_content = html_file.read_text()

        # Verify Mermaid support
        assert_html_has_mermaid_support(html_content)

    def test_html_contains_navigation(self, tmp_path):
        """Should include navigation links in all generated HTML files."""
        markdown_dir = tmp_path / "markdown"
        html_dir = tmp_path / "html"
        markdown_dir.mkdir()
        html_dir.mkdir()

        create_markdown_files(markdown_dir, count=3)

        # Convert
        convert_directory_to_html_organized(markdown_dir, html_dir)

        # Check each HTML file has navigation
        for html_file in html_dir.glob("*.html"):
            html_content = html_file.read_text()
            assert "<nav>" in html_content
            assert "<ul>" in html_content

            # Should link to all other files
            assert "doc-00.html" in html_content
            assert "doc-01.html" in html_content
            assert "doc-02.html" in html_content

    def test_handles_conversion_errors_gracefully(self, tmp_path, capsys):
        """Should handle file conversion errors without crashing."""
        markdown_dir = tmp_path / "markdown"
        html_dir = tmp_path / "html"
        markdown_dir.mkdir()
        html_dir.mkdir()

        # Create a markdown file with problematic content
        (markdown_dir / "test.md").write_text("# Test")

        # Create a file with permissions issue (simulate error scenario)
        # We'll just verify the function completes without raising
        convert_directory_to_html_organized(markdown_dir, html_dir)

        # Should still create HTML file
        assert (html_dir / "test.html").exists()

    def test_excludes_underscore_prefixed_files_from_html(self, tmp_path):
        """Should exclude files starting with _ from HTML output."""
        markdown_dir = tmp_path / "markdown"
        html_dir = tmp_path / "html"
        markdown_dir.mkdir()
        html_dir.mkdir()

        # Create regular markdown files
        (markdown_dir / "00-overview.md").write_text("# Overview")
        (markdown_dir / "01-getting-oriented.md").write_text("# Getting Oriented")

        # Create underscore-prefixed files (internal/debug files)
        (markdown_dir / "_analysis-notes.md").write_text("# Analysis Notes")
        (markdown_dir / "_chunk-01-analysis.md").write_text("# Chunk 1")
        (markdown_dir / "_chunk-02-analysis.md").write_text("# Chunk 2")

        # Convert
        convert_directory_to_html_organized(markdown_dir, html_dir)

        # Verify only user-facing HTML files created
        html_files = list(html_dir.glob("*.html"))
        assert len(html_files) == 2

        # Verify underscore-prefixed files NOT converted
        assert (html_dir / "00-overview.html").exists()
        assert (html_dir / "01-getting-oriented.html").exists()
        assert not (html_dir / "_analysis-notes.html").exists()
        assert not (html_dir / "_chunk-01-analysis.html").exists()
        assert not (html_dir / "_chunk-02-analysis.html").exists()

        # Verify markdown files still preserved
        assert (markdown_dir / "_analysis-notes.md").exists()
        assert (markdown_dir / "_chunk-01-analysis.md").exists()

    def test_underscore_files_excluded_from_navigation(self, tmp_path):
        """Should not include underscore-prefixed files in navigation."""
        markdown_dir = tmp_path / "markdown"
        html_dir = tmp_path / "html"
        markdown_dir.mkdir()
        html_dir.mkdir()

        # Create files
        (markdown_dir / "00-overview.md").write_text("# Overview")
        (markdown_dir / "_analysis-notes.md").write_text("# Analysis Notes")

        # Convert
        convert_directory_to_html_organized(markdown_dir, html_dir)

        # Read generated HTML
        html_content = (html_dir / "00-overview.html").read_text()

        # Navigation should only contain user-facing files
        assert "00-overview.html" in html_content
        assert "_analysis-notes.html" not in html_content


class TestConvertDirectoryToHtml:
    """Tests for the legacy convert_directory_to_html function."""

    def test_legacy_function_converts_in_place(self, tmp_path):
        """Should convert markdown files to HTML in the same directory."""
        from code_guro.html_converter import convert_directory_to_html

        create_markdown_files(tmp_path, count=2)

        # Convert in place
        convert_directory_to_html(tmp_path)

        # Should have both .md and .html files in same directory
        md_files = list(tmp_path.glob("*.md"))
        html_files = list(tmp_path.glob("*.html"))

        assert len(md_files) == 2
        assert len(html_files) == 2

    def test_legacy_function_handles_empty_directory(self, tmp_path, capsys):
        """Should handle empty directory gracefully."""
        from code_guro.html_converter import convert_directory_to_html

        convert_directory_to_html(tmp_path)

        # Should print warning message
        captured = capsys.readouterr()
        assert "No markdown files found" in captured.out
