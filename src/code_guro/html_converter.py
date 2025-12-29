"""HTML conversion for Code Guro.

Converts markdown documentation to styled HTML with Mermaid support.
"""

from pathlib import Path
from typing import List

import markdown
from rich.console import Console

console = Console()

# HTML template with embedded CSS
HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Code Guro - {title}</title>
    <script src="https://cdn.jsdelivr.net/npm/mermaid/dist/mermaid.min.js"></script>
    <style>
        :root {{
            --bg-color: #ffffff;
            --text-color: #1a1a1a;
            --code-bg: #f5f5f5;
            --border-color: #e0e0e0;
            --link-color: #0066cc;
            --heading-color: #2c3e50;
        }}

        @media (prefers-color-scheme: dark) {{
            :root {{
                --bg-color: #1a1a2e;
                --text-color: #e0e0e0;
                --code-bg: #16213e;
                --border-color: #3a3a5a;
                --link-color: #64b5f6;
                --heading-color: #90caf9;
            }}
        }}

        * {{
            box-sizing: border-box;
        }}

        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, sans-serif;
            line-height: 1.7;
            color: var(--text-color);
            background-color: var(--bg-color);
            max-width: 900px;
            margin: 0 auto;
            padding: 2rem;
        }}

        h1, h2, h3, h4, h5, h6 {{
            color: var(--heading-color);
            margin-top: 2rem;
            margin-bottom: 1rem;
            font-weight: 600;
        }}

        h1 {{
            font-size: 2.5rem;
            border-bottom: 2px solid var(--border-color);
            padding-bottom: 0.5rem;
        }}

        h2 {{
            font-size: 1.75rem;
            border-bottom: 1px solid var(--border-color);
            padding-bottom: 0.3rem;
        }}

        h3 {{
            font-size: 1.4rem;
        }}

        p {{
            margin: 1rem 0;
        }}

        a {{
            color: var(--link-color);
            text-decoration: none;
        }}

        a:hover {{
            text-decoration: underline;
        }}

        code {{
            font-family: 'SF Mono', 'Fira Code', 'Consolas', monospace;
            font-size: 0.9em;
            background-color: var(--code-bg);
            padding: 0.2em 0.4em;
            border-radius: 4px;
        }}

        pre {{
            background-color: var(--code-bg);
            padding: 1rem;
            border-radius: 8px;
            overflow-x: auto;
            border: 1px solid var(--border-color);
        }}

        pre code {{
            background: none;
            padding: 0;
        }}

        blockquote {{
            border-left: 4px solid var(--link-color);
            margin: 1rem 0;
            padding: 0.5rem 1rem;
            background-color: var(--code-bg);
            border-radius: 0 8px 8px 0;
        }}

        ul, ol {{
            padding-left: 2rem;
        }}

        li {{
            margin: 0.5rem 0;
        }}

        table {{
            width: 100%;
            border-collapse: collapse;
            margin: 1rem 0;
        }}

        th, td {{
            border: 1px solid var(--border-color);
            padding: 0.75rem;
            text-align: left;
        }}

        th {{
            background-color: var(--code-bg);
            font-weight: 600;
        }}

        tr:nth-child(even) {{
            background-color: var(--code-bg);
        }}

        .mermaid {{
            margin: 2rem 0;
            text-align: center;
        }}

        nav {{
            background-color: var(--code-bg);
            padding: 1rem;
            border-radius: 8px;
            margin-bottom: 2rem;
        }}

        nav ul {{
            list-style: none;
            padding: 0;
            margin: 0;
            display: flex;
            flex-wrap: wrap;
            gap: 1rem;
        }}

        nav li {{
            margin: 0;
        }}

        nav a {{
            display: inline-block;
            padding: 0.5rem 1rem;
            background-color: var(--bg-color);
            border-radius: 4px;
            border: 1px solid var(--border-color);
        }}

        nav a:hover {{
            background-color: var(--link-color);
            color: white;
            text-decoration: none;
        }}

        nav a.current {{
            background-color: var(--link-color);
            color: white;
        }}

        hr {{
            border: none;
            border-top: 1px solid var(--border-color);
            margin: 2rem 0;
        }}

        .footer {{
            margin-top: 4rem;
            padding-top: 2rem;
            border-top: 1px solid var(--border-color);
            text-align: center;
            color: #888;
            font-size: 0.9rem;
        }}

        @media (max-width: 768px) {{
            body {{
                padding: 1rem;
            }}

            h1 {{
                font-size: 1.75rem;
            }}

            h2 {{
                font-size: 1.4rem;
            }}

            nav ul {{
                flex-direction: column;
            }}

            pre {{
                font-size: 0.85em;
            }}
        }}
    </style>
</head>
<body>
    <nav>
        <ul>
            {navigation}
        </ul>
    </nav>

    <main>
        {content}
    </main>

    <footer class="footer">
        Generated by <a href="https://github.com/nicoladevera/code-guro">Code Guro</a>
    </footer>

    <script>
        // Initialize Mermaid
        mermaid.initialize({{
            startOnLoad: true,
            theme: window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'default',
            securityLevel: 'loose'
        }});

        // Handle mermaid code blocks
        document.querySelectorAll('pre code.language-mermaid').forEach(function(block) {{
            const pre = block.parentElement;
            const div = document.createElement('div');
            div.className = 'mermaid';
            div.textContent = block.textContent;
            pre.parentElement.replaceChild(div, pre);
        }});
    </script>
</body>
</html>"""


def get_navigation_links(files: List[Path], current: Path) -> str:
    """Generate navigation links for HTML files.

    Args:
        files: List of all HTML files
        current: Current file

    Returns:
        HTML string with navigation links
    """
    links = []
    for f in sorted(files):
        name = f.stem.replace("-", " ").title()
        # Clean up the name
        if name.startswith("0"):
            name = name[3:]  # Remove "00 ", "01 ", etc.

        css_class = ' class="current"' if f == current else ""
        links.append(f'<li><a href="{f.name}"{css_class}>{name}</a></li>')

    return "\n            ".join(links)


def convert_markdown_to_html(md_content: str) -> str:
    """Convert markdown content to HTML.

    Args:
        md_content: Markdown content

    Returns:
        HTML content
    """
    # Configure markdown extensions
    md = markdown.Markdown(
        extensions=[
            "fenced_code",
            "tables",
            "toc",
            "nl2br",
            "sane_lists",
        ]
    )

    return md.convert(md_content)


def convert_file_to_html(md_path: Path, all_files: List[Path]) -> str:
    """Convert a markdown file to HTML.

    Args:
        md_path: Path to markdown file
        all_files: List of all HTML files for navigation

    Returns:
        Complete HTML document
    """
    # Read markdown content
    md_content = md_path.read_text()

    # Convert to HTML
    html_content = convert_markdown_to_html(md_content)

    # Get title from first heading or filename
    title = md_path.stem.replace("-", " ").title()
    if title.startswith("0"):
        title = title[3:]  # Remove number prefix

    # Generate navigation
    html_files = [f.with_suffix(".html") for f in all_files]
    current_html = md_path.with_suffix(".html")
    navigation = get_navigation_links(html_files, current_html)

    # Fill template
    return HTML_TEMPLATE.format(
        title=title,
        navigation=navigation,
        content=html_content,
    )


def convert_directory_to_html(output_dir: Path) -> None:
    """Convert all markdown files in a directory to HTML.

    Args:
        output_dir: Directory containing markdown files
    """
    from rich.progress import Progress, SpinnerColumn, TextColumn

    md_files = list(output_dir.glob("*.md"))

    if not md_files:
        console.print("[yellow]No markdown files found to convert.[/yellow]")
        return

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
        transient=True,
    ) as progress:
        task = progress.add_task("Converting to HTML...", total=len(md_files))

        for md_file in md_files:
            progress.update(task, description=f"Converting {md_file.name}...")

            try:
                html_content = convert_file_to_html(md_file, md_files)
                html_path = md_file.with_suffix(".html")
                html_path.write_text(html_content)
            except Exception as e:
                console.print(f"[yellow]Warning:[/yellow] Could not convert {md_file.name}: {e}")

            progress.advance(task)

    console.print(f"[green]Converted {len(md_files)} files to HTML[/green]")
