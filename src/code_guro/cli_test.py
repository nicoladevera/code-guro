"""Tests for CLI commands."""

from pathlib import Path

import pytest
from click.testing import CliRunner

from code_guro.analyzer import AnalysisResult
from code_guro.cli import main
from code_guro.conftest import assert_dual_format_structure, create_markdown_files


class TestCLIBasics:
    """Tests for basic CLI functionality."""

    def test_version_option(self):
        """Should display version when --version is used."""
        runner = CliRunner()
        result = runner.invoke(main, ["--version"])

        assert result.exit_code == 0
        assert "code-guro" in result.output.lower() or "version" in result.output.lower()

    def test_help_option(self):
        """Should display help when --help is used."""
        runner = CliRunner()
        result = runner.invoke(main, ["--help"])

        assert result.exit_code == 0
        assert "analyze" in result.output.lower()
        assert "convert" in result.output.lower()


class TestAnalyzeCommand:
    """Tests for the analyze command."""

    @pytest.fixture
    def mock_dependencies(self, monkeypatch, mock_analysis_result):
        """Mock all external dependencies for analyze command."""
        # Mock API key check
        monkeypatch.setattr("code_guro.cli.require_api_key", lambda: "fake-api-key")

        # Mock internet connection check
        monkeypatch.setattr("code_guro.cli.check_internet_connection", lambda: True)

        # Mock analyze_codebase to return test data (imported within the function)
        monkeypatch.setattr(
            "code_guro.analyzer.analyze_codebase", lambda path: mock_analysis_result
        )

        # Mock confirm_analysis to always return True
        monkeypatch.setattr("code_guro.analyzer.confirm_analysis", lambda result: True)

        # Mock is_github_url to return False (test local paths)
        monkeypatch.setattr("code_guro.utils.is_github_url", lambda path: False)

    def test_analyze_default_creates_dual_format(
        self, tmp_path, mock_dependencies, mock_anthropic_client
    ):
        """Should create dual-format structure (markdown/ and html/) by default."""
        runner = CliRunner()

        with runner.isolated_filesystem(temp_dir=tmp_path):
            # Create a simple codebase
            (Path.cwd() / "main.py").write_text("print('test')")

            # Run analyze command without --markdown-only flag
            result = runner.invoke(main, ["analyze", "."])

            # Command should succeed
            assert result.exit_code == 0, f"Error: {result.output}"

            # Verify dual-format structure created
            output_dir = Path.cwd() / "code-guro-output"
            assert output_dir.exists()

            markdown_dir = output_dir / "markdown"
            html_dir = output_dir / "html"

            assert markdown_dir.exists()
            assert html_dir.exists()

            # Verify files were created
            md_files = list(markdown_dir.glob("*.md"))
            html_files = list(html_dir.glob("*.html"))

            assert len(md_files) > 0, "No markdown files were created"
            assert len(html_files) > 0, "No HTML files were created"
            assert len(md_files) == len(
                html_files
            ), f"File count mismatch: {len(md_files)} markdown, {len(html_files)} HTML"

    def test_analyze_markdown_only_flag(self, tmp_path, mock_dependencies, mock_anthropic_client):
        """Should create flat structure with only markdown files when --markdown-only is used."""
        runner = CliRunner()

        with runner.isolated_filesystem(temp_dir=tmp_path):
            # Create a simple codebase
            (Path.cwd() / "main.py").write_text("print('test')")

            # Run analyze with --markdown-only flag
            result = runner.invoke(main, ["analyze", ".", "--markdown-only"])

            # Command should succeed
            assert result.exit_code == 0, f"Error: {result.output}"

            # Verify flat structure created
            output_dir = Path.cwd() / "code-guro-output"
            assert output_dir.exists()

            # Should NOT have subdirectories
            markdown_dir = output_dir / "markdown"
            html_dir = output_dir / "html"
            assert not markdown_dir.exists(), "markdown/ subdirectory should not exist"
            assert not html_dir.exists(), "html/ subdirectory should not exist"

            # Markdown files should be in root of output_dir
            md_files = list(output_dir.glob("*.md"))
            html_files = list(output_dir.glob("*.html"))

            assert len(md_files) > 0, "No markdown files were created"
            assert len(html_files) == 0, "HTML files should not be created with --markdown-only"

    def test_analyze_directory_structure_dual_format(
        self, tmp_path, mock_dependencies, mock_anthropic_client
    ):
        """Should create proper directory structure for dual-format output."""
        runner = CliRunner()

        with runner.isolated_filesystem(temp_dir=tmp_path):
            (Path.cwd() / "main.py").write_text("print('test')")

            result = runner.invoke(main, ["analyze", "."])
            assert result.exit_code == 0

            output_dir = Path.cwd() / "code-guro-output"

            # Use helper function to verify structure
            assert_dual_format_structure(output_dir)

    def test_analyze_directory_structure_markdown_only(
        self, tmp_path, mock_dependencies, mock_anthropic_client
    ):
        """Should create flat directory structure for markdown-only output."""
        runner = CliRunner()

        with runner.isolated_filesystem(temp_dir=tmp_path):
            (Path.cwd() / "main.py").write_text("print('test')")

            result = runner.invoke(main, ["analyze", ".", "--markdown-only"])
            assert result.exit_code == 0

            output_dir = Path.cwd() / "code-guro-output"
            assert output_dir.exists()
            assert output_dir.is_dir()

            # Files should be in root
            md_files = list(output_dir.glob("*.md"))
            assert len(md_files) > 0

            # No subdirectories should exist
            subdirs = [d for d in output_dir.iterdir() if d.is_dir()]
            assert len(subdirs) == 0, f"Found unexpected subdirectories: {subdirs}"

    def test_analyze_nonexistent_directory(self, mock_dependencies):
        """Should handle nonexistent directory with proper error message."""
        runner = CliRunner()

        # Try to analyze a directory that doesn't exist
        result = runner.invoke(main, ["analyze", "/nonexistent/path/to/directory"])

        # Should fail with exit code 1
        assert result.exit_code == 1

        # Should have helpful error message
        assert "Error" in result.output or "not found" in result.output.lower()

    def test_analyze_file_instead_of_directory(self, tmp_path, mock_dependencies):
        """Should handle file path instead of directory."""
        runner = CliRunner()

        with runner.isolated_filesystem(temp_dir=tmp_path):
            # Create a file instead of directory
            (Path.cwd() / "test.txt").write_text("test")

            result = runner.invoke(main, ["analyze", "test.txt"])

            # Should fail
            assert result.exit_code == 1
            assert "not a directory" in result.output.lower() or "error" in result.output.lower()

    def test_analyze_with_no_files(self, tmp_path, mock_dependencies, monkeypatch):
        """Should handle directory with no analyzable files."""
        runner = CliRunner()

        # Mock analyze_codebase to return empty result
        empty_result = AnalysisResult(
            root=Path("."),
            files=[],  # No files
            frameworks=[],
            total_tokens=0,
            estimated_cost=0.0,
            needs_chunking=False,
            chunk_count=1,
            skipped_files=[],
            warnings=[],
        )
        monkeypatch.setattr("code_guro.analyzer.analyze_codebase", lambda path: empty_result)

        with runner.isolated_filesystem(temp_dir=tmp_path):
            (Path.cwd() / "test.txt").write_text("test")

            result = runner.invoke(main, ["analyze", "."])

            # Should fail with warning about no files
            assert result.exit_code == 1
            assert "no" in result.output.lower() and (
                "file" in result.output.lower() or "warning" in result.output.lower()
            )

    def test_analyze_with_api_exception(self, tmp_path, mock_dependencies, monkeypatch):
        """Should handle API exceptions gracefully."""
        runner = CliRunner()

        # Mock generate_documentation to raise an exception (imported inside function)
        def mock_generate_error(result, markdown_only=False):
            raise Exception("API Error: Rate limit exceeded")

        monkeypatch.setattr("code_guro.generator.generate_documentation", mock_generate_error)

        with runner.isolated_filesystem(temp_dir=tmp_path):
            (Path.cwd() / "main.py").write_text("print('test')")

            result = runner.invoke(main, ["analyze", "."])

            # Should handle error gracefully
            assert result.exit_code == 1

    def test_analyze_user_cancels_confirmation(self, tmp_path, mock_dependencies, monkeypatch):
        """Should exit gracefully when user cancels analysis confirmation."""
        runner = CliRunner()

        # Mock confirm_analysis to return False (user cancels)
        monkeypatch.setattr("code_guro.analyzer.confirm_analysis", lambda result: False)

        with runner.isolated_filesystem(temp_dir=tmp_path):
            (Path.cwd() / "main.py").write_text("print('test')")

            result = runner.invoke(main, ["analyze", "."])

            # Should exit with 0 (user choice, not error)
            assert result.exit_code == 0
            assert "cancelled" in result.output.lower() or "cancel" in result.output.lower()


class TestConvertCommand:
    """Tests for the convert command."""

    def test_convert_reorganizes_markdown_to_subdirectory(self, tmp_path):
        """Should move markdown files to markdown/ subdirectory."""
        runner = CliRunner()

        with runner.isolated_filesystem(temp_dir=tmp_path):
            # Create output directory with markdown files
            output_dir = Path.cwd() / "code-guro-output"
            output_dir.mkdir()

            # Create markdown files in root
            create_markdown_files(output_dir, count=3)

            # Run convert command
            result = runner.invoke(main, ["convert", str(output_dir)])

            # Command should succeed
            assert result.exit_code == 0, f"Error: {result.output}"

            # Verify markdown files moved to subdirectory
            markdown_dir = output_dir / "markdown"
            assert markdown_dir.exists()

            md_files = list(markdown_dir.glob("*.md"))
            assert len(md_files) == 3

            # No markdown files should remain in root
            root_md_files = list(output_dir.glob("*.md"))
            assert len(root_md_files) == 0

    def test_convert_generates_html_in_subdirectory(self, tmp_path):
        """Should generate HTML files in html/ subdirectory."""
        runner = CliRunner()

        with runner.isolated_filesystem(temp_dir=tmp_path):
            # Create output directory with markdown files
            output_dir = Path.cwd() / "code-guro-output"
            output_dir.mkdir()

            create_markdown_files(output_dir, count=3)

            # Run convert command
            result = runner.invoke(main, ["convert", str(output_dir)])

            assert result.exit_code == 0

            # Verify HTML files created
            html_dir = output_dir / "html"
            assert html_dir.exists()

            html_files = list(html_dir.glob("*.html"))
            assert len(html_files) == 3

            # Verify HTML file names match markdown
            for html_file in html_files:
                assert html_file.name.startswith("doc-")
                assert html_file.suffix == ".html"

    def test_convert_preserves_markdown_content(self, tmp_path):
        """Should preserve original markdown content during conversion."""
        runner = CliRunner()

        with runner.isolated_filesystem(temp_dir=tmp_path):
            output_dir = Path.cwd() / "code-guro-output"
            output_dir.mkdir()

            # Create markdown files and store their content
            md_files = create_markdown_files(output_dir, count=2)
            original_content = {f.name: f.read_text() for f in md_files}

            # Run convert
            result = runner.invoke(main, ["convert", str(output_dir)])
            assert result.exit_code == 0

            # Verify content preserved in new location
            markdown_dir = output_dir / "markdown"
            for filename, content in original_content.items():
                moved_file = markdown_dir / filename
                assert moved_file.exists()
                assert moved_file.read_text() == content

    def test_convert_on_nonexistent_directory(self):
        """Should handle nonexistent directory with proper error."""
        runner = CliRunner()

        result = runner.invoke(main, ["convert", "/nonexistent/directory"])

        # Should fail
        assert result.exit_code == 1

        # Should have error message
        assert "Error" in result.output or "not found" in result.output.lower()

    def test_convert_on_directory_without_markdown(self, tmp_path):
        """Should handle directory with no markdown files gracefully."""
        runner = CliRunner()

        with runner.isolated_filesystem(temp_dir=tmp_path):
            # Create empty output directory
            output_dir = Path.cwd() / "empty-output"
            output_dir.mkdir()

            # Add a non-markdown file
            (output_dir / "readme.txt").write_text("Not a markdown file")

            result = runner.invoke(main, ["convert", str(output_dir)])

            # Should fail or warn
            assert result.exit_code == 1

            # Should mention no markdown files
            assert "markdown" in result.output.lower() or "no" in result.output.lower()

    def test_convert_on_file_instead_of_directory(self, tmp_path):
        """Should handle file path instead of directory."""
        runner = CliRunner()

        with runner.isolated_filesystem(temp_dir=tmp_path):
            # Create a file instead of directory
            (Path.cwd() / "test.md").write_text("# Test")

            result = runner.invoke(main, ["convert", "test.md"])

            # Should fail
            assert result.exit_code == 1
            assert "not a directory" in result.output.lower() or "error" in result.output.lower()

    def test_convert_with_exception_during_conversion(self, tmp_path, monkeypatch):
        """Should handle exceptions during conversion gracefully."""
        runner = CliRunner()

        # Mock convert_directory_to_html_organized to raise an exception (imported inside function)
        def mock_convert_error(markdown_dir, html_dir):
            raise Exception("Conversion error")

        monkeypatch.setattr(
            "code_guro.html_converter.convert_directory_to_html_organized", mock_convert_error
        )

        with runner.isolated_filesystem(temp_dir=tmp_path):
            output_dir = Path.cwd() / "code-guro-output"
            output_dir.mkdir()
            create_markdown_files(output_dir, count=1)

            result = runner.invoke(main, ["convert", str(output_dir)])

            # Should handle error gracefully
            assert result.exit_code == 1
            assert "error" in result.output.lower()


class TestConfigureCommand:
    """Tests for the configure command."""

    def test_configure_with_valid_api_key(self, tmp_path, monkeypatch):
        """Should save API key when valid key is provided."""
        runner = CliRunner()

        # Mock the validation and save functions (validate_api_key returns tuple)
        monkeypatch.setattr("code_guro.cli.validate_api_key", lambda key: (True, "Valid"))
        monkeypatch.setattr("code_guro.cli.save_api_key", lambda key: None)
        monkeypatch.setattr("code_guro.cli.is_api_key_configured", lambda: False)

        # Simulate user input
        result = runner.invoke(main, ["configure"], input="sk-test-key\n")

        # Should succeed
        assert result.exit_code == 0
        assert "saved successfully" in result.output.lower() or "success" in result.output.lower()

    def test_configure_with_invalid_api_key(self, monkeypatch):
        """Should reject invalid API key."""
        runner = CliRunner()

        # Mock validation to fail (returns tuple)
        monkeypatch.setattr(
            "code_guro.cli.validate_api_key", lambda key: (False, "Invalid API key")
        )
        monkeypatch.setattr("code_guro.cli.is_api_key_configured", lambda: False)

        result = runner.invoke(main, ["configure"], input="invalid-key\n")

        # Should fail with error
        assert result.exit_code == 1
        assert "invalid" in result.output.lower() or "error" in result.output.lower()


class TestExplainCommand:
    """Tests for the explain command."""

    def test_explain_nonexistent_file(self, monkeypatch):
        """Should handle nonexistent file gracefully."""
        runner = CliRunner()

        # Mock the decorators
        monkeypatch.setattr("code_guro.cli.require_api_key", lambda: "fake-key")
        monkeypatch.setattr("code_guro.cli.check_internet_connection", lambda: True)

        result = runner.invoke(main, ["explain", "/nonexistent/file.py"])

        # Should fail with error (file doesn't exist) - exit code 1 or 2
        assert result.exit_code in [1, 2]

    def test_explain_requires_api_key(self, tmp_path, monkeypatch):
        """Should require API key before running explain."""
        runner = CliRunner()

        # Mock API key check to return None (no key)
        monkeypatch.setattr("code_guro.cli.require_api_key", lambda: None)

        with runner.isolated_filesystem(temp_dir=tmp_path):
            (Path.cwd() / "test.py").write_text("print('test')")

            result = runner.invoke(main, ["explain", "test.py"])

            # Should exit due to missing API key
            assert result.exit_code == 1
