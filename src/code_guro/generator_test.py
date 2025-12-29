"""Tests for documentation generator module."""

from pathlib import Path
from unittest.mock import patch

from code_guro.conftest import assert_dual_format_structure
from code_guro.generator import generate_documentation


class TestGenerateDocumentation:
    """Tests for generate_documentation function."""

    def test_markdown_only_mode_creates_flat_structure(
        self, tmp_path, mock_analysis_result, mock_anthropic_client
    ):
        """Should create flat directory structure when markdown_only=True."""
        # Change root to tmp_path
        mock_analysis_result.root = tmp_path

        # Generate documentation in markdown-only mode
        output_dir = generate_documentation(mock_analysis_result, markdown_only=True)

        # Verify output directory created
        assert output_dir.exists()
        assert output_dir.is_dir()

        # Should NOT have subdirectories for markdown and HTML
        markdown_subdir = output_dir / "markdown"
        html_subdir = output_dir / "html"
        assert not markdown_subdir.exists()
        assert not html_subdir.exists()

        # Markdown files should be in root of output_dir
        md_files = list(output_dir.glob("*.md"))
        assert len(md_files) > 0, "No markdown files were created"

        # No HTML files should exist
        html_files = list(output_dir.glob("*.html"))
        assert len(html_files) == 0, "HTML files should not be created in markdown-only mode"

    def test_dual_format_mode_creates_subdirectories(
        self, tmp_path, mock_analysis_result, mock_anthropic_client
    ):
        """Should create markdown/ and html/ subdirectories when markdown_only=False."""
        # Change root to tmp_path
        mock_analysis_result.root = tmp_path

        # Generate documentation in dual-format mode (default)
        output_dir = generate_documentation(mock_analysis_result, markdown_only=False)

        # Verify subdirectories exist
        markdown_dir = output_dir / "markdown"
        html_dir = output_dir / "html"

        assert markdown_dir.exists()
        assert markdown_dir.is_dir()
        assert html_dir.exists()
        assert html_dir.is_dir()

        # Verify files in subdirectories
        md_files = list(markdown_dir.glob("*.md"))
        html_files = list(html_dir.glob("*.html"))

        assert len(md_files) > 0, "No markdown files in markdown/ directory"
        assert len(html_files) > 0, "No HTML files in html/ directory"

        # Verify equal counts
        assert len(md_files) == len(
            html_files
        ), f"File count mismatch: {len(md_files)} markdown, {len(html_files)} HTML"

    def test_dual_format_calls_html_converter(
        self, tmp_path, mock_analysis_result, mock_anthropic_client
    ):
        """Should call HTML converter when markdown_only=False."""
        mock_analysis_result.root = tmp_path

        # Patch the HTML converter at its source (imported inside the function)
        with patch(
            "code_guro.html_converter.convert_directory_to_html_organized"
        ) as mock_converter:
            output_dir = generate_documentation(mock_analysis_result, markdown_only=False)

            # Verify HTML converter was called
            assert mock_converter.called, "HTML converter should be called in dual-format mode"

            # Verify it was called with correct arguments
            call_args = mock_converter.call_args
            markdown_dir = output_dir / "markdown"
            html_dir = output_dir / "html"

            assert call_args[0][0] == markdown_dir
            assert call_args[0][1] == html_dir

    def test_markdown_only_skips_html_converter(
        self, tmp_path, mock_analysis_result, mock_anthropic_client
    ):
        """Should NOT call HTML converter when markdown_only=True."""
        mock_analysis_result.root = tmp_path

        # Patch the HTML converter at its source
        with patch(
            "code_guro.html_converter.convert_directory_to_html_organized"
        ) as mock_converter:
            generate_documentation(mock_analysis_result, markdown_only=True)

            # Verify HTML converter was NOT called
            assert (
                not mock_converter.called
            ), "HTML converter should not be called in markdown-only mode"

    def test_return_value_is_output_directory(
        self, tmp_path, mock_analysis_result, mock_anthropic_client
    ):
        """Should return the output directory path."""
        mock_analysis_result.root = tmp_path

        # Test markdown-only mode
        output_dir_md = generate_documentation(mock_analysis_result, markdown_only=True)
        assert isinstance(output_dir_md, Path)
        assert output_dir_md.exists()
        assert output_dir_md.name == "code-guro-output"

        # Test dual-format mode
        # Need to delete the existing output directory first
        import shutil

        shutil.rmtree(output_dir_md)

        output_dir_dual = generate_documentation(mock_analysis_result, markdown_only=False)
        assert isinstance(output_dir_dual, Path)
        assert output_dir_dual.exists()
        assert output_dir_dual.name == "code-guro-output"

    def test_directory_structure_validation(
        self, tmp_path, mock_analysis_result, mock_anthropic_client
    ):
        """Should create correct directory structure that passes validation."""
        mock_analysis_result.root = tmp_path

        # Generate dual-format documentation
        output_dir = generate_documentation(mock_analysis_result, markdown_only=False)

        # Use helper function to validate structure
        assert_dual_format_structure(output_dir)

        # Verify expected documentation files exist
        markdown_dir = output_dir / "markdown"
        expected_files = [
            "00-overview.md",
            "01-getting-oriented.md",
            "02-architecture.md",
            "03-core-files.md",
            "05-quality-analysis.md",
            "06-next-steps.md",
        ]

        for filename in expected_files:
            filepath = markdown_dir / filename
            assert filepath.exists(), f"Expected file {filename} not found"

            # Verify file is not empty
            content = filepath.read_text()
            assert len(content) > 0, f"File {filename} is empty"

    def test_chunked_analysis_workflow(self, tmp_path, mock_anthropic_client):
        """Should handle chunked analysis for large codebases."""
        from code_guro.analyzer import AnalysisResult, FileInfo

        # Create a result that needs chunking
        large_result = AnalysisResult(
            root=tmp_path,
            files=[
                FileInfo(
                    path=Path("file.py"),
                    relative_path="file.py",
                    content="x" * 1000,
                    tokens=100,
                    extension=".py",
                )
            ],
            frameworks=[],
            total_tokens=200000,  # Large enough to trigger chunking
            estimated_cost=5.0,
            needs_chunking=True,  # Trigger chunking
            chunk_count=3,
            skipped_files=[],
            warnings=[],
        )

        # Generate documentation with chunked analysis
        output_dir = generate_documentation(large_result, markdown_only=True)

        # Should still create output
        assert output_dir.exists()

        # Should have created markdown files
        md_files = list(output_dir.glob("*.md"))
        assert len(md_files) > 0

    def test_generates_module_deep_dives(self, tmp_path, mock_anthropic_client, monkeypatch):
        """Should generate deep dive files for identified modules."""
        from code_guro.analyzer import AnalysisResult, FileInfo

        # Mock identify_modules to return test modules with correct structure
        def mock_identify_modules(result):
            return [
                {
                    "name": "Authentication",
                    "path": "auth",
                    "files": result.files[:1],
                    "file_count": 1,
                    "tokens": 50,
                },
                {
                    "name": "Database",
                    "path": "db",
                    "files": result.files[:1],
                    "file_count": 1,
                    "tokens": 50,
                },
            ]

        monkeypatch.setattr("code_guro.generator.identify_modules", mock_identify_modules)

        result = AnalysisResult(
            root=tmp_path,
            files=[
                FileInfo(
                    path=Path("auth.py"),
                    relative_path="auth.py",
                    content="# Auth code",
                    tokens=50,
                    extension=".py",
                )
            ],
            frameworks=[],
            total_tokens=1000,
            estimated_cost=0.01,
            needs_chunking=False,
            chunk_count=1,
            skipped_files=[],
            warnings=[],
        )

        # Generate documentation
        output_dir = generate_documentation(result, markdown_only=True)

        # Should have created deep dive files
        deep_dive_files = list(output_dir.glob("04-deep-dive-*.md"))
        assert len(deep_dive_files) >= 2, "Should create deep dive files for modules"

        # Verify specific deep dive files exist
        auth_file = output_dir / "04-deep-dive-authentication.md"
        db_file = output_dir / "04-deep-dive-database.md"

        # At least one should exist
        assert auth_file.exists() or db_file.exists(), "Deep dive files should be created"

    def test_generate_documentation_creates_output_directory(self, tmp_path, mock_anthropic_client):
        """Should create output directory if it doesn't exist."""
        from code_guro.analyzer import AnalysisResult, FileInfo

        result = AnalysisResult(
            root=tmp_path,
            files=[
                FileInfo(
                    path=Path("test.py"),
                    relative_path="test.py",
                    content="# Test",
                    tokens=10,
                    extension=".py",
                )
            ],
            frameworks=[],
            total_tokens=100,
            estimated_cost=0.01,
            needs_chunking=False,
            chunk_count=1,
            skipped_files=[],
            warnings=[],
        )

        # Generate documentation
        output_dir = generate_documentation(result, markdown_only=True)

        # Output directory should have been created
        assert output_dir.exists()
        assert output_dir.name == "code-guro-output"
