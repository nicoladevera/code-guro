"""HTML conversion for Code Guro.

Converts markdown documentation to styled HTML with Mermaid support.
"""

from pathlib import Path
from typing import List

import markdown
from rich.console import Console

console = Console()

# HTML template with embedded CSS - Yuno-inspired modern design
HTML_TEMPLATE = r"""<!DOCTYPE html>
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

            /* Sidebar dark mode adjustments */
            .sidebar {{
                border-right-color: var(--border-color);
            }}

            .sidebar-overlay {{
                background-color: rgba(0, 0, 0, 0.7);
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
            display: flex;
            -webkit-font-smoothing: antialiased;
            -moz-osx-font-smoothing: grayscale;
        }}

        /* Hide toggle checkbox */
        .nav-toggle {{
            display: none;
        }}

        /* Main content wrapper */
        .main-wrapper {{
            flex: 1;
            display: flex;
            flex-direction: column;
            min-height: 100vh;
            margin-left: 280px;
            padding: 0 2rem;
            transition: margin-left 0.3s ease;
        }}

        /* Sidebar container */
        .sidebar {{
            position: fixed;
            top: 0;
            left: 0;
            width: 280px;
            height: 100vh;
            background-color: var(--bg-card);
            border-right: 1px solid var(--border-light);
            box-shadow: var(--shadow-medium);
            z-index: 1000;
            display: flex;
            flex-direction: column;
            overflow-y: auto;
            overflow-x: hidden;
            transition: transform 0.3s ease;
        }}

        /* Sidebar header */
        .sidebar-header {{
            padding: 1.5rem;
            border-bottom: 1px solid var(--border-light);
            display: flex;
            justify-content: space-between;
            align-items: center;
            background-color: var(--bg-card);
            position: sticky;
            top: 0;
            z-index: 10;
        }}

        .sidebar-title {{
            font-family: 'Fraunces', Georgia, serif;
            font-size: 1.25rem;
            font-weight: 700;
            color: var(--accent-primary);
            margin: 0;
        }}

        .close-btn {{
            display: none;
            font-size: 2rem;
            color: var(--text-muted);
            cursor: pointer;
            line-height: 1;
            padding: 0.25rem;
            transition: color 0.2s ease;
        }}

        .close-btn:hover {{
            color: var(--accent-primary);
        }}

        /* Sidebar navigation */
        .sidebar-nav {{
            flex: 1;
            padding: 1rem 0;
        }}

        .sidebar-nav ul {{
            list-style: none;
            padding: 0;
            margin: 0;
        }}

        .sidebar-nav li {{
            margin: 0;
        }}

        .sidebar-nav a {{
            display: block;
            padding: 0.75rem 1.5rem;
            font-size: 0.9375rem;
            font-weight: 500;
            color: var(--text-secondary);
            text-decoration: none;
            border-left: 3px solid transparent;
            transition: all 0.2s ease;
        }}

        .sidebar-nav a:hover {{
            background-color: var(--bg-card-alt);
            color: var(--accent-primary);
            border-left-color: var(--accent-secondary);
        }}

        .sidebar-nav a:focus {{
            outline: 2px solid var(--accent-secondary);
            outline-offset: -2px;
        }}

        .sidebar-nav a.current {{
            background-color: var(--bg-card-alt);
            color: var(--accent-primary);
            border-left-color: var(--accent-primary);
            font-weight: 600;
        }}

        /* Hamburger toggle button */
        .nav-toggle-label {{
            display: none;
            position: fixed;
            top: 1rem;
            left: 1rem;
            z-index: 1001;
            cursor: pointer;
            padding: 0.5rem;
            background-color: var(--bg-card);
            border-radius: var(--radius-md);
            box-shadow: var(--shadow-soft);
            border: 1px solid var(--border-light);
            transition: all 0.2s ease;
        }}

        .nav-toggle-label:hover {{
            background-color: var(--bg-card-alt);
            box-shadow: var(--shadow-medium);
        }}

        .hamburger-icon {{
            display: block;
            width: 24px;
            height: 20px;
            position: relative;
        }}

        .hamburger-icon span {{
            display: block;
            position: absolute;
            height: 3px;
            width: 100%;
            background-color: var(--text-primary);
            border-radius: 2px;
            opacity: 1;
            left: 0;
            transform: rotate(0deg);
            transition: 0.25s ease-in-out;
        }}

        .hamburger-icon span:nth-child(1) {{
            top: 0;
        }}

        .hamburger-icon span:nth-child(2) {{
            top: 8px;
        }}

        .hamburger-icon span:nth-child(3) {{
            top: 16px;
        }}

        /* Hide hamburger when sidebar is open (only show close button inside sidebar) */
        .nav-toggle:checked ~ .nav-toggle-label {{
            display: none;
        }}

        /* Mobile overlay backdrop */
        .sidebar-overlay {{
            display: none;
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background-color: rgba(26, 26, 46, 0.5);
            z-index: 999;
            cursor: pointer;
            opacity: 0;
            pointer-events: none;
            transition: opacity 0.3s ease;
        }}

        /* Custom scrollbar for sidebar */
        .sidebar::-webkit-scrollbar {{
            width: 6px;
        }}

        .sidebar::-webkit-scrollbar-track {{
            background: var(--bg-card);
        }}

        .sidebar::-webkit-scrollbar-thumb {{
            background: var(--border-color);
            border-radius: 3px;
        }}

        .sidebar::-webkit-scrollbar-thumb:hover {{
            background: var(--text-muted);
        }}

        /* Firefox scrollbar */
        .sidebar {{
            scrollbar-width: thin;
            scrollbar-color: var(--border-color) var(--bg-card);
        }}

        /* Main content card */
        main {{
            flex: 1;
            max-width: 1200px;
            margin: 2rem auto;
            width: 100%;
            padding: 3rem;
            background-color: var(--bg-card);
            border-radius: var(--radius-xl);
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

        /* Force dark text for light-colored Mermaid nodes in dark mode */
        @media (prefers-color-scheme: dark) {{
            /* Target light orange nodes */
            .mermaid svg .node rect[style*="rgb(255, 153, 102)"] ~ .nodeLabel,
            .mermaid svg .node rect[style*="rgb(255, 153, 102)"] ~ text,
            .mermaid svg .node polygon[style*="rgb(255, 153, 102)"] ~ .nodeLabel,
            .mermaid svg .node polygon[style*="rgb(255, 153, 102)"] ~ text,
            /* Target light purple/lavender nodes */
            .mermaid svg .node rect[style*="rgb(180, 167, 214)"] ~ .nodeLabel,
            .mermaid svg .node rect[style*="rgb(180, 167, 214)"] ~ text,
            .mermaid svg .node polygon[style*="rgb(180, 167, 214)"] ~ .nodeLabel,
            .mermaid svg .node polygon[style*="rgb(180, 167, 214)"] ~ text,
            /* Target light teal/cyan nodes */
            .mermaid svg .node rect[style*="rgb(100, 181, 198)"] ~ .nodeLabel,
            .mermaid svg .node rect[style*="rgb(100, 181, 198)"] ~ text,
            .mermaid svg .node polygon[style*="rgb(100, 181, 198)"] ~ .nodeLabel,
            .mermaid svg .node polygon[style*="rgb(100, 181, 198)"] ~ text,
            /* Target any light-colored backgrounds (fallback) */
            .mermaid svg .nodeLabel,
            .mermaid svg text.nodeLabel {{
                fill: #1a1a2e !important;
            }}
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
            z-index: 1002;
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
            .main-wrapper {{
                margin-left: 280px;
                padding: 0 1.5rem;
            }}

            main {{
                padding: 2rem;
                margin: 1.5rem 0;
            }}
        }}

        @media (max-width: 768px) {{
            /* Show hamburger button */
            .nav-toggle-label {{
                display: block;
            }}

            /* Show close button in sidebar */
            .close-btn {{
                display: block;
            }}

            /* Remove main content margin (sidebar overlays instead) */
            .main-wrapper {{
                margin-left: 0;
                padding: 4rem 1rem 0 1rem;
            }}

            /* Hide sidebar by default on mobile */
            .sidebar {{
                transform: translateX(-100%);
            }}

            /* Show sidebar when toggle is checked */
            .nav-toggle:checked ~ .sidebar {{
                transform: translateX(0);
            }}

            /* Show overlay when sidebar is open */
            .nav-toggle:checked ~ .sidebar-overlay {{
                display: block;
                opacity: 1;
                pointer-events: auto;
            }}

            /* Adjust main content */
            main {{
                padding: 1.5rem;
                margin: 1rem 0;
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
            .sidebar {{
                width: 85%;
                max-width: 320px;
            }}

            .main-wrapper {{
                padding: 4rem 0.5rem 0 0.5rem;
            }}

            main {{
                padding: 1.25rem;
                margin: 0.5rem 0;
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

            .sidebar, .nav-toggle-label, .sidebar-overlay {{
                display: none;
            }}

            .main-wrapper {{
                margin-left: 0;
            }}

            main {{
                box-shadow: none;
                padding: 0;
                margin: 0;
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

    <!-- Hamburger toggle (CSS checkbox hack - no JS needed) -->
    <input type="checkbox" id="nav-toggle" class="nav-toggle" aria-label="Toggle navigation menu">
    <label for="nav-toggle" class="nav-toggle-label" aria-label="Open navigation menu">
        <span class="hamburger-icon">
            <span></span>
            <span></span>
            <span></span>
        </span>
    </label>

    <!-- Sidebar navigation -->
    <aside class="sidebar" role="navigation" aria-label="Documentation navigation">
        <div class="sidebar-header">
            <h2 class="sidebar-title">Code Guro</h2>
            <label for="nav-toggle" class="close-btn" aria-label="Close navigation menu">
                <span>&times;</span>
            </label>
        </div>
        <nav class="sidebar-nav">
            <ul>
                {navigation}
            </ul>
        </nav>
    </aside>

    <!-- Mobile overlay backdrop -->
    <label for="nav-toggle" class="sidebar-overlay" aria-label="Close navigation menu"></label>

    <!-- Main content wrapper -->
    <div class="main-wrapper">
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
            themeVariables: isDarkMode ? {{
                primaryTextColor: '#1a1a2e',
                secondaryTextColor: '#1a1a2e',
                tertiaryTextColor: '#f0f0f6',
                primaryColor: '#ff9966',
                primaryBorderColor: '#ff7733',
                secondaryColor: '#b4a7d6',
                secondaryBorderColor: '#9575cd'
            }} : {{}},
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

        // Fix text colors in dark mode Mermaid diagrams after rendering
        function fixMermaidTextColors() {{
            if (!window.matchMedia('(prefers-color-scheme: dark)').matches) return;

            document.querySelectorAll('.mermaid svg').forEach(function(svg) {{
                // Get all text elements within nodes
                svg.querySelectorAll('.node text, .nodeLabel, text').forEach(function(textEl) {{
                    // Get the parent node's background color
                    const parentNode = textEl.closest('.node');
                    if (!parentNode) return;

                    // Find rect or polygon shape in the node
                    const shape = parentNode.querySelector('rect, polygon');
                    if (!shape) return;

                    const fill = shape.style.fill || shape.getAttribute('fill');
                    if (!fill) return;

                    // Convert to RGB to analyze brightness
                    const rgb = fill.match(/rgb\((\d+),\s*(\d+),\s*(\d+)\)/);
                    if (!rgb) return;

                    const r = parseInt(rgb[1]);
                    const g = parseInt(rgb[2]);
                    const b = parseInt(rgb[3]);

                    // Calculate relative luminance
                    const luminance = (0.299 * r + 0.587 * g + 0.114 * b) / 255;

                    // If background is light (luminance > 0.5), use dark text
                    if (luminance > 0.5) {{
                        textEl.style.fill = '#1a1a2e';
                        textEl.style.color = '#1a1a2e';
                    }} else {{
                        // Dark background gets light text
                        textEl.style.fill = '#f0f0f6';
                        textEl.style.color = '#f0f0f6';
                    }}
                }});
            }});
        }}

        // Run after Mermaid finishes rendering
        setTimeout(fixMermaidTextColors, 100);

        // Listen for theme changes and re-render mermaid diagrams
        window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', function(e) {{
            const newTheme = e.matches ? 'dark' : 'default';
            mermaid.initialize({{
                startOnLoad: false,
                theme: newTheme,
                themeVariables: e.matches ? {{
                    primaryTextColor: '#1a1a2e',
                    secondaryTextColor: '#1a1a2e',
                    tertiaryTextColor: '#f0f0f6',
                    primaryColor: '#ff9966',
                    primaryBorderColor: '#ff7733',
                    secondaryColor: '#b4a7d6',
                    secondaryBorderColor: '#9575cd'
                }} : {{}},
                securityLevel: 'loose'
            }});
            document.querySelectorAll('.mermaid').forEach(function(diagram) {{
                const code = diagram.getAttribute('data-processed') ? diagram.innerHTML : diagram.textContent;
                diagram.removeAttribute('data-processed');
                diagram.innerHTML = code;
            }});
            mermaid.init(undefined, '.mermaid');
            // Fix text colors after re-rendering
            setTimeout(fixMermaidTextColors, 100);
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
