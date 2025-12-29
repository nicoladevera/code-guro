# Code Guro

A CLI tool to help non-technical product managers and AI-native builders understand codebases.

## Etymology

The name "Code Guro" is a play on two words:
- **"Guro"** - Tagalog (Filipino) word for "teacher"
- **"Guru"** - Expert or master in a particular field

This reflects the tool's purpose: to serve as both a teacher (guro) and expert guide (guru) for understanding code.

## Overview

Many product managers are now using AI coding agents (Claude Code, Cursor, etc.) to build functional prototypes and MVPs, but lack the programming background to truly understand the code that's generated. This creates hesitation when scaling products or bringing in users.

Code Guro analyzes a codebase and generates structured, beginner-friendly learning documentation. Unlike conversational AI tools that answer specific questions, Code Guro proactively creates a complete curriculum tailored to your specific codebase.

## Installation

```bash
pip install code-guro
```

**Requirements:**
- Python 3.8 or higher
- Internet connection (for Claude API calls)
- Claude API key from [console.anthropic.com](https://console.anthropic.com)

## Quick Start

### 1. Configure your API key

```bash
code-guro configure
```

You'll be prompted to enter your Claude API key. The key is stored securely in `~/.config/code-guro/config.json` with restricted file permissions.

Alternatively, you can set the `CLAUDE_API_KEY` or `ANTHROPIC_API_KEY` environment variable:

```bash
export CLAUDE_API_KEY="your-api-key-here"
```

### 2. Analyze a codebase

```bash
# Analyze current directory
code-guro analyze .

# Analyze a specific path
code-guro analyze /path/to/project

# Analyze from GitHub
code-guro analyze https://github.com/user/repo

# Generate HTML output (in addition to markdown)
code-guro analyze . --format html
```

### 3. Deep dive into specific files

```bash
# Explain a specific folder
code-guro explain ./src/auth

# Interactive mode for follow-up questions
code-guro explain ./src/auth --interactive

# Print explanation to console instead of file
code-guro explain ./src/auth --output console
```

## Output

Code Guro generates structured learning documentation in a `code-guro-output/` directory:

```
code-guro-output/
├── 00-overview.md           # Executive summary: what the app does, tech stack
├── 01-getting-oriented.md   # File structure, extensions glossary, entry points
├── 02-architecture.md       # Patterns, conventions, architectural decisions
├── 03-core-files.md         # The 20% of files that matter most
├── 04-deep-dive-[module].md # Deep dives for each major module
├── 05-quality-analysis.md   # What's good, what's risky, potential pitfalls
└── 06-next-steps.md         # Suggested exploration paths, follow-up commands
```

Each document includes:
- Beginner-friendly explanations
- Visual diagrams (Mermaid)
- Code snippets with inline comments
- Glossary of technical terms

## Commands

### `code-guro configure`

Set up your Claude API key for first-time use.

```bash
code-guro configure
```

### `code-guro analyze <path>`

Analyze a codebase and generate documentation.

```bash
code-guro analyze .                    # Current directory
code-guro analyze /path/to/project     # Specific path
code-guro analyze https://github.com/user/repo  # GitHub URL
```

**Options:**
- `--format [markdown|html]` - Output format (default: markdown)

### `code-guro explain <path>`

Get a detailed explanation of a specific file or folder.

```bash
code-guro explain ./src/auth           # Analyze a folder
code-guro explain ./src/app.py         # Analyze a single file
```

**Options:**
- `-i, --interactive` - Launch interactive Q&A mode
- `--output [file|console]` - Where to output (default: file)

### `code-guro --version`

Display the current version.

### `code-guro --help`

Show help information.

## Supported Frameworks

Code Guro provides enhanced context for these frameworks:

| Framework | Detection Method |
|-----------|-----------------|
| **Next.js** | `package.json` with "next", `next.config.js` |
| **React** | `package.json` with "react", `.jsx/.tsx` files |
| **Vue.js** | `package.json` with "vue", `.vue` files |
| **Django** | `requirements.txt` with "Django", `manage.py` |
| **Flask** | `requirements.txt` with "Flask", `app.py` patterns |
| **Express.js** | `package.json` with "express" |
| **Ruby on Rails** | `Gemfile` with "rails", `config/routes.rb` |

When a framework is detected, the documentation includes:
- Framework-specific architecture patterns
- Common conventions and best practices
- Known gotchas and pitfalls

## Cost Estimation

Code Guro estimates API costs before running analysis based on:
- Token count of files to analyze
- Current Claude API pricing (~$3/million input tokens, ~$15/million output tokens)

**Cost confirmation:**
- For estimates under $1.00: Proceeds automatically
- For estimates over $1.00: Asks for confirmation before continuing

Typical costs:
- Small project (10-50 files): $0.05 - $0.30
- Medium project (50-200 files): $0.30 - $1.00
- Large project (200+ files): $1.00 - $5.00

## Interactive Mode

The `--interactive` flag launches a conversational Q&A session:

```bash
code-guro explain ./src/auth --interactive
```

You can ask questions like:
- "Why was this pattern used?"
- "What does this function do?"
- "How does this connect to the database?"
- "What would happen if I changed X?"

Type `exit` or `quit` to end the session. Your conversation is saved to `code-guro-output/explain-[path]-session.md`.

## Troubleshooting

### "No API key configured"

Run `code-guro configure` to set up your API key, or set the `CLAUDE_API_KEY` environment variable.

### "No internet connection detected"

Code Guro requires an internet connection for Claude API calls and GitHub cloning. Check your network connection.

### "Estimated cost exceeds $1.00"

For large codebases, you'll be asked to confirm before proceeding. You can:
- Enter `y` to continue
- Enter `n` to cancel
- Try analyzing a specific subdirectory instead

### "File too large to analyze"

Files larger than 1MB are skipped to avoid excessive API costs. This is typically fine since large files are often generated code, dependencies, or data files.

### GitHub clone failures

Ensure the repository URL is correct and the repository is public. Private repositories are not currently supported.

## Development

### Setup

```bash
# Clone the repository
git clone https://github.com/nicoladevera/code-guro.git
cd code-guro

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install in development mode
pip install -e ".[dev]"
```

### Running Tests

```bash
pytest
```

### Code Formatting

```bash
black src/
ruff check src/
```

## License

MIT

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## Acknowledgments

Built with:
- [Anthropic Claude API](https://www.anthropic.com/)
- [Click](https://click.palletsprojects.com/) - CLI framework
- [Rich](https://rich.readthedocs.io/) - Terminal formatting
- [tiktoken](https://github.com/openai/tiktoken) - Token counting
