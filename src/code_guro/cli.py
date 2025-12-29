"""Code Guro CLI - Main entry point."""

import functools
import sys
from pathlib import Path
from typing import Callable

import click
from rich.console import Console
from rich.prompt import Prompt

from code_guro import __version__
from code_guro.config import (
    get_api_key,
    is_api_key_configured,
    mask_api_key,
    require_api_key,
    save_api_key,
    validate_api_key,
)
from code_guro.errors import check_internet_connection, handle_api_error

console = Console()


def require_api_key_decorator(f: Callable) -> Callable:
    """Decorator to require API key before running a command."""

    @functools.wraps(f)
    def wrapper(*args, **kwargs):
        api_key = require_api_key()
        if not api_key:
            sys.exit(1)
        return f(*args, **kwargs)

    return wrapper


def require_internet_decorator(f: Callable) -> Callable:
    """Decorator to require internet connection before running a command."""

    @functools.wraps(f)
    def wrapper(*args, **kwargs):
        if not check_internet_connection():
            console.print(
                "\n[bold red]Error:[/bold red] No internet connection detected.\n"
                "\n"
                "Code Guro requires an internet connection to analyze code.\n"
                "Please check your connection and try again.\n"
            )
            sys.exit(1)
        return f(*args, **kwargs)

    return wrapper


@click.group()
@click.version_option(version=__version__, prog_name="code-guro")
def main():
    """Code Guro - Understand your codebase like a guru.

    A CLI tool to help non-technical product managers and AI-native builders
    understand codebases through structured, beginner-friendly documentation.
    """
    pass


@main.command()
@click.argument("path", type=click.Path(exists=False))
@click.option(
    "--format",
    "output_format",
    type=click.Choice(["markdown", "html"]),
    default="markdown",
    help="Output format for documentation (default: markdown)",
)
@require_internet_decorator
@require_api_key_decorator
def analyze(path: str, output_format: str):
    """Analyze a codebase and generate learning documentation.

    PATH can be a local directory or a GitHub repository URL.

    Examples:

        code-guro analyze .

        code-guro analyze /path/to/project

        code-guro analyze https://github.com/user/repo

        code-guro analyze . --format html
    """
    from code_guro.analyzer import analyze_codebase, confirm_analysis
    from code_guro.generator import generate_documentation
    from code_guro.utils import is_github_url

    console.print()
    console.print("[bold]Code Guro Analysis[/bold]")
    console.print()

    # Validate path
    if not is_github_url(path):
        path_obj = Path(path).resolve()
        if not path_obj.exists():
            console.print(f"[red]Error:[/red] Directory not found: {path}")
            sys.exit(1)
        if not path_obj.is_dir():
            console.print(f"[red]Error:[/red] Not a directory: {path}")
            sys.exit(1)

    try:
        # Analyze codebase
        console.print(f"[dim]Analyzing: {path}[/dim]")
        result = analyze_codebase(path)

        if not result.files:
            console.print(
                "\n[yellow]Warning:[/yellow] No analyzable files found.\n"
                "The directory may be empty or contain only binary/ignored files."
            )
            sys.exit(1)

        # Confirm if cost is high
        if not confirm_analysis(result):
            console.print("[yellow]Analysis cancelled.[/yellow]")
            sys.exit(0)

        # Generate documentation
        console.print()
        output_dir = generate_documentation(result, output_format)

        # Print summary
        console.print()
        console.print("[bold green]Analysis complete![/bold green]")
        console.print()
        console.print("Generated documentation:")
        for f in sorted(output_dir.glob("*.md")):
            console.print(f"  [cyan]{f.name}[/cyan]")
        if output_format == "html":
            for f in sorted(output_dir.glob("*.html")):
                console.print(f"  [cyan]{f.name}[/cyan]")
        console.print()
        console.print(f"[dim]Open {output_dir}/00-overview.md to start learning![/dim]")

    except Exception as e:
        handle_api_error(e)
        sys.exit(1)


@main.command()
@click.argument("path", type=click.Path(exists=True))
@click.option(
    "--interactive",
    "-i",
    is_flag=True,
    help="Launch interactive mode for follow-up questions",
)
@click.option(
    "--output",
    type=click.Choice(["file", "console"]),
    default="file",
    help="Where to output the explanation (default: file)",
)
@require_internet_decorator
@require_api_key_decorator
def explain(path: str, interactive: bool, output: str):
    """Explain a specific file or folder in depth.

    PATH must be a file or folder within a previously analyzed codebase.

    Examples:

        code-guro explain ./src/auth

        code-guro explain ./src/auth/login.ts --interactive

        code-guro explain ./src/auth --output console
    """
    from code_guro.analyzer import analyze_codebase
    from code_guro.generator import generate_explain_document, create_output_dir
    from code_guro.utils import read_file_safely, traverse_directory

    path_obj = Path(path).resolve()

    console.print()
    console.print("[bold]Code Guro Explain[/bold]")
    console.print()
    console.print(f"[dim]Analyzing: {path}[/dim]")

    try:
        # Get content to explain
        if path_obj.is_file():
            content = read_file_safely(path_obj)
            if content is None:
                console.print(f"[red]Error:[/red] Could not read file: {path}")
                sys.exit(1)
        else:
            # It's a directory - get all files
            files_content = []
            for f in traverse_directory(path_obj):
                file_content = read_file_safely(f)
                if file_content:
                    rel_path = f.relative_to(path_obj)
                    files_content.append(f"## {rel_path}\n```\n{file_content}\n```\n")
            content = "\n".join(files_content)

        if not content:
            console.print(f"[yellow]Warning:[/yellow] No content to explain in {path}")
            sys.exit(1)

        # Detect frameworks from parent directory
        parent = path_obj.parent if path_obj.is_file() else path_obj
        while parent != parent.parent:
            if (parent / "package.json").exists() or (parent / "pyproject.toml").exists():
                break
            parent = parent.parent

        from code_guro.frameworks import detect_frameworks
        frameworks = detect_frameworks(parent)

        if interactive:
            # Launch interactive mode
            from code_guro.repl import start_repl
            start_repl(path_obj, content, frameworks)
        else:
            # Generate explanation document
            console.print("[dim]Generating explanation...[/dim]")
            doc = generate_explain_document(path_obj, content, frameworks)

            if output == "console":
                console.print()
                console.print(doc)
            else:
                # Save to file
                output_dir = create_output_dir(parent)
                filename = f"explain-{path_obj.name.replace('/', '-')}.md"
                filepath = output_dir / filename
                filepath.write_text(doc)
                console.print()
                console.print(f"[green]Explanation saved to:[/green] {filepath}")

    except Exception as e:
        handle_api_error(e)
        sys.exit(1)


@main.command()
def configure():
    """Configure Code Guro with your Claude API key.

    This command will prompt you to enter your Claude API key and save it
    securely for future use.

    Get your API key at: https://console.anthropic.com
    """
    console.print()
    console.print("[bold]Code Guro Configuration[/bold]")
    console.print()

    # Check if already configured
    if is_api_key_configured():
        current_key = get_api_key()
        console.print(f"Current API key: [cyan]{mask_api_key(current_key)}[/cyan]")
        console.print()

        if not Prompt.ask(
            "Do you want to replace the existing API key?",
            choices=["y", "n"],
            default="n",
        ) == "y":
            console.print("[yellow]Configuration unchanged.[/yellow]")
            return

    console.print(
        "Enter your Claude API key (get one at [link=https://console.anthropic.com]console.anthropic.com[/link]):"
    )
    console.print()

    # Prompt for API key
    api_key = Prompt.ask("API key", password=True)

    if not api_key:
        console.print("[red]Error: API key cannot be empty.[/red]")
        sys.exit(1)

    # Validate the key
    console.print()
    console.print("[dim]Validating API key...[/dim]")

    is_valid, message = validate_api_key(api_key)

    if not is_valid:
        console.print(f"[red]Error: {message}[/red]")
        console.print()
        console.print("Please check your API key and try again.")
        sys.exit(1)

    # Save the key
    save_api_key(api_key)

    console.print()
    console.print("[green]✓ API key saved successfully![/green]")
    console.print()
    console.print(
        "You can now use [bold cyan]code-guro analyze[/bold cyan] to analyze a codebase."
    )


if __name__ == "__main__":
    main()
