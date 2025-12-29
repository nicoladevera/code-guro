"""Documentation generator for Code Guro.

Generates structured learning documentation from codebase analysis.
"""

import os
from pathlib import Path
from typing import Dict, List, Optional

import anthropic
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn

from code_guro.analyzer import AnalysisResult, FileInfo, chunk_files, get_critical_files
from code_guro.config import get_api_key
from code_guro.frameworks import get_framework_context
from code_guro.prompts import (
    ARCHITECTURE_PROMPT,
    CORE_FILES_PROMPT,
    DEEP_DIVE_PROMPT,
    NEXT_STEPS_PROMPT,
    ORIENTATION_PROMPT,
    OVERVIEW_PROMPT,
    QUALITY_PROMPT,
    SYSTEM_PROMPT,
)

console = Console()

# Output directory name
OUTPUT_DIR = "code-guro-output"

# Claude model to use
MODEL = "claude-sonnet-4-20250514"


def create_output_dir(root: Path) -> Path:
    """Create the output directory for documentation.

    Args:
        root: Root directory of the codebase

    Returns:
        Path to the output directory
    """
    output_dir = root / OUTPUT_DIR
    output_dir.mkdir(exist_ok=True)
    return output_dir


def generate_file_tree(files: List[FileInfo], max_depth: int = 4) -> str:
    """Generate a text representation of the file tree.

    Args:
        files: List of files
        max_depth: Maximum depth to show

    Returns:
        Text representation of file tree
    """
    tree_lines = []
    seen_dirs = set()

    # Sort files by path
    sorted_files = sorted(files, key=lambda f: f.relative_path)

    for f in sorted_files:
        parts = f.relative_path.split("/")

        # Add directory entries
        for i in range(1, min(len(parts), max_depth + 1)):
            dir_path = "/".join(parts[:i])
            if dir_path not in seen_dirs and i < len(parts):
                indent = "  " * (i - 1)
                tree_lines.append(f"{indent}{parts[i-1]}/")
                seen_dirs.add(dir_path)

        # Add file entry (if within depth limit)
        if len(parts) <= max_depth + 1:
            indent = "  " * (len(parts) - 1)
            tree_lines.append(f"{indent}{parts[-1]}")

    return "\n".join(tree_lines[:100])  # Limit to 100 lines


def format_file_content(files: List[FileInfo], max_tokens: int = 50000) -> str:
    """Format file contents for inclusion in prompts.

    Args:
        files: List of files
        max_tokens: Maximum tokens to include

    Returns:
        Formatted file contents
    """
    result = []
    total_tokens = 0

    for f in files:
        if total_tokens + f.tokens > max_tokens:
            break

        result.append(f"## {f.relative_path}\n")
        result.append(f"```{f.extension.lstrip('.')}\n{f.content}\n```\n\n")
        total_tokens += f.tokens

    return "\n".join(result)


def call_claude(prompt: str, system: str = SYSTEM_PROMPT) -> str:
    """Make a call to the Claude API.

    Args:
        prompt: The user prompt
        system: The system prompt

    Returns:
        Claude's response text
    """
    api_key = get_api_key()
    client = anthropic.Anthropic(api_key=api_key)

    message = client.messages.create(
        model=MODEL,
        max_tokens=4096,
        system=system,
        messages=[{"role": "user", "content": prompt}],
    )

    return message.content[0].text


def generate_overview(result: AnalysisResult) -> str:
    """Generate the overview document.

    Args:
        result: Analysis result

    Returns:
        Generated markdown content
    """
    critical_files = get_critical_files(result, limit=10)
    framework_names = ", ".join(f.name for f in result.frameworks) or "None detected"

    prompt = OVERVIEW_PROMPT.format(
        root=result.root.name,
        file_count=len(result.files),
        frameworks=framework_names,
        file_tree=generate_file_tree(result.files),
        key_files=format_file_content(critical_files, max_tokens=30000),
    )

    return call_claude(prompt)


def generate_orientation(result: AnalysisResult) -> str:
    """Generate the getting oriented document.

    Args:
        result: Analysis result

    Returns:
        Generated markdown content
    """
    framework_names = ", ".join(f.name for f in result.frameworks) or "None detected"

    # Get a sample of diverse files
    sample_files = []
    extensions_seen = set()
    for f in result.files:
        if f.extension not in extensions_seen and len(sample_files) < 10:
            sample_files.append(f)
            extensions_seen.add(f.extension)

    prompt = ORIENTATION_PROMPT.format(
        root=result.root.name,
        frameworks=framework_names,
        file_tree=generate_file_tree(result.files, max_depth=3),
        sample_files=format_file_content(sample_files, max_tokens=20000),
    )

    return call_claude(prompt)


def generate_architecture(result: AnalysisResult) -> str:
    """Generate the architecture document.

    Args:
        result: Analysis result

    Returns:
        Generated markdown content
    """
    critical_files = get_critical_files(result, limit=15)
    framework_names = ", ".join(f.name for f in result.frameworks) or "None detected"
    framework_context = get_framework_context(result.frameworks)

    prompt = ARCHITECTURE_PROMPT.format(
        frameworks=framework_names,
        file_count=len(result.files),
        framework_context=framework_context or "No specific framework context available.",
        key_files=format_file_content(critical_files, max_tokens=40000),
        file_tree=generate_file_tree(result.files),
    )

    return call_claude(prompt)


def generate_core_files(result: AnalysisResult) -> str:
    """Generate the core files document.

    Args:
        result: Analysis result

    Returns:
        Generated markdown content
    """
    critical_files = get_critical_files(result, limit=20)
    framework_names = ", ".join(f.name for f in result.frameworks) or "None detected"

    prompt = CORE_FILES_PROMPT.format(
        frameworks=framework_names,
        file_count=len(result.files),
        critical_files=format_file_content(critical_files, max_tokens=50000),
    )

    return call_claude(prompt)


def identify_modules(result: AnalysisResult) -> List[Dict]:
    """Identify major modules/features in the codebase.

    Args:
        result: Analysis result

    Returns:
        List of module info dicts
    """
    # Group files by top-level directories
    dir_groups: Dict[str, List[FileInfo]] = {}

    for f in result.files:
        parts = f.relative_path.split("/")
        if len(parts) > 1:
            top_dir = parts[0]
            # Skip common non-module directories
            if top_dir in ("node_modules", "dist", "build", "public", "static", "assets"):
                continue
            if top_dir not in dir_groups:
                dir_groups[top_dir] = []
            dir_groups[top_dir].append(f)

    # Create module info for significant directories
    modules = []
    for dir_name, files in dir_groups.items():
        if len(files) >= 3:  # Only include if has 3+ files
            total_tokens = sum(f.tokens for f in files)
            modules.append({
                "name": dir_name,
                "path": dir_name,
                "files": files,
                "file_count": len(files),
                "tokens": total_tokens,
            })

    # Sort by token count (largest modules first)
    modules.sort(key=lambda m: m["tokens"], reverse=True)

    # Return top 5 modules
    return modules[:5]


def generate_deep_dive(module: Dict, result: AnalysisResult) -> str:
    """Generate a deep dive document for a module.

    Args:
        module: Module info dict
        result: Analysis result

    Returns:
        Generated markdown content
    """
    framework_context = get_framework_context(result.frameworks)

    prompt = DEEP_DIVE_PROMPT.format(
        module_name=module["name"],
        module_path=module["path"],
        module_files=format_file_content(module["files"], max_tokens=40000),
        framework_context=framework_context or "No specific framework context available.",
    )

    return call_claude(prompt)


def generate_quality_analysis(result: AnalysisResult) -> str:
    """Generate the quality analysis document.

    Args:
        result: Analysis result

    Returns:
        Generated markdown content
    """
    framework_names = ", ".join(f.name for f in result.frameworks) or "None detected"

    # Get test count
    test_count = sum(1 for f in result.files if f.is_test)

    # Get config files
    config_files = [f for f in result.files if f.is_config]

    # Get a sample of code
    sample_files = get_critical_files(result, limit=10)

    prompt = QUALITY_PROMPT.format(
        frameworks=framework_names,
        file_count=len(result.files),
        test_count=test_count,
        sample_code=format_file_content(sample_files, max_tokens=30000),
        config_files=format_file_content(config_files, max_tokens=10000),
    )

    return call_claude(prompt)


def generate_next_steps(result: AnalysisResult) -> str:
    """Generate the next steps document.

    Args:
        result: Analysis result

    Returns:
        Generated markdown content
    """
    framework_names = ", ".join(f.name for f in result.frameworks) or "None detected"
    modules = identify_modules(result)
    module_names = ", ".join(m["name"] for m in modules) or "No clear modules identified"

    prompt = NEXT_STEPS_PROMPT.format(
        frameworks=framework_names,
        modules=module_names,
    )

    return call_claude(prompt)


def generate_documentation(
    result: AnalysisResult,
    output_format: str = "markdown",
) -> Path:
    """Generate all documentation for a codebase.

    Args:
        result: Analysis result
        output_format: Output format ("markdown" or "html")

    Returns:
        Path to output directory
    """
    output_dir = create_output_dir(result.root)

    documents = [
        ("00-overview.md", "Generating overview...", generate_overview),
        ("01-getting-oriented.md", "Generating orientation guide...", generate_orientation),
        ("02-architecture.md", "Generating architecture analysis...", generate_architecture),
        ("03-core-files.md", "Generating core files guide...", generate_core_files),
        ("05-quality-analysis.md", "Generating quality analysis...", generate_quality_analysis),
        ("06-next-steps.md", "Generating next steps...", generate_next_steps),
    ]

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TaskProgressColumn(),
        console=console,
    ) as progress:
        task = progress.add_task("Generating documentation...", total=len(documents) + 1)

        # Generate main documents
        for filename, description, generator in documents:
            progress.update(task, description=description)
            content = generator(result)

            filepath = output_dir / filename
            filepath.write_text(content)
            progress.advance(task)

        # Generate deep dives for modules
        progress.update(task, description="Generating module deep dives...")
        modules = identify_modules(result)

        for i, module in enumerate(modules):
            content = generate_deep_dive(module, result)
            filename = f"04-deep-dive-{module['name'].lower().replace(' ', '-')}.md"
            filepath = output_dir / filename
            filepath.write_text(content)

        progress.advance(task)

    # Convert to HTML if requested
    if output_format == "html":
        from code_guro.html_converter import convert_directory_to_html
        convert_directory_to_html(output_dir)

    console.print()
    console.print(f"[green]Documentation generated successfully![/green]")
    console.print(f"[dim]Output directory: {output_dir}[/dim]")

    return output_dir


def generate_explain_document(
    path: Path,
    content: str,
    frameworks: List,
) -> str:
    """Generate an explanation document for a specific file or folder.

    Args:
        path: Path to the file or folder
        content: Content to explain
        frameworks: Detected frameworks

    Returns:
        Generated markdown content
    """
    from code_guro.prompts import EXPLAIN_PROMPT

    framework_names = ", ".join(f.name for f in frameworks) or "None detected"
    file_type = "folder" if path.is_dir() else f"{path.suffix} file"

    prompt = EXPLAIN_PROMPT.format(
        path=str(path),
        content=content,
        framework=framework_names,
        file_type=file_type,
    )

    return call_claude(prompt)
