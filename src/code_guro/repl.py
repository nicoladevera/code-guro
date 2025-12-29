"""Interactive REPL mode for Code Guro.

Provides a conversational interface for exploring code.
"""

from datetime import datetime
from pathlib import Path
from typing import List, Tuple

import anthropic
from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel
from rich.prompt import Prompt

from code_guro.config import get_api_key
from code_guro.frameworks import FrameworkInfo
from code_guro.generator import create_output_dir
from code_guro.prompts import INTERACTIVE_SYSTEM_PROMPT

console = Console()

# Model for interactive mode (use faster model for responsiveness)
MODEL = "claude-sonnet-4-20250514"

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
    api_key = get_api_key()
    client = anthropic.Anthropic(api_key=api_key)

    system_prompt = create_system_prompt(path, content, frameworks)
    conversation_history: List[Tuple[str, str]] = []
    messages: List[dict] = []

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

            # Add user message
            messages.append({"role": "user", "content": question})

            # Check if conversation is getting too long
            if len(messages) > MAX_HISTORY_PAIRS * 2:
                console.print(
                    "[yellow]Note:[/yellow] Conversation is getting long. "
                    "Consider starting a fresh session for best results."
                )
                # Keep only the last N pairs
                messages = messages[-(MAX_HISTORY_PAIRS * 2):]

            # Call API
            console.print()
            console.print("[dim]Thinking...[/dim]")

            try:
                response = client.messages.create(
                    model=MODEL,
                    max_tokens=2048,
                    system=system_prompt,
                    messages=messages,
                )

                answer = response.content[0].text

                # Add assistant message to history
                messages.append({"role": "assistant", "content": answer})
                conversation_history.append((question, answer))

                # Display response with markdown formatting
                console.print()
                console.print(Markdown(answer))
                console.print()

            except anthropic.RateLimitError:
                console.print(
                    "[yellow]Rate limit reached.[/yellow] "
                    "Please wait a moment before asking another question."
                )
                # Remove the user message since we didn't get a response
                messages.pop()

            except anthropic.APIConnectionError:
                console.print(
                    "[red]Connection error.[/red] "
                    "Please check your internet connection and try again."
                )
                # Remove the user message since we didn't get a response
                messages.pop()

            except Exception as e:
                console.print(f"[red]Error:[/red] {str(e)}")
                # Remove the user message since we didn't get a response
                messages.pop()

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
