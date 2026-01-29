"""Interactive REPL mode for Code Guro.

Provides a conversational interface for exploring code.
"""

from datetime import datetime
from pathlib import Path
from typing import List, Tuple

from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel
from rich.prompt import Prompt

from code_guro.frameworks import FrameworkInfo
from code_guro.generator import create_output_dir
from code_guro.prompts import INTERACTIVE_SYSTEM_PROMPT
from code_guro.providers.factory import get_provider

console = Console()

# Maximum conversation history to maintain
MAX_HISTORY_PAIRS = 10


def create_system_prompt(path: Path, content: str, frameworks: List[FrameworkInfo]) -> str:
    """Create a system prompt for interactive mode.

    Args:
        path: Path being explained
        content: Content of the file/folder
        frameworks: Detected frameworks

    Returns:
        System prompt string
    """
    framework_context = ""
    if frameworks:
        framework_context = "Detected frameworks: " + ", ".join(f.name for f in frameworks)

    return INTERACTIVE_SYSTEM_PROMPT.format(
        path=str(path),
        content=content[:50000],  # Limit content to avoid token limits
        framework=framework_context or "No specific framework detected",
    )


def format_session_log(
    path: Path,
    history: List[Tuple[str, str]],
) -> str:
    """Format conversation history as markdown.

    Args:
        path: Path being explained
        history: List of (question, answer) tuples

    Returns:
        Markdown formatted session log
    """
    lines = [
        f"# Interactive Session: {path.name}",
        "",
        f"**Date:** {datetime.now().strftime('%Y-%m-%d %H:%M')}",
        f"**Path:** `{path}`",
        "",
        "---",
        "",
    ]

    for i, (question, answer) in enumerate(history, 1):
        lines.append(f"## Question {i}")
        lines.append("")
        lines.append(f"> {question}")
        lines.append("")
        lines.append("### Answer")
        lines.append("")
        lines.append(answer)
        lines.append("")
        lines.append("---")
        lines.append("")

    return "\n".join(lines)


def start_repl(
    path: Path,
    content: str,
    frameworks: List[FrameworkInfo],
) -> None:
    """Start an interactive REPL session.

    Args:
        path: Path to the file/folder being explained
        content: Content of the file/folder
        frameworks: Detected frameworks
    """
    provider = get_provider()
    system_prompt = create_system_prompt(path, content, frameworks)
    conversation_history: List[Tuple[str, str]] = []
    # Store conversation as simple prompt strings for provider abstraction
    conversation_context = ""

    # Welcome message
    console.print()
    console.print(
        Panel(
            f"[bold]Interactive Mode[/bold]\n\n"
            f"Exploring: [cyan]{path}[/cyan]\n\n"
            f"Ask questions about this code, or type [bold]exit[/bold] to quit.",
            title="Code Guro",
            border_style="cyan",
        )
    )
    console.print()

    try:
        while True:
            # Get user input
            try:
                question = Prompt.ask("[bold cyan]code-guro[/bold cyan]")
            except (EOFError, KeyboardInterrupt):
                console.print("\n")
                break

            # Check for exit commands
            if question.lower().strip() in ("exit", "quit", "q"):
                break

            if not question.strip():
                continue

            # Build prompt with conversation history
            # For simplicity, include recent conversation in the prompt
            # This works across all providers
            prompt_parts = []
            if conversation_context:
                prompt_parts.append("Previous conversation:")
                prompt_parts.append(conversation_context)
                prompt_parts.append("")
            prompt_parts.append(f"User question: {question}")

            full_prompt = "\n".join(prompt_parts)

            # Check if conversation is getting too long
            if len(conversation_history) >= MAX_HISTORY_PAIRS:
                console.print(
                    "[yellow]Note:[/yellow] Conversation is getting long. "
                    "Consider starting a fresh session for best results."
                )
                # Keep only the last N pairs
                conversation_history = conversation_history[-MAX_HISTORY_PAIRS:]
                # Rebuild context from remaining history
                conversation_context = "\n".join(
                    f"Q: {q}\nA: {a}" for q, a in conversation_history
                )

            # Call API
            console.print()
            console.print("[dim]Thinking...[/dim]")

            try:
                answer = provider.call(
                    prompt=full_prompt,
                    system=system_prompt,
                    max_tokens=2048,
                )

                # Add to conversation history
                conversation_history.append((question, answer))
                # Update context (keep last few exchanges)
                recent_history = conversation_history[-3:]  # Last 3 Q&A pairs
                conversation_context = "\n".join(
                    f"Q: {q}\nA: {a}" for q, a in recent_history
                )

                # Display response with markdown formatting
                console.print()
                console.print(Markdown(answer))
                console.print()

            except Exception as e:
                from code_guro.errors import handle_api_error

                error_msg = str(e).lower()
                if "rate limit" in error_msg or "quota" in error_msg:
                    console.print(
                        "[yellow]Rate limit reached.[/yellow] "
                        "Please wait a moment before asking another question."
                    )
                elif "connection" in error_msg or "network" in error_msg:
                    console.print(
                        "[red]Connection error.[/red] "
                        "Please check your internet connection and try again."
                    )
                else:
                    handle_api_error(e, provider.get_provider_name().lower())

    except KeyboardInterrupt:
        console.print("\n")

    # Save session log
    if conversation_history:
        try:
            # Find project root for output
            parent = path.parent if path.is_file() else path
            while parent != parent.parent:
                if (parent / "package.json").exists() or (parent / "pyproject.toml").exists():
                    break
                parent = parent.parent

            output_dir = create_output_dir(parent)
            session_log = format_session_log(path, conversation_history)

            filename = f"explain-{path.name.replace('/', '-')}-session.md"
            filepath = output_dir / filename
            filepath.write_text(session_log)

            console.print()
            console.print(f"[dim]Session saved to: {filepath}[/dim]")

        except Exception as e:
            console.print(f"[yellow]Could not save session:[/yellow] {str(e)}")

    console.print()
    console.print("[dim]Goodbye![/dim]")
