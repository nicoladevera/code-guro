"""Code analysis engine for Code Guro.

Handles codebase traversal, analysis, and preparation for documentation generation.
"""

import os
import shutil
import tempfile
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from urllib.parse import urlparse

import git
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.prompt import Confirm

from code_guro.frameworks import FrameworkInfo, detect_frameworks
from code_guro.utils import (
    MAX_FILE_SIZE,
    SAFE_CONTEXT_TOKENS,
    count_tokens,
    estimate_cost,
    format_cost,
    is_binary_file,
    is_file_too_large,
    is_github_url,
    read_file_safely,
    traverse_directory,
)

console = Console()


@dataclass
class FileInfo:
    """Information about a source file."""

    path: Path
    relative_path: str
    content: str
    tokens: int
    extension: str
    is_entry_point: bool = False
    is_config: bool = False
    is_test: bool = False


@dataclass
class AnalysisResult:
    """Result of analyzing a codebase."""

    root: Path
    files: List[FileInfo] = field(default_factory=list)
    frameworks: List[FrameworkInfo] = field(default_factory=list)
    total_tokens: int = 0
    estimated_cost: float = 0.0
    needs_chunking: bool = False
    chunk_count: int = 1
    skipped_files: List[Tuple[str, str]] = field(default_factory=list)  # (path, reason)
    warnings: List[str] = field(default_factory=list)


# Entry point patterns
ENTRY_POINT_PATTERNS = {
    "index.js",
    "index.ts",
    "index.jsx",
    "index.tsx",
    "main.js",
    "main.ts",
    "main.py",
    "app.py",
    "app.js",
    "app.ts",
    "server.js",
    "server.ts",
    "manage.py",
    "wsgi.py",
    "asgi.py",
}

# Configuration file patterns
CONFIG_PATTERNS = {
    "package.json",
    "tsconfig.json",
    "pyproject.toml",
    "setup.py",
    "setup.cfg",
    "requirements.txt",
    "Gemfile",
    "Cargo.toml",
    "go.mod",
    "next.config.js",
    "next.config.mjs",
    "vite.config.js",
    "vite.config.ts",
    "webpack.config.js",
    ".env.example",
    "docker-compose.yml",
    "Dockerfile",
}

# Test file patterns
TEST_PATTERNS = {"test_", "_test", ".test.", ".spec.", "tests/", "__tests__/"}


def clone_github_repo(url: str) -> Path:
    """Clone a GitHub repository to a temporary directory.

    Args:
        url: GitHub repository URL

    Returns:
        Path to the cloned repository
    """
    temp_dir = tempfile.mkdtemp(prefix="code-guro-")
    console.print(f"[dim]Cloning repository to {temp_dir}...[/dim]")

    try:
        git.Repo.clone_from(url, temp_dir, depth=1)
        return Path(temp_dir)
    except git.GitCommandError as e:
        shutil.rmtree(temp_dir, ignore_errors=True)
        raise RuntimeError(f"Failed to clone repository: {e}")


def is_entry_point(path: Path) -> bool:
    """Check if a file is likely an entry point."""
    name = path.name.lower()
    return name in ENTRY_POINT_PATTERNS


def is_config_file(path: Path) -> bool:
    """Check if a file is a configuration file."""
    name = path.name.lower()
    return name in CONFIG_PATTERNS


def is_test_file(path: Path) -> bool:
    """Check if a file is a test file."""
    path_str = str(path).lower()
    return any(pattern in path_str for pattern in TEST_PATTERNS)


def analyze_codebase(
    path: str,
    show_progress: bool = True,
) -> AnalysisResult:
    """Analyze a codebase and prepare for documentation generation.

    Args:
        path: Path to local directory or GitHub URL
        show_progress: Whether to show progress indicators

    Returns:
        AnalysisResult with all analysis data
    """
    result = AnalysisResult(root=Path(path))
    temp_dir = None

    try:
        # Handle GitHub URLs
        if is_github_url(path):
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=console,
                transient=True,
            ) as progress:
                progress.add_task("Cloning repository...", total=None)
                temp_dir = clone_github_repo(path)
                result.root = temp_dir
        else:
            result.root = Path(path).resolve()

        if not result.root.exists():
            raise FileNotFoundError(f"Directory not found: {result.root}")

        if not result.root.is_dir():
            raise NotADirectoryError(f"Not a directory: {result.root}")

        # Detect frameworks
        if show_progress:
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=console,
                transient=True,
            ) as progress:
                progress.add_task("Detecting frameworks...", total=None)
                result.frameworks = detect_frameworks(result.root)
        else:
            result.frameworks = detect_frameworks(result.root)

        if result.frameworks:
            framework_names = ", ".join(f.name for f in result.frameworks)
            console.print(f"[green]Detected frameworks:[/green] {framework_names}")

        # Traverse and analyze files
        if show_progress:
            console.print("[dim]Analyzing files...[/dim]")

        files_by_extension: Dict[str, int] = {}

        for filepath in traverse_directory(result.root):
            relative = str(filepath.relative_to(result.root))

            # Check file size
            if is_file_too_large(filepath):
                result.skipped_files.append((relative, "File too large (>1MB)"))
                result.warnings.append(f"Skipped large file: {relative}")
                continue

            # Read file content
            content = read_file_safely(filepath)
            if content is None:
                result.skipped_files.append((relative, "Could not read file"))
                continue

            # Count tokens
            tokens = count_tokens(content)

            # Create file info
            file_info = FileInfo(
                path=filepath,
                relative_path=relative,
                content=content,
                tokens=tokens,
                extension=filepath.suffix.lower(),
                is_entry_point=is_entry_point(filepath),
                is_config=is_config_file(filepath),
                is_test=is_test_file(filepath),
            )

            result.files.append(file_info)
            result.total_tokens += tokens

            # Track extensions
            ext = filepath.suffix.lower() or "(no extension)"
            files_by_extension[ext] = files_by_extension.get(ext, 0) + 1

        # Check if chunking is needed
        if result.total_tokens > SAFE_CONTEXT_TOKENS:
            result.needs_chunking = True
            result.chunk_count = (result.total_tokens // SAFE_CONTEXT_TOKENS) + 1
            result.warnings.append(
                f"Large codebase detected ({result.total_tokens:,} tokens). "
                f"Analysis will be performed in {result.chunk_count} chunks."
            )

        # Estimate cost (input tokens + estimated output)
        # Assume output is roughly 1/3 of input for documentation
        estimated_output = result.total_tokens // 3
        result.estimated_cost = estimate_cost(result.total_tokens, estimated_output)

        # Print summary
        if show_progress:
            console.print()
            console.print(f"[bold]Files analyzed:[/bold] {len(result.files)}")
            console.print(f"[bold]Total tokens:[/bold] {result.total_tokens:,}")
            console.print(
                f"[bold]Estimated cost:[/bold] {format_cost(result.estimated_cost)}"
            )

            if result.skipped_files:
                console.print(
                    f"[yellow]Files skipped:[/yellow] {len(result.skipped_files)}"
                )

        return result

    except Exception as e:
        # Clean up temp directory on error
        if temp_dir:
            shutil.rmtree(temp_dir, ignore_errors=True)
        raise


def confirm_analysis(result: AnalysisResult, cost_threshold: float = 1.0) -> bool:
    """Ask user to confirm analysis if cost exceeds threshold.

    Args:
        result: Analysis result
        cost_threshold: Cost threshold for confirmation

    Returns:
        True if user confirms or cost is below threshold
    """
    if result.estimated_cost <= cost_threshold:
        return True

    console.print()
    console.print(
        f"[yellow]Warning:[/yellow] Estimated cost ({format_cost(result.estimated_cost)}) "
        f"exceeds ${cost_threshold:.2f}."
    )

    if result.needs_chunking:
        console.print(
            f"[yellow]Note:[/yellow] This codebase will be analyzed in "
            f"{result.chunk_count} chunks, which may affect cross-module insights."
        )

    console.print()
    return Confirm.ask("Do you want to proceed?", default=False)


def get_critical_files(result: AnalysisResult, limit: int = 20) -> List[FileInfo]:
    """Get the most critical files from the analysis.

    Prioritizes entry points, config files, and files with high token counts
    while excluding test files.

    Args:
        result: Analysis result
        limit: Maximum number of files to return

    Returns:
        List of critical FileInfo objects
    """

    def score_file(f: FileInfo) -> int:
        """Score a file for importance."""
        score = 0

        # Entry points are very important
        if f.is_entry_point:
            score += 100

        # Config files are important
        if f.is_config:
            score += 50

        # Test files are less important for understanding
        if f.is_test:
            score -= 30

        # Larger files often contain more logic
        # But cap this to avoid prioritizing just large files
        score += min(f.tokens // 100, 20)

        # Prefer files in src/ or app/ directories
        if "/src/" in f.relative_path or "/app/" in f.relative_path:
            score += 10

        # Prefer files closer to root (shorter paths)
        depth = f.relative_path.count("/")
        score -= depth * 2

        return score

    # Filter out test files for critical files list
    non_test_files = [f for f in result.files if not f.is_test]

    # Sort by score and return top N
    sorted_files = sorted(non_test_files, key=score_file, reverse=True)
    return sorted_files[:limit]


def chunk_files(
    files: List[FileInfo],
    max_tokens_per_chunk: int = SAFE_CONTEXT_TOKENS,
) -> List[List[FileInfo]]:
    """Split files into chunks that fit within token limits.

    Tries to keep related files (same directory) together.

    Args:
        files: List of files to chunk
        max_tokens_per_chunk: Maximum tokens per chunk

    Returns:
        List of file chunks
    """
    if not files:
        return []

    # Group files by top-level directory
    dir_groups: Dict[str, List[FileInfo]] = {}
    for f in files:
        parts = f.relative_path.split("/")
        top_dir = parts[0] if len(parts) > 1 else "(root)"
        if top_dir not in dir_groups:
            dir_groups[top_dir] = []
        dir_groups[top_dir].append(f)

    chunks: List[List[FileInfo]] = []
    current_chunk: List[FileInfo] = []
    current_tokens = 0

    for dir_name, dir_files in dir_groups.items():
        for f in dir_files:
            if current_tokens + f.tokens > max_tokens_per_chunk and current_chunk:
                chunks.append(current_chunk)
                current_chunk = []
                current_tokens = 0

            current_chunk.append(f)
            current_tokens += f.tokens

    if current_chunk:
        chunks.append(current_chunk)

    return chunks
