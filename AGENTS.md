# AGENTS.md - Code Guro

This document provides essential context for AI agents and developers working with the Code Guro codebase.

---

## 1. Tech Stack & Dependencies

### Core Runtime
- **Python 3.8+** (tested on 3.8, 3.9, 3.10, 3.11, 3.12)
- Package manager: pip with setuptools

### Production Dependencies

| Package | Version | Purpose |
|---------|---------|---------|
| `anthropic` | >=0.18.0 | Claude API client for LLM interactions |
| `click` | >=8.0 | CLI framework for command structure |
| `rich` | >=13.0 | Terminal formatting, progress bars, panels |
| `gitpython` | >=3.1 | Git repository cloning and manipulation |
| `tiktoken` | >=0.5.0 | Token counting for cost estimation |
| `markdown` | >=3.4 | Markdown to HTML conversion |

### Development Dependencies

| Package | Version | Purpose |
|---------|---------|---------|
| `pytest` | >=7.0 | Testing framework |
| `pytest-cov` | >=4.0 | Code coverage reporting |
| `black` | >=23.0 | Code formatter (100 char line length) |
| `ruff` | >=0.1.0 | Fast Python linter |

### Optional Enhanced Features
- `python-dotenv>=1.0` - Environment variable management
- `prompt_toolkit>=3.0` - Interactive REPL enhancements
- `pygments>=2.15` - Syntax highlighting

### Environment Requirements
- Internet connection required (connects to `api.anthropic.com:443`)
- Anthropic API key (set via `CLAUDE_API_KEY`, `ANTHROPIC_API_KEY`, or `code-guro configure`)
- Token encoding: `cl100k_base` (compatible with GPT-4/Claude)

---

## 2. Project Structure

```
code-guro/
├── src/code_guro/           # Main application package
│   ├── __init__.py          # Package version (0.1.0)
│   ├── cli.py               # CLI entry point - Click commands
│   ├── analyzer.py          # Codebase analysis engine
│   ├── generator.py         # Documentation generation via Claude
│   ├── frameworks.py        # Framework detection (Next.js, React, Django, etc.)
│   ├── prompts.py           # Claude API prompt templates
│   ├── config.py            # API key management and storage
│   ├── utils.py             # Token counting, file handling utilities
│   ├── errors.py            # Custom exception hierarchy
│   ├── repl.py              # Interactive conversation mode
│   ├── html_converter.py    # Markdown to HTML conversion
│   ├── templates/           # Mermaid diagram templates
│   ├── config_test.py       # Config module tests
│   ├── frameworks_test.py   # Framework detection tests
│   └── utils_test.py        # Utility function tests
├── tests/                   # Additional test directory
│   ├── __init__.py
│   └── integration/         # Integration tests
├── rules/                   # PRD and development guidelines
├── tasks/                   # Project task lists and documentation
├── pyproject.toml           # Project configuration (dependencies, tools)
├── setup.py                 # Minimal setuptools shim
├── README.md                # User documentation
└── .gitignore               # Git ignore rules
```

### Architectural Pattern
- **Modular CLI application** with clear separation of concerns
- **Data classes** for structured data (`FileInfo`, `AnalysisResult`, `FrameworkInfo`)
- **Decorator pattern** for cross-cutting concerns (API key validation, internet checks)

### Data Flow
```
CLI Input → Analyzer (file traversal, framework detection)
         → Generator (Claude API prompts)
         → Output files (code-guro-output/ directory)
```

---

## 3. Development Commands

### Installation

```bash
# Install in development mode with dev dependencies
pip install -e ".[dev]"

# Install with enhanced REPL features
pip install -e ".[enhanced]"

# Install everything (dev + enhanced)
pip install -e ".[all]"
```

### Testing

```bash
# Run all tests with verbose output
pytest

# Run specific test file
pytest src/code_guro/config_test.py
pytest src/code_guro/frameworks_test.py
pytest src/code_guro/utils_test.py

# Run with coverage
pytest --cov

# Run only tests matching a pattern
pytest -k "test_token"
```

### Code Quality

```bash
# Format code with Black
black src/

# Check linting with Ruff
ruff check src/

# Fix auto-fixable issues
ruff check src/ --fix
```

### CLI Commands

```bash
# Configure API key (stored in ~/.config/code-guro/config.json)
code-guro configure

# Analyze a local codebase
code-guro analyze .
code-guro analyze /path/to/project

# Analyze a GitHub repository
code-guro analyze https://github.com/user/repo

# Deep dive into specific files/folders
code-guro explain ./src/auth
code-guro explain ./src/auth --interactive
code-guro explain ./src/auth --output console

# Display version
code-guro --version
```

---

## 4. Testing Strategy

### Test Framework
- **pytest** with verbose output and short tracebacks
- Test discovery: files matching `*test*.py` or `test_*.py`
- Test paths: `src/` and `tests/` directories

### Test Configuration (pyproject.toml)
```toml
[tool.pytest.ini_options]
testpaths = ["src", "tests"]
python_files = ["*test*.py", "test_*.py"]
addopts = "-v --tb=short"
```

### Test Organization
Tests are colocated with source files in `src/code_guro/`:

| Test File | Coverage |
|-----------|----------|
| `config_test.py` | API key storage, environment variables, file permissions |
| `frameworks_test.py` | Framework detection for Next.js, React, Vue, Django, Flask, Express, Rails |
| `utils_test.py` | Token counting, cost estimation, file type detection |

### Test Patterns
- Class-based organization (e.g., `TestConfigDir`, `TestFrameworkMetadata`)
- Uses mocking and fixtures for isolated testing
- Tests cover edge cases: empty files, missing keys, invalid inputs

### Example Test Structure
```python
class TestTokenCounting:
    def test_count_tokens_empty_string(self):
        assert count_tokens("") == 0

    def test_count_tokens_with_content(self):
        result = count_tokens("Hello world")
        assert result > 0
```

---

## 5. Code Style & Standards

### Formatting (Black + Ruff)
- **Line length**: 100 characters
- **Target Python**: 3.8+
- **Ruff rules enabled**: E (pycodestyle), F (pyflakes), W (whitespace), I (isort), UP (upgrades), B (bugbear), C4 (comprehensions)
- **Ignored**: E501 (line too long - handled by Black)

### Naming Conventions

| Type | Convention | Example |
|------|------------|---------|
| Constants | UPPER_CASE | `MAX_FILE_SIZE`, `SAFE_CONTEXT_TOKENS` |
| Classes | PascalCase | `FileInfo`, `AnalysisResult` |
| Functions | snake_case | `analyze_codebase()`, `count_tokens()` |
| Boolean functions | Prefixed | `is_binary_file()`, `check_internet()` |
| Private functions | Underscore prefix | `_validate_key()` |

### Type Hints
- Full type hints throughout codebase
- Uses `Optional`, `List`, `Dict`, `Tuple` from typing
- Dataclasses with typed fields

### Docstring Style
```python
def analyze_codebase(path: str, max_files: int = 500) -> AnalysisResult:
    """Analyze a codebase and return structured results.

    Args:
        path: Path to the codebase directory or GitHub URL
        max_files: Maximum number of files to analyze

    Returns:
        AnalysisResult containing file info and framework detection

    Raises:
        AnalysisError: If the path is invalid or inaccessible
    """
```

### Import Organization
1. Standard library imports
2. Third-party imports (click, rich, anthropic)
3. Local imports (relative or absolute)

### Error Handling Pattern
- Custom exception hierarchy with `CodeGuroError` base class
- Specific exceptions: `ConfigurationError`, `APIKeyError`, `AnalysisError`, `NetworkError`, `GitHubError`
- User-friendly messages with hints in `ERROR_MESSAGES` dictionary

---

## 6. Boundaries & Constraints

### NEVER Modify or Commit

| Category | Items |
|----------|-------|
| **Secrets** | API keys, `~/.config/code-guro/config.json`, `.env` files |
| **Generated Output** | `code-guro-output/` directory (analysis results) |
| **Virtual Environments** | `venv/`, `.venv/`, `env/` |
| **Cache Directories** | `__pycache__/`, `.pytest_cache/`, `.ruff_cache/` |
| **Build Artifacts** | `build/`, `dist/`, `*.egg-info/` |
| **IDE Settings** | `.idea/`, `.vscode/` (unless shared configs) |

### File Filtering Rules (in analyzer.py)
These patterns are automatically skipped during analysis:

```python
ALWAYS_SKIP = {".git", "node_modules", "venv", ".venv", "__pycache__",
               ".pytest_cache", "dist", "build", ".next", ".nuxt"}
```

### Binary Extensions (30+ types)
Images, audio, archives, executables, and documents are automatically skipped.

### Size Limits
- **Max file size**: 1MB (larger files skipped)
- **Max context tokens**: 150,000 (safe working limit)
- **Max total tokens**: 200,000 (absolute limit)

### Deprecated Patterns to Avoid
- Direct API calls without error handling
- Hardcoded API keys
- Synchronous file operations for large files
- Print statements (use `rich.console.Console` instead)

### API Cost Awareness
- Input tokens: $3.00 per million
- Output tokens: $15.00 per million
- Cost confirmation threshold: $1.00 (prompts user)
- Always estimate costs before processing

---

## 7. Git Workflow

### Branching Strategy
- **`main`**: Production-ready code, always stable
- **`feature/*`**: Feature branches for new functionality
- Example: `feature/chunked-analysis`, `feature/code-guro-mvp`

### Commit Message Conventions
Follow conventional commits pattern:
```
<type>: <description>

[optional body]

[optional footer]
```

Types:
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `refactor`: Code refactoring
- `test`: Adding or updating tests
- `chore`: Maintenance tasks

### PR Requirements
- Feature branches merge to `main` via Pull Request
- PRs should include description of changes
- Tests should pass before merge

### Pre-commit Checks (Manual)
Before committing, run:
```bash
# Format code
black src/

# Check linting
ruff check src/

# Run tests
pytest
```

### .gitignore Categories
```
# Python artifacts
__pycache__/, *.pyc, *.pyo

# Testing
.pytest_cache/, .coverage, htmlcov/

# Virtual environments
venv/, .venv/, env/

# IDE
.idea/, .vscode/, *.swp

# Build
build/, dist/, *.egg-info/

# Project-specific
code-guro-output/
```

---

## Quick Reference

### Key Files for Common Tasks

| Task | Files to Modify |
|------|-----------------|
| Add CLI command | `src/code_guro/cli.py` |
| Modify analysis logic | `src/code_guro/analyzer.py` |
| Add new framework | `src/code_guro/frameworks.py` |
| Change Claude prompts | `src/code_guro/prompts.py` |
| Update error messages | `src/code_guro/errors.py` |
| Modify output format | `src/code_guro/generator.py` |

### Critical Constants (in utils.py)

```python
MAX_FILE_SIZE = 1_000_000        # 1MB
SAFE_CONTEXT_TOKENS = 150_000   # Safe working limit
MAX_CONTEXT_TOKENS = 200_000    # Absolute limit
INPUT_COST_PER_TOKEN = 0.000003  # $3/million
OUTPUT_COST_PER_TOKEN = 0.000015 # $15/million
```

### Claude Model Used
```python
MODEL = "claude-sonnet-4-20250514"
```

---

## Notes for AI Agents

1. **This is a Python CLI tool** - all source code is in `src/code_guro/`
2. **Tests are colocated** - test files live alongside source files
3. **Rich console is preferred** - use `rich.console.Console` for all output
4. **Cost awareness is critical** - always consider token costs when modifying prompts
5. **The tool generates documentation** - output goes to `code-guro-output/` directory
6. **Framework detection is extensible** - add new frameworks in `frameworks.py`
7. **API key is stored securely** - mode 0o600 in user config directory
