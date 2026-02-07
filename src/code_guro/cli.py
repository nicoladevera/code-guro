"""Code Guro CLI - Main entry point."""

import functools
import sys

# Filter out noisy dependency warnings that users can't act on
# These are from Google libraries and urllib3, not Code Guro itself
# Must be after imports but before other code to be effective
import warnings  # noqa: E402
from pathlib import Path
from typing import Callable, Optional

warnings.filterwarnings("ignore", category=FutureWarning, module="google.*")
warnings.filterwarnings("ignore", category=FutureWarning, module="urllib3.*")
warnings.filterwarnings("ignore", message=".*OpenSSL.*")
warnings.filterwarnings("ignore", message=".*google.generativeai.*")

import click  # noqa: E402
from rich.console import Console  # noqa: E402
from rich.prompt import Prompt  # noqa: E402

from code_guro import __version__  # noqa: E402
from code_guro.config import (  # noqa: E402
    get_api_key,
    get_config_file,
    get_provider_config,
    mask_api_key,
    require_provider,
    save_provider_config,
)
from code_guro.errors import check_internet_connection, handle_api_error  # noqa: E402

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


def handle_zero_argument_flow(ctx):
    """Handle 'code-guro' with no arguments - smart default behavior."""
    import time

    from rich.prompt import Confirm

    from code_guro.analyzer import analyze_codebase
    from code_guro.config import get_preference, is_provider_configured
    from code_guro.utils import format_cost

    cwd = Path.cwd()

    # Check emoji preference
    use_emoji = get_preference("emoji_enabled", True)

    console.print()
    if use_emoji:
        console.print("[bold]👋 Welcome to Code Guro![/bold]")
    else:
        console.print("[bold]Welcome to Code Guro![/bold]")
    console.print()

    # Check if provider configured
    if not is_provider_configured():
        console.print("[yellow]No provider configured yet.[/yellow]")
        console.print()
        if Confirm.ask("Would you like to configure Code Guro now?"):
            ctx.invoke(configure)
            console.print()
            console.print("Great! Now let's analyze your project.")
            console.print()
        else:
            console.print()
            console.print(
                "Run [bold cyan]code-guro configure[/bold cyan] when you're ready to set up."
            )
            console.print()
            console.print("For more information:")
            console.print("  [cyan]code-guro --help[/cyan]")
            sys.exit(0)

    # Check for edge case: home directory
    if cwd == Path.home():
        console.print(
            "[yellow]Warning:[/yellow] You're in your home directory.\n"
            "This may analyze thousands of files and could be expensive.\n"
        )
        if not Confirm.ask("Continue anyway?", default=False):
            console.print()
            console.print("[dim]Navigate to a project directory first:[/dim]")
            console.print("  [cyan]cd /path/to/your/project[/cyan]")
            console.print("  [cyan]code-guro[/cyan]")
            console.print()
            console.print("[dim]Or specify a path:[/dim]")
            console.print("  [cyan]code-guro analyze /path/to/project[/cyan]")
            sys.exit(0)
        console.print()

    # Check if recently analyzed
    output_dir = cwd / "code-guro-output"
    if output_dir.exists():
        try:
            mtime = output_dir.stat().st_mtime
            age_hours = (time.time() - mtime) / 3600

            if age_hours < 24:
                console.print(f"[dim]This project was analyzed {int(age_hours)} hours ago.[/dim]")
                console.print()
                if not Confirm.ask("Re-analyze now?", default=True):
                    console.print()
                    console.print("[dim]Opening existing documentation...[/dim]")
                    html_dir = output_dir / "html"
                    if html_dir.exists():
                        overview = html_dir / "00-overview.html"
                        if overview.exists():
                            console.print(f"[green]Open:[/green] {overview}")
                    else:
                        md_dir = (
                            output_dir / "markdown"
                            if (output_dir / "markdown").exists()
                            else output_dir
                        )
                        overview = md_dir / "00-overview.md"
                        if overview.exists():
                            console.print(f"[green]Open:[/green] {overview}")
                    sys.exit(0)
                console.print()
        except Exception:
            # Ignore errors checking file modification time
            pass

    # Run dry-run scan
    console.print("[dim]Scanning project...[/dim]")
    console.print()

    try:
        result = analyze_codebase(str(cwd), show_progress=False, dry_run=True)

        if not result.files and result.total_tokens == 0:
            # Try to count files another way for better error message
            file_count = sum(1 for _ in cwd.rglob("*") if _.is_file())

            console.print("[yellow]No analyzable code files found in this directory.[/yellow]\n")

            if file_count > 0:
                console.print(
                    f"[dim]Found {file_count} files, but they may be binary, too large, or in ignored directories.[/dim]\n"
                )

            console.print("Try:")
            console.print("  • Navigate to a project directory with code files")
            console.print("  • Specify a different path:")
            console.print("    [cyan]code-guro analyze /path/to/project[/cyan]")
            sys.exit(1)

        # Display project preview
        file_count = result.total_tokens // 200  # Rough estimate from dry-run
        framework_names = (
            ", ".join(f.name for f in result.frameworks) if result.frameworks else "None detected"
        )

        console.print(f"[bold]Found project at:[/bold] {cwd}")
        if result.frameworks:
            console.print(f"[bold]Framework detected:[/bold] {framework_names}")
        console.print(f"[bold]Estimated files:[/bold] ~{file_count} files")
        console.print(f"[bold]Estimated tokens:[/bold] ~{result.total_tokens:,}")
        console.print(f"[bold]Estimated cost:[/bold] {format_cost(result.estimated_cost)}")
        console.print()

        # Confirm analysis
        if Confirm.ask("Analyze this project?", default=True):
            console.print()
            # Invoke analyze command
            ctx.invoke(analyze, path=str(cwd), markdown_only=False, no_emoji=not use_emoji)
        else:
            console.print()
            console.print("[yellow]Analysis cancelled.[/yellow]")
            console.print()
            console.print(
                "[dim]Run[/dim] [cyan]code-guro analyze <path>[/cyan] [dim]to analyze a specific directory.[/dim]"
            )

    except Exception as e:
        console.print(f"[red]Error:[/red] {str(e)}")
        console.print()
        console.print("Try running with a specific path:")
        console.print("  [cyan]code-guro analyze /path/to/project[/cyan]")
        sys.exit(1)


@click.group(invoke_without_command=True)
@click.pass_context
@click.version_option(version=__version__, prog_name="code-guro")
def main(ctx):
    """Code Guro - Understand your codebase like a guru.

    A CLI tool to help non-technical product managers and AI-native builders
    understand codebases through structured, beginner-friendly documentation.
    """
    # If no subcommand provided, handle zero-argument flow
    if ctx.invoked_subcommand is None:
        handle_zero_argument_flow(ctx)


@main.command()
@click.argument("path", type=click.Path(exists=False))
@click.option(
    "--markdown-only",
    is_flag=True,
    help="Generate only markdown files (default: generates both HTML and markdown)",
)
@click.option(
    "--no-emoji",
    is_flag=True,
    help="Disable emoji in console output",
)
@require_internet_decorator
@require_api_key_decorator
def analyze(path: str, markdown_only: bool, no_emoji: bool):
    """Analyze a codebase and generate learning documentation.

    By default, generates both HTML and markdown files organized in subdirectories.
    HTML files include fully rendered Mermaid diagrams for the best viewing experience.

    PATH can be a local directory or a GitHub repository URL.

    Examples:

        code-guro analyze .

        code-guro analyze /path/to/project

        code-guro analyze https://github.com/user/repo

        code-guro analyze . --markdown-only

        code-guro analyze . --no-emoji
    """
    import time

    from code_guro.analyzer import analyze_codebase, confirm_analysis
    from code_guro.config import get_preference, set_preference
    from code_guro.generator import generate_documentation
    from code_guro.utils import is_github_url

    # Check emoji preference (flag overrides config)
    if no_emoji:
        use_emoji = False
    else:
        use_emoji = get_preference("emoji_enabled", True)

    # Save preference if explicitly set via flag
    if no_emoji and get_preference("emoji_enabled") is not False:
        set_preference("emoji_enabled", False)

    # Progress indicators
    check_mark = "✓" if use_emoji else "✓"
    hourglass = "⏳" if use_emoji else "..."
    chart = "📊" if use_emoji else "*"
    doc = "📄" if use_emoji else "*"
    globe = "🌐" if use_emoji else "*"

    console.print()
    if use_emoji:
        console.print(f"[bold]{chart} Understanding your codebase...[/bold]")
    else:
        console.print("[bold]Understanding your codebase...[/bold]")
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

    # Track milestones
    milestones = []

    def track_progress(event: str, data: dict):
        """Progress callback for milestone tracking."""
        if event == "scan_complete":
            duration = data.get("duration", 0)
            file_count = data.get("file_count", 0)
            milestones.append(
                (
                    "scan",
                    f"{check_mark} Scanned {file_count} files ({duration:.1f} seconds)",
                )
            )
            console.print(milestones[-1][1])
        elif event == "framework_detected":
            duration = data.get("duration", 0)
            frameworks = data.get("frameworks", [])
            framework_names = ", ".join(f.name for f in frameworks)
            milestones.append(
                (
                    "framework",
                    f"{check_mark} Detected {framework_names} ({duration:.1f} seconds)",
                )
            )
            console.print(milestones[-1][1])

    try:
        # Analyze codebase
        analysis_start = time.time()
        result = analyze_codebase(path, progress_callback=track_progress)

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
        time.time()

        # Estimate time based on tokens (rough estimate: 1000 tokens per second)
        estimated_seconds = result.total_tokens / 1000
        console.print(
            f"{hourglass} Generating documentation... "
            f"(~{int(estimated_seconds)} seconds estimated)"
        )

        output_dir = generate_documentation(result, markdown_only=markdown_only)

        total_elapsed = time.time() - analysis_start

        console.print(f"{check_mark} Documentation ready! ({int(total_elapsed)} seconds total)")
        console.print()

        # Print summary
        console.print("[bold green]Analysis complete![/bold green]")
        console.print()

        if markdown_only:
            console.print(f"{doc} Generated documents:")
            for f in sorted(output_dir.glob("*.md")):
                console.print(f"  • [cyan]{f.name}[/cyan]")
            console.print()
            console.print(f"[dim]Open {output_dir}/00-overview.md to start learning![/dim]")
        else:
            # Both formats generated in subdirectories
            output_dir / "markdown"
            html_dir = output_dir / "html"

            console.print(f"{doc} Generated documentation:")
            console.print("  • [bold]Overview[/bold] - What your app does")
            console.print("  • [bold]Getting Oriented[/bold] - File structure explained")
            console.print("  • [bold]Architecture[/bold] - How it's built")
            console.print("  • [bold]Core Files[/bold] - The important stuff")
            console.print("  • [bold]Deep Dives[/bold] - Detailed explanations")
            console.print("  • [bold]Quality Analysis[/bold] - What's good, what needs attention")
            console.print("  • [bold]Next Steps[/bold] - Where to explore next")
            console.print()
            console.print(
                f"{globe} [dim]Open {html_dir}/00-overview.html in your browser for the best experience![/dim]"
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
        console.print(
            "Run [bold cyan]code-guro analyze[/bold cyan] first to generate documentation."
        )
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

    This command will guide you through selecting a provider and setting up
    your API key with interactive prompts and immediate validation.
    """
    from rich.prompt import Confirm

    from code_guro.config import get_preference, save_api_key_to_config
    from code_guro.providers.factory import get_provider, list_providers

    # Check emoji preference
    use_emoji = get_preference("emoji_enabled", True)
    check_mark = "✓" if use_emoji else "✓"

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
                console.print(
                    f"[dim]Current provider:[/dim] [cyan]{current_provider.get_provider_name()}[/cyan]"
                )
                console.print(
                    f"[dim]Current API key:[/dim] [cyan]{mask_api_key(current_key)}[/cyan]"
                )
                console.print()

                if not Confirm.ask("Would you like to change your configuration?", default=False):
                    console.print("[yellow]Configuration unchanged.[/yellow]")
                    return
                console.print()
        except Exception:
            # Provider config exists but invalid, allow reconfiguration
            pass

    # Provider selection with detailed descriptions
    providers_info = {
        "anthropic": {
            "name": "Anthropic Claude (Claude Sonnet 4)",
            "best_for": "Code understanding and documentation",
            "cost": "$3/$15 per million tokens (input/output)",
            "url": "https://console.anthropic.com",
        },
        "openai": {
            "name": "OpenAI (GPT-4o)",
            "best_for": "General-purpose code analysis",
            "cost": "$2.50/$10 per million tokens (input/output)",
            "url": "https://platform.openai.com",
        },
        "google": {
            "name": "Google Gemini (Gemini 2.0 Flash)",
            "best_for": "Cost-effective analysis",
            "cost": "$0.075/$0.30 per million tokens (input/output)",
            "url": "https://aistudio.google.com",
        },
    }

    console.print("[bold]Select your LLM provider:[/bold]")
    console.print()

    providers = list_providers()
    for i, provider_id in enumerate(providers, 1):
        info = providers_info.get(provider_id, {})
        console.print(f"  [bold]{i}. {info.get('name', provider_id)}[/bold]")
        console.print(f"     [dim]• Best for:[/dim] {info.get('best_for', 'N/A')}")
        console.print(f"     [dim]• Cost:[/dim] {info.get('cost', 'N/A')}")
        console.print(f"     [dim]• Get API key:[/dim] {info.get('url', 'N/A')}")
        console.print()

    try:
        choice = Prompt.ask(
            "Enter choice",
            choices=[str(i) for i in range(1, len(providers) + 1)],
            default="1",
        )
        selected_provider_id = providers[int(choice) - 1]
    except (ValueError, IndexError, KeyboardInterrupt):
        console.print("[yellow]Configuration cancelled.[/yellow]")
        sys.exit(0)

    selected_provider = get_provider(selected_provider_id)
    selected_name = selected_provider.get_provider_name()
    selected_url = selected_provider.get_api_key_url()

    console.print()
    console.print(f"[bold]Setting up {selected_name}[/bold]")
    console.print()

    # Check if API key is already set in environment
    api_key = selected_provider.get_api_key()

    if api_key:
        console.print(f"[dim]Found API key in config or environment: {mask_api_key(api_key)}[/dim]")
        if Confirm.ask("Use this API key?", default=True):
            # Validate existing key
            console.print()
            console.print("[dim]Validating API key...[/dim]")
            is_valid, message = selected_provider.validate_api_key(api_key)

            if not is_valid:
                console.print(f"[red]Error:[/red] {message}")
                console.print()
                console.print("Please enter a valid API key below.")
                api_key = None
            else:
                console.print()
                console.print(f"[green]{check_mark} API key is valid![/green]")
                save_provider_config(selected_provider_id)
                console.print(f"[green]{check_mark} Provider saved: {selected_name}[/green]")
                console.print()
                console.print(
                    "You can now use [bold cyan]code-guro analyze[/bold cyan] to analyze a codebase."
                )
                return
        else:
            # User declined to use existing key - prompt for new one
            api_key = None

    # Prompt for API key input
    if not api_key:
        console.print(f"Please enter your {selected_name} API key:")
        console.print(f"[dim]Get your key at: {selected_url}[/dim]")
        console.print()

        api_key = Prompt.ask("API key (will be hidden)", password=True)

        if not api_key or not api_key.strip():
            console.print("[red]Error:[/red] API key cannot be empty.")
            sys.exit(1)

        api_key = api_key.strip()

    # Validate the key
    console.print()
    console.print("[dim]Validating API key...[/dim]")

    is_valid, message = selected_provider.validate_api_key(api_key)

    if not is_valid:
        console.print()
        console.print(f"[red]Error:[/red] {message}")
        console.print()
        console.print("Please check your API key and try again.")
        console.print("Run [bold cyan]code-guro configure[/bold cyan] to retry.")
        sys.exit(1)

    # Save configuration
    save_provider_config(selected_provider_id)
    save_api_key_to_config(selected_provider_id, api_key)

    console.print()
    console.print(
        f"[green]{check_mark} Success! Your API key is valid and has been saved securely.[/green]"
    )
    console.print()
    console.print(f"[dim]Configuration saved to: {get_config_file()}[/dim]")
    console.print()
    console.print("[bold]You're all set![/bold] Try analyzing a project:")
    console.print("  [cyan]cd /path/to/your/project[/cyan]")
    console.print("  [cyan]code-guro[/cyan]")
    console.print()
    console.print("[dim]Or specify a path explicitly:[/dim]")
    console.print("  [cyan]code-guro analyze /path/to/project[/cyan]")
    console.print()


if __name__ == "__main__":
    main()
