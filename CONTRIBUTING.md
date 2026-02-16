# Code Guro - Project Status

Code Guro is a **personal project** that I'm developing and maintaining solo. The code is public for transparency, learning, and forking - but I'm not accepting external contributions at this time.

## Bug Reports

If you encounter a bug, please open a GitHub Issue with:
- Your Python version and OS
- Steps to reproduce
- Expected vs actual behavior

I'll review and fix bugs as time permits.

## Feature Requests

Have an idea? Open an issue to discuss! I may add it to my roadmap if it aligns with the project vision, but there's no guarantee or timeline.

## Pull Requests

I want to keep Code Guro focused, high-quality, and aligned with my personal workflow. I'm **not accepting PRs** right now to maintain focus and control over the project direction.

## Forking

Want to take Code Guro in a different direction? **Forks are encouraged!** The MIT license allows you to:
- Modify the code for your needs
- Build your own variant
- Use it as a learning resource

---

## For Your Own Fork

If you're forking Code Guro and want to develop on it, here's the setup guide:

### Development Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/nicoladevera/code-guro.git
   cd code-guro
   ```

2. Create a virtual environment:
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install in development mode with dev dependencies:
   ```bash
   pip install -e ".[dev]"
   ```

4. Set up pre-commit hooks (recommended):
   ```bash
   pre-commit install
   ```

   This will automatically run Black and Ruff before each commit, preventing formatting issues.

5. Run tests:
   ```bash
   pytest
   ```

6. Check test coverage (optional):
   ```bash
   pytest --cov=code_guro --cov-report=term --cov-report=html
   ```

   This will generate a coverage report in `htmlcov/index.html`.

### Code Style

The codebase uses Black for formatting and Ruff for linting.

#### Automatic Checks (Recommended)

If you installed pre-commit hooks (step 4 above), these checks will run automatically before each commit:
- Black formatting
- Ruff linting
- Trailing whitespace removal
- File ending fixes

#### Manual Checks

If you prefer to run checks manually:

```bash
# Quick way - using Makefile
make quality

# Or run checks individually:
black src/              # Format code
ruff check src/ --fix   # Lint and auto-fix
pytest                  # Run tests
```

#### Other Useful Make Commands

```bash
make help         # Show all available commands
make format       # Format code only
make lint         # Lint code only
make test         # Run tests only
make pre-commit   # Run pre-commit on all files
make clean        # Clean up cache files
```

#### Python Version Compatibility

The codebase supports Python 3.8+. Keep these guidelines in mind:

- **Type hints**: Use `from __future__ import annotations` at the top of files that use modern type syntax
- **Avoid Python 3.9+ syntax**: Don't use `list[str]` or `dict[str, int]` without the future import; use `List[str]` from `typing` or add the annotations import
- **Avoid Python 3.10+ syntax**: Don't use `str | None`; use `Optional[str]` from `typing` instead

### Test Coverage

The codebase maintains high test coverage to ensure code quality and catch regressions early.

**Coverage Requirements:**
- **Target:** 80%+ overall coverage for production code
- **Minimum:** 60% coverage for new features
- **Critical modules:** 90%+ coverage for core functionality (generators, converters)

**Current Coverage:** 84% (51 tests across dual-format output, CLI commands, and generators)

**Running Coverage Reports:**

```bash
# Terminal report
pytest --cov=code_guro --cov-report=term

# HTML report (detailed, line-by-line)
pytest --cov=code_guro --cov-report=html
open htmlcov/index.html
```

**Writing Tests:**
- Place test files alongside the code they test (e.g., `cli.py` → `cli_test.py`)
- Use pytest fixtures from `conftest.py` for shared test infrastructure
- Mock external API calls (Claude API, GitHub, etc.) to keep tests fast and offline
- Use `tmp_path` fixture for file system tests to ensure isolation
- Write descriptive test names: `test_analyze_default_creates_dual_format`

**Test Organization:**
```
src/code_guro/
├── cli.py                    # Production code
├── cli_test.py               # Tests for cli.py
├── generator.py              # Production code
├── generator_test.py         # Tests for generator.py
├── html_converter.py         # Production code
├── html_converter_test.py    # Tests for html_converter.py
└── conftest.py               # Shared fixtures and test utilities
```
