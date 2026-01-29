"""Code Guro CLI - Main entry point."""

import functools
import sys
from pathlib import Path
from typing import Callable, Optional

import click
from rich.console import Console
from rich.prompt import Prompt

from code_guro import __version__
from code_guro.config import (
    get_provider_config,
    get_api_key,
    mask_api_key,
    require_provider,
    save_provider_config,
)
from code_guro.errors import check_internet_connection, handle_api_error

console = Console()


def require_api_key_decorator(f: Callable) -> Callable:
    """Decorator to require provider configuration before running a command."""

    @functools.wraps(f)
    def wrapper(*args, **kwargs):
        api_key = require_api_key()
        if not api_key:
            sys.exit(1)
        return f(*args, **kwargs)

    return wrapper


def require_api_key() -> Optional[str]:
    """Backward-compatible API key check for CLI decorators."""
    provider_name = require_provider()
    if not provider_name:
        return None
    from code_guro.providers.factory import get_provider

    try:
        provider = get_provider(provider_name)
        return provider.get_api_key()
    except ValueError:
        return get_api_key()


def validate_api_key(api_key: str):
    """Backward-compatible API key validation shim."""
    from code_guro.providers.factory import get_provider

    try:
        provider = get_provider()
    except ValueError:
        provider = get_provider("anthropic")
    return provider.validate_api_key(api_key)


def save_api_key(api_key: str) -> None:
    """Backward-compatible API key saver."""
    from code_guro.config import save_api_key as _save_api_key

    _save_api_key(api_key)


def require_internet_decorator(f: Callable) -> Callable:
    """Decorator to require internet connection before running a command."""

    @functools.wraps(f)
    def wrapper(*args, **kwargs):
        provider_name = get_provider_config()
        try:
            has_internet = check_internet_connection(provider_name)
        except TypeError:
            # Backwards compatibility for tests mocking a no-arg function
            has_internet = check_internet_connection()

        if not has_internet:
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
    "--markdown-only",
    is_flag=True,
    help="Generate only markdown files (default: generates both HTML and markdown)",
)
@require_internet_decorator
@require_api_key_decorator
def analyze(path: str, markdown_only: bool):
    """Analyze a codebase and generate learning documentation.

    By default, generates both HTML and markdown files organized in subdirectories.
    HTML files include fully rendered Mermaid diagrams for the best viewing experience.

    PATH can be a local directory or a GitHub repository URL.

    Examples:

        code-guro analyze .

        code-guro analyze /path/to/project

        code-guro analyze https://github.com/user/repo

        code-guro analyze . --markdown-only
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
        output_dir = generate_documentation(result, markdown_only=markdown_only)

        # Print summary
        console.print()
        console.print("[bold green]Analysis complete![/bold green]")
        console.print()

        if markdown_only:
            console.print("Generated documentation:")
            for f in sorted(output_dir.glob("*.md")):
                console.print(f"  [cyan]{f.name}[/cyan]")
            console.print()
            console.print(f"[dim]Open {output_dir}/00-overview.md to start learning![/dim]")
        else:
            # Both formats generated in subdirectories
            markdown_dir = output_dir / "markdown"
            html_dir = output_dir / "html"

            md_files = sorted(markdown_dir.glob("*.md"))
            html_files = sorted(html_dir.glob("*.html"))

            console.print("Directory structure:")
            console.print(f"  [cyan]{output_dir.name}/[/cyan]")
            console.print(f"    [cyan]markdown/[/cyan] ({len(md_files)} files)")
            console.print(f"    [cyan]html/[/cyan] ({len(html_files)} files)")
            console.print()
            console.print(
                f"[dim]Open {html_dir}/00-overview.html in your browser for the best "
                "experience![/dim]"
            )

        console.print()

    except Exception as e:
        from code_guro.providers.factory import get_provider

        try:
            provider = get_provider()
            provider_name = provider.get_provider_name().lower()
        except Exception:
            provider_name = None
        handle_api_error(e, provider_name)
        sys.exit(1)


@main.command()
@click.argument(
    "output_dir",
    type=click.Path(),
    default="code-guro-output",
    required=False,
)
def convert(output_dir: str):
    """Convert markdown-only output to include HTML files.

    OUTPUT_DIR is the directory containing markdown files (default: code-guro-output).

    Useful if you previously ran 'code-guro analyze --markdown-only' and now want
    to add HTML files. Organizes files into markdown/ and html/ subdirectories.

    Examples:

        code-guro convert

        code-guro convert ./code-guro-output

        code-guro convert /path/to/output
    """

    output_path = Path(output_dir).resolve()

    console.print()
    console.print("[bold]Code Guro Convert[/bold]")
    console.print()

    # Validate directory exists
    if not output_path.exists():
        console.print(f"[red]Error:[/red] Directory not found: {output_dir}")
        console.print()
        console.print("Run [bold cyan]code-guro analyze[/bold cyan] first to generate documentation.")
        sys.exit(1)

    if not output_path.is_dir():
        console.print(f"[red]Error:[/red] Not a directory: {output_dir}")
        sys.exit(1)

    # Check for markdown files
    md_files = list(output_path.glob("*.md"))
    if not md_files:
        console.print(f"[yellow]Warning:[/yellow] No markdown files found in {output_dir}")
        console.print()
        console.print("This directory doesn't appear to contain Code Guro output.")
        sys.exit(1)

    try:
        console.print(f"[dim]Converting {len(md_files)} markdown file(s) to HTML...[/dim]")
        console.print("[dim]Organizing files into subdirectories...[/dim]")
        console.print()

        # Create subdirectories
        markdown_dir = output_path / "markdown"
        html_dir = output_path / "html"
        markdown_dir.mkdir(exist_ok=True)
        html_dir.mkdir(exist_ok=True)

        # Move markdown files to markdown/ subdirectory
        import shutil

        for md_file in md_files:
            dest = markdown_dir / md_file.name
            shutil.move(str(md_file), str(dest))

        # Convert markdown to HTML in html/ subdirectory
        from code_guro.html_converter import convert_directory_to_html_organized

        convert_directory_to_html_organized(markdown_dir, html_dir)

        # List generated files
        md_files_moved = sorted(markdown_dir.glob("*.md"))
        html_files = sorted(html_dir.glob("*.html"))

        console.print("[bold green]Conversion complete![/bold green]")
        console.print()
        console.print("Directory structure:")
        console.print(f"  [cyan]{output_path.name}/[/cyan]")
        console.print(f"    [cyan]markdown/[/cyan] ({len(md_files_moved)} files)")
        console.print(f"    [cyan]html/[/cyan] ({len(html_files)} files)")
        console.print()
        console.print(f"[dim]Open {html_dir}/00-overview.html in your browser![/dim]")
        console.print()

    except Exception as e:
        console.print(f"[red]Error during conversion:[/red] {str(e)}")
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
    from code_guro.generator import create_output_dir, generate_explain_document
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
        from code_guro.providers.factory import get_provider

        try:
            provider = get_provider()
            provider_name = provider.get_provider_name().lower()
        except Exception:
            provider_name = None
        handle_api_error(e, provider_name)
        sys.exit(1)


@main.command()
def configure():
    """Configure Code Guro with your LLM provider.

    This command will prompt you to select a provider and guide you through
    setting up the API key as an environment variable.
    """
    from code_guro.providers.factory import get_provider, list_providers

    console.print()
    console.print("[bold]Code Guro Configuration[/bold]")
    console.print()

    # Check if already configured
    current_provider_name = get_provider_config()
    if current_provider_name:
        try:
            current_provider = get_provider(current_provider_name)
            current_key = current_provider.get_api_key()
            if current_key:
                console.print(f"Current provider: [cyan]{current_provider.get_provider_name()}[/cyan]")
                console.print(f"Current API key: [cyan]{mask_api_key(current_key)}[/cyan]")
                console.print()

                change_provider = Prompt.ask(
                    "Do you want to change the provider?",
                    choices=["y", "n"],
                    default="n",
                )
                if change_provider != "y":
                    console.print("[yellow]Configuration unchanged.[/yellow]")
                    return
        except Exception:
            # Provider config exists but invalid, allow reconfiguration
            pass

    # Provider selection
    providers = list_providers()

    console.print("Select your LLM provider:")
    console.print()
    for i, provider_id in enumerate(providers, 1):
        provider = get_provider(provider_id)
        console.print(f"  {i}. {provider.get_provider_name()}")
    console.print()

    try:
        choice = Prompt.ask("Choice", choices=[str(i) for i in range(1, len(providers) + 1)])
        selected_provider_id = providers[int(choice) - 1]
    except (ValueError, IndexError, KeyboardInterrupt):
        console.print("[yellow]Configuration cancelled.[/yellow]")
        sys.exit(0)

    selected_provider = get_provider(selected_provider_id)
    selected_name = selected_provider.get_provider_name()
    selected_env_var = selected_provider.get_api_key_env_var()
    selected_url = selected_provider.get_api_key_url()
    console.print()
    console.print(f"[bold]Setting up {selected_name}[/bold]")
    console.print()
    console.print(f"Please set your {selected_name} API key as an environment variable:")
    console.print()
    console.print(f"  [cyan]export {selected_env_var}=\"your-key-here\"[/cyan]")
    console.print()
    console.print("You can add this to your ~/.zshrc or ~/.bashrc to make it permanent.")
    console.print()
    console.print(f"Get your API key at: [link={selected_url}]{selected_url}[/link]")
    console.print()

    # Get provider instance and validate
    try:
        api_key = selected_provider.get_api_key()

        if not api_key:
            use_pasted_key = Prompt.ask(
                f"{selected_env_var} not found. Paste API key now to validate?",
                choices=["y", "n"],
                default="n",
            )
            if use_pasted_key != "y":
                console.print()
                console.print(
                    f"[yellow]Configuration not saved.[/yellow]\n\n"
                    f"Please set {selected_env_var} and run "
                    f"[bold cyan]code-guro configure[/bold cyan] again."
                )
                sys.exit(0)

            api_key = Prompt.ask("API key", password=True)
            if not api_key:
                console.print("[red]Error:[/red] API key cannot be empty.")
                sys.exit(1)

        # Validate the key
        console.print()
        console.print("[dim]Validating API key...[/dim]")

        is_valid, message = selected_provider.validate_api_key(api_key)

        if not is_valid:
            console.print(f"[red]Error: {message}[/red]")
            console.print()
            console.print("Please check your API key and try again.")
            sys.exit(1)

        # Save provider selection
        save_provider_config(selected_provider_id)

        console.print()
        console.print("[green]✓ API key validated successfully![/green]")
        console.print(f"[green]✓ Provider saved: {selected_name}[/green]")
        if not selected_provider.get_api_key():
            console.print(
                f"[yellow]Note:[/yellow] API keys are not stored by Code Guro.\n"
                f"Make sure {selected_env_var} is set before running commands."
            )
        console.print()
        console.print("You can now use [bold cyan]code-guro analyze[/bold cyan] to analyze a codebase.")

    except Exception as e:
        console.print(f"[red]Error:[/red] {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()
