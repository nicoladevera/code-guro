"""HTML conversion for Code Guro.

Converts markdown documentation to styled HTML with Mermaid support.
"""

from pathlib import Path
from typing import List

import markdown
from rich.console import Console

console = Console()

# HTML template with embedded CSS - Yuno-inspired modern design
HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Code Guro - {title}</title>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,500;9..144,600;9..144,700&family=Inter:wght@400;500;600&family=JetBrains+Mono:wght@400;500&display=swap" rel="stylesheet">
    <script src="https://cdn.jsdelivr.net/npm/mermaid/dist/mermaid.min.js"></script>
    <style>
        :root {{
            --bg-page: #e8e8f0;
            --bg-card: #ffffff;
            --bg-card-alt: #f4f4f8;
            --bg-code: #f0f0f6;
            --text-primary: #1a1a2e;
            --text-secondary: #5a5a6e;
            --text-muted: #8a8a9a;
            --accent-primary: #1a1a2e;
            --accent-secondary: #64b5c6;
            --accent-hover: #2d3a5c;
            --border-color: #d8d8e4;
            --border-light: #e8e8f0;
            --shadow-soft: 0 2px 8px rgba(26, 26, 46, 0.06);
            --shadow-medium: 0 4px 20px rgba(26, 26, 46, 0.08);
            --shadow-elevated: 0 8px 32px rgba(26, 26, 46, 0.12);
            --radius-sm: 8px;
            --radius-md: 12px;
            --radius-lg: 16px;
            --radius-xl: 24px;
            --radius-pill: 50px;
        }}

        @media (prefers-color-scheme: dark) {{
            :root {{
                --bg-page: #0f0f1a;
                --bg-card: #1a1a2e;
                --bg-card-alt: #22223a;
                --bg-code: #16162a;
                --text-primary: #f0f0f6;
                --text-secondary: #a8a8bc;
                --text-muted: #6a6a7e;
                --accent-primary: #64b5c6;
                --accent-secondary: #8fd4e6;
                --accent-hover: #7ac8d8;
                --border-color: #2a2a42;
                --border-light: #22223a;
                --shadow-soft: 0 2px 8px rgba(0, 0, 0, 0.2);
                --shadow-medium: 0 4px 20px rgba(0, 0, 0, 0.25);
                --shadow-elevated: 0 8px 32px rgba(0, 0, 0, 0.3);
            }}
        }}

        * {{
            box-sizing: border-box;
            margin: 0;
            padding: 0;
        }}

        html {{
            scroll-behavior: smooth;
        }}

        body {{
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            font-size: 16px;
            line-height: 1.7;
            color: var(--text-secondary);
            background-color: var(--bg-page);
            min-height: 100vh;
            -webkit-font-smoothing: antialiased;
            -moz-osx-font-smoothing: grayscale;
        }}

        .page-wrapper {{
            max-width: 1200px;
            margin: 0 auto;
            padding: 2rem;
        }}

        /* Navigation */
        .nav-container {{
            background-color: var(--bg-card);
            border-radius: var(--radius-lg);
            padding: 1rem 1.5rem;
            margin-bottom: 2rem;
            box-shadow: var(--shadow-soft);
            position: sticky;
            top: 1rem;
            z-index: 100;
            backdrop-filter: blur(10px);
        }}

        nav ul {{
            list-style: none;
            display: flex;
            flex-wrap: wrap;
            gap: 0.5rem;
            align-items: center;
        }}

        nav li {{
            margin: 0;
        }}

        nav a {{
            display: inline-block;
            padding: 0.5rem 1rem;
            font-size: 0.875rem;
            font-weight: 500;
            color: var(--text-secondary);
            text-decoration: none;
            border-radius: var(--radius-pill);
            transition: all 0.2s ease;
            border: 1px solid transparent;
        }}

        nav a:hover {{
            color: var(--accent-primary);
            background-color: var(--bg-card-alt);
            border-color: var(--border-light);
        }}

        nav a:focus {{
            outline: 2px solid var(--accent-secondary);
            outline-offset: 2px;
        }}

        nav a.current {{
            background-color: var(--accent-primary);
            color: var(--bg-card);
            font-weight: 600;
        }}

        /* Main content card */
        main {{
            background-color: var(--bg-card);
            border-radius: var(--radius-xl);
            padding: 3rem;
            box-shadow: var(--shadow-medium);
        }}

        /* Typography */
        h1, h2, h3, h4, h5, h6 {{
            font-family: 'Fraunces', Georgia, 'Times New Roman', serif;
            color: var(--text-primary);
            font-weight: 600;
            letter-spacing: -0.02em;
            margin-top: 2.5rem;
            margin-bottom: 1rem;
        }}

        h1 {{
            font-size: clamp(2rem, 5vw, 2.75rem);
            font-weight: 700;
            margin-top: 0;
            margin-bottom: 1.5rem;
            line-height: 1.2;
        }}

        h2 {{
            font-size: clamp(1.5rem, 4vw, 1.875rem);
            margin-top: 3rem;
            padding-top: 2rem;
            border-top: 1px solid var(--border-light);
        }}

        h2:first-of-type {{
            border-top: none;
            padding-top: 0;
        }}

        h3 {{
            font-size: clamp(1.25rem, 3vw, 1.5rem);
            font-family: 'Inter', sans-serif;
            font-weight: 600;
            letter-spacing: -0.01em;
        }}

        h4 {{
            font-size: 1.125rem;
            font-family: 'Inter', sans-serif;
            font-weight: 600;
        }}

        p {{
            margin: 1rem 0;
            max-width: 75ch;
        }}

        strong {{
            color: var(--text-primary);
            font-weight: 600;
        }}

        /* Links */
        a {{
            color: var(--accent-primary);
            text-decoration: none;
            font-weight: 500;
            transition: color 0.2s ease;
        }}

        a:hover {{
            color: var(--accent-hover);
            text-decoration: underline;
            text-underline-offset: 3px;
        }}

        a:focus {{
            outline: 2px solid var(--accent-secondary);
            outline-offset: 2px;
        }}

        /* Code styling */
        code {{
            font-family: 'JetBrains Mono', 'SF Mono', 'Fira Code', 'Consolas', monospace;
            font-size: 0.875em;
            background-color: var(--bg-code);
            color: var(--text-primary);
            padding: 0.2em 0.5em;
            border-radius: var(--radius-sm);
            border: 1px solid var(--border-light);
        }}

        pre {{
            background-color: var(--bg-code);
            padding: 1.25rem 1.5rem;
            border-radius: var(--radius-md);
            overflow-x: auto;
            border: 1px solid var(--border-light);
            margin: 1.5rem 0;
            box-shadow: inset 0 2px 4px rgba(0, 0, 0, 0.04);
        }}

        pre code {{
            background: none;
            padding: 0;
            border: none;
            font-size: 0.875rem;
            line-height: 1.6;
        }}

        /* Blockquotes */
        blockquote {{
            border-left: 3px solid var(--accent-secondary);
            margin: 1.5rem 0;
            padding: 1rem 1.5rem;
            background-color: var(--bg-card-alt);
            border-radius: 0 var(--radius-md) var(--radius-md) 0;
            font-style: italic;
            color: var(--text-secondary);
        }}

        blockquote p:first-child {{
            margin-top: 0;
        }}

        blockquote p:last-child {{
            margin-bottom: 0;
        }}

        /* Lists */
        ul, ol {{
            padding-left: 1.5rem;
            margin: 1rem 0;
        }}

        li {{
            margin: 0.5rem 0;
            padding-left: 0.25rem;
        }}

        li::marker {{
            color: var(--accent-secondary);
        }}

        /* Tables */
        table {{
            width: 100%;
            border-collapse: separate;
            border-spacing: 0;
            margin: 1.5rem 0;
            border-radius: var(--radius-md);
            overflow: hidden;
            box-shadow: var(--shadow-soft);
        }}

        th, td {{
            padding: 0.875rem 1rem;
            text-align: left;
            border-bottom: 1px solid var(--border-light);
        }}

        th {{
            background-color: var(--bg-card-alt);
            font-weight: 600;
            color: var(--text-primary);
            font-size: 0.875rem;
            text-transform: uppercase;
            letter-spacing: 0.05em;
        }}

        td {{
            background-color: var(--bg-card);
        }}

        tr:last-child td {{
            border-bottom: none;
        }}

        tr:hover td {{
            background-color: var(--bg-card-alt);
        }}

        /* Mermaid diagrams */
        .mermaid {{
            margin: 2rem 0;
            padding: 2rem;
            background-color: var(--bg-card-alt);
            border-radius: var(--radius-lg);
            text-align: center;
            border: 1px solid var(--border-light);
        }}

        /* Horizontal rule */
        hr {{
            border: none;
            height: 1px;
            background: linear-gradient(to right, transparent, var(--border-color), transparent);
            margin: 3rem 0;
        }}

        /* Footer */
        .footer {{
            margin-top: 2rem;
            padding: 1.5rem;
            text-align: center;
            color: var(--text-muted);
            font-size: 0.875rem;
        }}

        .footer a {{
            color: var(--text-muted);
            font-weight: 500;
        }}

        .footer a:hover {{
            color: var(--accent-primary);
        }}

        /* Feature cards for specific content sections */
        .content-section {{
            background-color: var(--bg-card-alt);
            border-radius: var(--radius-lg);
            padding: 1.5rem;
            margin: 1.5rem 0;
            border: 1px solid var(--border-light);
        }}

        /* Skip link for accessibility */
        .skip-link {{
            position: absolute;
            top: -100%;
            left: 0;
            background: var(--accent-primary);
            color: var(--bg-card);
            padding: 0.75rem 1.5rem;
            border-radius: 0 0 var(--radius-md) 0;
            z-index: 1000;
            font-weight: 600;
        }}

        .skip-link:focus {{
            top: 0;
        }}

        /* Images */
        img {{
            max-width: 100%;
            height: auto;
            border-radius: var(--radius-md);
        }}

        /* Selection */
        ::selection {{
            background-color: var(--accent-secondary);
            color: var(--text-primary);
        }}

        /* Responsive Design */
        @media (max-width: 1024px) {{
            .page-wrapper {{
                padding: 1.5rem;
            }}

            main {{
                padding: 2rem;
            }}
        }}

        @media (max-width: 768px) {{
            .page-wrapper {{
                padding: 1rem;
            }}

            .nav-container {{
                position: relative;
                top: 0;
                padding: 1rem;
            }}

            nav ul {{
                gap: 0.375rem;
            }}

            nav a {{
                padding: 0.375rem 0.75rem;
                font-size: 0.8125rem;
            }}

            main {{
                padding: 1.5rem;
                border-radius: var(--radius-lg);
            }}

            h1 {{
                font-size: 1.75rem;
            }}

            h2 {{
                font-size: 1.375rem;
                margin-top: 2rem;
                padding-top: 1.5rem;
            }}

            h3 {{
                font-size: 1.125rem;
            }}

            pre {{
                padding: 1rem;
                font-size: 0.8125rem;
                border-radius: var(--radius-sm);
            }}

            table {{
                font-size: 0.875rem;
            }}

            th, td {{
                padding: 0.625rem 0.75rem;
            }}

            .mermaid {{
                padding: 1rem;
            }}
        }}

        @media (max-width: 480px) {{
            nav ul {{
                flex-direction: column;
                align-items: stretch;
            }}

            nav a {{
                display: block;
                text-align: center;
            }}

            main {{
                padding: 1.25rem;
            }}

            h2 {{
                font-size: 1.25rem;
            }}
        }}

        /* Print styles */
        @media print {{
            body {{
                background: white;
                color: black;
            }}

            .nav-container {{
                display: none;
            }}

            main {{
                box-shadow: none;
                padding: 0;
            }}

            a {{
                color: black;
                text-decoration: underline;
            }}

            pre {{
                border: 1px solid #ccc;
                page-break-inside: avoid;
            }}
        }}

        /* Focus visible for keyboard navigation */
        :focus-visible {{
            outline: 2px solid var(--accent-secondary);
            outline-offset: 2px;
        }}

        /* Reduce motion for accessibility */
        @media (prefers-reduced-motion: reduce) {{
            * {{
                transition-duration: 0.01ms !important;
                animation-duration: 0.01ms !important;
            }}

            html {{
                scroll-behavior: auto;
            }}
        }}
    </style>
</head>
<body>
    <a href="#main-content" class="skip-link">Skip to main content</a>

    <div class="page-wrapper">
        <div class="nav-container" role="navigation" aria-label="Documentation navigation">
            <nav>
                <ul>
                    {navigation}
                </ul>
            </nav>
        </div>

        <main id="main-content" role="main">
            {content}
        </main>

        <footer class="footer" role="contentinfo">
            Generated by <a href="https://github.com/nicoladevera/code-guro">Code Guro</a>
        </footer>
    </div>

    <script>
        // Initialize Mermaid with theme detection
        const isDarkMode = window.matchMedia('(prefers-color-scheme: dark)').matches;
        mermaid.initialize({{
            startOnLoad: true,
            theme: isDarkMode ? 'dark' : 'default',
            securityLevel: 'loose',
            fontFamily: 'Inter, -apple-system, BlinkMacSystemFont, sans-serif',
            flowchart: {{
                curve: 'basis',
                padding: 20
            }}
        }});

        // Handle mermaid code blocks - transform pre/code to div.mermaid
        document.querySelectorAll('pre code.language-mermaid').forEach(function(block) {{
            const pre = block.parentElement;
            const div = document.createElement('div');
            div.className = 'mermaid';
            div.setAttribute('role', 'img');
            div.setAttribute('aria-label', 'Mermaid diagram');
            div.textContent = block.textContent;
            pre.parentElement.replaceChild(div, pre);
        }});

        // Listen for theme changes and re-render mermaid diagrams
        window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', function(e) {{
            const newTheme = e.matches ? 'dark' : 'default';
            mermaid.initialize({{
                startOnLoad: false,
                theme: newTheme,
                securityLevel: 'loose'
            }});
            document.querySelectorAll('.mermaid').forEach(function(diagram) {{
                const code = diagram.getAttribute('data-processed') ? diagram.innerHTML : diagram.textContent;
                diagram.removeAttribute('data-processed');
                diagram.innerHTML = code;
            }});
            mermaid.init(undefined, '.mermaid');
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

    # Filter out internal files (prefixed with _) from user-facing HTML output
    user_facing_files = [f for f in md_files if not f.name.startswith("_")]

    if not user_facing_files:
        console.print("[yellow]No markdown files found to convert.[/yellow]")
        return

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
        transient=True,
    ) as progress:
        task = progress.add_task("Converting to HTML...", total=len(user_facing_files))

        for md_file in user_facing_files:
            progress.update(task, description=f"Converting {md_file.name}...")

            try:
                html_content = convert_file_to_html(md_file, user_facing_files)
                html_path = md_file.with_suffix(".html")
                html_path.write_text(html_content)
            except Exception as e:
                console.print(f"[yellow]Warning:[/yellow] Could not convert {md_file.name}: {e}")

            progress.advance(task)

    console.print(f"[green]Converted {len(user_facing_files)} files to HTML[/green]")


def convert_directory_to_html_organized(markdown_dir: Path, html_dir: Path) -> None:
    """Convert markdown files from one directory to HTML in another directory.

    Args:
        markdown_dir: Directory containing source markdown files
        html_dir: Directory where HTML files will be created
    """
    from rich.progress import Progress, SpinnerColumn, TextColumn

    md_files = list(markdown_dir.glob("*.md"))

    # Filter out internal files (prefixed with _) from user-facing HTML output
    user_facing_files = [f for f in md_files if not f.name.startswith("_")]

    if not user_facing_files:
        console.print("[yellow]No markdown files found to convert.[/yellow]")
        return

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
        transient=True,
    ) as progress:
        task = progress.add_task("Converting to HTML...", total=len(user_facing_files))

        for md_file in user_facing_files:
            progress.update(task, description=f"Converting {md_file.name}...")

            try:
                html_content = convert_file_to_html(md_file, user_facing_files)
                html_path = html_dir / md_file.with_suffix(".html").name
                html_path.write_text(html_content)
            except Exception as e:
                console.print(f"[yellow]Warning:[/yellow] Could not convert {md_file.name}: {e}")

            progress.advance(task)

    console.print(f"[green]Converted {len(user_facing_files)} files to HTML[/green]")
