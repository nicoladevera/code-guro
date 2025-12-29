## Relevant Files

- `pyproject.toml` - Package configuration, dependencies, and metadata for PyPI distribution
- `src/code_guro/__init__.py` - Package initialization and version info
- `src/code_guro/cli.py` - Main CLI entry point with Click commands (analyze, explain, configure)
- `src/code_guro/cli.test.py` - Unit tests for CLI commands
- `src/code_guro/config.py` - API key configuration, storage, and validation logic
- `src/code_guro/config.test.py` - Unit tests for configuration management
- `src/code_guro/analyzer.py` - Core code analysis engine (file traversal, framework detection, token estimation)
- `src/code_guro/analyzer.test.py` - Unit tests for analyzer
- `src/code_guro/frameworks.py` - Framework detection logic (Next.js, React, Vue, Django, Flask, Express, Rails)
- `src/code_guro/frameworks.test.py` - Unit tests for framework detection
- `src/code_guro/generator.py` - Documentation generation logic (markdown files)
- `src/code_guro/generator.test.py` - Unit tests for documentation generator
- `src/code_guro/html_converter.py` - Markdown to HTML conversion with styling and Mermaid support
- `src/code_guro/html_converter.test.py` - Unit tests for HTML converter
- `src/code_guro/repl.py` - Interactive REPL mode for explain --interactive command
- `src/code_guro/repl.test.py` - Unit tests for REPL functionality
- `src/code_guro/utils.py` - Utility functions (file encoding, gitignore handling, token counting)
- `src/code_guro/utils.test.py` - Unit tests for utilities
- `src/code_guro/prompts.py` - Claude API system prompts and prompt templates
- `src/code_guro/errors.py` - Custom exception classes and error messages
- `src/code_guro/templates/` - HTML template and CSS styles for HTML output
- `README.md` - Installation, setup, usage examples, and troubleshooting guide
- `tests/integration/` - Integration tests for full workflows
- `.gitignore` - Git ignore patterns for Python project

### Notes

- Unit tests should be placed alongside the code files they are testing (e.g., `cli.py` and `cli.test.py`)
- Use `pytest` to run tests: `pytest` for all tests, `pytest src/code_guro/cli.test.py` for specific file
- This is a Python CLI application using Click, Rich, and the Anthropic SDK
- Target Python version: 3.8+
- Package will be distributed via PyPI as `code-guro`

## Instructions for Completing Tasks

**IMPORTANT:** As you complete each task, you must check it off in this markdown file by changing `- [ ]` to `- [x]`. This helps track progress and ensures you don't skip any steps.

Example:
- `- [ ] 1.1 Read file` → `- [x] 1.1 Read file` (after completing)

Update the file after completing each sub-task, not just after completing an entire parent task.

## Tasks

- [x] 0.0 Create feature branch
  - [x] 0.1 Create and checkout a new branch for this feature (`git checkout -b feature/code-guro-mvp`)

- [x] 1.0 Project Setup & Package Configuration
  - [x] 1.1 Create Python package directory structure (`src/code_guro/`)
  - [x] 1.2 Create `pyproject.toml` with project metadata (name: code-guro, version, description, author, license)
  - [x] 1.3 Add required dependencies: anthropic (>=0.18.0), click (>=8.0), rich (>=13.0), gitpython (>=3.1), tiktoken (>=0.5.0), markdown (>=3.4)
  - [x] 1.4 Add optional dependencies: python-dotenv (>=1.0), prompt_toolkit, pygments
  - [x] 1.5 Add development dependencies: pytest, pytest-cov, black, ruff
  - [x] 1.6 Configure CLI entry point in pyproject.toml (`code-guro = "code_guro.cli:main"`)
  - [x] 1.7 Create `src/code_guro/__init__.py` with version string
  - [x] 1.8 Create `.gitignore` for Python project (venv, __pycache__, .egg-info, etc.)
  - [x] 1.9 Verify package installs locally with `pip install -e .`

- [x] 2.0 Core CLI Framework with Click
  - [x] 2.1 Create `src/code_guro/cli.py` with Click group as main entry point
  - [x] 2.2 Implement `code-guro --version` option to display version
  - [x] 2.3 Implement `code-guro --help` with usage description
  - [x] 2.4 Create `analyze` command skeleton with path argument (accepts directory or GitHub URL)
  - [x] 2.5 Add `--format` option to analyze command (choices: markdown, html; default: markdown)
  - [x] 2.6 Create `explain` command skeleton with path argument (file or folder)
  - [x] 2.7 Add `--interactive` flag to explain command
  - [x] 2.8 Add `--output` option to explain command (choices: file, console; default: file)
  - [x] 2.9 Create `configure` command skeleton for API key setup
  - [x] 2.10 Add API key check decorator/helper that runs before analyze and explain commands

- [x] 3.0 API Key Configuration & Secure Storage
  - [x] 3.1 Create `src/code_guro/config.py` module
  - [x] 3.2 Implement function to get config directory path (`~/.config/code-guro/`)
  - [x] 3.3 Implement function to create config directory with proper permissions
  - [x] 3.4 Implement function to read API key from config.json
  - [x] 3.5 Implement function to write API key to config.json with chmod 600
  - [x] 3.6 Implement environment variable fallback (`CLAUDE_API_KEY` takes precedence)
  - [x] 3.7 Implement API key validation by making a small test request to Claude API
  - [x] 3.8 Implement `configure` command flow: prompt for key, validate, save, show success/error
  - [x] 3.9 Add helper function to get API key (checks env var first, then config file)
  - [x] 3.10 Ensure API key is never logged or printed to console (mask in any debug output)

- [x] 4.0 Code Analysis Engine
  - [x] 4.1 Create `src/code_guro/analyzer.py` module
  - [x] 4.2 Implement directory traversal function that respects `.gitignore` patterns
  - [x] 4.3 Implement file filtering to skip binary files, images, and non-text files
  - [x] 4.4 Implement file encoding detection and handling (UTF-8, ASCII, etc.)
  - [x] 4.5 Implement function to skip extremely large files (>1MB) with warning
  - [x] 4.6 Implement GitHub URL detection and cloning using gitpython
  - [x] 4.7 Create `src/code_guro/frameworks.py` for framework detection
  - [x] 4.8 Implement Next.js detection (package.json "next", next.config.js)
  - [x] 4.9 Implement React detection (package.json "react", .jsx/.tsx files)
  - [x] 4.10 Implement Vue detection (package.json "vue", .vue files)
  - [x] 4.11 Implement Django detection (requirements.txt "Django", manage.py, settings.py)
  - [x] 4.12 Implement Flask detection (requirements.txt "Flask", app.py patterns)
  - [x] 4.13 Implement Express detection (package.json "express")
  - [x] 4.14 Implement Ruby on Rails detection (Gemfile "rails", config/routes.rb)
  - [x] 4.15 Create `src/code_guro/utils.py` with token counting using tiktoken
  - [x] 4.16 Implement cost estimation function (input: ~$3/M tokens, output: ~$15/M tokens)
  - [x] 4.17 Implement cost confirmation prompt for estimates exceeding $1.00
  - [x] 4.18 Implement chunking detection (trigger if >150K tokens)
  - [x] 4.19 Implement chunking strategy: by module/directory structure, fallback to file count
  - [x] 4.20 Add chunking warning and confirmation prompt for users
  - [x] 4.21 Implement function to identify critical 20% of files (entry points, config, core logic)

- [x] 5.0 Structured Documentation Generation
  - [x] 5.1 Create `src/code_guro/generator.py` module
  - [x] 5.2 Create `src/code_guro/prompts.py` with Claude system prompts for code tutoring
  - [x] 5.3 Implement function to create `code-guro-output/` directory in analyzed project
  - [x] 5.4 Design prompt template for executive summary generation
  - [x] 5.5 Implement generation of `00-overview.md` (what app does, tech stack, high-level architecture)
  - [x] 5.6 Design prompt template for file structure analysis
  - [x] 5.7 Implement generation of `01-getting-oriented.md` (file structure, folder purposes, extensions glossary, entry points)
  - [x] 5.8 Design prompt template for architecture analysis
  - [x] 5.9 Implement generation of `02-architecture.md` (patterns, conventions, architectural decisions)
  - [x] 5.10 Design prompt template for critical files identification
  - [x] 5.11 Implement generation of `03-core-files.md` (the 20% of files that matter most)
  - [x] 5.12 Design prompt template for module deep dives
  - [x] 5.13 Implement generation of `04-deep-dive-[module].md` files (one per major module, dynamic)
  - [x] 5.14 Design prompt template for quality analysis
  - [x] 5.15 Implement generation of `05-quality-analysis.md` (what's done well, risks, pitfalls, security)
  - [x] 5.16 Design prompt template for next steps
  - [x] 5.17 Implement generation of `06-next-steps.md` (suggested exploration, drill-down commands)
  - [x] 5.18 Implement Mermaid diagram generation for architecture visualization
  - [x] 5.19 Implement Mermaid diagram generation for file relationships
  - [x] 5.20 Add framework-specific context sections when frameworks are detected
  - [x] 5.21 Implement chunked analysis workflow: analyze chunks separately, then synthesize
  - [x] 5.22 Add glossary sections explaining technical terms for beginners

- [x] 6.0 HTML Output Generation with Mermaid Support
  - [x] 6.1 Create `src/code_guro/html_converter.py` module
  - [x] 6.2 Create `src/code_guro/templates/` directory for HTML templates
  - [x] 6.3 Create base HTML template with proper doctype, meta tags, and structure
  - [x] 6.4 Create embedded CSS stylesheet (clean typography, system fonts, line spacing)
  - [x] 6.5 Add responsive CSS for desktop and mobile readability
  - [x] 6.6 Integrate Mermaid.js CDN script in HTML template
  - [x] 6.7 Add Mermaid initialization script for diagram rendering
  - [x] 6.8 Implement markdown to HTML conversion using `markdown` library
  - [x] 6.9 Configure markdown extensions: fenced_code, tables, toc
  - [ ] 6.10 Integrate Pygments for code syntax highlighting in HTML
  - [x] 6.11 Implement navigation links generation between sections
  - [x] 6.12 Implement function to generate .html files alongside .md files
  - [x] 6.13 Ensure HTML generation adds minimal overhead (<2 seconds typical)

- [x] 7.0 Interactive Drill-Down Mode (REPL)
  - [x] 7.1 Create `src/code_guro/repl.py` module
  - [x] 7.2 Implement `explain` command logic: load file/folder content
  - [x] 7.3 Create system prompt for Claude as beginner-friendly code tutor
  - [x] 7.4 Implement focused analysis generation for explain command (without --interactive)
  - [x] 7.5 Implement saving explain output to `code-guro-output/explain-[path-name].md`
  - [x] 7.6 Implement --output console option to print to console instead of saving file
  - [x] 7.7 Implement REPL initialization with welcome message
  - [x] 7.8 Implement REPL prompt loop (`code-guro> `)
  - [x] 7.9 Implement exit command handling (exit, quit, Ctrl+C/KeyboardInterrupt)
  - [x] 7.10 Implement question sending to Claude API with file context
  - [x] 7.11 Implement conversation history management (last 10 Q&A pairs)
  - [x] 7.12 Implement context overflow warning and fresh session offer
  - [x] 7.13 Display responses with Rich syntax highlighting for code snippets
  - [x] 7.14 Implement session saving to `code-guro-output/explain-[path-name]-session.md`
  - [x] 7.15 Handle network errors gracefully (display error, allow retry without exiting)
  - [x] 7.16 Handle API rate limits (show wait time, pause session)

- [x] 8.0 Error Handling & Progress Indicators
  - [x] 8.1 Create `src/code_guro/errors.py` with custom exception classes
  - [x] 8.2 Define beginner-friendly error message templates
  - [x] 8.3 Implement Rich progress bar for "Analyzing file structure..."
  - [x] 8.4 Implement Rich progress bar for "Detecting frameworks..."
  - [x] 8.5 Implement Rich progress bar for "Estimating costs..."
  - [x] 8.6 Implement Rich progress bar for "Generating documentation..." (per section)
  - [x] 8.7 Implement Rich progress bar for "Converting to HTML..." (when applicable)
  - [x] 8.8 Implement error handler for missing/invalid API key with setup instructions
  - [x] 8.9 Implement error handler for directory not found
  - [x] 8.10 Implement error handler for invalid GitHub URL
  - [x] 8.11 Implement error handler for GitHub clone failures (network, auth, not found)
  - [x] 8.12 Implement error handler for API rate limits with retry guidance
  - [x] 8.13 Implement error handler for API timeouts
  - [x] 8.14 Implement internet connectivity check at startup
  - [x] 8.15 Implement friendly error message for no internet connection
  - [x] 8.16 Implement error handler for file encoding issues
  - [x] 8.17 Implement warning for skipped large files (>1MB)
  - [ ] 8.18 Implement warning when secrets may be present (.env files, API keys in code)

- [x] 9.0 Testing & Quality Assurance
  - [x] 9.1 Set up pytest configuration in pyproject.toml
  - [ ] 9.2 Create test fixtures for sample codebases (small, medium, with frameworks)
  - [ ] 9.3 Write unit tests for CLI commands (analyze, explain, configure invocation)
  - [x] 9.4 Write unit tests for config module (read, write, validate API key)
  - [x] 9.5 Write unit tests for file system operations (traversal, filtering, encoding)
  - [x] 9.6 Write unit tests for framework detection (each of the 7 frameworks)
  - [x] 9.7 Write unit tests for token estimation and cost calculation
  - [ ] 9.8 Write unit tests for markdown generation functions
  - [ ] 9.9 Write unit tests for HTML conversion
  - [ ] 9.10 Write unit tests for REPL session management
  - [x] 9.11 Create `tests/integration/` directory
  - [ ] 9.12 Write integration test for full analyze workflow (directory → markdown output)
  - [ ] 9.13 Write integration test for analyze with HTML output
  - [ ] 9.14 Write integration test for explain command
  - [ ] 9.15 Write integration test for configure command flow
  - [ ] 9.16 Test cross-platform compatibility (macOS, Linux, Windows path handling)
  - [x] 9.17 Add test coverage reporting with pytest-cov

- [x] 10.0 PyPI Distribution & README Documentation
  - [x] 10.1 Verify pyproject.toml has all required PyPI metadata (name, version, description, author, license, classifiers)
  - [x] 10.2 Add project URLs to pyproject.toml (homepage, repository, documentation)
  - [x] 10.3 Create README.md with project introduction and Code Guro etymology
  - [x] 10.4 Add installation instructions to README (`pip install code-guro`)
  - [x] 10.5 Add API key setup guide to README (getting key from console.anthropic.com)
  - [x] 10.6 Add usage examples for `code-guro configure`
  - [x] 10.7 Add usage examples for `code-guro analyze` (local directory, GitHub URL, --format html)
  - [x] 10.8 Add usage examples for `code-guro explain` (file, folder, --interactive)
  - [x] 10.9 Add troubleshooting section with common issues and solutions
  - [x] 10.10 Add section on cost estimation and confirmation thresholds
  - [x] 10.11 Add section on supported frameworks
  - [ ] 10.12 Build distribution packages (`python -m build`)
  - [ ] 10.13 Test installation from built wheel in clean virtual environment
  - [ ] 10.14 Create account on PyPI if needed
  - [ ] 10.15 Upload to TestPyPI first for validation (`twine upload --repository testpypi dist/*`)
  - [ ] 10.16 Test installation from TestPyPI
  - [ ] 10.17 Upload to PyPI (`twine upload dist/*`)
  - [ ] 10.18 Verify `pip install code-guro` works from PyPI
